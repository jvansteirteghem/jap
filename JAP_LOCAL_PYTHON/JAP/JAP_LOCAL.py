"""
JAP
Copyright (C) 2012 Jeroen Van Steirteghem

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
"""

from twisted.internet import protocol, reactor
import struct
import json
import socket
import logging
import TUNNEL

logger = logging.getLogger("JAP.JAP_LOCAL")

def setDefaultConfiguration(configuration):
    configuration.setdefault("LOGGER", {})
    configuration["LOGGER"].setdefault("LEVEL", 10)
    configuration.setdefault("LOCAL_PROXY_SERVER", {})
    configuration["LOCAL_PROXY_SERVER"].setdefault("ADDRESS", "")
    configuration["LOCAL_PROXY_SERVER"].setdefault("PORT", 0)
    configuration.setdefault("PROXY_SERVER", {})
    configuration["PROXY_SERVER"].setdefault("ADDRESS", "")
    configuration["PROXY_SERVER"].setdefault("PORT", 0)
    configuration["PROXY_SERVER"].setdefault("AUTHENTICATION", {})
    configuration["PROXY_SERVER"]["AUTHENTICATION"].setdefault("USERNAME", "")
    configuration["PROXY_SERVER"]["AUTHENTICATION"].setdefault("PASSWORD", "")

class OutputProtocol(protocol.Protocol):
    def __init__(self):
        logger.debug("OutputProtocol.__init__")
        
        self.inputProtocol = None
        self.connectionState = 0
        
    def connectionMade(self):
        logger.debug("OutputProtocol.connectionMade")
        
        self.connectionState = 1
        
        self.inputProtocol.outputProtocol_connectionMade()
        
    def connectionLost(self, reason):
        logger.debug("OutputProtocol.connectionLost")
        
        self.connectionState = 2
        
        self.inputProtocol.outputProtocol_connectionLost(reason)
        
    def dataReceived(self, data):
        logger.debug("OutputProtocol.dataReceived")
        
        self.inputProtocol.outputProtocol_dataReceived(data)
        
    def inputProtocol_connectionMade(self):
        logger.debug("OutputProtocol.inputProtocol_connectionMade")
        
    def inputProtocol_connectionLost(self, reason):
        logger.debug("OutputProtocol.inputProtocol_connectionLost")
        
        if self.connectionState == 1:
            self.transport.loseConnection()
        
    def inputProtocol_dataReceived(self, data):
        logger.debug("OutputProtocol.inputProtocol_dataReceived")
        
        if self.connectionState == 1:
            self.transport.write(data)

class OutputProtocolFactory(protocol.ClientFactory):
    def __init__(self, inputProtocol):
        logger.debug("OutputProtocolFactory.__init__")
        
        self.inputProtocol = inputProtocol
        
    def buildProtocol(self, *args, **kw):
        outputProtocol = protocol.ClientFactory.buildProtocol(self, *args, **kw)
        outputProtocol.inputProtocol = self.inputProtocol
        outputProtocol.inputProtocol.outputProtocol = outputProtocol
        return outputProtocol

