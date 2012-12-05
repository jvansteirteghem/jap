"""
JAP
Copyright (C) 2012 Jeroen Van Steirteghem

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
"""

from twisted.internet import protocol, reactor, defer
from twisted.conch.ssh import transport, userauth, connection, keys, channel, forwarding
import struct
import json
import random
import JAP_LOCAL
import TUNNEL

class SSHChannel(channel.SSHChannel):
    name = 'direct-tcpip'
    
    def __init__(self, *args, **kw):
        print "SSHChannel.__init__"
        
        channel.SSHChannel.__init__(self, *args, **kw)
        
        self.peer = None
        
    def channelOpen(self, specificData):
        print "SSHChannel.channelOpen"
        
        self.peer.peer = self
        self.peer.peer_connectionMade()

    def openFailed(self, reason):
        print "SSHChannel.openFailed"
        
        if self.peer is not None:
            self.peer.peer = None
            self.peer.peer_connectionLost(reason)
            self.peer = None

    def dataReceived(self, data):
        print "SSHChannel.dataReceived"
        
        self.peer.peer_dataReceived(data)
    
    def eofReceived(self):
        print "SSHChannel.eofReceived"
        
        if self.peer is not None:
            self.peer.peer_connectionLost(None)
            self.peer = None
    
    def closeReceived(self):
        print "SSHChannel.closeReceived"
        
        if self.peer is not None:
            self.peer.peer_connectionLost(None)
            self.peer = None
            
    def closed(self):
        print "SSHChannel.closed"
        
        if self.peer is not None:
            self.peer.peer = None
            self.peer.peer_connectionLost(None)
            self.peer = None
            
    def peer_connectionMade(self):
        print "SSHChannel.peer_connectionMade"
        
    def peer_connectionLost(self, reason):
        print "SSHChannel.peer_connectionLost"
        
        self.loseConnection()
        
    def peer_dataReceived(self, data):
        print "SSHChannel.peer_dataReceived"
        
        self.write(data)

class SSHClientTransport(transport.SSHClientTransport):
    def __init__(self):
        self.configuration = None
        self.i = 0
        self.sshConnection = None
        
    def verifyHostKey(self, hostKey, fingerprint):
        print 'SSHClientTransport.verifyHostKey'
        print 'SSHClientTransport.verifyHostKey: fingerprint1=' + fingerprint
        print 'SSHClientTransport.verifyHostKey: fingerprint2=' + self.configuration["REMOTE_PROXY_SERVERS"][self.i]["KEY"]["AUTHENTICATION"]["FINGERPRINT"]
        
        if self.configuration["REMOTE_PROXY_SERVERS"][self.i]["KEY"]["AUTHENTICATION"]["FINGERPRINT"] != "":
            if self.configuration["REMOTE_PROXY_SERVERS"][self.i]["KEY"]["AUTHENTICATION"]["FINGERPRINT"] != fingerprint:
                print 'SSHClientTransport.verifyHostKey: fingerprint1!=fingerprint2'
                
                return defer.fail(0)
        
        return defer.succeed(1) 

    def connectionSecure(self):
        print "SSHClientTransport.connectionSecure"
        
        self.sshConnection = SSHConnection()
        self.requestService(SSHUserAuthClient(self.configuration, self.i, self.sshConnection))
                
class SSHClientTransportFactory(protocol.ReconnectingClientFactory):
    def __init__(self):
        print "SSHClientTransportFactory.__init__"
        self.configuration = None
        self.i = 0
   
    def buildProtocol(self, address):
        print "SSHClientTransportFactory.buildProtocol"
        
        p = protocol.ClientFactory.buildProtocol(self, address)
        p.configuration = self.configuration
        p.i = self.i
        return p
        
class SSHUserAuthClient(userauth.SSHUserAuthClient):
    def __init__(self, configuration, i, instance):
        print "SSHUserAuthClient.__init__"
        
        self.configuration = configuration
        self.i = i
        self.j = -1
        
        userauth.SSHUserAuthClient.__init__(self, str(self.configuration["REMOTE_PROXY_SERVERS"][self.i]["AUTHENTICATION"]["USERNAME"]), instance)
        
    def getPassword(self):
        print "SSHUserAuthClient.getPassword"
        
        return defer.succeed(str(self.configuration["REMOTE_PROXY_SERVERS"][self.i]["AUTHENTICATION"]["PASSWORD"]))
        
    def getPublicKey(self):
        print "SSHUserAuthClient.getPublicKey"
        
        if self.configuration["REMOTE_PROXY_SERVERS"][self.i]["AUTHENTICATION"]["PASSWORD"] != "":
            return None
        
        self.j = self.j + 1
        if self.j == len(self.configuration["LOCAL_PROXY_SERVER"]["KEYS"]):
            return None
        
        return keys.Key.fromFile(self.configuration["LOCAL_PROXY_SERVER"]["KEYS"][self.j]["PUBLIC"]["FILE"]).blob()

    def getPrivateKey(self):
        print "SSHUserAuthClient.getPrivateKey"
        
        return defer.succeed(keys.Key.fromFile(self.configuration["LOCAL_PROXY_SERVER"]["KEYS"][self.j]["PRIVATE"]["FILE"], passphrase=str(self.configuration["LOCAL_PROXY_SERVER"]["KEYS"][self.j]["PRIVATE"]["PASSPHRASE"])).keyObject)

