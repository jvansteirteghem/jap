"""
JAP
Copyright (C) 2012 Jeroen Van Steirteghem

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
"""

from twisted.internet import reactor, protocol, ssl
import struct
import json
import base64
import socket
import logging
import autobahn.websocket

logger = logging.getLogger("JAP.JAP_WS_REMOTE")

def setDefaultConfiguration(configuration):
    configuration.setdefault("LOGGER", {})
    configuration["LOGGER"].setdefault("LEVEL", "")
    configuration.setdefault("REMOTE_PROXY_SERVER", {})
    configuration["REMOTE_PROXY_SERVER"].setdefault("TYPE", "")
    configuration["REMOTE_PROXY_SERVER"].setdefault("ADDRESS", "")
    configuration["REMOTE_PROXY_SERVER"].setdefault("PORT", 0)
    configuration["REMOTE_PROXY_SERVER"].setdefault("AUTHENTICATION", [])
    i = 0
    while i < len(configuration["REMOTE_PROXY_SERVER"]["AUTHENTICATION"]):
        configuration["REMOTE_PROXY_SERVER"]["AUTHENTICATION"][i].setdefault("USERNAME", "")
        configuration["REMOTE_PROXY_SERVER"]["AUTHENTICATION"][i].setdefault("PASSWORD", "")
        i = i + 1
    configuration["REMOTE_PROXY_SERVER"].setdefault("CERTIFICATE", {})
    configuration["REMOTE_PROXY_SERVER"]["CERTIFICATE"].setdefault("KEY", {})
    configuration["REMOTE_PROXY_SERVER"]["CERTIFICATE"]["KEY"].setdefault("FILE", "")
    configuration["REMOTE_PROXY_SERVER"]["CERTIFICATE"].setdefault("FILE", "")
        
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
        
        decoder = json.JSONDecoder()
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
        
        factory = WSOutputProtocolFactory(self)
        factory.protocol = WSOutputProtocol
        reactor.connectTCP(self.remoteAddress, self.remotePort, factory)
    
    def processMessageState1(self):
        logger.debug("WSInputProtocol.processMessageState1")
        
        self.outputProtocol.inputProtocol_dataReceived(self.message)
        
        self.message = ""
        
    def outputProtocol_connectionMade(self):
        logger.debug("InputProtocol.outputProtocol_connectionMade")
        
        if self.connectionState == 1:
            response = {}
            response["REMOTE_ADDRESS"] = self.remoteAddress
            response["REMOTE_PORT"] = self.remotePort
            
            encoder = json.JSONEncoder()
            message = encoder.encode(response)
            
            self.sendMessage(message, False)
            
            self.message = ""
            self.messageState = 1
        else:
            if self.connectionState == 2:
                self.outputProtocol.inputProtocol_connectionLost(None)
        
    def outputProtocol_connectionLost(self, reason):
        logger.debug("InputProtocol.outputProtocol_connectionLost")
        
        if self.connectionState == 1:
            self.sendClose()
        else:
            if self.connectionState == 2:
                self.outputProtocol.inputProtocol_connectionLost(None)
        
    def outputProtocol_dataReceived(self, data):
        logger.debug("InputProtocol.outputProtocol_dataReceived")
        
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

class WSOutputProtocol(protocol.Protocol):
    def __init__(self):
        logger.debug("WSOutputProtocol.__init__")
        
        self.inputProtocol = None
        self.connectionState = 0
    
    def connectionMade(self):
        logger.debug("WSOutputProtocol.connectionMade")
        
        self.connectionState = 1
        
        self.inputProtocol.outputProtocol_connectionMade()

    def connectionLost(self, reason):
        logger.debug("WSOutputProtocol.connectionLost")
        
        self.connectionState = 2
        
        self.inputProtocol.outputProtocol_connectionLost(reason)
        
    def dataReceived(self, data):
        logger.debug("WSOutputProtocol.dataReceived")
        
        self.inputProtocol.outputProtocol_dataReceived(data)
        
    def inputProtocol_connectionMade(self):
        logger.debug("WSOutputProtocol.inputProtocol_connectionMade")
        
    def inputProtocol_connectionLost(self, reason):
        logger.debug("WSOutputProtocol.inputProtocol_connectionLost")
        
        if self.connectionState == 1:
            self.transport.loseConnection()
        
    def inputProtocol_dataReceived(self, data):
        logger.debug("WSOutputProtocol.inputProtocol_dataReceived")
        
        if self.connectionState == 1:
            self.transport.write(data)


class WSOutputProtocolFactory(protocol.ClientFactory):
    def __init__(self, inputProtocol):
        logger.debug("WSOutputProtocolFactory.__init__")
        
        self.inputProtocol = inputProtocol
    
    def buildProtocol(self, *args, **kw):
        outputProtocol = protocol.ClientFactory.buildProtocol(self, *args, **kw)
        outputProtocol.inputProtocol = self.inputProtocol
        outputProtocol.inputProtocol.outputProtocol = outputProtocol
        return outputProtocol