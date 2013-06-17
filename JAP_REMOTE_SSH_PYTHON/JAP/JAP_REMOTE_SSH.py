"""
JAP
Copyright (C) 2012 Jeroen Van Steirteghem

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
"""

from zope.interface import implements
from twisted.internet import defer
from twisted.conch import avatar, interfaces
from twisted.conch.error import ValidPublicKey
from twisted.conch.ssh import channel, factory, forwarding, keys
from twisted.cred import portal, checkers, credentials
from twisted.cred.error import UnauthorizedLogin
import logging
import collections
import JAP_LOCAL

logger = logging.getLogger(__name__)

def getDefaultConfiguration(configuration=None):
    if configuration is None:
        configuration = collections.OrderedDict()
    
    configuration.setdefault("LOGGER", collections.OrderedDict())
    configuration["LOGGER"].setdefault("LEVEL", "")
    configuration.setdefault("REMOTE_PROXY_SERVER", collections.OrderedDict())
    configuration["REMOTE_PROXY_SERVER"].setdefault("ADDRESS", "")
    configuration["REMOTE_PROXY_SERVER"].setdefault("PORT", 0)
    configuration["REMOTE_PROXY_SERVER"].setdefault("AUTHENTICATION", [])
    i = 0
    while i < len(configuration["REMOTE_PROXY_SERVER"]["AUTHENTICATION"]):
        configuration["REMOTE_PROXY_SERVER"]["AUTHENTICATION"][i].setdefault("USERNAME", "")
        configuration["REMOTE_PROXY_SERVER"]["AUTHENTICATION"][i].setdefault("PASSWORD", "")
        configuration["REMOTE_PROXY_SERVER"]["AUTHENTICATION"][i].setdefault("KEYS", [])
        j = 0
        while j < len(configuration["REMOTE_PROXY_SERVER"]["AUTHENTICATION"][i]["KEYS"]):
            configuration["REMOTE_PROXY_SERVER"]["AUTHENTICATION"][i]["KEYS"][j].setdefault("PUBLIC", collections.OrderedDict())
            configuration["REMOTE_PROXY_SERVER"]["AUTHENTICATION"][i]["KEYS"][j]["PUBLIC"].setdefault("FILE", "")
            configuration["REMOTE_PROXY_SERVER"]["AUTHENTICATION"][i]["KEYS"][j]["PUBLIC"].setdefault("PASSPHRASE", "")
            j = j + 1
        i = i + 1
    configuration["REMOTE_PROXY_SERVER"].setdefault("KEY", collections.OrderedDict())
    configuration["REMOTE_PROXY_SERVER"]["KEY"].setdefault("PUBLIC", collections.OrderedDict())
    configuration["REMOTE_PROXY_SERVER"]["KEY"]["PUBLIC"].setdefault("FILE", "")
    configuration["REMOTE_PROXY_SERVER"]["KEY"]["PUBLIC"].setdefault("PASSPHRASE", "")
    configuration["REMOTE_PROXY_SERVER"]["KEY"].setdefault("PRIVATE", collections.OrderedDict())
    configuration["REMOTE_PROXY_SERVER"]["KEY"]["PRIVATE"].setdefault("FILE", "")
    configuration["REMOTE_PROXY_SERVER"]["KEY"]["PRIVATE"].setdefault("PASSPHRASE", "")
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
    
    defaultConfiguration = collections.OrderedDict()
    defaultConfiguration["LOGGER"] = collections.OrderedDict()
    defaultConfiguration["LOGGER"]["LEVEL"] = configuration["LOGGER"]["LEVEL"]
    defaultConfiguration["REMOTE_PROXY_SERVER"] = collections.OrderedDict()
    defaultConfiguration["REMOTE_PROXY_SERVER"]["ADDRESS"] = configuration["REMOTE_PROXY_SERVER"]["ADDRESS"]
    defaultConfiguration["REMOTE_PROXY_SERVER"]["PORT"] = configuration["REMOTE_PROXY_SERVER"]["PORT"]
    defaultConfiguration["REMOTE_PROXY_SERVER"]["AUTHENTICATION"] = [collections.OrderedDict()] * len(configuration["REMOTE_PROXY_SERVER"]["AUTHENTICATION"])
    i = 0
    while i < len(configuration["REMOTE_PROXY_SERVER"]["AUTHENTICATION"]):
        defaultConfiguration["REMOTE_PROXY_SERVER"]["AUTHENTICATION"][i]["USERNAME"] = configuration["REMOTE_PROXY_SERVER"]["AUTHENTICATION"][i]["USERNAME"]
        defaultConfiguration["REMOTE_PROXY_SERVER"]["AUTHENTICATION"][i]["PASSWORD"] = configuration["REMOTE_PROXY_SERVER"]["AUTHENTICATION"][i]["PASSWORD"]
        defaultConfiguration["REMOTE_PROXY_SERVER"]["AUTHENTICATION"][i]["KEYS"] = [collections.OrderedDict()] * len(configuration["REMOTE_PROXY_SERVER"]["AUTHENTICATION"][i]["KEYS"])
        j = 0
        while j < len(configuration["REMOTE_PROXY_SERVER"]["AUTHENTICATION"][i]["KEYS"]):
            defaultConfiguration["REMOTE_PROXY_SERVER"]["AUTHENTICATION"][i]["KEYS"][j]["PUBLIC"] = collections.OrderedDict()
            defaultConfiguration["REMOTE_PROXY_SERVER"]["AUTHENTICATION"][i]["KEYS"][j]["PUBLIC"]["FILE"] = configuration["REMOTE_PROXY_SERVER"]["AUTHENTICATION"][i]["KEYS"][j]["PUBLIC"]["FILE"]
            defaultConfiguration["REMOTE_PROXY_SERVER"]["AUTHENTICATION"][i]["KEYS"][j]["PUBLIC"]["PASSPHRASE"] = configuration["REMOTE_PROXY_SERVER"]["AUTHENTICATION"][i]["KEYS"][j]["PUBLIC"]["PASSPHRASE"]
            j = j + 1
        i = i + 1
    defaultConfiguration["REMOTE_PROXY_SERVER"]["KEY"] = collections.OrderedDict()
    defaultConfiguration["REMOTE_PROXY_SERVER"]["KEY"]["PUBLIC"] = collections.OrderedDict()
    defaultConfiguration["REMOTE_PROXY_SERVER"]["KEY"]["PUBLIC"]["FILE"] = configuration["REMOTE_PROXY_SERVER"]["KEY"]["PUBLIC"]["FILE"]
    defaultConfiguration["REMOTE_PROXY_SERVER"]["KEY"]["PUBLIC"]["PASSPHRASE"] = configuration["REMOTE_PROXY_SERVER"]["KEY"]["PUBLIC"]["PASSPHRASE"]
    defaultConfiguration["REMOTE_PROXY_SERVER"]["KEY"]["PRIVATE"] = collections.OrderedDict()
    defaultConfiguration["REMOTE_PROXY_SERVER"]["KEY"]["PRIVATE"]["FILE"] = configuration["REMOTE_PROXY_SERVER"]["KEY"]["PRIVATE"]["FILE"]
    defaultConfiguration["REMOTE_PROXY_SERVER"]["KEY"]["PRIVATE"]["PASSPHRASE"] = configuration["REMOTE_PROXY_SERVER"]["KEY"]["PRIVATE"]["PASSPHRASE"]
    defaultConfiguration["PROXY_SERVERS"] = [collections.OrderedDict()] * len(configuration["PROXY_SERVERS"])
    i = 0
    while i < len(configuration["PROXY_SERVERS"]):
        defaultConfiguration["PROXY_SERVERS"][i]["TYPE"] = configuration["PROXY_SERVERS"][i]["TYPE"]
        defaultConfiguration["PROXY_SERVERS"][i]["ADDRESS"] = configuration["PROXY_SERVERS"][i]["ADDRESS"]
        defaultConfiguration["PROXY_SERVERS"][i]["PORT"] = configuration["PROXY_SERVERS"][i]["PORT"]
        defaultConfiguration["PROXY_SERVERS"][i]["AUTHENTICATION"] = collections.OrderedDict()
        defaultConfiguration["PROXY_SERVERS"][i]["AUTHENTICATION"]["USERNAME"] = configuration["PROXY_SERVERS"][i]["AUTHENTICATION"]["USERNAME"]
        defaultConfiguration["PROXY_SERVERS"][i]["AUTHENTICATION"]["PASSWORD"] = configuration["PROXY_SERVERS"][i]["AUTHENTICATION"]["PASSWORD"]
        
        i = i + 1
    
    return defaultConfiguration

