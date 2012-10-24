/*
JAP
Copyright (C) 2012 Jeroen Van Steirteghem

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
*/

(function() {
	var fs = require("fs");
	var http = require("http");
	var https = require("https");
	var net = require("net");
	
	var configurationFile = process.argv[2] || "JAP_REMOTE_NODE.json";
	var configuration = JSON.parse(fs.readFileSync(configurationFile));
	configuration = configuration || {};
	configuration.REMOTE_PROXY_SERVER = configuration.REMOTE_PROXY_SERVER || {};
	configuration.REMOTE_PROXY_SERVER.TYPE = configuration.REMOTE_PROXY_SERVER.TYPE || "";
	configuration.REMOTE_PROXY_SERVER.ADDRESS = configuration.REMOTE_PROXY_SERVER.ADDRESS || "";
	configuration.REMOTE_PROXY_SERVER.PORT = configuration.REMOTE_PROXY_SERVER.PORT || 0;
	configuration.REMOTE_PROXY_SERVER.AUTHENTICATION = configuration.REMOTE_PROXY_SERVER.AUTHENTICATION || [];
	for(var i = 0; i < configuration.REMOTE_PROXY_SERVER.AUTHENTICATION.length; i = i + 1) {
		configuration.REMOTE_PROXY_SERVER.AUTHENTICATION[i].USERNAME = configuration.REMOTE_PROXY_SERVER.AUTHENTICATION[i].USERNAME || "";
		configuration.REMOTE_PROXY_SERVER.AUTHENTICATION[i].PASSWORD = configuration.REMOTE_PROXY_SERVER.AUTHENTICATION[i].PASSWORD || "";
	}
	configuration.REMOTE_PROXY_SERVER.CERTIFICATE = configuration.REMOTE_PROXY_SERVER.CERTIFICATE || {};
	configuration.REMOTE_PROXY_SERVER.CERTIFICATE.KEY = configuration.REMOTE_PROXY_SERVER.CERTIFICATE.KEY || {};
	configuration.REMOTE_PROXY_SERVER.CERTIFICATE.KEY.FILE = configuration.REMOTE_PROXY_SERVER.CERTIFICATE.KEY.FILE || "";
	configuration.REMOTE_PROXY_SERVER.CERTIFICATE.FILE = configuration.REMOTE_PROXY_SERVER.CERTIFICATE.FILE || "";
	
	var server = null;
	
	if(configuration.REMOTE_PROXY_SERVER.TYPE === 'HTTP') {
		server = http.createServer(function(req, res) {
			res.writeHead(200, {
				'Content-Type': 'text/plain'
			});
			res.end('HTTP OK');
			
			return;
		});
	} else {
		var serverOptions = {};
		serverOptions.key = fs.readFileSync(configuration.REMOTE_PROXY_SERVER.CERTIFICATE.KEY.FILE);
		serverOptions.cert = fs.readFileSync(configuration.REMOTE_PROXY_SERVER.CERTIFICATE.FILE);
		
		server = https.createServer(serverOptions, function(req, res) {
			res.writeHead(200, {
				'Content-Type': 'text/plain'
			});
			res.end('HTTPS OK');
			
			return;
		});
	}
	
	server.on('upgrade', function(req, connection, head) {
		console.log("server connected");
		console.log("concurrent connections: " + server.connections);
		
		var stage = 0;
		var localConnection = null;
		var remoteConnection = null;
		var destinationAddress = null;
		var destinationPort = null;
		
		localConnection = connection;
		
		var authorized = false;
		
		if(configuration.REMOTE_PROXY_SERVER.AUTHENTICATION.length === 0) {
			authorized = true;
		}
		
		if(authorized === false) {
			if(req.headers.authorization) {
				var i = 0;
				
				while(i < configuration.REMOTE_PROXY_SERVER.AUTHENTICATION.length) {
					var authorization = 'Basic ' + new Buffer(configuration.REMOTE_PROXY_SERVER.AUTHENTICATION[i].USERNAME + ':' + configuration.REMOTE_PROXY_SERVER.AUTHENTICATION[i].PASSWORD).toString('base64');
					
					if(req.headers.authorization === authorization) {
						authorized = true;
						
						break;
					}
					
					i = i + 1;
				}
			}
		}
		
		if(authorized === false) {
			try {
				localConnection.write(
					'HTTP/1.1 401 Unauthorized\r\n' + 
					'WWW-Authenticate: Basic realm=\"JAP\"\r\n' + 
					'\r\n'
				);
			} catch (e) {
				console.log("localConnection error: " + e);
				
				return;
			}
			
			return;
		}
		
		try {
			localConnection.write(
				'HTTP/1.1 101 Web Socket Protocol Handshake\r\n' + 
				'Upgrade: WebSocket\r\n' + 
				'Connection: Upgrade\r\n' + 
				'\r\n'
			);
		} catch (e) {
			console.log("localConnection error: " + e);
			
			return;
		}
		
		localConnection.on("data", function(data) {
			if (stage === 0) {
				// request
				//   field 4: address type, 1 byte:
				//     0x01 = IPv4 address
				if (data[3] === 1) {
					// request
					//   field 5: destination address of 
					//     4 bytes for IPv4 address
					destinationAddress = data[4] + "." + data[5] + "." + data[6] + "." + data[7];
					//   field 6: network byte order port number, 2 bytes
					destinationPort = data.readUInt16BE(8);
				}
				
				// request
				//   field 4: address type, 1 byte:
				//     0x03 = Domain name
				if (data[3] === 3) {
					// request
					//   field 5: destination address of 
					//     1 byte of name length followed by the name for Domain name
					var destinationAddressLength = data[4];
					destinationAddress = data.slice(5, 5 + destinationAddressLength).toString("binary");
					//   field 6: network byte order port number, 2 bytes
					destinationPort = data.readUInt16BE(5 + destinationAddressLength);
				}
				
				console.log("connecting " + destinationAddress);
				
				remoteConnection = net.connect(destinationPort, destinationAddress, function() {
					// response
					var buffer = new Buffer(10);
					//   field 1: SOCKS protocol version, 1 byte (0x05 for this version)
					buffer.write("\u0005", 0, 1, "binary");
					//   field 2: status, 1 byte: 
					//     0x00 = request granted
					buffer.write("\u0000", 1, 1, "binary");
					//   field 3: reserved, must be 0x00
					buffer.write("\u0000", 2, 1, "binary");
					//   field 4: address type, 1 byte: 
					//     0x01 = IPv4 address
					buffer.write("\u0001", 3, 1, "binary");
					//   field 5: destination address of 
					//     4 bytes for IPv4 address
					buffer.write("\u0000\u0000\u0000\u0000", 4, 4, "binary");
					//   field 6: network byte order port number, 2 bytes
					buffer.writeInt16BE(destinationPort, 8);
					
					try {
						localConnection.write(buffer);
					} catch (e) {
						console.log("localConnection error: " + e);
						
						return;
					}
					
					stage = 1;
					
					return;
				});
				
				remoteConnection.on("data", function(data) {
					try {
						if (!localConnection.write(data)) {
							remoteConnection.pause();
						}
					} catch (e) {
						console.log("localConnection error: " + e);
						
						return;
					}
				});
				
				remoteConnection.on("end", function() {
					console.log("remoteConnection disconnected");
					console.log("concurrent connections: " + server.connections);
					return localConnection.end();
				});
				
				remoteConnection.on("error", function() {
					console.log("remoteConnection error");
					localConnection.end();
					return console.log("concurrent connections: " + server.connections);
				});
				
				remoteConnection.on("drain", function() {
					return localConnection.resume();
				});
				
				remoteConnection.setTimeout(60000, function() {
					localConnection.end();
					return remoteConnection.end();
				});
				
				return;
			}
			
			if (stage === 1) {
				try {
					if (!remoteConnection.write(data)) {
						localConnection.pause();
					}
				} catch (e) {
					console.log("remoteConnection error: " + e);
					
					return;
				}
			}
		});
		
		localConnection.on("end", function() {
			console.log("server disconnected");
			if (remoteConnection) {
				remoteConnection.end();
			}
			return console.log("concurrent connections: " + server.connections);
		});
		
		localConnection.on("error", function() {
			console.log("server error");
			if (remoteConnection) {
				remoteConnection.end();
			}
			return console.log("concurrent connections: " + server.connections);
		});
		
		return localConnection.on("drain", function() {
			if (remoteConnection) {
				return remoteConnection.resume();
			}
		});
	});
	
	server.listen(configuration.REMOTE_PROXY_SERVER.PORT, configuration.REMOTE_PROXY_SERVER.ADDRESS, 511, function() {
		return console.log("server listening at port " + configuration.REMOTE_PROXY_SERVER.PORT);
	});
	
	server.on("error", function(e) {
		if (e.code === "EADDRINUSE") {
			return console.log("address in use, aborting");
		}
	});
}).call(this);
