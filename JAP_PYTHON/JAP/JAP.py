"""
JAP
Copyright (C) 2012 Jeroen Van Steirteghem

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
"""

from zope.interface import implements
from twisted.cred import portal, checkers, credentials, error
from twisted.internet import defer, reactor, ssl, tcp
from twisted.web import server, static, resource, guard
import json
import logging
import LOCAL.JAP_LOCAL
import LOCAL_SSH.JAP_LOCAL_SSH
import LOCAL_WS.JAP_LOCAL_WS
import REMOTE_WS.JAP_REMOTE_WS

def setDefaultConfiguration(configuration):
    configuration.setdefault("LOGGER", {})
    configuration["LOGGER"].setdefault("LEVEL", "")
    configuration.setdefault("LOCAL_SERVER", {})
    configuration["LOCAL_SERVER"].setdefault("ADDRESS", "")
    configuration["LOCAL_SERVER"].setdefault("PORT", 0)
    configuration["LOCAL_SERVER"].setdefault("AUTHENTICATION", {})
    configuration["LOCAL_SERVER"]["AUTHENTICATION"].setdefault("USERNAME", "")
    configuration["LOCAL_SERVER"]["AUTHENTICATION"].setdefault("PASSWORD", "")

class API(resource.Resource):
    def __init__(self):
        self.port_LOCAL = None
        self.port_LOCAL_SSH = None
        self.port_LOCAL_WS = None
        self.port_REMOTE_WS = None
    
    def render_GET(self, request):
        action = request.args["action"][0]
        
        if action == "LOCAL":
            return self.action_LOCAL(request)
        elif action == "LOCAL_SSH":
            return self.action_LOCAL_SSH(request)
        elif action == "LOCAL_WS":
            return self.action_LOCAL_WS(request)
        elif action == "REMOTE_WS":
            return self.action_REMOTE_WS(request)
    
    def action_LOCAL(self, request):
        file = open("./JAP_LOCAL.json", "r")
        data = file.read()
        file.close()
        
        return data
    
    def action_LOCAL_SSH(self, request):
        file = open("./JAP_LOCAL_SSH.json", "r")
        data = file.read()
        file.close()
        
        return data
    
    def action_LOCAL_WS(self, request):
        file = open("./JAP_LOCAL_WS.json", "r")
        data = file.read()
        file.close()
        
        return data
    
    def action_REMOTE_WS(self, request):
        file = open("./JAP_REMOTE_WS.json", "r")
        data = file.read()
        file.close()
        
        return data
    
    def render_POST(self, request):
        action = request.args["action"][0]
        
        if action == "LOCAL_UPDATE":
            return self.action_LOCAL_UPDATE(request)
        elif action == "LOCAL_START":
            return self.action_LOCAL_START(request)
        elif action == "LOCAL_STOP":
            return self.action_LOCAL_STOP(request)
        elif action == "LOCAL_SSH_UPDATE":
            return self.action_LOCAL_SSH_UPDATE(request)
        elif action == "LOCAL_SSH_START":
            return self.action_LOCAL_SSH_START(request)
        elif action == "LOCAL_SSH_STOP":
            return self.action_LOCAL_SSH_STOP(request)
        elif action == "LOCAL_WS_UPDATE":
            return self.action_LOCAL_WS_UPDATE(request)
        elif action == "LOCAL_WS_START":
            return self.action_LOCAL_WS_START(request)
        elif action == "LOCAL_WS_STOP":
            return self.action_LOCAL_WS_STOP(request)
        elif action == "REMOTE_WS_UPDATE":
            return self.action_REMOTE_WS_UPDATE(request)
        elif action == "REMOTE_WS_START":
            return self.action_REMOTE_WS_START(request)
        elif action == "REMOTE_WS_STOP":
            return self.action_REMOTE_WS_STOP(request)
    
    def action_LOCAL_UPDATE(self, request):
        data = request.args["data"][0]
        
        file = open("./JAP_LOCAL.json", "w")
        file.write(data)
        file.close()
        
        decoder = json.JSONDecoder()
        configuration = decoder.decode(data)
        
        logger = logging.getLogger("JAP.LOCAL")
        
        if configuration["LOGGER"]["LEVEL"] == "DEBUG":
            logger.setLevel(logging.DEBUG)
        elif configuration["LOGGER"]["LEVEL"] == "INFO":
            logger.setLevel(logging.INFO)
        elif configuration["LOGGER"]["LEVEL"] == "WARNING":
            logger.setLevel(logging.WARNING)
        elif configuration["LOGGER"]["LEVEL"] == "ERROR":
            logger.setLevel(logging.ERROR)
        elif configuration["LOGGER"]["LEVEL"] == "CRITICAL":
            logger.setLevel(logging.CRITICAL)
        else:
            logger.setLevel(logging.NOTSET)
        
        return ""
    
    def action_LOCAL_START(self, request):
        port = self.port_LOCAL
        
        if port == None:
            file = open("./JAP_LOCAL.json", "r")
            data = file.read()
            file.close()
            
            decoder = json.JSONDecoder()
            configuration = decoder.decode(data)
            
            logger = logging.getLogger("JAP.LOCAL")
            
            if configuration["LOGGER"]["LEVEL"] == "DEBUG":
                logger.setLevel(logging.DEBUG)
            elif configuration["LOGGER"]["LEVEL"] == "INFO":
                logger.setLevel(logging.INFO)
            elif configuration["LOGGER"]["LEVEL"] == "WARNING":
                logger.setLevel(logging.WARNING)
            elif configuration["LOGGER"]["LEVEL"] == "ERROR":
                logger.setLevel(logging.ERROR)
            elif configuration["LOGGER"]["LEVEL"] == "CRITICAL":
                logger.setLevel(logging.CRITICAL)
            else:
                logger.setLevel(logging.NOTSET)
            
            factory = LOCAL.JAP_LOCAL.InputProtocolFactory(configuration)
            factory.protocol = LOCAL.JAP_LOCAL.InputProtocol
            
            port = tcp.Port(configuration["LOCAL_PROXY_SERVER"]["PORT"], factory, 50, configuration["LOCAL_PROXY_SERVER"]["ADDRESS"], reactor)
            port.startListening()
            
            self.port_LOCAL = port
            
            return ""
    
    def action_LOCAL_STOP(self, request):
        port = self.port_LOCAL
        
        if port != None:
            port.stopListening()
            
            self.port_LOCAL = None
            
            return ""
    
    def action_LOCAL_SSH_UPDATE(self, request):
        data = request.args["data"][0]
        
        file = open("./JAP_LOCAL_SSH.json", "w")
        file.write(data)
        file.close()
        
        decoder = json.JSONDecoder()
        configuration = decoder.decode(data)
        
        logger = logging.getLogger("JAP.LOCAL_SSH")
        
        if configuration["LOGGER"]["LEVEL"] == "DEBUG":
            logger.setLevel(logging.DEBUG)
        elif configuration["LOGGER"]["LEVEL"] == "INFO":
            logger.setLevel(logging.INFO)
        elif configuration["LOGGER"]["LEVEL"] == "WARNING":
            logger.setLevel(logging.WARNING)
        elif configuration["LOGGER"]["LEVEL"] == "ERROR":
            logger.setLevel(logging.ERROR)
        elif configuration["LOGGER"]["LEVEL"] == "CRITICAL":
            logger.setLevel(logging.CRITICAL)
        else:
            logger.setLevel(logging.NOTSET)
        
        return ""
    
    def action_LOCAL_SSH_START(self, request):
        port = self.port_LOCAL_SSH
        
        if port == None:
            file = open("./JAP_LOCAL_SSH.json", "r")
            data = file.read()
            file.close()
            
            decoder = json.JSONDecoder()
            configuration = decoder.decode(data)
            
            logger = logging.getLogger("JAP.LOCAL_SSH")
            
            if configuration["LOGGER"]["LEVEL"] == "DEBUG":
                logger.setLevel(logging.DEBUG)
            elif configuration["LOGGER"]["LEVEL"] == "INFO":
                logger.setLevel(logging.INFO)
            elif configuration["LOGGER"]["LEVEL"] == "WARNING":
                logger.setLevel(logging.WARNING)
            elif configuration["LOGGER"]["LEVEL"] == "ERROR":
                logger.setLevel(logging.ERROR)
            elif configuration["LOGGER"]["LEVEL"] == "CRITICAL":
                logger.setLevel(logging.CRITICAL)
            else:
                logger.setLevel(logging.NOTSET)
            
            factory = LOCAL_SSH.JAP_LOCAL_SSH.SSHInputProtocolFactory(configuration)
            factory.protocol = LOCAL_SSH.JAP_LOCAL_SSH.SSHInputProtocol
            
            port = tcp.Port(configuration["LOCAL_PROXY_SERVER"]["PORT"], factory, 50, configuration["LOCAL_PROXY_SERVER"]["ADDRESS"], reactor)
            port.startListening()
            
            self.port_LOCAL_SSH = port
            
            return ""
    
    def action_LOCAL_SSH_STOP(self, request):
        port = self.port_LOCAL_SSH
        
        if port != None:
            port.stopListening()
            
            self.port_LOCAL_SSH = None
            
            return ""
    
    def action_LOCAL_WS_UPDATE(self, request):
        data = request.args["data"][0]
        
        file = open("./JAP_LOCAL_WS.json", "w")
        file.write(data)
        file.close()
        
        decoder = json.JSONDecoder()
        configuration = decoder.decode(data)
        
        logger = logging.getLogger("JAP.LOCAL_WS")
        
        if configuration["LOGGER"]["LEVEL"] == "DEBUG":
            logger.setLevel(logging.DEBUG)
        elif configuration["LOGGER"]["LEVEL"] == "INFO":
            logger.setLevel(logging.INFO)
        elif configuration["LOGGER"]["LEVEL"] == "WARNING":
            logger.setLevel(logging.WARNING)
        elif configuration["LOGGER"]["LEVEL"] == "ERROR":
            logger.setLevel(logging.ERROR)
        elif configuration["LOGGER"]["LEVEL"] == "CRITICAL":
            logger.setLevel(logging.CRITICAL)
        else:
            logger.setLevel(logging.NOTSET)
        
        return ""
    
    def action_LOCAL_WS_START(self, request):
        port = self.port_LOCAL_WS
        
        if port == None:
            file = open("./JAP_LOCAL_WS.json", "r")
            data = file.read()
            file.close()
            
            decoder = json.JSONDecoder()
            configuration = decoder.decode(data)
            
            logger = logging.getLogger("JAP.LOCAL_WS")
            
            if configuration["LOGGER"]["LEVEL"] == "DEBUG":
                logger.setLevel(logging.DEBUG)
            elif configuration["LOGGER"]["LEVEL"] == "INFO":
                logger.setLevel(logging.INFO)
            elif configuration["LOGGER"]["LEVEL"] == "WARNING":
                logger.setLevel(logging.WARNING)
            elif configuration["LOGGER"]["LEVEL"] == "ERROR":
                logger.setLevel(logging.ERROR)
            elif configuration["LOGGER"]["LEVEL"] == "CRITICAL":
                logger.setLevel(logging.CRITICAL)
            else:
                logger.setLevel(logging.NOTSET)
            
            factory = LOCAL_WS.JAP_LOCAL_WS.WSInputProtocolFactory(configuration)
            factory.protocol = LOCAL_WS.JAP_LOCAL_WS.WSInputProtocol
            
            port = tcp.Port(configuration["LOCAL_PROXY_SERVER"]["PORT"], factory, 50, configuration["LOCAL_PROXY_SERVER"]["ADDRESS"], reactor)
            port.startListening()
            
            self.port_LOCAL_WS = port
            
            return ""
    
    def action_LOCAL_WS_STOP(self, request):
        port = self.port_LOCAL_WS
        
        if port != None:
            port.stopListening()
            
            self.port_LOCAL_WS = None
            
            return ""
    
    def action_REMOTE_WS_UPDATE(self, request):
        data = request.args["data"][0]
        
        file = open("./JAP_REMOTE_WS.json", "w")
        file.write(data)
        file.close()
        
        decoder = json.JSONDecoder()
        configuration = decoder.decode(data)
        
        logger = logging.getLogger("JAP.REMOTE_WS")
        
        if configuration["LOGGER"]["LEVEL"] == "DEBUG":
            logger.setLevel(logging.DEBUG)
        elif configuration["LOGGER"]["LEVEL"] == "INFO":
            logger.setLevel(logging.INFO)
        elif configuration["LOGGER"]["LEVEL"] == "WARNING":
            logger.setLevel(logging.WARNING)
        elif configuration["LOGGER"]["LEVEL"] == "ERROR":
            logger.setLevel(logging.ERROR)
        elif configuration["LOGGER"]["LEVEL"] == "CRITICAL":
            logger.setLevel(logging.CRITICAL)
        else:
            logger.setLevel(logging.NOTSET)
        
        return ""
    
    def action_REMOTE_WS_START(self, request):
        port = self.port_REMOTE_WS
        
        if port == None:
            file = open("./JAP_REMOTE_WS.json", "r")
            data = file.read()
            file.close()
            
            decoder = json.JSONDecoder()
            configuration = decoder.decode(data)
            
            logger = logging.getLogger("JAP.REMOTE_WS")
            
            if configuration["LOGGER"]["LEVEL"] == "DEBUG":
                logger.setLevel(logging.DEBUG)
            elif configuration["LOGGER"]["LEVEL"] == "INFO":
                logger.setLevel(logging.INFO)
            elif configuration["LOGGER"]["LEVEL"] == "WARNING":
                logger.setLevel(logging.WARNING)
            elif configuration["LOGGER"]["LEVEL"] == "ERROR":
                logger.setLevel(logging.ERROR)
            elif configuration["LOGGER"]["LEVEL"] == "CRITICAL":
                logger.setLevel(logging.CRITICAL)
            else:
                logger.setLevel(logging.NOTSET)
            
            if configuration["REMOTE_PROXY_SERVER"]["TYPE"] == "HTTPS":
                factory = REMOTE_WS.JAP_REMOTE_WS.WSInputProtocolFactory(configuration, "wss://" + str(configuration["REMOTE_PROXY_SERVER"]["ADDRESS"]) + ":" + str(configuration["REMOTE_PROXY_SERVER"]["PORT"]), debug = False)
                factory.protocol = REMOTE_WS.JAP_REMOTE_WS.WSInputProtocol
                
                contextFactory = ssl.DefaultOpenSSLContextFactory(configuration["REMOTE_PROXY_SERVER"]["CERTIFICATE"]["KEY"]["FILE"], configuration["REMOTE_PROXY_SERVER"]["CERTIFICATE"]["FILE"])
                
                port = ssl.Port(configuration["REMOTE_PROXY_SERVER"]["PORT"], factory, contextFactory, 50, configuration["REMOTE_PROXY_SERVER"]["ADDRESS"], reactor)
                port.startListening()
                
                self.port_REMOTE_WS = port
            else:
                factory = REMOTE_WS.JAP_REMOTE_WS.WSInputProtocolFactory(configuration, "ws://" + str(configuration["REMOTE_PROXY_SERVER"]["ADDRESS"]) + ":" + str(configuration["REMOTE_PROXY_SERVER"]["PORT"]), debug = False)
                factory.protocol = REMOTE_WS.JAP_REMOTE_WS.WSInputProtocol
                
                port = tcp.Port(configuration["REMOTE_PROXY_SERVER"]["PORT"], factory, 50, configuration["REMOTE_PROXY_SERVER"]["ADDRESS"], reactor)
                port.startListening()
                
                self.port_REMOTE_WS = port
            
            return ""
    
    def action_REMOTE_WS_STOP(self, request):
        port = self.port_REMOTE_WS
        
        if port != None:
            port.stopListening()
            
            self.port_REMOTE_WS = None
            
            return ""