class SSHConnection(connection.SSHConnection):
    def serviceStarted(self):
        print "SSHConnection.serviceStarted"
        
        sshConnections.append(self)
        
        print "SSHConnection.serviceStarted: sshConnections=" + str(len(sshConnections))
        
    def serviceStopped(self):
        print "SSHConnection.serviceStopped"
        
        sshConnections.remove(self)
        
        print "SSHConnection.serviceStopped: sshConnections=" + str(len(sshConnections))

sshConnections = []

class SSHInputProtocol(JAP_LOCAL.InputProtocol):
    def __init__(self):
        print "SSHInputProtocol.__init__"
        
        JAP_LOCAL.InputProtocol.__init__(self)
        
        self.sshConnection = None
        self.i = 0
        
    def do_CONNECT(self):
        print "SSHInputProtocol.do_CONNECT"
        
        if len(sshConnections) == 0:
            self.transport.loseConnection()
            return
        
        self.i = random.randrange(0, len(sshConnections))
        
        self.sshConnection = sshConnections[self.i]
        self.peer = SSHChannel(conn = self.sshConnection)
        self.peer.peer = self
        localAddress = self.transport.getHost()
        data = forwarding.packOpen_direct_tcpip((self.remoteAddress, self.remotePort), (localAddress.host, localAddress.port))
        self.sshConnection.openChannel(self.peer, data)

class SSHInputProtocolFactory(JAP_LOCAL.InputProtocolFactory):
    def __init__(self, configuration):
        print "SSHInputProtocolFactory.__init__"
        
        JAP_LOCAL.InputProtocolFactory.__init__(self, configuration)
        
        self.configuration["LOCAL_PROXY_SERVER"].setdefault("KEYS", [])
        i = 0
        while i < len(self.configuration["LOCAL_PROXY_SERVER"]["KEYS"]):
            self.configuration["LOCAL_PROXY_SERVER"]["KEYS"][i].setdefault("PUBLIC", {})
            self.configuration["LOCAL_PROXY_SERVER"]["KEYS"][i]["PUBLIC"].setdefault("FILE", "")
            self.configuration["LOCAL_PROXY_SERVER"]["KEYS"][i].setdefault("PRIVATE", {})
            self.configuration["LOCAL_PROXY_SERVER"]["KEYS"][i]["PRIVATE"].setdefault("FILE", "")
            self.configuration["LOCAL_PROXY_SERVER"]["KEYS"][i]["PRIVATE"].setdefault("PASSPHRASE", "")
            i = i + 1
        self.configuration.setdefault("REMOTE_PROXY_SERVERS", [])
        i = 0
        while i < len(self.configuration["REMOTE_PROXY_SERVERS"]):
            self.configuration["REMOTE_PROXY_SERVERS"][i].setdefault("ADDRESS", "")
            self.configuration["REMOTE_PROXY_SERVERS"][i].setdefault("PORT", 0)
            self.configuration["REMOTE_PROXY_SERVERS"][i].setdefault("AUTHENTICATION", {})
            self.configuration["REMOTE_PROXY_SERVERS"][i]["AUTHENTICATION"].setdefault("USERNAME", "")
            self.configuration["REMOTE_PROXY_SERVERS"][i]["AUTHENTICATION"].setdefault("PASSWORD", "")
            self.configuration["REMOTE_PROXY_SERVERS"][i].setdefault("KEYS", {})
            self.configuration["REMOTE_PROXY_SERVERS"][i]["KEY"].setdefault("AUTHENTICATION", {})
            self.configuration["REMOTE_PROXY_SERVERS"][i]["KEY"]["AUTHENTICATION"].setdefault("FINGERPRINT", "")
            i = i + 1
    
    def startFactory(self):
        print "SSHInputProtocolFactory.startFactory"
        
        JAP_LOCAL.InputProtocolFactory.startFactory(self)
        
        i = 0
        while i < len(self.configuration["REMOTE_PROXY_SERVERS"]):
            factory = SSHClientTransportFactory()
            factory.protocol = SSHClientTransport
            factory.configuration = self.configuration
            factory.i = i
            
            if self.configuration["PROXY_SERVER"]["ADDRESS"] != "":
                tunnel = TUNNEL.Tunnel(self.configuration["PROXY_SERVER"]["ADDRESS"], self.configuration["PROXY_SERVER"]["PORT"], self.configuration["PROXY_SERVER"]["AUTHENTICATION"]["USERNAME"], self.configuration["PROXY_SERVER"]["AUTHENTICATION"]["PASSWORD"])
                tunnel.connectTCP(self.configuration["REMOTE_PROXY_SERVERS"][i]["ADDRESS"], self.configuration["REMOTE_PROXY_SERVERS"][i]["PORT"], factory, 50, None)
            else:
                reactor.connectTCP(self.configuration["REMOTE_PROXY_SERVERS"][i]["ADDRESS"], self.configuration["REMOTE_PROXY_SERVERS"][i]["PORT"], factory, 50, None)
            i = i + 1
            
    def stopFactory(self):
        print "SSHInputProtocolFactory.stopFactory"
        
        JAP_LOCAL.InputProtocolFactory.stopFactory(self)