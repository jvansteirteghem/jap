"""
JAP
Copyright (C) 2012 Jeroen Van Steirteghem

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
"""

from zope.interface import implements
from twisted.internet import protocol, reactor, tcp, interfaces, base
from twisted.internet.abstract import isIPAddress, isIPv6Address
from twisted.names import client, resolve, cache, hosts
import base64
import struct
import json
import socket
import logging
import re
import collections

logger = logging.getLogger(__name__)

class HostsResolver(hosts.Resolver):
    lookupAllRecords = hosts.Resolver.lookupAddress

class ClientResolver(client.Resolver):
    lookupAllRecords = client.Resolver.lookupAddress

def createResolver(configuration):
    resolverFile = configuration["DNS_RESOLVER"]["HOSTS"]["FILE"]
    resolverServers = []
    i = 0
    while i < len(configuration["DNS_RESOLVER"]["SERVERS"]):
        resolverServers.append((configuration["DNS_RESOLVER"]["SERVERS"][i]["ADDRESS"], configuration["DNS_RESOLVER"]["SERVERS"][i]["PORT"]))
        i = i + 1
    
    resolvers = []
    if resolverFile != "":
        resolvers.append(HostsResolver(file=resolverFile))
    if len(resolverServers) != 0:
        resolvers.append(cache.CacheResolver())
        resolvers.append(ClientResolver(servers=resolverServers))
    
    if len(resolvers) != 0:
        return resolve.ResolverChain(resolvers)
    else:
        return base.BlockingResolver()

class TunnelProtocol(protocol.Protocol):
    def __init__(self):
        logger.debug("TunnelProtocol.__init__")
        
        self.tunnelOutputProtocol = None
        self.tunnelOutputProtocolFactory = None
        
    def connectionMade(self):
        logger.debug("TunnelProtocol.connectionMade")
        
        if self.factory.configuration["PROXY_SERVERS"][self.factory.i]["TYPE"] == "HTTP":
            self.tunnelOutputProtocolFactory = HTTPTunnelOutputProtocolFactory(self.factory.i, self.factory.configuration, self.factory.address, self.factory.port, self)
            self.tunnelOutputProtocolFactory.protocol = HTTPTunnelOutputProtocol
        else:
            if self.factory.configuration["PROXY_SERVERS"][self.factory.i]["TYPE"] == "SOCKS5":
                self.tunnelOutputProtocolFactory = SOCKS5TunnelOutputProtocolFactory(self.factory.i, self.factory.configuration, self.factory.address, self.factory.port, self)
                self.tunnelOutputProtocolFactory.protocol = SOCKS5TunnelOutputProtocol
            else:
                self.transport.loseConnection()
                return
        
        self.tunnelOutputProtocol = self.tunnelOutputProtocolFactory.buildProtocol(self.transport.getPeer())
        self.tunnelOutputProtocol.makeConnection(self.transport)
        
    def connectionLost(self, reason):
        logger.debug("TunnelProtocol.connectionLost")
        
        if self.tunnelOutputProtocol is not None:
            self.tunnelOutputProtocol.connectionLost(reason)
        else:
            if self.factory.outputProtocol is not None:
                self.factory.outputProtocol.connectionLost(reason)
    
    def dataReceived(self, data):
        logger.debug("TunnelProtocol.dataReceived")
        
        if self.tunnelOutputProtocol is not None:
            self.tunnelOutputProtocol.dataReceived(data)
        else:
            if self.factory.outputProtocol is not None:
                self.factory.outputProtocol.dataReceived(data)
    
    def tunnelOutputProtocol_connectionMade(self, data):
        logger.debug("TunnelProtocol.tunnelOutputProtocol_connectionMade")
        
        self.tunnelOutputProtocol = None
        
        if self.factory.contextFactory is not None:
            self.transport.startTLS(self.factory.contextFactory)
        
        self.factory.outputProtocol = self.factory.outputProtocolFactory.buildProtocol(self.transport.getPeer())
        self.factory.outputProtocol.makeConnection(self.transport)
        
        if len(data) > 0:
            self.factory.outputProtocol.dataReceived(data)

