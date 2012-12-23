"""
JAP
Copyright (C) 2012 Jeroen Van Steirteghem

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
"""

from twisted.internet import reactor, ssl
import json
import os
import logging
import JAP.JAP_WS_REMOTE

configuration = json.load(open("JAP_WS_REMOTE.json"))

JAP.JAP_WS_REMOTE.setDefaultConfiguration(configuration)

logging.basicConfig()
logger = logging.getLogger("JAP")
logger.setLevel(configuration["LOGGER"]["LEVEL"])

if configuration["REMOTE_PROXY_SERVER"]["TYPE"] == "HTTPS":
    factory = JAP.JAP_WS_REMOTE.WSInputProtocolFactory(configuration, str(os.environ["DOTCLOUD_WWW_HTTP_URL"].replace("http://", "wss://")), debug = False)
    factory.protocol = JAP.JAP_WS_REMOTE.WSInputProtocol
else:
    factory = JAP.JAP_WS_REMOTE.WSInputProtocolFactory(configuration, str(os.environ["DOTCLOUD_WWW_HTTP_URL"].replace("http://", "ws://")), debug = False)
    factory.protocol = JAP.JAP_WS_REMOTE.WSInputProtocol
    
reactor.listenTCP(int(os.environ["PORT_WWW"]), factory, 50, "")
reactor.run()