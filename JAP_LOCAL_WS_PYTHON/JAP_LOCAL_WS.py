"""
JAP
Copyright (C) 2012 Jeroen Van Steirteghem

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
"""

from twisted.internet import reactor
import logging
import JAP.JAP_LOCAL
import JAP.JAP_LOCAL_WS

configuration = JAP.JAP_LOCAL.getConfiguration("./JAP_LOCAL_WS.json", JAP.JAP_LOCAL_WS.getDefaultConfiguration)

logging.basicConfig()
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

resolver = JAP.JAP_LOCAL.createResolver(configuration)
reactor.installResolver(resolver)

factory = JAP.JAP_LOCAL_WS.WSInputProtocolFactory(configuration)
factory.protocol = JAP.JAP_LOCAL_WS.WSInputProtocol
reactor.listenTCP(configuration["LOCAL_PROXY_SERVER"]["PORT"], factory, 50, configuration["LOCAL_PROXY_SERVER"]["ADDRESS"])
reactor.run()