"""
JAP
Copyright (C) 2012 Jeroen Van Steirteghem

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
"""

from twisted.internet import reactor
import json
import logging
import JAP.LOCAL_SSH.JAP_LOCAL_SSH

configuration = json.load(open("JAP_LOCAL_SSH.json"))

JAP.LOCAL_SSH.JAP_LOCAL_SSH.setDefaultConfiguration(configuration)

logging.basicConfig()
logger = logging.getLogger("JAP.LOCAL_SSH")

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

factory = JAP.LOCAL_SSH.JAP_LOCAL_SSH.SSHInputProtocolFactory(configuration)
factory.protocol = JAP.LOCAL_SSH.JAP_LOCAL_SSH.SSHInputProtocol
reactor.listenTCP(configuration["LOCAL_PROXY_SERVER"]["PORT"], factory, 50, configuration["LOCAL_PROXY_SERVER"]["ADDRESS"])
reactor.run()