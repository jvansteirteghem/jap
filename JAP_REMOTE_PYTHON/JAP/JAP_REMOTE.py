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

class InputProtocol(protocol.Protocol):
    def __init__(self):
        self.peer = None
        self.remoteAddressType = 0
        self.remoteAddress = ""
        self.remotePort = 0
        self.state = 0
        self.stateBuffer = ""
    
    def connectionMade(self):
        print "InputProtocol.connectionMade"

    def connectionLost(self, reason):
        print "InputProtocol.connectionLost"
        if self.peer is not None:
            self.peer.transport.loseConnection()
            self.peer = None
            
    def dataReceived(self, stateBuffer):
        print "InputProtocol.dataReceived"
        
        self.stateBuffer = self.stateBuffer + stateBuffer
        if self.state == 0:
            self.processState0()
            return
        if self.state == 1:
            self.processState1()
            return
        if self.state == 2:
            self.processState2()
            return
    
    def processState0(self):
        print "InputProtocol.processState0"
        
        if self.stateBuffer.find("\r\n\r\n") == -1:
            return
        
        authorized = False;

        if len(self.configuration["REMOTE_PROXY_SERVER"]["AUTHENTICATION"]) == 0:
            authorized = True
        
        if authorized == False:
            headers = self.stateBuffer.split("\r\n")
            
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
        
        self.state = 1
        self.stateBuffer = ""
    
    def processState1(self):
        print "InputProtocol.processState1"
        
        v, c, r, self.remoteAddressType = struct.unpack('!BBBB', self.stateBuffer[:4])
        
        # IPv4
        if self.remoteAddressType == 0x01:
            remoteAddress, self.remotePort = struct.unpack('!IH', self.stateBuffer[4:10])
            self.remoteAddress = socket.inet_ntoa(struct.pack('!I', remoteAddress))
        else:
            # DN
            if self.remoteAddressType == 0x03:
                remoteAddressLength = ord(self.stateBuffer[4])
                self.remoteAddress, self.remotePort = struct.unpack('!%dsH' % remoteAddressLength, self.stateBuffer[5:])
        
        print "InputProtocol.remoteAddressType: " + str(self.remoteAddressType)
        print "InputProtocol.remoteAddress: " + self.remoteAddress
        print "InputProtocol.remotePort: " + str(self.remotePort)
        
        factory = OutputProtocolFactory(self)
        factory.protocol = OutputProtocol
        reactor.connectTCP(self.remoteAddress, int(self.remotePort), factory)
    
    def processState2(self):
        print "InputProtocol.processState2"
        self.peer.transport.write(self.stateBuffer)
        
        self.stateBuffer = ""

class InputProtocolFactory(protocol.ClientFactory):
    def __init__(self, configuration):
        print "InputProtocolFactory.__init__"
        self.configuration = configuration
        self.configuration.setdefault("REMOTE_PROXY_SERVER", {})
        self.configuration["REMOTE_PROXY_SERVER"].setdefault("TYPE", "")
        self.configuration["REMOTE_PROXY_SERVER"].setdefault("ADDRESS", "")
        self.configuration["REMOTE_PROXY_SERVER"].setdefault("PORT", 0)
        self.configuration["REMOTE_PROXY_SERVER"].setdefault("AUTHENTICATION", [])
        i = 0
        while i < len(self.configuration["REMOTE_PROXY_SERVER"]["AUTHENTICATION"]):
            self.configuration["REMOTE_PROXY_SERVER"]["AUTHENTICATION"][i].setdefault("USERNAME", "")
            self.configuration["REMOTE_PROXY_SERVER"]["AUTHENTICATION"][i].setdefault("PASSWORD", "")
            i = i + 1
        self.configuration["REMOTE_PROXY_SERVER"].setdefault("CERTIFICATE", {})
        self.configuration["REMOTE_PROXY_SERVER"]["CERTIFICATE"].setdefault("KEY", {})
        self.configuration["REMOTE_PROXY_SERVER"]["CERTIFICATE"]["KEY"].setdefault("FILE", "")
        self.configuration["REMOTE_PROXY_SERVER"]["CERTIFICATE"].setdefault("FILE", "")
    
    def buildProtocol(self, *args, **kw):
        p = protocol.ClientFactory.buildProtocol(self, *args, **kw)
        p.configuration = self.configuration
        return p

class OutputProtocol(protocol.Protocol):
    def __init__(self):
        print "OutputProtocol.__init__"
        self.peer = None
    
    def connectionMade(self):
        print "OutputProtocol.connectionMade"
        self.peer.peer = self
        
        self.peer.state = 2
        self.peer.stateBuffer = ""
        
        #IPv4
        if self.peer.remoteAddressType == 0x01:
            remoteAddress = struct.unpack('!I', socket.inet_aton(self.peer.remoteAddress))[0]
            response = struct.pack('!BBBBIH', 0x05, 0x00, 0, 0x01, remoteAddress, self.peer.remotePort)
        else:
            # DN
            if self.peer.remoteAddressType == 0x03:
                remoteAddressLength = len(self.peer.remoteAddress)
                response = struct.pack('!BBBBB%dsH' % remoteAddressLength, 0x05, 0x00, 0, 0x03, remoteAddressLength, self.peer.remoteAddress, self.peer.remotePort)
        
        self.peer.transport.write(response)

    def connectionLost(self, reason):
        print "OutputProtocol.connectionLost"
        if self.peer is not None:
            self.peer.transport.loseConnection()
            self.peer = None
        
    def dataReceived(self, stateBuffer):
        print "OutputProtocol.dataReceived"
        self.peer.transport.write(stateBuffer)


class OutputProtocolFactory(protocol.ClientFactory):
    def __init__(self, peer):
        self.peer = peer
    
    def buildProtocol(self, *args, **kw):
        p = protocol.ClientFactory.buildProtocol(self, *args, **kw)
        p.peer = self.peer
        return p