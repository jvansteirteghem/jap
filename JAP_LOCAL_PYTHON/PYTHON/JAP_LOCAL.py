"""
JAP
Copyright (C) 2012 Jeroen Van Steirteghem

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
"""

from PYTHON.TUNNEL import Tunnel
from twisted.internet import protocol, reactor, ssl
import struct
import json
import random
import OpenSSL
import base64

class OutputProtocol(protocol.Protocol):
    def __init__(self):
        print "OutputProtocol.__init__"
        self.peer = None
        self.state = 0
        self.stateBuffer = ""
        
    def connectionMade(self):
        print "OutputProtocol.connectionMade"
        self.peer.peer = self
        
        request = "GET / HTTP/1.1\r\n"
        request = request + "Host: " + str(self.peer.configuration["REMOTE_PROXY_SERVERS"][self.peer.i]["ADDRESS"]) + ":" + str(self.peer.configuration["REMOTE_PROXY_SERVERS"][self.peer.i]["PORT"]) + "\r\n"
        
        if self.peer.configuration["REMOTE_PROXY_SERVERS"][self.peer.i]["AUTHENTICATION"]["USERNAME"] != "":
            request = request + "Authorization: Basic " + base64.standard_b64encode(self.peer.configuration["REMOTE_PROXY_SERVERS"][self.peer.i]["AUTHENTICATION"]["USERNAME"] + ":" + self.peer.configuration["REMOTE_PROXY_SERVERS"][self.peer.i]["AUTHENTICATION"]["PASSWORD"]) + "\r\n"
        
        request = request + "Upgrade: WebSocket\r\n"
        request = request + "Connection: Upgrade\r\n"
        request = request + "\r\n"
        
        self.transport.write(request)
        
        self.state = 0
        self.stateBuffer = ""

    def connectionLost(self, reason):
        print "OutputProtocol.connectionLost"
        if self.peer is not None:
            self.peer.transport.loseConnection()
            self.peer = None
        
    def dataReceived(self, stateBuffer):
        print "OutputProtocol.dataReceived"
        
        self.stateBuffer = self.stateBuffer + stateBuffer
        if self.state == 0:
            self.processState0()
            return
        if self.state == 1:
            self.processState1();
            return
        if self.state == 2:
            self.processState2();
            return
        
    def processState0(self):
        print "OutputProtocol.processState0"
        
        #IPv4
        if self.peer.remoteAddressType == 0x01:
            request = struct.pack('!BBBBIH', 0x05, 0x00, 0, 0x01, self.peer.remoteAddress, self.peer.remotePort)
        else:
            # DN
            if self.peer.remoteAddressType == 0x03:
                remoteAddressLength = len(self.peer.remoteAddress)
                request = struct.pack('!BBBBB%dsH' % remoteAddressLength, 0x05, 0x00, 0, 0x03, remoteAddressLength, self.peer.remoteAddress, self.peer.remotePort)
        
        self.transport.write(request)
        
        self.state = 1
        self.stateBuffer = ""
        
    def processState1(self):
        print "OutputProtocol.processState1"
        
        #IPv4
        if self.peer.remoteAddressType == 0x01:
            response = struct.pack('!BBBBIH', 0x05, 0x00, 0, 0x01, self.peer.remoteAddress, self.peer.remotePort)
        else:
            # DN
            if self.peer.remoteAddressType == 0x03:
                remoteAddressLength = len(self.peer.remoteAddress)
                response = struct.pack('!BBBBB%dsH' % remoteAddressLength, 0x05, 0x00, 0, 0x03, remoteAddressLength, self.peer.remoteAddress, self.peer.remotePort)
        
        self.peer.transport.write(response)
        
        self.peer.state = 2
        self.peer.stateBuffer = ""
        
        self.state = 2
        self.stateBuffer = ""
        
    def processState2(self):
        print "OutputProtocol.processState2"
        
        self.peer.transport.write(self.stateBuffer)
        
        self.stateBuffer = ""

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
        self.i = 0
    
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
        
        # no authentication
        self.transport.write(struct.pack('!BB', 0x05, 0x00))
        
        self.state = 1
        self.stateBuffer = ""
    
    def processState1(self):
        print "InputProtocol.processState1"
        
        v, c, r, self.remoteAddressType = struct.unpack('!BBBB', self.stateBuffer[:4])
        
        # IPv4
        if self.remoteAddressType == 0x01:
            self.remoteAddress, self.remotePort = struct.unpack('!IH', self.stateBuffer[4:10])
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
        
        # connect
        if c == 0x01:
            self.i = random.randrange(0, len(self.configuration["REMOTE_PROXY_SERVERS"]))
            
            factory = OutputProtocolFactory(self)
            factory.protocol = OutputProtocol
            
            if self.configuration["REMOTE_PROXY_SERVERS"][self.i]["TYPE"] == "HTTPS":
                if self.configuration["REMOTE_PROXY_SERVERS"][self.i]["CERTIFICATE"]["AUTHENTICATION"]["FILE"] != "":
                    contextFactory = ClientContextFactory(self.configuration["REMOTE_PROXY_SERVERS"][self.i]["CERTIFICATE"]["AUTHENTICATION"]["FILE"])
                else:
                    contextFactory = ssl.ClientContextFactory()
                
                if self.configuration["PROXY_SERVER"]["ADDRESS"] != "":
                    tunnel = Tunnel(self.configuration["PROXY_SERVER"]["ADDRESS"], self.configuration["PROXY_SERVER"]["PORT"], self.configuration["PROXY_SERVER"]["AUTHENTICATION"]["USERNAME"], self.configuration["PROXY_SERVER"]["AUTHENTICATION"]["PASSWORD"])
                    tunnel.connectSSL(self.configuration["REMOTE_PROXY_SERVERS"][self.i]["ADDRESS"], self.configuration["REMOTE_PROXY_SERVERS"][self.i]["PORT"], factory, contextFactory, 50, None)
                else:
                    reactor.connectSSL(self.configuration["REMOTE_PROXY_SERVERS"][self.i]["ADDRESS"], self.configuration["REMOTE_PROXY_SERVERS"][self.i]["PORT"], factory, contextFactory, 50, None)
            else:
                if self.configuration["PROXY_SERVER"]["ADDRESS"] != "":
                    tunnel = Tunnel(self.configuration["PROXY_SERVER"]["ADDRESS"], self.configuration["PROXY_SERVER"]["PORT"], self.configuration["PROXY_SERVER"]["AUTHENTICATION"]["USERNAME"], self.configuration["PROXY_SERVER"]["AUTHENTICATION"]["PASSWORD"])
                    tunnel.connectTCP(self.configuration["REMOTE_PROXY_SERVERS"][self.i]["ADDRESS"], self.configuration["REMOTE_PROXY_SERVERS"][self.i]["PORT"], factory, 50, None)
                else:
                    reactor.connectTCP(self.configuration["REMOTE_PROXY_SERVERS"][self.i]["ADDRESS"], self.configuration["REMOTE_PROXY_SERVERS"][self.i]["PORT"], factory, 50, None)
        else:
            response = struct.pack('!BBBBIH', 0x05, 0x07, 0, 1, 0, 0)
            self.transport.write(response)
            self.transport.loseConnection()
            return
            
    def processState2(self):
        print "InputProtocol.processState0"
        self.peer.transport.write(self.stateBuffer)
        
        self.stateBuffer = ""