class TunnelProtocolFactory(protocol.ClientFactory):
    def __init__(self, i, configuration, address, port, outputProtocolFactory, contextFactory=None, timeout=30, bindAddress=None):
        logger.debug("TunnelProtocolFactory.__init__")
        
        self.i = i
        self.configuration = configuration
        self.address = address
        self.port = port
        self.outputProtocol = None
        self.outputProtocolFactory = outputProtocolFactory
        self.contextFactory = contextFactory
        self.timeout = timeout
        self.bindAddress = bindAddress
    
    def startedConnecting(self, connector):
        logger.debug("TunnelProtocolFactory.startedConnecting")
        
        self.outputProtocolFactory.startedConnecting(connector)
    
    def clientConnectionFailed(self, connector, reason):
        logger.debug("TunnelProtocolFactory.clientConnectionFailed")
        
        self.outputProtocolFactory.clientConnectionFailed(connector, reason)
    
    def clientConnectionLost(self, connector, reason):
        logger.debug("TunnelProtocolFactory.clientConnectionLost")
        
        if self.outputProtocol is None:
            self.outputProtocolFactory.clientConnectionFailed(connector, reason)
        else:
            self.outputProtocolFactory.clientConnectionLost(connector, reason)

class Tunnel(object):
    def __init__(self, configuration):
        logger.debug("Tunnel.__init__")
        
        self.configuration = configuration
    
    def connect(self, address, port, outputProtocolFactory, contextFactory=None, timeout=30, bindAddress=None):
        logger.debug("Tunnel.connect")
        
        if len(self.configuration["PROXY_SERVERS"]) == 0:
            if contextFactory is None:
                return reactor.connectTCP(address, port, outputProtocolFactory, timeout, bindAddress)
            else:
                return reactor.connectSSL(address, port, outputProtocolFactory, contextFactory, timeout, bindAddress)
        else:
            i = len(self.configuration["PROXY_SERVERS"])
            
            tunnelProtocolFactory = TunnelProtocolFactory(i - 1, self.configuration, address, port, outputProtocolFactory, contextFactory, timeout, bindAddress)
            tunnelProtocolFactory.protocol = TunnelProtocol
            
            i = i - 1
            
            while i > 0:
                tunnelProtocolFactory = TunnelProtocolFactory(i - 1, self.configuration, self.configuration["PROXY_SERVERS"][i]["ADDRESS"], self.configuration["PROXY_SERVERS"][i]["PORT"], tunnelProtocolFactory, contextFactory, timeout, bindAddress)
                tunnelProtocolFactory.protocol = TunnelProtocol
                
                i = i - 1
            
            return reactor.connectTCP(self.configuration["PROXY_SERVERS"][i]["ADDRESS"], self.configuration["PROXY_SERVERS"][i]["PORT"], tunnelProtocolFactory, timeout, bindAddress)

