"""
JAP
Copyright (C) 2012 Jeroen Van Steirteghem

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
"""

from twisted.internet import reactor, protocol
import logging
import collections
import autobahn.websocket
import JAP_LOCAL

logger = logging.getLogger(__name__)

def getDefaultConfiguration(configuration=None):
    if configuration is None:
        configuration = collections.OrderedDict()
    
    configuration.setdefault("LOGGER", collections.OrderedDict())
    configuration["LOGGER"].setdefault("LEVEL", "")
    configuration.setdefault("REMOTE_PROXY_SERVER", collections.OrderedDict())
    configuration["REMOTE_PROXY_SERVER"].setdefault("TYPE", "")
    configuration["REMOTE_PROXY_SERVER"].setdefault("ADDRESS", "")
    configuration["REMOTE_PROXY_SERVER"].setdefault("PORT", 0)
    configuration["REMOTE_PROXY_SERVER"].setdefault("AUTHENTICATION", [])
    i = 0
    while i < len(configuration["REMOTE_PROXY_SERVER"]["AUTHENTICATION"]):
        configuration["REMOTE_PROXY_SERVER"]["AUTHENTICATION"][i].setdefault("USERNAME", "")
        configuration["REMOTE_PROXY_SERVER"]["AUTHENTICATION"][i].setdefault("PASSWORD", "")
        i = i + 1
    configuration["REMOTE_PROXY_SERVER"].setdefault("CERTIFICATE", collections.OrderedDict())
    configuration["REMOTE_PROXY_SERVER"]["CERTIFICATE"].setdefault("KEY", collections.OrderedDict())
    configuration["REMOTE_PROXY_SERVER"]["CERTIFICATE"]["KEY"].setdefault("FILE", "")
    configuration["REMOTE_PROXY_SERVER"]["CERTIFICATE"].setdefault("FILE", "")
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
    defaultConfiguration["REMOTE_PROXY_SERVER"]["TYPE"] = configuration["REMOTE_PROXY_SERVER"]["TYPE"]
    defaultConfiguration["REMOTE_PROXY_SERVER"]["ADDRESS"] = configuration["REMOTE_PROXY_SERVER"]["ADDRESS"]
    defaultConfiguration["REMOTE_PROXY_SERVER"]["PORT"] = configuration["REMOTE_PROXY_SERVER"]["PORT"]
    defaultConfiguration["REMOTE_PROXY_SERVER"]["AUTHENTICATION"] = [collections.OrderedDict()] * len(configuration["REMOTE_PROXY_SERVER"]["AUTHENTICATION"])
    i = 0
    while i < len(configuration["REMOTE_PROXY_SERVER"]["AUTHENTICATION"]):
        defaultConfiguration["REMOTE_PROXY_SERVER"]["AUTHENTICATION"][i]["USERNAME"] = configuration["REMOTE_PROXY_SERVER"]["AUTHENTICATION"][i]["USERNAME"]
        defaultConfiguration["REMOTE_PROXY_SERVER"]["AUTHENTICATION"][i]["PASSWORD"] = configuration["REMOTE_PROXY_SERVER"]["AUTHENTICATION"][i]["PASSWORD"]
        i = i + 1
    defaultConfiguration["REMOTE_PROXY_SERVER"]["CERTIFICATE"] = collections.OrderedDict()
    defaultConfiguration["REMOTE_PROXY_SERVER"]["CERTIFICATE"]["KEY"] = collections.OrderedDict()
    defaultConfiguration["REMOTE_PROXY_SERVER"]["CERTIFICATE"]["KEY"]["FILE"] = configuration["REMOTE_PROXY_SERVER"]["CERTIFICATE"]["KEY"]["FILE"]
    defaultConfiguration["REMOTE_PROXY_SERVER"]["CERTIFICATE"]["FILE"] = configuration["REMOTE_PROXY_SERVER"]["CERTIFICATE"]["FILE"]
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

