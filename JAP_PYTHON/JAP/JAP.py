"""
JAP
Copyright (C) 2012 Jeroen Van Steirteghem

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
"""

from zope.interface import implements
from twisted.cred import portal, checkers, credentials
from twisted.cred.error import UnauthorizedLogin
from twisted.internet import defer, reactor, ssl, tcp
from twisted.web import server, static, resource, guard
import logging
import collections
import JAP
import JAP_LOCAL
import JAP_LOCAL_SSH
import JAP_LOCAL_WS
import JAP_REMOTE_SSH
import JAP_REMOTE_WS

def getDefaultConfiguration(configuration=None):
    if configuration is None:
        configuration = collections.OrderedDict()
    
    configuration.setdefault("LOGGER", collections.OrderedDict())
    configuration["LOGGER"].setdefault("LEVEL", "")
    configuration.setdefault("LOCAL_SERVER", collections.OrderedDict())
    configuration["LOCAL_SERVER"].setdefault("ADDRESS", "")
    configuration["LOCAL_SERVER"].setdefault("PORT", 0)
    configuration["LOCAL_SERVER"].setdefault("AUTHENTICATION", collections.OrderedDict())
    configuration["LOCAL_SERVER"]["AUTHENTICATION"].setdefault("USERNAME", "")
    configuration["LOCAL_SERVER"]["AUTHENTICATION"].setdefault("PASSWORD", "")
    
    defaultConfiguration = collections.OrderedDict()
    defaultConfiguration["LOGGER"] = collections.OrderedDict()
    defaultConfiguration["LOGGER"]["LEVEL"] = configuration["LOGGER"]["LEVEL"]
    defaultConfiguration["LOCAL_SERVER"] = collections.OrderedDict()
    defaultConfiguration["LOCAL_SERVER"]["ADDRESS"] = configuration["LOCAL_SERVER"]["ADDRESS"]
    defaultConfiguration["LOCAL_SERVER"]["PORT"] = configuration["LOCAL_SERVER"]["PORT"]
    defaultConfiguration["LOCAL_SERVER"]["AUTHENTICATION"] = collections.OrderedDict()
    defaultConfiguration["LOCAL_SERVER"]["AUTHENTICATION"]["USERNAME"] = configuration["LOCAL_SERVER"]["AUTHENTICATION"]["USERNAME"]
    defaultConfiguration["LOCAL_SERVER"]["AUTHENTICATION"]["PASSWORD"] = configuration["LOCAL_SERVER"]["AUTHENTICATION"]["PASSWORD"]
    
    return defaultConfiguration