class HTTPTunnelOutputProtocol(protocol.Protocol):
    def __init__(self):
        logger.debug("HTTPTunnelOutputProtocol.__init__")
        
        self.data = ""
        self.dataState = 0
        
    def connectionMade(self):
        logger.debug("HTTPTunnelOutputProtocol.connectionMade")
        
        request = "CONNECT " + str(self.factory.address) + ":" + str(self.factory.port) + " HTTP/1.0\r\n"
        
        if self.factory.configuration["PROXY_SERVERS"][self.factory.i]["AUTHENTICATION"]["USERNAME"] != "":
            request = request + "Proxy-Authorization: Basic " + base64.standard_b64encode(self.factory.configuration["PROXY_SERVERS"][self.factory.i]["AUTHENTICATION"]["USERNAME"] + ":" + self.factory.configuration["PROXY_SERVERS"][self.factory.i]["AUTHENTICATION"]["PASSWORD"]) + "\r\n"
        
        request = request + "\r\n"
        
        self.transport.write(request)
        
    def connectionLost(self, reason):
        logger.debug("HTTPTunnelOutputProtocol.connectionLost")
    
    def dataReceived(self, data):
        logger.debug("HTTPTunnelOutputProtocol.dataReceived")
        
        self.data = self.data + data
        if self.dataState == 0:
            self.processDataState0()
            return
    
    def processDataState0(self):
        logger.debug("HTTPTunnelOutputProtocol.processDataState0")
        
        i = self.data.find("\r\n\r\n")
        
        if i == -1:
            return
            
        i = i + 4
        
        dataLines = self.data[:i].split("\r\n")
        dataLine0 = dataLines[0]
        dataLine0Values = dataLine0.split(" ", 2)
        
        if len(dataLine0Values) != 3:
            self.transport.loseConnection()
            return
        
        if dataLine0Values[1] != "200":
            self.transport.loseConnection()
            return
        
        self.factory.tunnelProtocol.tunnelOutputProtocol_connectionMade(self.data[i:])
        
        self.data = ""
        self.dataState = 1

class HTTPTunnelOutputProtocolFactory(protocol.ClientFactory):
    def __init__(self, i, configuration, address, port, tunnelProtocol):
        logger.debug("HTTPTunnelOutputProtocolFactory.__init__")
        
        self.i = i
        self.configuration = configuration
        self.address = address
        self.port = port
        self.tunnelProtocol = tunnelProtocol
    
    def startedConnecting(self, connector):
        logger.debug("HTTPTunnelOutputProtocolFactory.startedConnecting")
    
    def clientConnectionFailed(self, connector, reason):
        logger.debug("HTTPTunnelOutputProtocolFactory.clientConnectionFailed")
    
    def clientConnectionLost(self, connector, reason):
        logger.debug("HTTPTunnelOutputProtocolFactory.clientConnectionLost")

class SOCKS5TunnelOutputProtocol(protocol.Protocol):
    def __init__(self):
        logger.debug("SOCKS5TunnelOutputProtocol.__init__")
        
        self.data = ""
        self.dataState = 0
    
    def connectionMade(self):
        logger.debug("SOCKS5TunnelOutputProtocol.connectionMade")
        
        request = struct.pack("!BBB", 0x05, 0x01, 0x00)
        
        self.transport.write(request)
    
    def connectionLost(self, reason):
        logger.debug("SOCKS5TunnelOutputProtocol.connectionLost")
    
    def dataReceived(self, data):
        logger.debug("SOCKS5TunnelOutputProtocol.dataReceived")
        
        self.data = self.data + data
        if self.dataState == 0:
            self.processDataState0()
            return
        
        if self.dataState == 1:
            self.processDataState1()
            return
    
    def processDataState0(self):
        logger.debug("SOCKS5TunnelOutputProtocol.processDataState0")
        
        if len(self.data) < 2:
            return
        
        if ord(self.data[0]) != 0x05:
            self.transport.loseConnection()
            return
        
        addressType = 0x03
        if isIPAddress(self.factory.address) == True:
            addressType = 0x01
        else:
            if isIPv6Address(self.factory.address) == True:
                addressType = 0x04
        
        request = struct.pack("!BBB", 0x05, 0x01, 0x00)
        
        if addressType == 0x01:
            address = struct.unpack("!I", socket.inet_aton(self.factory.address))[0]
            request = request + struct.pack("!BI", 0x01, address)
        else:
            if addressType == 0x03:
                address = str(self.factory.address)
                addressLength = len(address)
                request = request + struct.pack("!BB%ds" % addressLength, 0x03, addressLength, address)
            else:
                self.transport.loseConnection()
                return
        
        request = request + struct.pack("!H", self.factory.port)
        
        self.transport.write(request)
        
        self.data = ""
        self.dataState = 1
    
    def processDataState1(self):
        logger.debug("SOCKS5TunnelOutputProtocol.processDataState1")
        
        if len(self.data) < 10:
            return
        
        if ord(self.data[0]) != 0x05:
            self.transport.loseConnection()
            return
        
        if ord(self.data[1]) != 0x00:
            self.transport.loseConnection()
            return
        
        self.factory.tunnelProtocol.tunnelOutputProtocol_connectionMade(self.data[10:])
        
        self.data = ""
        self.dataState = 2

