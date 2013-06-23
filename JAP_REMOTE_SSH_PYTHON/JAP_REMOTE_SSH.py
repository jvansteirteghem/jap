"""
JAP
Copyright (C) 2012 Jeroen Van Steirteghem

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
"""

from twisted.internet import reactor
from twisted.names import client
import logging
import JAP.JAP_LOCAL
import JAP.JAP_REMOTE_SSH

configuration = JAP.JAP_LOCAL.getConfiguration("./JAP_REMOTE_SSH.json", JAP.JAP_REMOTE_SSH.getDefaultConfiguration)

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

resolverHosts = None
if configuration["DNS_RESOLVER"]["HOSTS"]["FILE"] != "":
    resolverHosts = configuration["DNS_RESOLVER"]["HOSTS"]["FILE"]

resolverServers = None
if len(configuration["DNS_RESOLVER"]["SERVERS"]) != 0:
    resolverServers = []
    i = 0
    while i < len(configuration["DNS_RESOLVER"]["SERVERS"]):
        resolverServers.append((configuration["DNS_RESOLVER"]["SERVERS"][i]["ADDRESS"], configuration["DNS_RESOLVER"]["SERVERS"][i]["PORT"]))
        i = i + 1

resolver = client.createResolver(hosts=resolverHosts, servers=resolverServers)
reactor.installResolver(resolver)

factory = JAP.JAP_REMOTE_SSH.SSHFactory(configuration)
reactor.listenTCP(configuration["REMOTE_PROXY_SERVER"]["PORT"], factory, 50, configuration["REMOTE_PROXY_SERVER"]["ADDRESS"])
reactor.run()