class SSHOutputProtocol(JAP_LOCAL.OutputProtocol):
    pass

class SSHOutputProtocolFactory(JAP_LOCAL.OutputProtocolFactory):
    pass

class SSHChannel(channel.SSHChannel):
    name = "direct-tcpip"
    
    def __init__(self, remoteAddressPort, *args, **kw):
        logger.debug("SSHChannel.__init__")
        
        channel.SSHChannel.__init__(self, *args, **kw)
        
        self.remoteAddress = remoteAddressPort[0]
        self.remotePort = remoteAddressPort[1]
        self.outputProtocol = None
        self.connectionState = 0
        self.data = ""
        self.dataState = 0
        
    def channelOpen(self, specificData):
        logger.debug("SSHChannel.channelOpen")
        
        self.connectionState = 1
        
        outputProtocolFactory = SSHOutputProtocolFactory(self)
        outputProtocolFactory.protocol = SSHOutputProtocol
        
        tunnel = JAP_LOCAL.Tunnel(self.avatar.configuration)
        tunnel.connect(self.remoteAddress, self.remotePort, outputProtocolFactory)

    def openFailed(self, reason):
        logger.debug("SSHChannel.openFailed")
        
        self.connectionState = 2

    def dataReceived(self, data):
        logger.debug("SSHChannel.dataReceived")
        
        self.data = self.data + data
        if self.dataState == 0:
            self.processDataState0()
            return
        if self.dataState == 1:
            self.processDataState1()
            return
    
    def processDataState0(self):
        logger.debug("SSHChannel.processDataState0")
        
    def processDataState1(self):
        logger.debug("SSHChannel.processDataState0")
        
        self.outputProtocol.inputProtocol_dataReceived(self.data)
        
        self.data = ""
        
    def eofReceived(self):
        logger.debug("SSHChannel.eofReceived")
        
        self.loseConnection()
    
    def closeReceived(self):
        logger.debug("SSHChannel.closeReceived")
        
        self.loseConnection()
            
    def closed(self):
        logger.debug("SSHChannel.closed")
        
        self.connectionState = 2
        
        if self.outputProtocol is not None:
            self.outputProtocol.inputProtocol_connectionLost(None)
        
    def outputProtocol_connectionMade(self):
        logger.debug("SSHChannel.outputProtocol_connectionMade")
        
        self.outputProtocol.inputProtocol_dataReceived(self.data)
        
        self.data = ""
        self.dataState = 1
        
    def outputProtocol_connectionFailed(self, reason):
        logger.debug("SSHChannel.outputProtocol_connectionFailed")
        
        if self.connectionState == 1:
            self.loseConnection()
        
    def outputProtocol_connectionLost(self, reason):
        logger.debug("SSHChannel.outputProtocol_connectionLost")
        
        if self.connectionState == 1:
            self.loseConnection()
        
    def outputProtocol_dataReceived(self, data):
        logger.debug("SSHChannel.outputProtocol_dataReceived")
        
        if self.connectionState == 1:
            self.write(data)

