"""
JAP
Copyright (C) 2012 Jeroen Van Steirteghem

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
"""

from twisted.internet import protocol, reactor, ssl
import struct
import random
import OpenSSL
import base64
import socket
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
    configuration.setdefault("REMOTE_PROXY_SERVERS", [])
    i = 0
    while i < len(configuration["REMOTE_PROXY_SERVERS"]):
        configuration["REMOTE_PROXY_SERVERS"][i].setdefault("TYPE", "")
        configuration["REMOTE_PROXY_SERVERS"][i].setdefault("ADDRESS", "")
        configuration["REMOTE_PROXY_SERVERS"][i].setdefault("PORT", 0)
        configuration["REMOTE_PROXY_SERVERS"][i].setdefault("AUTHENTICATION", collections.OrderedDict())
        configuration["REMOTE_PROXY_SERVERS"][i]["AUTHENTICATION"].setdefault("USERNAME", "")
        configuration["REMOTE_PROXY_SERVERS"][i]["AUTHENTICATION"].setdefault("PASSWORD", "")
        configuration["REMOTE_PROXY_SERVERS"][i].setdefault("CERTIFICATE", collections.OrderedDict())
        configuration["REMOTE_PROXY_SERVERS"][i]["CERTIFICATE"].setdefault("AUTHENTICATION", collections.OrderedDict())
        configuration["REMOTE_PROXY_SERVERS"][i]["CERTIFICATE"]["AUTHENTICATION"].setdefault("FILE", "")
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
        defaultConfiguration["PROXY_SERVERS"][i]["AUTHENTICATION"] = configuration["PROXY_SERVERS"][i]["AUTHENTICATION"]
        defaultConfiguration["PROXY_SERVERS"][i]["AUTHENTICATION"]["USERNAME"] = configuration["PROXY_SERVERS"][i]["AUTHENTICATION"]["USERNAME"]
        defaultConfiguration["PROXY_SERVERS"][i]["AUTHENTICATION"]["PASSWORD"] = configuration["PROXY_SERVERS"][i]["AUTHENTICATION"]["PASSWORD"]
        i = i + 1
    defaultConfiguration["LOCAL_PROXY_SERVER"] = collections.OrderedDict()
    defaultConfiguration["LOCAL_PROXY_SERVER"]["ADDRESS"] = configuration["LOCAL_PROXY_SERVER"]["ADDRESS"]
    defaultConfiguration["LOCAL_PROXY_SERVER"]["PORT"] = configuration["LOCAL_PROXY_SERVER"]["PORT"]
    defaultConfiguration["REMOTE_PROXY_SERVERS"] = []
    i = 0
    while i < len(configuration["REMOTE_PROXY_SERVERS"]):
        defaultConfiguration["REMOTE_PROXY_SERVERS"].append(collections.OrderedDict())
        defaultConfiguration["REMOTE_PROXY_SERVERS"][i]["TYPE"] = configuration["REMOTE_PROXY_SERVERS"][i]["TYPE"]
        defaultConfiguration["REMOTE_PROXY_SERVERS"][i]["ADDRESS"] = configuration["REMOTE_PROXY_SERVERS"][i]["ADDRESS"]
        defaultConfiguration["REMOTE_PROXY_SERVERS"][i]["PORT"] = configuration["REMOTE_PROXY_SERVERS"][i]["PORT"]
        defaultConfiguration["REMOTE_PROXY_SERVERS"][i]["AUTHENTICATION"] = collections.OrderedDict()
        defaultConfiguration["REMOTE_PROXY_SERVERS"][i]["AUTHENTICATION"]["USERNAME"] = configuration["REMOTE_PROXY_SERVERS"][i]["AUTHENTICATION"]["USERNAME"]
        defaultConfiguration["REMOTE_PROXY_SERVERS"][i]["AUTHENTICATION"]["PASSWORD"] = configuration["REMOTE_PROXY_SERVERS"][i]["AUTHENTICATION"]["PASSWORD"]
        defaultConfiguration["REMOTE_PROXY_SERVERS"][i]["CERTIFICATE"] = collections.OrderedDict()
        defaultConfiguration["REMOTE_PROXY_SERVERS"][i]["CERTIFICATE"]["AUTHENTICATION"] = collections.OrderedDict()
        defaultConfiguration["REMOTE_PROXY_SERVERS"][i]["CERTIFICATE"]["AUTHENTICATION"]["FILE"] = configuration["REMOTE_PROXY_SERVERS"][i]["CERTIFICATE"]["AUTHENTICATION"]["FILE"]
        i = i + 1
    
    return defaultConfiguration

