"""
JAP
Copyright (C) 2012 Jeroen Van Steirteghem

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
"""

from twisted.protocols import basic
from twisted.internet import protocol, reactor
import base64

class TunnelProtocol(basic.LineReceiver):
    delimiter = "\r\n"

    def __init__(self):
        self.headerLines = []
        
    def connectionMade(self):
        request = "CONNECT " + str(self.factory.address) + ":" + str(self.factory.port) + " HTTP/1.0\r\n"
        
        if self.factory.proxyServerUsername != "":
            request = request + "Proxy-Authorization: Basic " + base64.standard_b64encode(self.factory.proxyServerUsername + ":" + self.factory.proxyServerPassword) + "\r\n"
        
        request = request + "\r\n"
        
        self.transport.write(request)
        
    def lineReceived(self, line):
        if line:
            self.headerLines.append(line)
        else:
            self.setRawMode()
            v, statusCode, s = self.headerLines[0].split(" ", 2)
            lineBuffer = self.clearLineBuffer()
            if statusCode != "200":
                self.transport.loseConnection()
                return
            peer = self.transport.getPeer()
            otherProtocol = self.factory.otherProtocolFactory.buildProtocol(peer)
            self.transport.protocol = otherProtocol
            otherProtocol.transport = self.transport
            self.transport = None
            if self.factory.contextFactory:
                otherProtocol.transport.startTLS(self.factory.contextFactory)
            otherProtocol.connectionMade()
            if lineBuffer:
                otherProtocol.dataReceived(lineBuffer)


class TunnelFactory(protocol.ClientFactory):
    protocol = TunnelProtocol

    def __init__(self, address, port, proxyServerAddress, proxyServerPort, proxyServerUsername, proxyServerPassword, otherProtocolFactory, contextFactory=None):
        self.address = address
        self.port = port
        self.proxyServerAddress = proxyServerAddress
        self.proxyServerPort = proxyServerPort
        self.proxyServerUsername = proxyServerUsername
        self.proxyServerPassword = proxyServerPassword
        self.otherProtocolFactory = otherProtocolFactory
        self.contextFactory = contextFactory


class Tunnel(object):
    def __init__(self, proxyServerAddress, proxyServerPort, proxyServerUsername, proxyServerPassword):
        self.proxyServerAddress = proxyServerAddress
        self.proxyServerPort = proxyServerPort
        self.proxyServerUsername = proxyServerUsername
        self.proxyServerPassword = proxyServerPassword

    def connectTCP(self, address, port, factory, *args, **kwargs):
        tunnel_factory = TunnelFactory(address, port, self.proxyServerAddress, self.proxyServerPort, self.proxyServerUsername, self.proxyServerPassword, factory)
        return reactor.connectTCP(self.proxyServerAddress, self.proxyServerPort, tunnel_factory, *args, **kwargs)

    def connectSSL(self, address, port, factory, contextFactory, *args, **kwargs):
        tunnel_factory = TunnelFactory(address, port, self.proxyServerAddress, self.proxyServerPort, self.proxyServerUsername, self.proxyServerPassword, factory, contextFactory)
        return reactor.connectTCP(self.proxyServerAddress, self.proxyServerPort, tunnel_factory, *args, **kwargs)
