"""
JAP
Copyright (C) 2012 Jeroen Van Steirteghem

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
"""

from twisted.internet import protocol, reactor, ssl
import struct
import json
import random
import OpenSSL
import base64
import socket
import logging
import JAP_LOCAL
import TUNNEL

logger = logging.getLogger("JAP.JAP_WS_LOCAL")

def setDefaultConfiguration(configuration):
    JAP_LOCAL.setDefaultConfiguration(configuration)
    
    configuration.setdefault("REMOTE_PROXY_SERVERS", [])
    i = 0
    while i < len(configuration["REMOTE_PROXY_SERVERS"]):
        configuration["REMOTE_PROXY_SERVERS"][i].setdefault("TYPE", "")
        configuration["REMOTE_PROXY_SERVERS"][i].setdefault("ADDRESS", "")
        configuration["REMOTE_PROXY_SERVERS"][i].setdefault("PORT", 0)
        configuration["REMOTE_PROXY_SERVERS"][i].setdefault("AUTHENTICATION", {})
        configuration["REMOTE_PROXY_SERVERS"][i]["AUTHENTICATION"].setdefault("USERNAME", "")
        configuration["REMOTE_PROXY_SERVERS"][i]["AUTHENTICATION"].setdefault("PASSWORD", "")
        configuration["REMOTE_PROXY_SERVERS"][i].setdefault("CERTIFICATE", {})
        configuration["REMOTE_PROXY_SERVERS"][i]["CERTIFICATE"].setdefault("AUTHENTICATION", {})
        configuration["REMOTE_PROXY_SERVERS"][i]["CERTIFICATE"]["AUTHENTICATION"].setdefault("FILE", "")
        i = i + 1

class WSOutputProtocol(JAP_LOCAL.OutputProtocol):
    def __init__(self):
        logger.debug("WSOutputProtocol.__init__")
        
        JAP_LOCAL.OutputProtocol.__init__(self)
        
        self.state = 0
        self.stateBuffer = ""
        
    def connectionMade(self):
        logger.debug("WSOutputProtocol.connectionMade")
        
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
        
    def dataReceived(self, data):
        logger.debug("WSOutputProtocol.dataReceived")
        
        self.stateBuffer = self.stateBuffer + data
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
        logger.debug("WSOutputProtocol.processState0")
        
        if self.stateBuffer.find("\r\n\r\n") == -1:
            return
        
        #IPv4
        if self.peer.remoteAddressType == 0x01:
            remoteAddress = struct.unpack('!I', socket.inet_aton(self.peer.remoteAddress))[0]
            request = struct.pack('!BBBBIH', 0x05, 0x00, 0, 0x01, remoteAddress, self.peer.remotePort)
        else:
            # DN
            if self.peer.remoteAddressType == 0x03:
                remoteAddressLength = len(self.peer.remoteAddress)
                request = struct.pack('!BBBBB%dsH' % remoteAddressLength, 0x05, 0x00, 0, 0x03, remoteAddressLength, self.peer.remoteAddress, self.peer.remotePort)
        
        self.transport.write(request)
        
        self.state = 1
        self.stateBuffer = ""
        
    def processState1(self):
        logger.debug("WSOutputProtocol.processState1")
        
        self.peer.peer_connectionMade()
        
        self.state = 2
        self.stateBuffer = ""
        
    def processState2(self):
        logger.debug("WSOutputProtocol.processState2")
        
        self.peer.peer_dataReceived(self.stateBuffer)
        
        self.stateBuffer = ""

class WSOutputProtocolFactory(JAP_LOCAL.OutputProtocolFactory):
    pass

