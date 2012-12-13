"""
JAP
Copyright (C) 2012 Jeroen Van Steirteghem

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
"""

from twisted.internet import reactor, protocol, ssl
import struct
import json
import base64
import socket
import logging

logger = logging.getLogger("JAP.JAP_WS_REMOTE")

def setDefaultConfiguration(configuration):
    configuration.setdefault("REMOTE_PROXY_SERVER", {})
    configuration["REMOTE_PROXY_SERVER"].setdefault("TYPE", "")
    configuration["REMOTE_PROXY_SERVER"].setdefault("ADDRESS", "")
    configuration["REMOTE_PROXY_SERVER"].setdefault("PORT", 0)
    configuration["REMOTE_PROXY_SERVER"].setdefault("AUTHENTICATION", [])
    i = 0
    while i < len(configuration["REMOTE_PROXY_SERVER"]["AUTHENTICATION"]):
        configuration["REMOTE_PROXY_SERVER"]["AUTHENTICATION"][i].setdefault("USERNAME", "")
        configuration["REMOTE_PROXY_SERVER"]["AUTHENTICATION"][i].setdefault("PASSWORD", "")
        i = i + 1
    configuration["REMOTE_PROXY_SERVER"].setdefault("CERTIFICATE", {})
    configuration["REMOTE_PROXY_SERVER"]["CERTIFICATE"].setdefault("KEY", {})
    configuration["REMOTE_PROXY_SERVER"]["CERTIFICATE"]["KEY"].setdefault("FILE", "")
    configuration["REMOTE_PROXY_SERVER"]["CERTIFICATE"].setdefault("FILE", "")
        
class WSInputProtocol(protocol.Protocol):
    def __init__(self):
        logger.debug("WSInputProtocol.__init__")
        
        self.peer = None
        self.remoteAddressType = 0
        self.remoteAddress = ""
        self.remotePort = 0
        self.connectionState = 0
        self.data = ""
        self.dataState = 0
    
    def connectionMade(self):
        logger.debug("WSInputProtocol.connectionMade")
        
        self.connectionState = 1

    def connectionLost(self, reason):
        logger.debug("WSInputProtocol.connectionLost")
        
        self.connectionState = 2
        
        if self.peer is not None:
            self.peer.peer_connectionLost(reason)
            
    def dataReceived(self, data):
        logger.debug("WSInputProtocol.dataReceived")
        
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
        logger.debug("WSInputProtocol.processDataState0")
        
        if self.data.find("\r\n\r\n") == -1:
            return
        
        authorized = False;

        if len(self.configuration["REMOTE_PROXY_SERVER"]["AUTHENTICATION"]) == 0:
            authorized = True
        
        if authorized == False:
            headers = self.data.split("\r\n")
            
            for header in headers:
                headerValues = header.split(": ")
                if headerValues[0].upper() == "Authorization".upper():
                    authorization1 = headerValues[1]
                    
                    i = 0
                    while i < len(self.configuration["REMOTE_PROXY_SERVER"]["AUTHENTICATION"]):
                        authorization2 = "Basic " + base64.standard_b64encode(self.configuration["REMOTE_PROXY_SERVER"]["AUTHENTICATION"][i]["USERNAME"] + ":" + self.configuration["REMOTE_PROXY_SERVER"]["AUTHENTICATION"][i]["PASSWORD"])
                        
                        if authorization1 == authorization2:
                            authorized = True
                            break
                        
                        i = i + 1
        
        if authorized == False:
            response = "HTTP/1.1 401 Unauthorized\r\n"
            response = response + "WWW-Authenticate: Basic realm=\"JAP\"\r\n"
            response = response + "\r\n"
            
            self.transport.write(response)
            self.transport.loseConnection()
            
            return
        
        response = "HTTP/1.1 101 Web Socket Protocol Handshake\r\n"
        response = response + "Upgrade: WebSocket\r\n"
        response = response + "Connection: Upgrade\r\n"
        response = response + "\r\n"
        
        self.transport.write(response)
        
        self.data = ""
        self.dataState = 1
    
    def processDataState1(self):
        logger.debug("WSInputProtocol.processDataState1")
        
        v, c, r, self.remoteAddressType = struct.unpack('!BBBB', self.data[:4])
        
        # IPv4
        if self.remoteAddressType == 0x01:
            remoteAddress, self.remotePort = struct.unpack('!IH', self.data[4:10])
            self.remoteAddress = socket.inet_ntoa(struct.pack('!I', remoteAddress))
        else:
            # DN
            if self.remoteAddressType == 0x03:
                remoteAddressLength = ord(self.data[4])
                self.remoteAddress, self.remotePort = struct.unpack('!%dsH' % remoteAddressLength, self.data[5:])
        
        logger.debug("WSInputProtocol.remoteAddressType: " + str(self.remoteAddressType))
        logger.debug("WSInputProtocol.remoteAddress: " + self.remoteAddress)
        logger.debug("WSInputProtocol.remotePort: " + str(self.remotePort))
        
        factory = WSOutputProtocolFactory(self)
        factory.protocol = WSOutputProtocol
        reactor.connectTCP(self.remoteAddress, int(self.remotePort), factory)
    
    def processDataState2(self):
        logger.debug("WSInputProtocol.processDataState2")
        
        self.peer.peer_dataReceived(self.data)
        
        self.data = ""
        
    def peer_connectionMade(self):
        logger.debug("InputProtocol.peer_connectionMade")
        
        if self.connectionState == 1:
            #IPv4
            if self.remoteAddressType == 0x01:
                remoteAddress = struct.unpack('!I', socket.inet_aton(self.remoteAddress))[0]
                response = struct.pack('!BBBBIH', 0x05, 0x00, 0, 0x01, remoteAddress, self.remotePort)
            else:
                # DN
                if self.remoteAddressType == 0x03:
                    remoteAddressLength = len(self.remoteAddress)
                    response = struct.pack('!BBBBB%dsH' % remoteAddressLength, 0x05, 0x00, 0, 0x03, remoteAddressLength, self.remoteAddress, self.remotePort)
            
            self.transport.write(response)
            
            self.data = ""
            self.dataState = 2
        else:
            if self.connectionState == 2:
                self.peer.peer_connectionLost(None)
        
    def peer_connectionLost(self, reason):
        logger.debug("InputProtocol.peer_connectionLost")
        
        if self.connectionState == 1:
            self.transport.loseConnection()
        else:
            if self.connectionState == 2:
                self.peer.peer_connectionLost(None)
        
    def peer_dataReceived(self, data):
        logger.debug("InputProtocol.peer_dataReceived")
        
        if self.connectionState == 1:
            self.transport.write(data)
        else:
            if self.connectionState == 2:
                self.peer.peer_connectionLost(None)

