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
import random
import logging
import collections
import JAP_LOCAL

logger = logging.getLogger(__name__)

sshConnections = []

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
    configuration["LOCAL_PROXY_SERVER"].setdefault("KEYS", [])
    i = 0
    while i < len(configuration["LOCAL_PROXY_SERVER"]["KEYS"]):
        configuration["LOCAL_PROXY_SERVER"]["KEYS"][i].setdefault("PUBLIC", collections.OrderedDict())
        configuration["LOCAL_PROXY_SERVER"]["KEYS"][i]["PUBLIC"].setdefault("FILE", "")
        configuration["LOCAL_PROXY_SERVER"]["KEYS"][i]["PUBLIC"].setdefault("PASSPHRASE", "")
        configuration["LOCAL_PROXY_SERVER"]["KEYS"][i].setdefault("PRIVATE", collections.OrderedDict())
        configuration["LOCAL_PROXY_SERVER"]["KEYS"][i]["PRIVATE"].setdefault("FILE", "")
        configuration["LOCAL_PROXY_SERVER"]["KEYS"][i]["PRIVATE"].setdefault("PASSPHRASE", "")
        i = i + 1
    configuration.setdefault("REMOTE_PROXY_SERVERS", [])
    i = 0
    while i < len(configuration["REMOTE_PROXY_SERVERS"]):
        configuration["REMOTE_PROXY_SERVERS"][i].setdefault("ADDRESS", "")
        configuration["REMOTE_PROXY_SERVERS"][i].setdefault("PORT", 0)
        configuration["REMOTE_PROXY_SERVERS"][i].setdefault("AUTHENTICATION", collections.OrderedDict())
        configuration["REMOTE_PROXY_SERVERS"][i]["AUTHENTICATION"].setdefault("USERNAME", "")
        configuration["REMOTE_PROXY_SERVERS"][i]["AUTHENTICATION"].setdefault("PASSWORD", "")
        configuration["REMOTE_PROXY_SERVERS"][i].setdefault("KEY", collections.OrderedDict())
        configuration["REMOTE_PROXY_SERVERS"][i]["KEY"].setdefault("AUTHENTICATION", collections.OrderedDict())
        configuration["REMOTE_PROXY_SERVERS"][i]["KEY"]["AUTHENTICATION"].setdefault("FINGERPRINT", "")
        i = i + 1
    
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
        defaultConfiguration["PROXY_SERVERS"][i]["AUTHENTICATION"] = collections.OrderedDict()
        defaultConfiguration["PROXY_SERVERS"][i]["AUTHENTICATION"]["USERNAME"] = configuration["PROXY_SERVERS"][i]["AUTHENTICATION"]["USERNAME"]
        defaultConfiguration["PROXY_SERVERS"][i]["AUTHENTICATION"]["PASSWORD"] = configuration["PROXY_SERVERS"][i]["AUTHENTICATION"]["PASSWORD"]
        i = i + 1
    defaultConfiguration["LOCAL_PROXY_SERVER"] = collections.OrderedDict()
    defaultConfiguration["LOCAL_PROXY_SERVER"]["ADDRESS"] = configuration["LOCAL_PROXY_SERVER"]["ADDRESS"]
    defaultConfiguration["LOCAL_PROXY_SERVER"]["PORT"] = configuration["LOCAL_PROXY_SERVER"]["PORT"]
    defaultConfiguration["LOCAL_PROXY_SERVER"]["KEYS"] = []
    i = 0
    while i < len(configuration["LOCAL_PROXY_SERVER"]["KEYS"]):
        defaultConfiguration["LOCAL_PROXY_SERVER"]["KEYS"].append(collections.OrderedDict())
        defaultConfiguration["LOCAL_PROXY_SERVER"]["KEYS"][i]["PUBLIC"] = collections.OrderedDict()
        defaultConfiguration["LOCAL_PROXY_SERVER"]["KEYS"][i]["PUBLIC"]["FILE"] = configuration["LOCAL_PROXY_SERVER"]["KEYS"][i]["PUBLIC"]["FILE"]
        defaultConfiguration["LOCAL_PROXY_SERVER"]["KEYS"][i]["PUBLIC"]["PASSPHRASE"] = configuration["LOCAL_PROXY_SERVER"]["KEYS"][i]["PUBLIC"]["PASSPHRASE"]
        defaultConfiguration["LOCAL_PROXY_SERVER"]["KEYS"][i]["PRIVATE"] = collections.OrderedDict()
        defaultConfiguration["LOCAL_PROXY_SERVER"]["KEYS"][i]["PRIVATE"]["FILE"] = configuration["LOCAL_PROXY_SERVER"]["KEYS"][i]["PRIVATE"]["FILE"]
        defaultConfiguration["LOCAL_PROXY_SERVER"]["KEYS"][i]["PRIVATE"]["PASSPHRASE"] = configuration["LOCAL_PROXY_SERVER"]["KEYS"][i]["PRIVATE"]["PASSPHRASE"]
        i = i + 1
    defaultConfiguration["REMOTE_PROXY_SERVERS"] = []
    i = 0
    while i < len(configuration["REMOTE_PROXY_SERVERS"]):
        defaultConfiguration["REMOTE_PROXY_SERVERS"].append(collections.OrderedDict())
        defaultConfiguration["REMOTE_PROXY_SERVERS"][i]["ADDRESS"] = configuration["REMOTE_PROXY_SERVERS"][i]["ADDRESS"]
        defaultConfiguration["REMOTE_PROXY_SERVERS"][i]["PORT"] = configuration["REMOTE_PROXY_SERVERS"][i]["PORT"]
        defaultConfiguration["REMOTE_PROXY_SERVERS"][i]["AUTHENTICATION"] = collections.OrderedDict()
        defaultConfiguration["REMOTE_PROXY_SERVERS"][i]["AUTHENTICATION"]["USERNAME"] = configuration["REMOTE_PROXY_SERVERS"][i]["AUTHENTICATION"]["USERNAME"]
        defaultConfiguration["REMOTE_PROXY_SERVERS"][i]["AUTHENTICATION"]["PASSWORD"] = configuration["REMOTE_PROXY_SERVERS"][i]["AUTHENTICATION"]["PASSWORD"]
        defaultConfiguration["REMOTE_PROXY_SERVERS"][i]["KEY"] = collections.OrderedDict()
        defaultConfiguration["REMOTE_PROXY_SERVERS"][i]["KEY"]["AUTHENTICATION"] = collections.OrderedDict()
        defaultConfiguration["REMOTE_PROXY_SERVERS"][i]["KEY"]["AUTHENTICATION"]["FINGERPRINT"] = configuration["REMOTE_PROXY_SERVERS"][i]["KEY"]["AUTHENTICATION"]["FINGERPRINT"]
        i = i + 1
    
    return defaultConfiguration

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
        
        self.requestService(SSHUserAuthClient(self.configuration, self.i))
                