class ClientContextFactory(ssl.ClientContextFactory):
    def __init__(self, verify_locations):
        self.verify_locations = verify_locations
        
    def getContext(self):
        self.method = OpenSSL.SSL.TLSv1_METHOD
        
        context = ssl.ClientContextFactory.getContext(self)
        context.load_verify_locations(self.verify_locations)
        context.set_verify(OpenSSL.SSL.VERIFY_PEER | OpenSSL.SSL.VERIFY_FAIL_IF_NO_PEER_CERT, self.verify)
        
        return context
        
    def verify(self, connection, certificate, errorNumber, errorDepth, certificateOk):
        if certificateOk:
            print "ClientContextFactory: certificate ok"
        else:
            print "ClientContextFactory: certificate not ok"
        
        return certificateOk

class InputProtocolFactory(protocol.ClientFactory):
    def __init__(self, configuration):
        print "InputProtocolFactory.__init__"
        self.configuration = configuration
        self.configuration.setdefault("LOCAL_PROXY_SERVER", {})
        self.configuration["LOCAL_PROXY_SERVER"].setdefault("ADDRESS", "")
        self.configuration["LOCAL_PROXY_SERVER"].setdefault("PORT", 0)
        self.configuration.setdefault("REMOTE_PROXY_SERVERS", [])
        i = 0
        while i < len(self.configuration["REMOTE_PROXY_SERVERS"]):
            self.configuration["REMOTE_PROXY_SERVERS"][i].setdefault("TYPE", "")
            self.configuration["REMOTE_PROXY_SERVERS"][i].setdefault("ADDRESS", "")
            self.configuration["REMOTE_PROXY_SERVERS"][i].setdefault("PORT", 0)
            self.configuration["REMOTE_PROXY_SERVERS"][i].setdefault("AUTHENTICATION", {})
            self.configuration["REMOTE_PROXY_SERVERS"][i]["AUTHENTICATION"].setdefault("USERNAME", "")
            self.configuration["REMOTE_PROXY_SERVERS"][i]["AUTHENTICATION"].setdefault("PASSWORD", "")
            self.configuration["REMOTE_PROXY_SERVERS"][i].setdefault("CERTIFICATE", {})
            self.configuration["REMOTE_PROXY_SERVERS"][i]["CERTIFICATE"].setdefault("AUTHENTICATION", {})
            self.configuration["REMOTE_PROXY_SERVERS"][i]["CERTIFICATE"]["AUTHENTICATION"].setdefault("FILE", "")
            i = i + 1
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