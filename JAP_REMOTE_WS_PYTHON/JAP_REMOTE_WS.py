"""
JAP
Copyright (C) 2012 Jeroen Van Steirteghem

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
"""

from twisted.internet import reactor, ssl
import json
import logging
import JAP.REMOTE_WS.JAP_REMOTE_WS

configuration = json.load(open("JAP_REMOTE_WS.json"))

JAP.REMOTE_WS.JAP_REMOTE_WS.setDefaultConfiguration(configuration)

logging.basicConfig()
logger = logging.getLogger("JAP.REMOTE_WS")

if configuration["LOGGER"]["LEVEL"] == "DEBUG":
    logger.setLevel(logging.DEBUG)
else:
    if configuration["LOGGER"]["LEVEL"] == "INFO":
        logger.setLevel(logging.INFO)
    else:
        if configuration["LOGGER"]["LEVEL"] == "WARNING":
            logger.setLevel(logging.WARNING)
        else:
            if configuration["LOGGER"]["LEVEL"] == "ERROR":
                logger.setLevel(logging.ERROR)
            else:
                if configuration["LOGGER"]["LEVEL"] == "CRITICAL":
                    logger.setLevel(logging.CRITICAL)
                else:
                    logger.setLevel(logging.NOTSET)

if configuration["REMOTE_PROXY_SERVER"]["TYPE"] == "HTTPS":
    factory = JAP.REMOTE_WS.JAP_REMOTE_WS.WSInputProtocolFactory(configuration, "wss://" + str(configuration["REMOTE_PROXY_SERVER"]["ADDRESS"]) + ":" + str(configuration["REMOTE_PROXY_SERVER"]["PORT"]), debug = False)
    factory.protocol = JAP.REMOTE_WS.JAP_REMOTE_WS.WSInputProtocol
    
    contextFactory = ssl.DefaultOpenSSLContextFactory(configuration["REMOTE_PROXY_SERVER"]["CERTIFICATE"]["KEY"]["FILE"], configuration["REMOTE_PROXY_SERVER"]["CERTIFICATE"]["FILE"])
    
    reactor.listenSSL(configuration["REMOTE_PROXY_SERVER"]["PORT"], factory, contextFactory, 50, configuration["REMOTE_PROXY_SERVER"]["ADDRESS"])
else:
    factory = JAP.REMOTE_WS.JAP_REMOTE_WS.WSInputProtocolFactory(configuration, "ws://" + str(configuration["REMOTE_PROXY_SERVER"]["ADDRESS"]) + ":" + str(configuration["REMOTE_PROXY_SERVER"]["PORT"]), debug = False)
    factory.protocol = JAP.REMOTE_WS.JAP_REMOTE_WS.WSInputProtocol
    
    reactor.listenTCP(configuration["REMOTE_PROXY_SERVER"]["PORT"], factory, 50, configuration["REMOTE_PROXY_SERVER"]["ADDRESS"])

reactor.run()