class WSInputProtocol(autobahn.websocket.WebSocketServerProtocol):
    def __init__(self):
        logger.debug("WSInputProtocol.__init__")
        
        self.configuration = None
        self.outputProtocol = None
        self.remoteAddress = ""
        self.remotePort = 0
        self.connectionState = 0
        self.message = ""
        self.messageState = 0
    
    def onOpen(self):
        logger.debug("WSInputProtocol.onOpen")
        
        self.connectionState = 1

    def onClose(self, wasClean, code, reason):
        logger.debug("WSInputProtocol.onClose")
        
        self.connectionState = 2
        
        if self.outputProtocol is not None:
            self.outputProtocol.inputProtocol_connectionLost(reason)
            
    def onMessage(self, message, binary):
        logger.debug("WSInputProtocol.onMessage")
        
        self.message = self.message + message
        if self.messageState == 0:
            self.processMessageState0()
            return
        if self.messageState == 1:
            self.processMessageState1()
            return
    
    def processMessageState0(self):
        logger.debug("WSInputProtocol.processMessageState0")
        
        decoder = JAP_LOCAL.JSONDecoder()
        request = decoder.decode(self.message)
        
        authorized = False;

        if len(self.configuration["REMOTE_PROXY_SERVER"]["AUTHENTICATION"]) == 0:
            authorized = True
        
        if authorized == False:
            i = 0
            while i < len(self.configuration["REMOTE_PROXY_SERVER"]["AUTHENTICATION"]):
                if self.configuration["REMOTE_PROXY_SERVER"]["AUTHENTICATION"][i]["USERNAME"] == request["REMOTE_PROXY_SERVER"]["AUTHENTICATION"]["USERNAME"] and self.configuration["REMOTE_PROXY_SERVER"]["AUTHENTICATION"][i]["PASSWORD"] == request["REMOTE_PROXY_SERVER"]["AUTHENTICATION"]["PASSWORD"]:
                    authorized = True
                    break
                
                i = i + 1
        
        if authorized == False:
            self.sendClose()
            
            return
        
        self.remoteAddress = request["REMOTE_ADDRESS"]
        self.remotePort = request["REMOTE_PORT"]
        
        logger.debug("WSInputProtocol.remoteAddress: " + self.remoteAddress)
        logger.debug("WSInputProtocol.remotePort: " + str(self.remotePort))
        
        outputProtocolFactory = WSOutputProtocolFactory(self)
        outputProtocolFactory.protocol = WSOutputProtocol
        
        tunnel = JAP_LOCAL.Tunnel(self.configuration)
        tunnel.connect(self.remoteAddress, self.remotePort, outputProtocolFactory)
    
    def processMessageState1(self):
        logger.debug("WSInputProtocol.processMessageState1")
        
        self.outputProtocol.inputProtocol_dataReceived(self.message)
        
        self.message = ""
        
    def outputProtocol_connectionMade(self):
        logger.debug("WSInputProtocol.outputProtocol_connectionMade")
        
        if self.connectionState == 1:
            response = collections.OrderedDict()
            response["REMOTE_ADDRESS"] = self.remoteAddress
            response["REMOTE_PORT"] = self.remotePort
            
            encoder = JAP_LOCAL.JSONEncoder()
            message = encoder.encode(response)
            
            self.sendMessage(message, False)
            
            self.message = ""
            self.messageState = 1
        else:
            if self.connectionState == 2:
                self.outputProtocol.inputProtocol_connectionLost(None)
        
    def outputProtocol_connectionFailed(self, reason):
        logger.debug("WSInputProtocol.outputProtocol_connectionFailed")
        
        if self.connectionState == 1:
            self.sendClose()
        
    def outputProtocol_connectionLost(self, reason):
        logger.debug("WSInputProtocol.outputProtocol_connectionLost")
        
        if self.connectionState == 1:
            self.sendClose()
        else:
            if self.connectionState == 2:
                self.outputProtocol.inputProtocol_connectionLost(None)
        
    def outputProtocol_dataReceived(self, data):
        logger.debug("WSInputProtocol.outputProtocol_dataReceived")
        
        if self.connectionState == 1:
            self.sendMessage(data, True)
        else:
            if self.connectionState == 2:
                self.outputProtocol.inputProtocol_connectionLost(None)

class WSInputProtocolFactory(autobahn.websocket.WebSocketServerFactory):
    def __init__(self, configuration, *args, **kwargs):
        logger.debug("WSInputProtocolFactory.__init__")
        
        autobahn.websocket.WebSocketServerFactory.__init__(self, *args, **kwargs)
        
        self.configuration = configuration
    
    def buildProtocol(self, *args, **kwargs):
        inputProtocol = autobahn.websocket.WebSocketServerFactory.buildProtocol(self, *args, **kwargs)
        inputProtocol.configuration = self.configuration
        return inputProtocol

class WSOutputProtocol(JAP_LOCAL.OutputProtocol):
    pass

class WSOutputProtocolFactory(JAP_LOCAL.OutputProtocolFactory):
    pass
