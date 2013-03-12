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
import logging
import JAP_LOCAL
import TUNNEL

logger = logging.getLogger("JAP.JAP_SSH_LOCAL")

sshConnections = []

def setDefaultConfiguration(configuration):
    JAP_LOCAL.setDefaultConfiguration(configuration)
    
    configuration["LOCAL_PROXY_SERVER"].setdefault("KEYS", [])
    i = 0
    while i < len(configuration["LOCAL_PROXY_SERVER"]["KEYS"]):
        configuration["LOCAL_PROXY_SERVER"]["KEYS"][i].setdefault("PUBLIC", {})
        configuration["LOCAL_PROXY_SERVER"]["KEYS"][i]["PUBLIC"].setdefault("FILE", "")
        configuration["LOCAL_PROXY_SERVER"]["KEYS"][i].setdefault("PRIVATE", {})
        configuration["LOCAL_PROXY_SERVER"]["KEYS"][i]["PRIVATE"].setdefault("FILE", "")
        configuration["LOCAL_PROXY_SERVER"]["KEYS"][i]["PRIVATE"].setdefault("PASSPHRASE", "")
        i = i + 1
    configuration.setdefault("REMOTE_PROXY_SERVERS", [])
    i = 0
    while i < len(configuration["REMOTE_PROXY_SERVERS"]):
        configuration["REMOTE_PROXY_SERVERS"][i].setdefault("ADDRESS", "")
        configuration["REMOTE_PROXY_SERVERS"][i].setdefault("PORT", 0)
        configuration["REMOTE_PROXY_SERVERS"][i].setdefault("AUTHENTICATION", {})
        configuration["REMOTE_PROXY_SERVERS"][i]["AUTHENTICATION"].setdefault("USERNAME", "")
        configuration["REMOTE_PROXY_SERVERS"][i]["AUTHENTICATION"].setdefault("PASSWORD", "")
        configuration["REMOTE_PROXY_SERVERS"][i].setdefault("KEYS", {})
        configuration["REMOTE_PROXY_SERVERS"][i]["KEY"].setdefault("AUTHENTICATION", {})
        configuration["REMOTE_PROXY_SERVERS"][i]["KEY"]["AUTHENTICATION"].setdefault("FINGERPRINT", "")
        i = i + 1

class SSHChannel(channel.SSHChannel):
    name = "direct-tcpip"
    
    def __init__(self, *args, **kw):
        logger.debug("SSHChannel.__init__")
        
        channel.SSHChannel.__init__(self, *args, **kw)
        
        self.inputProtocol = None
        self.connectionState = 0
        
    def channelOpen(self, specificData):
        logger.debug("SSHChannel.channelOpen")
        
        self.connectionState = 1
        
        self.inputProtocol.outputProtocol_connectionMade()

    def openFailed(self, reason):
        logger.debug("SSHChannel.openFailed")
        
        self.connectionState = 2
        
        self.inputProtocol.outputProtocol_connectionFailed(reason)

    def dataReceived(self, data):
        logger.debug("SSHChannel.dataReceived")
        
        self.inputProtocol.outputProtocol_dataReceived(data)
    
    def eofReceived(self):
        logger.debug("SSHChannel.eofReceived")
        
        self.loseConnection()
    
    def closeReceived(self):
        logger.debug("SSHChannel.closeReceived")
        
        self.loseConnection()
            
    def closed(self):
        logger.debug("SSHChannel.closed")
        
        self.connectionState = 2
        
        self.inputProtocol.outputProtocol_connectionLost(None)
        
    def inputProtocol_connectionMade(self):
        logger.debug("SSHChannel.inputProtocol_connectionMade")
        
    def inputProtocol_connectionLost(self, reason):
        logger.debug("SSHChannel.inputProtocol_connectionLost")
        
        if self.connectionState == 1:
            self.loseConnection()
        
    def inputProtocol_dataReceived(self, data):
        logger.debug("SSHChannel.inputProtocol_dataReceived")
        
        if self.connectionState == 1:
            self.write(data)

class SSHClientTransport(transport.SSHClientTransport):
    def __init__(self):
        logger.debug("SSHClientTransport.__init__")
        
        self.configuration = None
        self.i = 0
        
    def verifyHostKey(self, hostKey, fingerprint):
        logger.debug("SSHClientTransport.verifyHostKey")
        logger.debug("SSHClientTransport.verifyHostKey: fingerprint1=" + fingerprint)
        logger.debug("SSHClientTransport.verifyHostKey: fingerprint2=" + self.configuration["REMOTE_PROXY_SERVERS"][self.i]["KEY"]["AUTHENTICATION"]["FINGERPRINT"])
        
        if self.configuration["REMOTE_PROXY_SERVERS"][self.i]["KEY"]["AUTHENTICATION"]["FINGERPRINT"] != "":
            if self.configuration["REMOTE_PROXY_SERVERS"][self.i]["KEY"]["AUTHENTICATION"]["FINGERPRINT"] != fingerprint:
                logger.debug("SSHClientTransport.verifyHostKey: fingerprint1!=fingerprint2")
                
                return defer.fail(0)
        
        return defer.succeed(1) 

    def connectionSecure(self):
        logger.debug("SSHClientTransport.connectionSecure")
        
        sshConnection = SSHConnection()
        self.requestService(SSHUserAuthClient(self.configuration, self.i, sshConnection))
                