class API(resource.Resource):
    def __init__(self):
        self.port_JAP_LOCAL = None
        self.port_JAP_LOCAL_SSH = None
        self.port_JAP_LOCAL_WS = None
        self.port_JAP_REMOTE_SSH = None
        self.port_JAP_REMOTE_WS = None
    
    def render_GET(self, request):
        action = request.args["action"][0]
        
        if action == "JAP":
            return self.action_JAP(request)
        elif action == "JAP_LOCAL":
            return self.action_JAP_LOCAL(request)
        elif action == "JAP_LOCAL_SSH":
            return self.action_JAP_LOCAL_SSH(request)
        elif action == "JAP_LOCAL_WS":
            return self.action_JAP_LOCAL_WS(request)
        elif action == "JAP_REMOTE_SSH":
            return self.action_JAP_REMOTE_SSH(request)
        elif action == "JAP_REMOTE_WS":
            return self.action_JAP_REMOTE_WS(request)
    
    def action_JAP(self, request):
        configuration = JAP_LOCAL.getConfiguration("./JAP.json", getDefaultConfiguration)
        
        encoder = JAP_LOCAL.JSONEncoder()
        data = encoder.encode(configuration)
        
        return data
    
    def action_JAP_LOCAL(self, request):
        configuration = JAP_LOCAL.getConfiguration("./JAP_LOCAL.json", JAP_LOCAL.getDefaultConfiguration)
        
        encoder = JAP_LOCAL.JSONEncoder()
        data = encoder.encode(configuration)
        
        return data
    
    def action_JAP_LOCAL_SSH(self, request):
        configuration = JAP_LOCAL.getConfiguration("./JAP_LOCAL_SSH.json", JAP_LOCAL_SSH.getDefaultConfiguration)
        
        encoder = JAP_LOCAL.JSONEncoder()
        data = encoder.encode(configuration)
        
        return data
    
    def action_JAP_LOCAL_WS(self, request):
        configuration = JAP_LOCAL.getConfiguration("./JAP_LOCAL_WS.json", JAP_LOCAL_WS.getDefaultConfiguration)
        
        encoder = JAP_LOCAL.JSONEncoder()
        data = encoder.encode(configuration)
        
        return data
    
    def action_JAP_REMOTE_SSH(self, request):
        configuration = JAP_LOCAL.getConfiguration("./JAP_REMOTE_SSH.json", JAP_REMOTE_SSH.getDefaultConfiguration)
        
        encoder = JAP_LOCAL.JSONEncoder()
        data = encoder.encode(configuration)
        
        return data
    
    def action_JAP_REMOTE_WS(self, request):
        configuration = JAP_LOCAL.getConfiguration("./JAP_REMOTE_WS.json", JAP_REMOTE_WS.getDefaultConfiguration)
        
        encoder = JAP_LOCAL.JSONEncoder()
        data = encoder.encode(configuration)
        
        return data
    
    def render_POST(self, request):
        action = request.args["action"][0]
        
        if action == "JAP_UPDATE":
            return self.action_JAP_UPDATE(request)
        elif action == "JAP_LOCAL_UPDATE":
            return self.action_JAP_LOCAL_UPDATE(request)
        elif action == "JAP_LOCAL_START":
            return self.action_JAP_LOCAL_START(request)
        elif action == "JAP_LOCAL_STOP":
            return self.action_JAP_LOCAL_STOP(request)
        elif action == "JAP_LOCAL_SSH_UPDATE":
            return self.action_JAP_LOCAL_SSH_UPDATE(request)
        elif action == "JAP_LOCAL_SSH_START":
            return self.action_JAP_LOCAL_SSH_START(request)
        elif action == "JAP_LOCAL_SSH_STOP":
            return self.action_JAP_LOCAL_SSH_STOP(request)
        elif action == "JAP_LOCAL_WS_UPDATE":
            return self.action_JAP_LOCAL_WS_UPDATE(request)
        elif action == "JAP_LOCAL_WS_START":
            return self.action_JAP_LOCAL_WS_START(request)
        elif action == "JAP_LOCAL_WS_STOP":
            return self.action_JAP_LOCAL_WS_STOP(request)
        elif action == "JAP_REMOTE_SSH_UPDATE":
            return self.action_JAP_REMOTE_SSH_UPDATE(request)
        elif action == "JAP_REMOTE_SSH_START":
            return self.action_JAP_REMOTE_SSH_START(request)
        elif action == "JAP_REMOTE_SSH_STOP":
            return self.action_JAP_REMOTE_SSH_STOP(request)
        elif action == "JAP_REMOTE_WS_UPDATE":
            return self.action_JAP_REMOTE_WS_UPDATE(request)
        elif action == "JAP_REMOTE_WS_START":
            return self.action_JAP_REMOTE_WS_START(request)
        elif action == "JAP_REMOTE_WS_STOP":
            return self.action_JAP_REMOTE_WS_STOP(request)
    
    def action_JAP_UPDATE(self, request):
        data = request.args["data"][0]
        
        decoder = JAP_LOCAL.JSONDecoder()
        configuration = decoder.decode(data)
        
        JAP_LOCAL.setConfiguration("./JAP.json", configuration, getDefaultConfiguration)
        
        logger = logging.getLogger("JAP")
        
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
    
    def action_JAP_LOCAL_UPDATE(self, request):
        data = request.args["data"][0]
        
        decoder = JAP_LOCAL.JSONDecoder()
        configuration = decoder.decode(data)
        
        JAP_LOCAL.setConfiguration("./JAP_LOCAL.json", configuration, JAP_LOCAL.getDefaultConfiguration)
        
        return ""
    
    def action_JAP_LOCAL_START(self, request):
        port = self.port_JAP_LOCAL
        
        if port == None:
            configuration = JAP_LOCAL.getConfiguration("./JAP_LOCAL.json", JAP_LOCAL.getDefaultConfiguration)
            
            factory = JAP_LOCAL.InputProtocolFactory(configuration)
            factory.protocol = JAP_LOCAL.InputProtocol
            
            port = tcp.Port(configuration["LOCAL_PROXY_SERVER"]["PORT"], factory, 50, configuration["LOCAL_PROXY_SERVER"]["ADDRESS"], reactor)
            port.startListening()
            
            self.port_JAP_LOCAL = port
            
            return ""
    
    def action_JAP_LOCAL_STOP(self, request):
        port = self.port_JAP_LOCAL
        
        if port != None:
            port.stopListening()
            
            self.port_JAP_LOCAL = None
            
            return ""
    
    def action_JAP_LOCAL_SSH_UPDATE(self, request):
        data = request.args["data"][0]
        
        decoder = JAP_LOCAL.JSONDecoder()
        configuration = decoder.decode(data)
        
        JAP_LOCAL.setConfiguration("./JAP_LOCAL_SSH.json", configuration, JAP_LOCAL_SSH.getDefaultConfiguration)
        
        return ""
    
    def action_JAP_LOCAL_SSH_START(self, request):
        port = self.port_JAP_LOCAL_SSH
        
        if port == None:
            configuration = JAP_LOCAL.getConfiguration("./JAP_LOCAL_SSH.json", JAP_LOCAL_SSH.getDefaultConfiguration)
            
            factory = JAP_LOCAL_SSH.SSHInputProtocolFactory(configuration)
            factory.protocol = JAP_LOCAL_SSH.SSHInputProtocol
            
            port = tcp.Port(configuration["LOCAL_PROXY_SERVER"]["PORT"], factory, 50, configuration["LOCAL_PROXY_SERVER"]["ADDRESS"], reactor)
            port.startListening()
            
            self.port_JAP_LOCAL_SSH = port
            
            return ""
    
    def action_JAP_LOCAL_SSH_STOP(self, request):
        port = self.port_JAP_LOCAL_SSH
        
        if port != None:
            port.stopListening()
            
            self.port_JAP_LOCAL_SSH = None
            
            return ""
    
    def action_JAP_LOCAL_WS_UPDATE(self, request):
        data = request.args["data"][0]
        
        decoder = JAP_LOCAL.JSONDecoder()
        configuration = decoder.decode(data)
        
        JAP_LOCAL.setConfiguration("./JAP_LOCAL_WS.json", configuration, JAP_LOCAL_WS.getDefaultConfiguration)
        
        return ""
    
    def action_JAP_LOCAL_WS_START(self, request):
        port = self.port_JAP_LOCAL_WS
        
        if port == None:
            configuration = JAP_LOCAL.getConfiguration("./JAP_LOCAL_WS.json", JAP_LOCAL_WS.getDefaultConfiguration)
            
            factory = JAP_LOCAL_WS.WSInputProtocolFactory(configuration)
            factory.protocol = JAP_LOCAL_WS.WSInputProtocol
            
            port = tcp.Port(configuration["LOCAL_PROXY_SERVER"]["PORT"], factory, 50, configuration["LOCAL_PROXY_SERVER"]["ADDRESS"], reactor)
            port.startListening()
            
            self.port_JAP_LOCAL_WS = port
            
            return ""
    
    def action_JAP_LOCAL_WS_STOP(self, request):
        port = self.port_JAP_LOCAL_WS
        
        if port != None:
            port.stopListening()
            
            self.port_JAP_LOCAL_WS = None
            
            return ""
    
    def action_JAP_REMOTE_SSH_UPDATE(self, request):
        data = request.args["data"][0]
        
        decoder = JAP_LOCAL.JSONDecoder()
        configuration = decoder.decode(data)
        
        JAP_LOCAL.setConfiguration("./JAP_REMOTE_SSH.json", configuration, JAP_REMOTE_SSH.getDefaultConfiguration)
        
        return ""
    
    def action_JAP_REMOTE_SSH_START(self, request):
        port = self.port_JAP_REMOTE_SSH
        
        if port == None:
            configuration = JAP_LOCAL.getConfiguration("./JAP_REMOTE_SSH.json", JAP_REMOTE_SSH.getDefaultConfiguration)
            
            factory = JAP_REMOTE_SSH.SSHFactory(configuration)
            
            port = tcp.Port(configuration["REMOTE_PROXY_SERVER"]["PORT"], factory, 50, configuration["REMOTE_PROXY_SERVER"]["ADDRESS"], reactor)
            port.startListening()
            
            self.port_JAP_REMOTE_SSH = port
            
            return ""
    
    def action_JAP_REMOTE_SSH_STOP(self, request):
        port = self.port_JAP_REMOTE_SSH
        
        if port != None:
            port.stopListening()
            
            self.port_JAP_REMOTE_SSH = None
            
            return ""
    
    def action_JAP_REMOTE_WS_UPDATE(self, request):
        data = request.args["data"][0]
        
        decoder = JAP_LOCAL.JSONDecoder()
        configuration = decoder.decode(data)
        
        JAP_LOCAL.setConfiguration("./JAP_REMOTE_WS.json", configuration, JAP_REMOTE_WS.getDefaultConfiguration)
        
        return ""
    
    def action_JAP_REMOTE_WS_START(self, request):
        port = self.port_JAP_REMOTE_WS
        
        if port == None:
            configuration = JAP_LOCAL.getConfiguration("./JAP_REMOTE_WS.json", JAP_REMOTE_WS.getDefaultConfiguration)
            
            if configuration["REMOTE_PROXY_SERVER"]["TYPE"] == "HTTPS":
                factory = JAP_REMOTE_WS.WSInputProtocolFactory(configuration, "wss://" + str(configuration["REMOTE_PROXY_SERVER"]["ADDRESS"]) + ":" + str(configuration["REMOTE_PROXY_SERVER"]["PORT"]), debug = False)
                factory.protocol = JAP_REMOTE_WS.WSInputProtocol
                
                contextFactory = ssl.DefaultOpenSSLContextFactory(configuration["REMOTE_PROXY_SERVER"]["CERTIFICATE"]["KEY"]["FILE"], configuration["REMOTE_PROXY_SERVER"]["CERTIFICATE"]["FILE"])
                
                port = ssl.Port(configuration["REMOTE_PROXY_SERVER"]["PORT"], factory, contextFactory, 50, configuration["REMOTE_PROXY_SERVER"]["ADDRESS"], reactor)
                port.startListening()
                
                self.port_JAP_REMOTE_WS = port
            else:
                factory = JAP_REMOTE_WS.WSInputProtocolFactory(configuration, "ws://" + str(configuration["REMOTE_PROXY_SERVER"]["ADDRESS"]) + ":" + str(configuration["REMOTE_PROXY_SERVER"]["PORT"]), debug = False)
                factory.protocol = JAP_REMOTE_WS.WSInputProtocol
                
                port = tcp.Port(configuration["REMOTE_PROXY_SERVER"]["PORT"], factory, 50, configuration["REMOTE_PROXY_SERVER"]["ADDRESS"], reactor)
                port.startListening()
                
                self.port_JAP_REMOTE_WS = port
            
            return ""
    
    def action_JAP_REMOTE_WS_STOP(self, request):
        port = self.port_JAP_REMOTE_WS
        
        if port != None:
            port.stopListening()
            
            self.port_JAP_REMOTE_WS = None
            
            return ""