class WSInputProtocolFactory(protocol.ClientFactory):
    def __init__(self, configuration):
        logger.debug("WSInputProtocolFactory.__init__")
        
        self.configuration = configuration
    
    def buildProtocol(self, *args, **kw):
        p = protocol.ClientFactory.buildProtocol(self, *args, **kw)
        p.configuration = self.configuration
        return p

class WSOutputProtocol(protocol.Protocol):
    def __init__(self):
        logger.debug("WSOutputProtocol.__init__")
        
        self.peer = None
        self.connectionState = 0
    
    def connectionMade(self):
        logger.debug("WSOutputProtocol.connectionMade")
        
        self.connectionState = 1
        
        self.peer.peer_connectionMade()

    def connectionLost(self, reason):
        logger.debug("WSOutputProtocol.connectionLost")
        
        self.connectionState = 2
        
        self.peer.peer_connectionLost(reason)
        
    def dataReceived(self, data):
        logger.debug("WSOutputProtocol.dataReceived")
        
        self.peer.peer_dataReceived(data)
        
    def peer_connectionMade(self):
        logger.debug("WSOutputProtocol.peer_connectionMade")
        
    def peer_connectionLost(self, reason):
        logger.debug("WSOutputProtocol.peer_connectionLost")
        
        if self.connectionState == 1:
            self.transport.abortConnection()
        
    def peer_dataReceived(self, data):
        logger.debug("WSOutputProtocol.peer_dataReceived")
        
        if self.connectionState == 1:
            self.transport.write(data)


class WSOutputProtocolFactory(protocol.ClientFactory):
    def __init__(self, peer):
        logger.debug("WSOutputProtocolFactory.__init__")
        
        self.peer = peer
    
    def buildProtocol(self, *args, **kw):
        p = protocol.ClientFactory.buildProtocol(self, *args, **kw)
        p.peer = self.peer
        p.peer.peer = p
        return p