class WSOutputProtocol(autobahn.websocket.WebSocketClientProtocol):
    def __init__(self):
        logger.debug("WSOutputProtocol.__init__")
        
        self.inputProtocol = None
        self.connectionState = 0
        self.message = ""
        self.messageState = 0
        
    def onOpen(self):
        logger.debug("WSOutputProtocol.onOpen")
        
        self.connectionState = 1
        
        request = collections.OrderedDict()
        request["REMOTE_PROXY_SERVER"] = collections.OrderedDict()
        request["REMOTE_PROXY_SERVER"]["AUTHENTICATION"] = collections.OrderedDict()
        request["REMOTE_PROXY_SERVER"]["AUTHENTICATION"]["USERNAME"] = str(self.inputProtocol.configuration["REMOTE_PROXY_SERVERS"][self.inputProtocol.i]["AUTHENTICATION"]["USERNAME"])
        request["REMOTE_PROXY_SERVER"]["AUTHENTICATION"]["PASSWORD"] = str(self.inputProtocol.configuration["REMOTE_PROXY_SERVERS"][self.inputProtocol.i]["AUTHENTICATION"]["PASSWORD"])
        request["REMOTE_ADDRESS"] = str(self.inputProtocol.remoteAddress)
        request["REMOTE_PORT"] = self.inputProtocol.remotePort
        
        encoder = JAP_LOCAL.JSONEncoder()
        message = encoder.encode(request)
        
        self.sendMessage(message, False)
        
        self.message = ""
        self.messageState = 0

    def onClose(self, wasClean, code, reason):
        logger.debug("WSOutputProtocol.onClose")
        
        self.connectionState = 2
        
        self.inputProtocol.outputProtocol_connectionLost(reason)
        
    def onMessage(self, message, binary):
        logger.debug("WSOutputProtocol.onMessage")
        
        self.message = self.message + message
        if self.messageState == 0:
            self.processMessageState0();
            return
        if self.messageState == 1:
            self.processMessageState1();
            return
        
    def processMessageState0(self):
        logger.debug("WSOutputProtocol.processMessageState0")
        
        decoder = JAP_LOCAL.JSONDecoder()
        response = decoder.decode(self.message)
        
        self.inputProtocol.outputProtocol_connectionMade()
        
        self.message = ""
        self.messageState = 1
        
    def processMessageState1(self):
        logger.debug("WSOutputProtocol.processMessageState1")
        
        self.inputProtocol.outputProtocol_dataReceived(self.message)
        
        self.message = ""
        
    def inputProtocol_connectionMade(self):
        logger.debug("WSOutputProtocol.inputProtocol_connectionMade")
        
    def inputProtocol_connectionLost(self, reason):
        logger.debug("WSOutputProtocol.inputProtocol_connectionLost")
        
        if self.connectionState == 1:
            self.sendClose()
        
    def inputProtocol_dataReceived(self, data):
        logger.debug("WSOutputProtocol.inputProtocol_dataReceived")
        
        if self.connectionState == 1:
            self.sendMessage(data, True)

class WSOutputProtocolFactory(autobahn.websocket.WebSocketClientFactory):
    def __init__(self, inputProtocol, *args, **kwargs):
        logger.debug("WSOutputProtocolFactory.__init__")
        
        autobahn.websocket.WebSocketClientFactory.__init__(self, *args, **kwargs)
        
        self.inputProtocol = inputProtocol
        
    def buildProtocol(self, *args, **kwargs):
        outputProtocol = autobahn.websocket.WebSocketClientFactory.buildProtocol(self, *args, **kwargs)
        outputProtocol.inputProtocol = self.inputProtocol
        outputProtocol.inputProtocol.outputProtocol = outputProtocol
        return outputProtocol
        
    def clientConnectionFailed(self, connector, reason):
        logger.debug("WSOutputProtocolFactory.clientConnectionFailed")
        
        self.inputProtocol.outputProtocol_connectionFailed(reason)

class WSInputProtocol(JAP_LOCAL.InputProtocol):
    def __init__(self):
        logger.debug("WSInputProtocol.__init__")
        
        JAP_LOCAL.InputProtocol.__init__(self)
        
        self.i = 0
        
    def connect(self):
        logger.debug("WSInputProtocol.connect")
        
        self.i = random.randrange(0, len(self.configuration["REMOTE_PROXY_SERVERS"]))
        
        if self.configuration["REMOTE_PROXY_SERVERS"][self.i]["TYPE"] == "HTTPS":
            factory = WSOutputProtocolFactory(self, "wss://" + str(self.configuration["REMOTE_PROXY_SERVERS"][self.i]["ADDRESS"]) + ":" + str(self.configuration["REMOTE_PROXY_SERVERS"][self.i]["PORT"]), debug = False)
            factory.protocol = WSOutputProtocol
            
            if self.configuration["REMOTE_PROXY_SERVERS"][self.i]["CERTIFICATE"]["AUTHENTICATION"]["FILE"] != "":
                contextFactory = ClientContextFactory(self.configuration["REMOTE_PROXY_SERVERS"][self.i]["CERTIFICATE"]["AUTHENTICATION"]["FILE"])
            else:
                contextFactory = ssl.ClientContextFactory()
            
            tunnel = JAP_LOCAL.Tunnel(self.configuration)
            tunnel.connect(self.configuration["REMOTE_PROXY_SERVERS"][self.i]["ADDRESS"], self.configuration["REMOTE_PROXY_SERVERS"][self.i]["PORT"], factory, contextFactory)
        else:
            factory = WSOutputProtocolFactory(self, "ws://" + str(self.configuration["REMOTE_PROXY_SERVERS"][self.i]["ADDRESS"]) + ":" + str(self.configuration["REMOTE_PROXY_SERVERS"][self.i]["PORT"]), debug = False)
            factory.protocol = WSOutputProtocol
            
            tunnel = JAP_LOCAL.Tunnel(self.configuration)
            tunnel.connect(self.configuration["REMOTE_PROXY_SERVERS"][self.i]["ADDRESS"], self.configuration["REMOTE_PROXY_SERVERS"][self.i]["PORT"], factory)

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
    pass