class SOCKS5TunnelOutputProtocolFactory(protocol.ClientFactory):
    def __init__(self, i, configuration, address, port, tunnelProtocol):
        logger.debug("SOCKS5TunnelOutputProtocolFactory.__init__")
        
        self.i = i
        self.configuration = configuration
        self.address = address
        self.port = port
        self.tunnelProtocol = tunnelProtocol
    
    def startedConnecting(self, connector):
        logger.debug("SOCKS5TunnelOutputProtocolFactory.startedConnecting")
    
    def clientConnectionFailed(self, connector, reason):
        logger.debug("SOCKS5TunnelOutputProtocolFactory.clientConnectionFailed")
    
    def clientConnectionLost(self, connector, reason):
        logger.debug("SOCKS5TunnelOutputProtocolFactory.clientConnectionLost")

class JSONDecoder(json.JSONDecoder):
    def __init__(self):
        json.JSONDecoder.__init__(self, object_pairs_hook=collections.OrderedDict)
    
    def decode(self, data):
        data = re.sub(re.compile("/\*.*?\*/", re.DOTALL), "", data)
        
        return super(JSONDecoder, self).decode(data)

class JSONEncoder(json.JSONEncoder):
    def __init__(self):
        json.JSONEncoder.__init__(self, sort_keys=False, indent=4, separators=(",", ": "))
    
    def encode(self, data):
        return super(JSONEncoder, self).encode(data)