class CredentialsChecker:
    implements(checkers.ICredentialsChecker)
    credentialInterfaces = (credentials.IUsernamePassword, )
     
    def __init__(self, configuration):
        self.configuration = configuration
     
    def requestAvatarId(self, credentials):
        if credentials.username == self.configuration["LOCAL_SERVER"]["AUTHENTICATION"]["USERNAME"]:
            if credentials.password == self.configuration["LOCAL_SERVER"]["AUTHENTICATION"]["PASSWORD"]:
                return defer.succeed(credentials.username)
            else:
                return defer.fail(error.UnauthorizedLogin("PASSWORD NOT OK"))
        else:
            return defer.fail(error.UnauthorizedLogin("USERNAME NOT OK"))
 
class Realm(object):
    implements(portal.IRealm)
     
    def __init__(self, WWW):
        self.WWW = WWW
    
    def requestAvatar(self, user, mind, *interfaces):
        if resource.IResource in interfaces:
            return (resource.IResource, self.WWW, lambda: None)
        
        raise NotImplementedError()

def createSite(configuration):
    WWW = static.File("./WWW")
    WWW.putChild("API", API())
    
    if configuration["LOCAL_SERVER"]["AUTHENTICATION"]["USERNAME"] != "":
        realm = Realm(WWW)
        
        credentialsChecker = CredentialsChecker(configuration)
        checkers = [credentialsChecker]
        
        basicCredentialFactory = guard.BasicCredentialFactory("JAP")
        credentialFactories = [basicCredentialFactory]
        
        WWW = guard.HTTPAuthSessionWrapper(portal.Portal(realm, checkers), credentialFactories)
    
    site = server.Site(WWW)
    
    return site