class InputProtocol(protocol.Protocol):
    def __init__(self):
        logger.debug("InputProtocol.__init__")
        
        self.configuration = None
        self.outputProtocol = None
        self.remoteAddressType = 0
        self.remoteAddress = ""
        self.remotePort = 0
        self.connectionState = 0
        self.data = ""
        self.dataState = 0
    
    def connectionMade(self):
        logger.debug("InputProtocol.connectionMade")
        
        self.connectionState = 1
    
    def connectionLost(self, reason):
        logger.debug("InputProtocol.connectionLost")
        
        self.connectionState = 2
        
        if self.outputProtocol is not None:
            self.outputProtocol.inputProtocol_connectionLost(reason)
    
    def dataReceived(self, data):
        logger.debug("InputProtocol.dataReceived")
        
        self.data = self.data + data
        if self.dataState == 0:
            self.processDataState0()
            return
        if self.dataState == 1:
            self.processDataState1()
            return
        if self.dataState == 2:
            self.processDataState2()
            return
    
    def processDataState0(self):
        logger.debug("InputProtocol.processDataState0")
        
        # no authentication
        self.transport.write(struct.pack('!BB', 0x05, 0x00))
        
        self.data = ""
        self.dataState = 1
    
    def processDataState1(self):
        logger.debug("InputProtocol.processDataState1")
        
        v, c, r, self.remoteAddressType = struct.unpack('!BBBB', self.data[:4])
        
        # IPv4
        if self.remoteAddressType == 0x01:
            remoteAddress, self.remotePort = struct.unpack('!IH', self.data[4:10])
            self.remoteAddress = socket.inet_ntoa(struct.pack('!I', remoteAddress))
            self.data = self.data[10:]
        else:
            # DN
            if self.remoteAddressType == 0x03:
                remoteAddressLength = ord(self.data[4])
                self.remoteAddress, self.remotePort = struct.unpack('!%dsH' % remoteAddressLength, self.data[5:])
                self.data = self.data[7 + remoteAddressLength:]
            # IPv6
            else:
                response = struct.pack('!BBBBIH', 0x05, 0x08, 0, 1, 0, 0)
                self.transport.write(response)
                self.transport.loseConnection()
                return
        
        logger.debug("InputProtocol.remoteAddressType: " + str(self.remoteAddressType))
        logger.debug("InputProtocol.remoteAddress: " + self.remoteAddress)
        logger.debug("InputProtocol.remotePort: " + str(self.remotePort))
        
        # connect
        if c == 0x01:
            self.do_CONNECT()
        else:
            response = struct.pack('!BBBBIH', 0x05, 0x07, 0, 1, 0, 0)
            self.transport.write(response)
            self.transport.loseConnection()
            return
            
    def do_CONNECT(self):
        logger.debug("InputProtocol.do_CONNECT")
        
        factory = OutputProtocolFactory(self)
        factory.protocol = OutputProtocol
        
        if self.configuration["PROXY_SERVER"]["ADDRESS"] != "":
            tunnel = TUNNEL.Tunnel(self.configuration["PROXY_SERVER"]["ADDRESS"], self.configuration["PROXY_SERVER"]["PORT"], self.configuration["PROXY_SERVER"]["AUTHENTICATION"]["USERNAME"], self.configuration["PROXY_SERVER"]["AUTHENTICATION"]["PASSWORD"])
            tunnel.connectTCP(self.remoteAddress, self.remotePort, factory, 50, None)
        else:
            reactor.connectTCP(self.remoteAddress, self.remotePort, factory, 50, None)
        
    def processDataState2(self):
        logger.debug("InputProtocol.processDataState2")
        
        self.outputProtocol.inputProtocol_dataReceived(self.data)
        
        self.data = ""
        
    def outputProtocol_connectionMade(self):
        logger.debug("InputProtocol.outputProtocol_connectionMade")
        
        if self.connectionState == 1:
            #IPv4
            if self.remoteAddressType == 0x01:
                remoteAddress = struct.unpack('!I', socket.inet_aton(self.remoteAddress))[0]
                response = struct.pack('!BBBBIH', 0x05, 0x00, 0, 0x01, remoteAddress, self.remotePort)
            else:
                # DN
                if self.remoteAddressType == 0x03:
                    remoteAddressLength = len(self.remoteAddress)
                    response = struct.pack('!BBBBB%dsH' % remoteAddressLength, 0x05, 0x00, 0, 0x03, remoteAddressLength, self.remoteAddress, self.remotePort)
            
            self.transport.write(response)
            
            self.data = ""
            self.dataState = 2
        else:
            if self.connectionState == 2:
                self.outputProtocol.inputProtocol_connectionLost(None)
        
    def outputProtocol_connectionLost(self, reason):
        logger.debug("InputProtocol.outputProtocol_connectionLost")
        
        if self.connectionState == 1:
            if self.dataState != 2:
                response = struct.pack('!BBBBIH', 0x05, 0x05, 0, 1, 0, 0)
                self.transport.write(response)
            
            self.transport.loseConnection()
        else:
            if self.connectionState == 2:
                self.outputProtocol.inputProtocol_connectionLost(None)
        
    def outputProtocol_dataReceived(self, data):
        logger.debug("InputProtocol.outputProtocol_dataReceived")
        
        if self.connectionState == 1:
            self.transport.write(data)
        else:
            if self.connectionState == 2:
                self.outputProtocol.inputProtocol_connectionLost(None)
        
class InputProtocolFactory(protocol.ClientFactory):
    def __init__(self, configuration):
        logger.debug("InputProtocolFactory.__init__")
        
        self.configuration = configuration
    
    def buildProtocol(self, *args, **kw):
        inputProtocol = protocol.ClientFactory.buildProtocol(self, *args, **kw)
        inputProtocol.configuration = self.configuration
        return inputProtocol