class SSHClientTransportFactory(protocol.ReconnectingClientFactory):
    def __init__(self):
        logger.debug("SSHClientTransportFactory.__init__")
        
        self.configuration = None
        self.i = 0
        self.connectors = []
        
    def buildProtocol(self, address):
        logger.debug("SSHClientTransportFactory.buildProtocol")
        
        p = protocol.ClientFactory.buildProtocol(self, address)
        p.configuration = self.configuration
        p.i = self.i
        return p
        
    def startFactory(self):
        logger.debug("SSHClientTransportFactory.startFactory")
        
    def stopFactory(self):
        logger.debug("SSHClientTransportFactory.stopFactory")
        
    def connect(self):
        logger.debug("SSHClientTransportFactory.connect")
        
        tunnel = JAP_LOCAL.Tunnel(self.configuration)
        tunnel.connect(self.configuration["REMOTE_PROXY_SERVERS"][self.i]["ADDRESS"], self.configuration["REMOTE_PROXY_SERVERS"][self.i]["PORT"], self)
        
    def disconnect(self):
        logger.debug("SSHClientTransportFactory.disconnect")
        
        self.stopTrying()
        
        i = 0
        while i < len(self.connectors):
            connector = self.connectors[i]
            connector.disconnect()
            
            i = i + 1
        
    def startedConnecting(self, connector):
        logger.debug("SSHClientTransportFactory.startedConnecting")
        
        self.connectors.append(connector)
        
        protocol.ReconnectingClientFactory.startedConnecting(self, connector)
        
    def clientConnectionFailed(self, connector, reason):
        logger.debug("SSHClientTransportFactory.clientConnectionFailed")
        
        self.connectors.remove(connector)
        
        protocol.ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)
        
    def clientConnectionLost(self, connector, reason):
        logger.debug("SSHClientTransportFactory.clientConnectionLost")
        
        self.connectors.remove(connector)
        
        protocol.ReconnectingClientFactory.clientConnectionLost(self, connector, reason)
        
class SSHUserAuthClient(userauth.SSHUserAuthClient):
    def __init__(self, configuration, i):
        logger.debug("SSHUserAuthClient.__init__")
        
        self.configuration = configuration
        self.i = i
        self.j = -1
        
        userauth.SSHUserAuthClient.__init__(self, str(self.configuration["REMOTE_PROXY_SERVERS"][self.i]["AUTHENTICATION"]["USERNAME"]), SSHConnection())
        
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
        
        return keys.Key.fromFile(self.configuration["LOCAL_PROXY_SERVER"]["KEYS"][self.j]["PUBLIC"]["FILE"], passphrase=str(self.configuration["LOCAL_PROXY_SERVER"]["KEYS"][self.j]["PUBLIC"]["PASSPHRASE"])).blob()

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
        
        self.sshClientTransportFactories = []
        
        i = 0
        while i < len(self.configuration["REMOTE_PROXY_SERVERS"]):
            sshClientTransportFactory = SSHClientTransportFactory()
            sshClientTransportFactory.protocol = SSHClientTransport
            sshClientTransportFactory.configuration = self.configuration
            sshClientTransportFactory.i = i
            
            self.sshClientTransportFactories.append(sshClientTransportFactory)
            
            i = i + 1
        
    def startFactory(self):
        logger.debug("SSHInputProtocolFactory.startFactory")
        
        JAP_LOCAL.InputProtocolFactory.startFactory(self)
        
        i = 0
        while i < len(self.sshClientTransportFactories):
            sshClientTransportFactory = self.sshClientTransportFactories[i]
            sshClientTransportFactory.connect()
            
            i = i + 1
        
    def stopFactory(self):
        logger.debug("SSHInputProtocolFactory.stopFactory")
        
        JAP_LOCAL.InputProtocolFactory.stopFactory(self)
        
        i = 0
        while i < len(self.sshClientTransportFactories):
            sshClientTransportFactory = self.sshClientTransportFactories[i]
            sshClientTransportFactory.disconnect()
            
            i = i + 1