def getDefaultConfiguration(configuration=None):
    if configuration is None:
        configuration = collections.OrderedDict()
    
    configuration.setdefault("LOGGER", collections.OrderedDict())
    configuration["LOGGER"].setdefault("LEVEL", "")
    configuration.setdefault("DNS_RESOLVER", collections.OrderedDict())
    configuration["DNS_RESOLVER"].setdefault("HOSTS", collections.OrderedDict())
    configuration["DNS_RESOLVER"]["HOSTS"].setdefault("FILE", "")
    configuration["DNS_RESOLVER"].setdefault("SERVERS", [])
    i = 0
    while i < len(configuration["DNS_RESOLVER"]["SERVERS"]):
        configuration["DNS_RESOLVER"]["SERVERS"][i].setdefault("ADDRESS", "")
        configuration["DNS_RESOLVER"]["SERVERS"][i].setdefault("PORT", 0)
        i = i + 1
    configuration.setdefault("PROXY_SERVERS", [])
    i = 0
    while i < len(configuration["PROXY_SERVERS"]):
        configuration["PROXY_SERVERS"][i].setdefault("TYPE", "")
        configuration["PROXY_SERVERS"][i].setdefault("ADDRESS", "")
        configuration["PROXY_SERVERS"][i].setdefault("PORT", 0)
        configuration["PROXY_SERVERS"][i].setdefault("AUTHENTICATION", collections.OrderedDict())
        configuration["PROXY_SERVERS"][i]["AUTHENTICATION"].setdefault("USERNAME", "")
        configuration["PROXY_SERVERS"][i]["AUTHENTICATION"].setdefault("PASSWORD", "")
        i = i + 1
    configuration.setdefault("LOCAL_PROXY_SERVER", collections.OrderedDict())
    configuration["LOCAL_PROXY_SERVER"].setdefault("ADDRESS", "")
    configuration["LOCAL_PROXY_SERVER"].setdefault("PORT", 0)
    
    defaultConfiguration = collections.OrderedDict()
    defaultConfiguration["LOGGER"] = collections.OrderedDict()
    defaultConfiguration["LOGGER"]["LEVEL"] = configuration["LOGGER"]["LEVEL"]
    defaultConfiguration["DNS_RESOLVER"] = collections.OrderedDict()
    defaultConfiguration["DNS_RESOLVER"]["HOSTS"] = collections.OrderedDict()
    defaultConfiguration["DNS_RESOLVER"]["HOSTS"]["FILE"] = configuration["DNS_RESOLVER"]["HOSTS"]["FILE"]
    defaultConfiguration["DNS_RESOLVER"]["SERVERS"] = []
    i = 0
    while i < len(configuration["DNS_RESOLVER"]["SERVERS"]):
        defaultConfiguration["DNS_RESOLVER"]["SERVERS"].append(collections.OrderedDict())
        defaultConfiguration["DNS_RESOLVER"]["SERVERS"][i]["ADDRESS"] = configuration["DNS_RESOLVER"]["SERVERS"][i]["ADDRESS"]
        defaultConfiguration["DNS_RESOLVER"]["SERVERS"][i]["PORT"] = configuration["DNS_RESOLVER"]["SERVERS"][i]["PORT"]
        i = i + 1
    defaultConfiguration["PROXY_SERVERS"] = []
    i = 0
    while i < len(configuration["PROXY_SERVERS"]):
        defaultConfiguration["PROXY_SERVERS"].append(collections.OrderedDict())
        defaultConfiguration["PROXY_SERVERS"][i]["TYPE"] = configuration["PROXY_SERVERS"][i]["TYPE"]
        defaultConfiguration["PROXY_SERVERS"][i]["ADDRESS"] = configuration["PROXY_SERVERS"][i]["ADDRESS"]
        defaultConfiguration["PROXY_SERVERS"][i]["PORT"] = configuration["PROXY_SERVERS"][i]["PORT"]
        defaultConfiguration["PROXY_SERVERS"][i]["AUTHENTICATION"] = configuration["PROXY_SERVERS"][i]["AUTHENTICATION"]
        defaultConfiguration["PROXY_SERVERS"][i]["AUTHENTICATION"]["USERNAME"] = configuration["PROXY_SERVERS"][i]["AUTHENTICATION"]["USERNAME"]
        defaultConfiguration["PROXY_SERVERS"][i]["AUTHENTICATION"]["PASSWORD"] = configuration["PROXY_SERVERS"][i]["AUTHENTICATION"]["PASSWORD"]
        i = i + 1
    defaultConfiguration["LOCAL_PROXY_SERVER"] = collections.OrderedDict()
    defaultConfiguration["LOCAL_PROXY_SERVER"]["ADDRESS"] = configuration["LOCAL_PROXY_SERVER"]["ADDRESS"]
    defaultConfiguration["LOCAL_PROXY_SERVER"]["PORT"] = configuration["LOCAL_PROXY_SERVER"]["PORT"]
    
    return defaultConfiguration

def getConfiguration(configurationFile, getDefaultConfiguration=None):
    file = open(configurationFile, "r")
    data = file.read()
    file.close()
    
    decoder = JSONDecoder()
    configuration = decoder.decode(data)
    
    if getDefaultConfiguration is not None:
        configuration = getDefaultConfiguration(configuration)
    
    return configuration

def setConfiguration(configurationFile, configuration, getDefaultConfiguration=None):
    if getDefaultConfiguration is not None:
        configuration = getDefaultConfiguration(configuration)
    
    encoder = JSONEncoder()
    data = encoder.encode(configuration)
    
    file = open(configurationFile, "w")
    file.write(data)
    file.close()