class WSInputProtocol(JAP_LOCAL.InputProtocol):
    def __init__(self):
        logger.debug("WSInputProtocol.__init__")
        
        JAP_LOCAL.InputProtocol.__init__(self)
        
        self.i = 0
        
    def do_CONNECT(self):
        logger.debug("WSInputProtocol.do_CONNECT")
        
        self.i = random.randrange(0, len(self.configuration["REMOTE_PROXY_SERVERS"]))
        
        factory = WSOutputProtocolFactory(self)
        factory.protocol = WSOutputProtocol
        
        if self.configuration["REMOTE_PROXY_SERVERS"][self.i]["TYPE"] == "HTTPS":
            if self.configuration["REMOTE_PROXY_SERVERS"][self.i]["CERTIFICATE"]["AUTHENTICATION"]["FILE"] != "":
                contextFactory = ClientContextFactory(self.configuration["REMOTE_PROXY_SERVERS"][self.i]["CERTIFICATE"]["AUTHENTICATION"]["FILE"])
            else:
                contextFactory = ssl.ClientContextFactory()
            
            if self.configuration["PROXY_SERVER"]["ADDRESS"] != "":
                tunnel = TUNNEL.Tunnel(self.configuration["PROXY_SERVER"]["ADDRESS"], self.configuration["PROXY_SERVER"]["PORT"], self.configuration["PROXY_SERVER"]["AUTHENTICATION"]["USERNAME"], self.configuration["PROXY_SERVER"]["AUTHENTICATION"]["PASSWORD"])
                tunnel.connectSSL(self.configuration["REMOTE_PROXY_SERVERS"][self.i]["ADDRESS"], self.configuration["REMOTE_PROXY_SERVERS"][self.i]["PORT"], factory, contextFactory, 50, None)
            else:
                reactor.connectSSL(self.configuration["REMOTE_PROXY_SERVERS"][self.i]["ADDRESS"], self.configuration["REMOTE_PROXY_SERVERS"][self.i]["PORT"], factory, contextFactory, 50, None)
        else:
            if self.configuration["PROXY_SERVER"]["ADDRESS"] != "":
                tunnel = TUNNEL.Tunnel(self.configuration["PROXY_SERVER"]["ADDRESS"], self.configuration["PROXY_SERVER"]["PORT"], self.configuration["PROXY_SERVER"]["AUTHENTICATION"]["USERNAME"], self.configuration["PROXY_SERVER"]["AUTHENTICATION"]["PASSWORD"])
                tunnel.connectTCP(self.configuration["REMOTE_PROXY_SERVERS"][self.i]["ADDRESS"], self.configuration["REMOTE_PROXY_SERVERS"][self.i]["PORT"], factory, 50, None)
            else:
                reactor.connectTCP(self.configuration["REMOTE_PROXY_SERVERS"][self.i]["ADDRESS"], self.configuration["REMOTE_PROXY_SERVERS"][self.i]["PORT"], factory, 50, None)

class ClientContextFactory(ssl.ClientContextFactory):
    def __init__(self, verify_locations):
        logger.debug("ClientContextFactory.__init__")
        
        self.verify_locations = verify_locations
        
    def getContext(self):
        logger.debug("ClientContextFactory.getContext")
        
        self.method = OpenSSL.SSL.TLSv1_METHOD
        
        context = ssl.ClientContextFactory.getContext(self)
        context.load_verify_locations(self.verify_locations)
        context.set_verify(OpenSSL.SSL.VERIFY_PEER | OpenSSL.SSL.VERIFY_FAIL_IF_NO_PEER_CERT, self.verify)
        
        return context
        
    def verify(self, connection, certificate, errorNumber, errorDepth, certificateOk):
        logger.debug("ClientContextFactory.verify")
        
        if certificateOk:
            logger.debug("ClientContextFactory: certificate ok")
        else:
            logger.debug("ClientContextFactory: certificate not ok")
        
        return certificateOk

class WSInputProtocolFactory(JAP_LOCAL.InputProtocolFactory):
    def __init__(self, configuration):
        logger.debug("WSInputProtocolFactory.__init__")
        
        JAP_LOCAL.InputProtocolFactory.__init__(self, configuration)