class SSHClientTransportFactory(protocol.ReconnectingClientFactory):
    def __init__(self):
        logger.debug("SSHClientTransportFactory.__init__")
        
        self.configuration = None
        self.i = 0
   
    def buildProtocol(self, address):
        logger.debug("SSHClientTransportFactory.buildProtocol")
        
        p = protocol.ClientFactory.buildProtocol(self, address)
        p.configuration = self.configuration
        p.i = self.i
        return p
        
class SSHUserAuthClient(userauth.SSHUserAuthClient):
    def __init__(self, configuration, i, instance):
        logger.debug("SSHUserAuthClient.__init__")
        
        self.configuration = configuration
        self.i = i
        self.j = -1
        
        userauth.SSHUserAuthClient.__init__(self, str(self.configuration["REMOTE_PROXY_SERVERS"][self.i]["AUTHENTICATION"]["USERNAME"]), instance)
        
    def getPassword(self):
        logger.debug("SSHUserAuthClient.getPassword")
        
        return defer.succeed(str(self.configuration["REMOTE_PROXY_SERVERS"][self.i]["AUTHENTICATION"]["PASSWORD"]))
        
    def getPublicKey(self):
        logger.debug("SSHUserAuthClient.getPublicKey")
        
        if self.configuration["REMOTE_PROXY_SERVERS"][self.i]["AUTHENTICATION"]["PASSWORD"] != "":
            return None
        
        self.j = self.j + 1
        if self.j == len(self.configuration["LOCAL_PROXY_SERVER"]["KEYS"]):
            return None
        
        return keys.Key.fromFile(self.configuration["LOCAL_PROXY_SERVER"]["KEYS"][self.j]["PUBLIC"]["FILE"]).blob()

    def getPrivateKey(self):
        logger.debug("SSHUserAuthClient.getPrivateKey")
        
        return defer.succeed(keys.Key.fromFile(self.configuration["LOCAL_PROXY_SERVER"]["KEYS"][self.j]["PRIVATE"]["FILE"], passphrase=str(self.configuration["LOCAL_PROXY_SERVER"]["KEYS"][self.j]["PRIVATE"]["PASSPHRASE"])).keyObject)

class SSHConnection(connection.SSHConnection):
    def serviceStarted(self):
        logger.debug("SSHConnection.serviceStarted")
        
        connection.SSHConnection.serviceStarted(self)
        
        sshConnections.append(self)
        
        logger.debug("SSHConnection.serviceStarted: sshConnections=" + str(len(sshConnections)))
        
    def serviceStopped(self):
        logger.debug("SSHConnection.serviceStopped")
        
        connection.SSHConnection.serviceStopped(self)
        
        sshConnections.remove(self)
        
        logger.debug("SSHConnection.serviceStopped: sshConnections=" + str(len(sshConnections)))

class SSHInputProtocol(JAP_LOCAL.InputProtocol):
    def __init__(self):
        logger.debug("SSHInputProtocol.__init__")
        
        JAP_LOCAL.InputProtocol.__init__(self)
        
        self.i = 0
        
    def connect(self):
        logger.debug("SSHInputProtocol.connect")
        
        if len(sshConnections) == 0:
            self.transport.loseConnection()
            return
        
        self.i = random.randrange(0, len(sshConnections))
        
        sshConnection = sshConnections[self.i]
        self.outputProtocol = SSHChannel(conn = sshConnection)
        self.outputProtocol.inputProtocol = self
        localAddress = self.transport.getHost()
        data = forwarding.packOpen_direct_tcpip((self.remoteAddress, self.remotePort), (localAddress.host, localAddress.port))
        sshConnection.openChannel(self.outputProtocol, data)

class SSHInputProtocolFactory(JAP_LOCAL.InputProtocolFactory):
    def __init__(self, configuration):
        logger.debug("SSHInputProtocolFactory.__init__")
        
        JAP_LOCAL.InputProtocolFactory.__init__(self, configuration)
    
    def startFactory(self):
        logger.debug("SSHInputProtocolFactory.startFactory")
        
        JAP_LOCAL.InputProtocolFactory.startFactory(self)
        
        i = 0
        while i < len(self.configuration["REMOTE_PROXY_SERVERS"]):
            factory = SSHClientTransportFactory()
            factory.protocol = SSHClientTransport
            factory.configuration = self.configuration
            factory.i = i
            
            tunnel = TUNNEL.Tunnel(self.configuration)
            tunnel.connect(self.configuration["REMOTE_PROXY_SERVERS"][i]["ADDRESS"], self.configuration["REMOTE_PROXY_SERVERS"][i]["PORT"], factory)
            
            i = i + 1
            
    def stopFactory(self):
        logger.debug("SSHInputProtocolFactory.stopFactory")
        
        JAP_LOCAL.InputProtocolFactory.stopFactory(self)