class OutputProtocol(protocol.Protocol):
    implements(interfaces.IPushProducer)
    
    def __init__(self):
        logger.debug("OutputProtocol.__init__")
        
        self.inputProtocol = None
        self.connectionState = 0
        
    def connectionMade(self):
        logger.debug("OutputProtocol.connectionMade")
        
        self.connectionState = 1
        
        self.inputProtocol.outputProtocol_connectionMade()
        
    def connectionLost(self, reason):
        logger.debug("OutputProtocol.connectionLost")
        
        self.connectionState = 2
        
        self.inputProtocol.outputProtocol_connectionLost(reason)
        
    def dataReceived(self, data):
        logger.debug("OutputProtocol.dataReceived")
        
        self.inputProtocol.outputProtocol_dataReceived(data)
        
    def inputProtocol_connectionMade(self):
        logger.debug("OutputProtocol.inputProtocol_connectionMade")
        
        if self.connectionState == 1:
            self.transport.registerProducer(self.inputProtocol, True)
        
    def inputProtocol_connectionLost(self, reason):
        logger.debug("OutputProtocol.inputProtocol_connectionLost")
        
        if self.connectionState == 1:
            self.transport.unregisterProducer()
            self.transport.loseConnection()
        
    def inputProtocol_dataReceived(self, data):
        logger.debug("OutputProtocol.inputProtocol_dataReceived")
        
        if self.connectionState == 1:
            self.transport.write(data)
    
    def pauseProducing(self):
        logger.debug("OutputProtocol.pauseProducing")
        
        if self.connectionState == 1:
            self.transport.pauseProducing()
    
    def resumeProducing(self):
        logger.debug("OutputProtocol.resumeProducing")
        
        if self.connectionState == 1:
            self.transport.resumeProducing()
    
    def stopProducing(self):
        logger.debug("OutputProtocol.stopProducing")
        
        if self.connectionState == 1:
            self.transport.stopProducing()

class OutputProtocolFactory(protocol.ClientFactory):
    def __init__(self, inputProtocol):
        logger.debug("OutputProtocolFactory.__init__")
        
        self.inputProtocol = inputProtocol
        
    def buildProtocol(self, *args, **kw):
        outputProtocol = protocol.ClientFactory.buildProtocol(self, *args, **kw)
        outputProtocol.inputProtocol = self.inputProtocol
        outputProtocol.inputProtocol.outputProtocol = outputProtocol
        return outputProtocol
    
    def clientConnectionFailed(self, connector, reason):
        logger.debug("OutputProtocolFactory.clientConnectionFailed")
        
        self.inputProtocol.outputProtocol_connectionFailed(reason)

