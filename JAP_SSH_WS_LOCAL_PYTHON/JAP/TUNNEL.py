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
import socket
import logging

logger = logging.getLogger("JAP.TUNNEL")

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
        
        connector = tcp.Connector(self.factory.address, self.factory.port, self.factory, self.factory.timeout, self.factory.bindAddress, reactor)
        
        if self.tunnelOutputProtocol is not None:
            self.tunnelOutputProtocol.connectionLost(reason)
            
            self.factory.outputProtocolFactory.clientConnectionFailed(connector, reason)
        else:
            if self.outputProtocol is not None:
                self.outputProtocol.connectionLost(reason)
                
                self.factory.outputProtocolFactory.clientConnectionLost(connector, reason)
            else:
                self.factory.outputProtocolFactory.clientConnectionFailed(connector, reason)
    
    def dataReceived(self, data):
        logger.debug("TunnelProtocol.dataReceived")
        
        if self.tunnelOutputProtocol is not None:
            self.tunnelOutputProtocol.dataReceived(data)
        else:
            if self.outputProtocol is not None:
                self.outputProtocol.dataReceived(data)
    
    def tunnelOutputProtocol_connectionMade(self):
        logger.debug("TunnelProtocol.tunnelOutputProtocol_connectionMade")
        
        self.tunnelOutputProtocol = None
        
        if self.factory.contextFactory is not None:
            self.transport.startTLS(self.factory.contextFactory)
        
        self.outputProtocol = self.factory.outputProtocolFactory.buildProtocol(self.transport.getPeer())
        self.outputProtocol.makeConnection(self.transport)

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
        
        #self.outputProtocolFactory.clientConnectionLost(connector, reason)

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
        
        if len(self.data) < 4:
            return
        
        if self.data[-4:] != "\r\n\r\n":
            return
        
        dataLines = self.data.split("\r\n")
        dataLine0 = dataLines[0]
        dataLine0Values = dataLine0.split(" ", 2)
        
        if len(dataLine0Values) != 3:
            self.transport.loseConnection()
            return
        
        if dataLine0Values[1] != "200":
            self.transport.loseConnection()
            return
        
        self.factory.tunnelProtocol.tunnelOutputProtocol_connectionMade()
        
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
        
        self.factory.tunnelProtocol.tunnelOutputProtocol_connectionMade()
        
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