def openSSHChannel(remoteWindow, remoteMaxPacket, data, avatar):
    remoteAdressPort, localAddressPort = forwarding.unpackOpen_direct_tcpip(data)
    
    return SSHChannel(remoteAdressPort, remoteWindow=remoteWindow, remoteMaxPacket=remoteMaxPacket, avatar=avatar)

class SSHConchUser(avatar.ConchUser):
    def __init__(self, configuration):
        logger.debug("SSHConchUser.__init__")
        
        avatar.ConchUser.__init__(self)
        
        self.configuration = configuration
        
        self.channelLookup["direct-tcpip"] = openSSHChannel

class SSHUsernamePasswordCredentialsChecker(object):
    implements(checkers.ICredentialsChecker)
    credentialInterfaces = (credentials.IUsernamePassword, )
    
    def __init__(self, configuration):
        logger.debug("SSHUsernamePasswordCredentialsChecker.__init__")
        
        self.configuration = configuration
    
    def requestAvatarId(self, credentials):
        logger.debug("SSHUsernamePasswordCredentialsChecker.requestAvatarId")
        
        authorized = False
        
        if len(self.configuration["REMOTE_PROXY_SERVER"]["AUTHENTICATION"]) == 0:
            authorized = True
        
        if authorized == False:
            i = 0
            while i < len(self.configuration["REMOTE_PROXY_SERVER"]["AUTHENTICATION"]):
                if self.configuration["REMOTE_PROXY_SERVER"]["AUTHENTICATION"][i]["USERNAME"] == credentials.username:
                    if self.configuration["REMOTE_PROXY_SERVER"]["AUTHENTICATION"][i]["PASSWORD"] != "":
                        if self.configuration["REMOTE_PROXY_SERVER"]["AUTHENTICATION"][i]["PASSWORD"] == credentials.password:
                            authorized = True
                    
                    if authorized == False:
                        return defer.fail(UnauthorizedLogin("ERROR_CREDENTIALS_PASSWORD"))
                    
                    break
                i = i + 1
            
            if authorized == False:
                return defer.fail(UnauthorizedLogin("ERROR_CREDENTIALS_USERNAME"))
        
        return defer.succeed(credentials.username)

