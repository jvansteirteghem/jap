"""
JAP
Copyright (C) 2012 Jeroen Van Steirteghem

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
"""

from twisted.internet import protocol, reactor, tcp
from twisted.internet.abstract import isIPAddress, isIPv6Address
import base64
import struct
import json
import socket
import logging

logger = logging.getLogger(__name__)

class TunnelProtocol(protocol.Protocol):
    def __init__(self):
        logger.debug("TunnelProtocol.__init__")
        
        self.tunnelOutputProtocol = None
        self.outputProtocol = None
        
    def connectionMade(self):
        logger.debug("TunnelProtocol.connectionMade")
        
        tunnelOutputProtocolFactory = None
        
        if self.factory.configuration["PROXY_SERVER"]["TYPE"] == "HTTP":
            tunnelOutputProtocolFactory = HTTPTunnelOutputProtocolFactory(self.factory.configuration, self.factory.address, self.factory.port, self)
            tunnelOutputProtocolFactory.protocol = HTTPTunnelOutputProtocol
        else:
            if self.factory.configuration["PROXY_SERVER"]["TYPE"] == "SOCKS5":
                tunnelOutputProtocolFactory = SOCKS5TunnelOutputProtocolFactory(self.factory.configuration, self.factory.address, self.factory.port, self)
                tunnelOutputProtocolFactory.protocol = SOCKS5TunnelOutputProtocol
            else:
                self.transport.loseConnection()
                return
        
        self.tunnelOutputProtocol = tunnelOutputProtocolFactory.buildProtocol(self.transport.getPeer())
        self.tunnelOutputProtocol.makeConnection(self.transport)
        
    def connectionLost(self, reason):
        logger.debug("TunnelProtocol.connectionLost")
        
        if self.tunnelOutputProtocol is not None:
            self.tunnelOutputProtocol.connectionLost(reason)
        else:
            if self.outputProtocol is not None:
                self.outputProtocol.connectionLost(reason)
    
    def dataReceived(self, data):
        logger.debug("TunnelProtocol.dataReceived")
        
        if self.tunnelOutputProtocol is not None:
            self.tunnelOutputProtocol.dataReceived(data)
        else:
            if self.outputProtocol is not None:
                self.outputProtocol.dataReceived(data)
    
    def tunnelOutputProtocol_connectionMade(self, data):
        logger.debug("TunnelProtocol.tunnelOutputProtocol_connectionMade")
        
        self.tunnelOutputProtocol = None
        
        if self.factory.contextFactory is not None:
            self.transport.startTLS(self.factory.contextFactory)
        
        self.outputProtocol = self.factory.outputProtocolFactory.buildProtocol(self.transport.getPeer())
        self.outputProtocol.makeConnection(self.transport)
        
        if len(data) > 0:
            self.outputProtocol.dataReceived(data)

class TunnelProtocolFactory(protocol.ClientFactory):
    def __init__(self, configuration, address, port, outputProtocolFactory, contextFactory=None, timeout=30, bindAddress=None):
        logger.debug("TunnelProtocolFactory.__init__")
        
        self.configuration = configuration
        self.address = address
        self.port = port
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
        
        self.outputProtocolFactory.clientConnectionLost(connector, reason)

class Tunnel(object):
    def __init__(self, configuration):
        logger.debug("Tunnel.__init__")
        
        self.configuration = configuration
    
    def connect(self, address, port, outputProtocolFactory, contextFactory=None, timeout=30, bindAddress=None):
        logger.debug("Tunnel.connect")
        
        if self.configuration["PROXY_SERVER"]["TYPE"] == "":
            if contextFactory is None:
                return reactor.connectTCP(address, port, outputProtocolFactory, timeout, bindAddress)
            else:
                return reactor.connectSSL(address, port, outputProtocolFactory, contextFactory, timeout, bindAddress)
        else:
            tunnelProtocolFactory = TunnelProtocolFactory(self.configuration, address, port, outputProtocolFactory, contextFactory, timeout, bindAddress)
            tunnelProtocolFactory.protocol = TunnelProtocol
            
            return reactor.connectTCP(self.configuration["PROXY_SERVER"]["ADDRESS"], self.configuration["PROXY_SERVER"]["PORT"], tunnelProtocolFactory, timeout, bindAddress)

class HTTPTunnelOutputProtocol(protocol.Protocol):
    def __init__(self):
        logger.debug("HTTPTunnelOutputProtocol.__init__")
        
        self.data = ""
        self.dataState = 0
        
    def connectionMade(self):
        logger.debug("HTTPTunnelOutputProtocol.connectionMade")
        
        request = "CONNECT " + str(self.factory.address) + ":" + str(self.factory.port) + " HTTP/1.0\r\n"
        
        if self.factory.configuration["PROXY_SERVER"]["AUTHENTICATION"]["USERNAME"] != "":
            request = request + "Proxy-Authorization: Basic " + base64.standard_b64encode(self.factory.configuration["PROXY_SERVER"]["AUTHENTICATION"]["USERNAME"] + ":" + self.factory.configuration["PROXY_SERVER"]["AUTHENTICATION"]["PASSWORD"]) + "\r\n"
        
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
    def __init__(self, configuration, address, port, tunnelProtocol):
        logger.debug("HTTPTunnelOutputProtocolFactory.__init__")
        
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
    def __init__(self, configuration, address, port, tunnelProtocol):
        logger.debug("SOCKS5TunnelOutputProtocolFactory.__init__")
        
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

def setDefaultConfiguration(configuration):
    configuration.setdefault("LOGGER", {})
    configuration["LOGGER"].setdefault("LEVEL", "")
    configuration.setdefault("LOCAL_PROXY_SERVER", {})
    configuration["LOCAL_PROXY_SERVER"].setdefault("ADDRESS", "")
    configuration["LOCAL_PROXY_SERVER"].setdefault("PORT", 0)
    configuration.setdefault("PROXY_SERVER", {})
    configuration["PROXY_SERVER"].setdefault("TYPE", "")
    configuration["PROXY_SERVER"].setdefault("ADDRESS", "")
    configuration["PROXY_SERVER"].setdefault("PORT", 0)
    configuration["PROXY_SERVER"].setdefault("AUTHENTICATION", {})
    configuration["PROXY_SERVER"]["AUTHENTICATION"].setdefault("USERNAME", "")
    configuration["PROXY_SERVER"]["AUTHENTICATION"].setdefault("PASSWORD", "")

class OutputProtocol(protocol.Protocol):
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
        
    def inputProtocol_connectionLost(self, reason):
        logger.debug("OutputProtocol.inputProtocol_connectionLost")
        
        if self.connectionState == 1:
            self.transport.loseConnection()
        
    def inputProtocol_dataReceived(self, data):
        logger.debug("OutputProtocol.inputProtocol_dataReceived")
        
        if self.connectionState == 1:
            self.transport.write(data)

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
            response = struct.pack('!BBBBIH', 0x05, 0x00, 0x00, 0x01, 0, 0)
            self.transport.write(response)
            
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
        
class InputProtocolFactory(protocol.ClientFactory):
    def __init__(self, configuration):
        logger.debug("InputProtocolFactory.__init__")
        
        self.configuration = configuration
    
    def buildProtocol(self, *args, **kw):
        inputProtocol = protocol.ClientFactory.buildProtocol(self, *args, **kw)
        inputProtocol.configuration = self.configuration
        return inputProtocol