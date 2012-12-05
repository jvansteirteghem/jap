"""
JAP
Copyright (C) 2012 Jeroen Van Steirteghem

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
"""

from twisted.internet import protocol, reactor
import struct
import json
import socket
import TUNNEL

class OutputProtocol(protocol.Protocol):
    def __init__(self):
        print "OutputProtocol.__init__"
        
        self.peer = None
        
    def connectionMade(self):
        print "OutputProtocol.connectionMade"
        
        self.peer.peer = self
        self.peer.peer_connectionMade()
        
    def connectionLost(self, reason):
        print "OutputProtocol.connectionLost"
        
        if self.peer is not None:
            self.peer.peer_connectionLost(reason)
            self.peer = None
        
    def dataReceived(self, data):
        print "OutputProtocol.dataReceived"
        
        self.peer.peer_dataReceived(data)
        
    def peer_connectionMade(self):
        print "OutputProtocol.peer_connectionMade"
        
    def peer_connectionLost(self, reason):
        print "OutputProtocol.peer_connectionLost"
        
        self.transport.loseConnection()
        
    def peer_dataReceived(self, data):
        print "OutputProtocol.peer_dataReceived"
        
        self.transport.write(data)

class OutputProtocolFactory(protocol.ClientFactory):
    def __init__(self, peer):
        print "OutputProtocolFactory.__init__"
        
        self.peer = peer
        
    def buildProtocol(self, *args, **kw):
        p = protocol.ClientFactory.buildProtocol(self, *args, **kw)
        p.peer = self.peer
        return p

class InputProtocol(protocol.Protocol):
    def __init__(self):
        print "InputProtocol.__init__"
        
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
            self.peer.peer_connectionLost(reason)
            self.peer = None
    
    def dataReceived(self, data):
        print "InputProtocol.dataReceived"
        
        self.stateBuffer = self.stateBuffer + data
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
        
        # no authentication
        self.transport.write(struct.pack('!BB', 0x05, 0x00))
        
        self.state = 1
        self.stateBuffer = ""
    
    def processState1(self):
        print "InputProtocol.processState1"
        
        v, c, r, self.remoteAddressType = struct.unpack('!BBBB', self.stateBuffer[:4])
        
        # IPv4
        if self.remoteAddressType == 0x01:
            remoteAddress, self.remotePort = struct.unpack('!IH', self.stateBuffer[4:10])
            self.remoteAddress = socket.inet_ntoa(struct.pack('!I', remoteAddress))
            self.stateBuffer = self.stateBuffer[10:]
        else:
            # DN
            if self.remoteAddressType == 0x03:
                remoteAddressLength = ord(self.stateBuffer[4])
                self.remoteAddress, self.remotePort = struct.unpack('!%dsH' % remoteAddressLength, self.stateBuffer[5:])
                self.stateBuffer = self.stateBuffer[7 + remoteAddressLength:]
            # IPv6
            else:
                response = struct.pack('!BBBBIH', 0x05, 0x08, 0, 1, 0, 0)
                self.transport.write(response)
                self.transport.loseConnection()
                return
        
        print "InputProtocol.remoteAddressType: " + str(self.remoteAddressType)
        print "InputProtocol.remoteAddress: " + self.remoteAddress
        print "InputProtocol.remotePort: " + str(self.remotePort)
        
        # connect
        if c == 0x01:
            self.do_CONNECT()
        else:
            response = struct.pack('!BBBBIH', 0x05, 0x07, 0, 1, 0, 0)
            self.transport.write(response)
            self.transport.loseConnection()
            return
            
    def do_CONNECT(self):
        factory = OutputProtocolFactory(self)
        factory.protocol = OutputProtocol
        
        if self.configuration["PROXY_SERVER"]["ADDRESS"] != "":
            tunnel = TUNNEL.Tunnel(self.configuration["PROXY_SERVER"]["ADDRESS"], self.configuration["PROXY_SERVER"]["PORT"], self.configuration["PROXY_SERVER"]["AUTHENTICATION"]["USERNAME"], self.configuration["PROXY_SERVER"]["AUTHENTICATION"]["PASSWORD"])
            tunnel.connectTCP(self.remoteAddress, self.remotePort, factory, 50, None)
        else:
            reactor.connectTCP(self.remoteAddress, self.remotePort, factory, 50, None)
        
    def processState2(self):
        print "InputProtocol.processState2"
        
        self.peer.peer_dataReceived(self.stateBuffer)
        
        self.stateBuffer = ""
        
    def peer_connectionMade(self):
        print "InputProtocol.peer_connectionMade"
        
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
        
        self.state = 2
        self.stateBuffer = ""
        
    def peer_connectionLost(self, reason):
        print "InputProtocol.peer_connectionLost"
        
        if self.state != 2:
            response = struct.pack('!BBBBIH', 0x05, 0x05, 0, 1, 0, 0)
            self.transport.write(response)
        
        self.transport.loseConnection()
        
    def peer_dataReceived(self, stateBuffer):
        print "InputProtocol.peer_dataReceived"
        
        self.transport.write(stateBuffer)
        
class InputProtocolFactory(protocol.ClientFactory):
    def __init__(self, configuration):
        print "InputProtocolFactory.__init__"
        
        self.configuration = configuration
        self.configuration.setdefault("LOCAL_PROXY_SERVER", {})
        self.configuration["LOCAL_PROXY_SERVER"].setdefault("ADDRESS", "")
        self.configuration["LOCAL_PROXY_SERVER"].setdefault("PORT", 0)
        self.configuration.setdefault("PROXY_SERVER", {})
        self.configuration["PROXY_SERVER"].setdefault("ADDRESS", "")
        self.configuration["PROXY_SERVER"].setdefault("PORT", 0)
        self.configuration["PROXY_SERVER"].setdefault("AUTHENTICATION", {})
        self.configuration["PROXY_SERVER"]["AUTHENTICATION"].setdefault("USERNAME", "")
        self.configuration["PROXY_SERVER"]["AUTHENTICATION"].setdefault("PASSWORD", "")
    
    def buildProtocol(self, *args, **kw):
        p = protocol.ClientFactory.buildProtocol(self, *args, **kw)
        p.configuration = self.configuration
        return p