class SSHPrivateKeyCredentialsChecker(object):
    implements(checkers.ICredentialsChecker)
    credentialInterfaces = (credentials.ISSHPrivateKey, )
    
    def __init__(self, configuration):
        logger.debug("SSHPrivateKeyCredentialsChecker.__init__")
        
        self.configuration = configuration
    
    def requestAvatarId(self, credentials):
        logger.debug("SSHPrivateKeyCredentialsChecker.requestAvatarId")
        
        authorized = False
        
        if len(self.configuration["REMOTE_PROXY_SERVER"]["AUTHENTICATION"]) == 0:
            authorized = True
        
        if authorized == False:
            i = 0
            while i < len(self.configuration["REMOTE_PROXY_SERVER"]["AUTHENTICATION"]):
                if self.configuration["REMOTE_PROXY_SERVER"]["AUTHENTICATION"][i]["USERNAME"] == credentials.username:
                    j = 0
                    while j < len(self.configuration["REMOTE_PROXY_SERVER"]["AUTHENTICATION"][i]["KEYS"]):
                        if self.configuration["REMOTE_PROXY_SERVER"]["AUTHENTICATION"][i]["KEYS"][j]["PUBLIC"]["FILE"] != "":
                            key = keys.Key.fromFile(self.configuration["REMOTE_PROXY_SERVER"]["AUTHENTICATION"][i]["KEYS"][j]["PUBLIC"]["FILE"], passphrase=str(self.configuration["REMOTE_PROXY_SERVER"]["AUTHENTICATION"][i]["KEYS"][j]["PUBLIC"]["PASSPHRASE"]))
                            
                            if key.blob() == credentials.blob:
                                if credentials.signature is None:
                                    return defer.fail(ValidPublicKey("ERROR_CREDENTIALS_SIGNATURE"))
                                
                                if key.verify(credentials.signature, credentials.sigData):
                                    authorized = True
                                
                                if authorized == False:
                                    return defer.fail(UnauthorizedLogin("ERROR_CREDENTIALS_SIGNATURE"))
                                
                                break
                        
                        j = j + 1
                    
                    if authorized == False:
                        return defer.fail(UnauthorizedLogin("ERROR_CREDENTIALS_BLOB"))
                    
                    break
                
                i = i + 1
            
            if authorized == False:
                return defer.fail(UnauthorizedLogin("ERROR_CREDENTIALS_USERNAME"))
        
        return defer.succeed(credentials.username)

class SSHRealm(object):
    implements(portal.IRealm)
    
    def __init__(self, configuration):
        logger.debug("SSHRealm.__init__")
        
        self.configuration = configuration
        
    def requestAvatar(self, avatarId, mind, *avatarInterfaces):
        logger.debug("SSHRealm.requestAvatar")
        
        return (interfaces.IConchUser, SSHConchUser(self.configuration), lambda: None)

class SSHFactory(factory.SSHFactory):
    def __init__(self, configuration):
        logger.debug("SSHFactory.__init__")
        
        self.configuration = configuration
        
        realm = SSHRealm(self.configuration)
        
        checkers = [
            SSHUsernamePasswordCredentialsChecker(configuration),
            SSHPrivateKeyCredentialsChecker(configuration)
        ]
        
        self.portal = portal.Portal(realm, checkers)
        
        key = keys.Key.fromFile(self.configuration["REMOTE_PROXY_SERVER"]["KEY"]["PUBLIC"]["FILE"], passphrase=str(self.configuration["REMOTE_PROXY_SERVER"]["KEY"]["PUBLIC"]["PASSPHRASE"]))
        self.publicKeys = {
            key.sshType(): key
        }
        
        logger.debug("SSHFactory.__init__: fingerprint=" + str(key.fingerprint()))
        
        key = keys.Key.fromFile(self.configuration["REMOTE_PROXY_SERVER"]["KEY"]["PRIVATE"]["FILE"], passphrase=str(self.configuration["REMOTE_PROXY_SERVER"]["KEY"]["PRIVATE"]["PASSPHRASE"]))
        self.privateKeys = {
            key.sshType(): key
        }