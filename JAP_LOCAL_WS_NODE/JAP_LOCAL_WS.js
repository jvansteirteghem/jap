/*
JAP
Copyright (C) 2012 Jeroen Van Steirteghem

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
*/

var jap = require("./JAP/JAP_LOCAL_WS");

var configuration = require("./JAP_LOCAL_WS.json");
configuration = jap.setDefaultConfiguration(configuration);

server = jap.createServer(configuration);

if (configuration.LOCAL_PROXY_SERVER.ADDRESS === "") {
	server.listen(configuration.LOCAL_PROXY_SERVER.PORT);
} else {
	server.listen(configuration.LOCAL_PROXY_SERVER.PORT, configuration.LOCAL_PROXY_SERVER.ADDRESS);
}