class HTTPUsernamePasswordCredentialsChecker:
    implements(checkers.ICredentialsChecker)
    credentialInterfaces = (credentials.IUsernamePassword, )
    
    def __init__(self, configuration):
        self.configuration = configuration
    
    def requestAvatarId(self, credentials):
        authorized = False;
        
        if self.configuration["LOCAL_SERVER"]["AUTHENTICATION"]["USERNAME"] == credentials.username:
            if self.configuration["LOCAL_SERVER"]["AUTHENTICATION"]["PASSWORD"] != "":
                if self.configuration["LOCAL_SERVER"]["AUTHENTICATION"]["PASSWORD"] == credentials.password:
                    authorized = True
            
            if authorized == False:
                return defer.fail(UnauthorizedLogin("ERROR_CREDENTIALS_PASSWORD"))
        
        if authorized == False:
            return defer.fail(UnauthorizedLogin("ERROR_CREDENTIALS_USERNAME"))
        
        return defer.succeed(credentials.username)
 
class HTTPRealm(object):
    implements(portal.IRealm)
    
    def __init__(self, resource):
        self.resource = resource
    
    def requestAvatar(self, avatarId, mind, *avatarInterfaces):
        return (resource.IResource, self.resource, lambda: None)

def createSite(configuration):
    resource = static.File("./WWW")
    resource.putChild("API", API())
    
    realm = HTTPRealm(resource)
    
    checkers = [
        HTTPUsernamePasswordCredentialsChecker(configuration)
    ]
    
    credentialFactories = [
        guard.BasicCredentialFactory("JAP")
    ]
    
    resource = guard.HTTPAuthSessionWrapper(portal.Portal(realm, checkers), credentialFactories)
    
    site = server.Site(resource)
    
    return site