class InputProtocol(protocol.Protocol):
    implements(interfaces.IPushProducer)
    
    def __init__(self):
        logger.debug("InputProtocol.__init__")
        
        self.configuration = None
        self.outputProtocol = None
        self.remoteAddressType = 0
        self.remoteAddress = ""
        self.remotePort = 0
        self.connectionState = 0
        self.data = ""
        self.dataState = 0
    
    def connect(self):
        logger.debug("InputProtocol.connect")
        
        outputProtocolFactory = OutputProtocolFactory(self)
        outputProtocolFactory.protocol = OutputProtocol
        
        tunnel = Tunnel(self.configuration)
        tunnel.connect(self.remoteAddress, self.remotePort, outputProtocolFactory)
    
    def connectionMade(self):
        logger.debug("InputProtocol.connectionMade")
        
        self.connectionState = 1
    
    def connectionLost(self, reason):
        logger.debug("InputProtocol.connectionLost")
        
        self.connectionState = 2
        
        if self.outputProtocol is not None:
            self.outputProtocol.inputProtocol_connectionLost(reason)
    
    def dataReceived(self, data):
        logger.debug("InputProtocol.dataReceived")
        
        self.data = self.data + data
        if self.dataState == 0:
            self.processDataState0()
            return
        if self.dataState == 1:
            self.processDataState1()
            return
        if self.dataState == 2:
            self.processDataState2()
            return
    
    def processDataState0(self):
        logger.debug("InputProtocol.processDataState0")
        
        # no authentication
        self.transport.write(struct.pack('!BB', 0x05, 0x00))
        
        self.data = ""
        self.dataState = 1
    
    def processDataState1(self):
        logger.debug("InputProtocol.processDataState1")
        
        v, c, r, self.remoteAddressType = struct.unpack('!BBBB', self.data[:4])
        
        # IPv4
        if self.remoteAddressType == 0x01:
            remoteAddress, self.remotePort = struct.unpack('!IH', self.data[4:10])
            self.remoteAddress = socket.inet_ntoa(struct.pack('!I', remoteAddress))
            self.data = self.data[10:]
        else:
            # DN
            if self.remoteAddressType == 0x03:
                remoteAddressLength = ord(self.data[4])
                self.remoteAddress, self.remotePort = struct.unpack('!%dsH' % remoteAddressLength, self.data[5:])
                self.data = self.data[7 + remoteAddressLength:]
            # IPv6
            else:
                response = struct.pack('!BBBBIH', 0x05, 0x08, 0x00, 0x01, 0, 0)
                self.transport.write(response)
                self.transport.loseConnection()
                return
        
        logger.debug("InputProtocol.remoteAddressType: " + str(self.remoteAddressType))
        logger.debug("InputProtocol.remoteAddress: " + self.remoteAddress)
        logger.debug("InputProtocol.remotePort: " + str(self.remotePort))
        
        # connect
        if c == 0x01:
            self.connect()
        else:
            response = struct.pack('!BBBBIH', 0x05, 0x07, 0x00, 0x01, 0, 0)
            self.transport.write(response)
            self.transport.loseConnection()
            return
        
    def processDataState2(self):
        logger.debug("InputProtocol.processDataState2")
        
        self.outputProtocol.inputProtocol_dataReceived(self.data)
        
        self.data = ""
        
    def outputProtocol_connectionMade(self):
        logger.debug("InputProtocol.outputProtocol_connectionMade")
        
        if self.connectionState == 1:
            self.transport.registerProducer(self.outputProtocol, True)
            
            response = struct.pack('!BBBBIH', 0x05, 0x00, 0x00, 0x01, 0, 0)
            self.transport.write(response)
            
            self.outputProtocol.inputProtocol_connectionMade()
            
            self.data = ""
            self.dataState = 2
        else:
            if self.connectionState == 2:
                self.outputProtocol.inputProtocol_connectionLost(None)
        
    def outputProtocol_connectionFailed(self, reason):
        logger.debug("InputProtocol.outputProtocol_connectionFailed")
        
        if self.connectionState == 1:
            response = struct.pack('!BBBBIH', 0x05, 0x05, 0x00, 0x01, 0, 0)
            self.transport.write(response)
            self.transport.loseConnection()
        
    def outputProtocol_connectionLost(self, reason):
        logger.debug("InputProtocol.outputProtocol_connectionLost")
        
        if self.connectionState == 1:
            self.transport.unregisterProducer()
            self.transport.loseConnection()
        else:
            if self.connectionState == 2:
                self.outputProtocol.inputProtocol_connectionLost(None)
        
    def outputProtocol_dataReceived(self, data):
        logger.debug("InputProtocol.outputProtocol_dataReceived")
        
        if self.connectionState == 1:
            self.transport.write(data)
        else:
            if self.connectionState == 2:
                self.outputProtocol.inputProtocol_connectionLost(None)
    
    def pauseProducing(self):
        logger.debug("InputProtocol.pauseProducing")
        
        if self.connectionState == 1:
            self.transport.pauseProducing()
    
    def resumeProducing(self):
        logger.debug("InputProtocol.resumeProducing")
        
        if self.connectionState == 1:
            self.transport.resumeProducing()
    
    def stopProducing(self):
        logger.debug("InputProtocol.stopProducing")
        
        if self.connectionState == 1:
            self.transport.stopProducing()
        
class InputProtocolFactory(protocol.ClientFactory):
    def __init__(self, configuration):
        logger.debug("InputProtocolFactory.__init__")
        
        self.configuration = configuration
    
    def buildProtocol(self, *args, **kw):
        inputProtocol = protocol.ClientFactory.buildProtocol(self, *args, **kw)
        inputProtocol.configuration = self.configuration
        return inputProtocol