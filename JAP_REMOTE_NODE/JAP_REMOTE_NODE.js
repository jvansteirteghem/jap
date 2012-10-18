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
	var net = require("net");
	
	var configuration = JSON.parse(fs.readFileSync("JAP_REMOTE_NODE.json"));
	
	var server = http.createServer(function(req, res) {
		res.writeHead(200, {
			'Content-Type': 'text/plain'
		});
		res.end('200');
		
		return;
	});
	
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
		
		if(configuration.REMOTE_PROXY_SERVER.AUTHORIZATION.length === 0) {
			authorized = true;
		}
		
		if(authorized === false) {
			if(req.headers.authorization) {
				var i = 0;
				
				while(i < configuration.REMOTE_PROXY_SERVER.AUTHORIZATION.length) {
					var authorization = 'Basic ' + new Buffer(configuration.REMOTE_PROXY_SERVER.AUTHORIZATION[i].USERNAME + ':' + configuration.REMOTE_PROXY_SERVER.AUTHORIZATION[i].PASSWORD).toString('base64');
					
					if(req.headers.authorization === authorization) {
						authorized = true;
						
						break;
					}
					
					i = i + 1;
				}
			}
		}
		
		if(authorized === false) {
			localConnection.write(
				'HTTP/1.1 401 Unauthorized\r\n' + 
				'WWW-Authenticate: Basic realm=\"JAP\"\r\n' + 
				'\r\n'
			);
			
			return;
		}
		
		localConnection.write(
			'HTTP/1.1 101 Web Socket Protocol Handshake\r\n' + 
			'Upgrade: WebSocket\r\n' + 
			'Connection: Upgrade\r\n' + 
			'\r\n'
		);
		
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
				
				console.log(destinationAddress);
				
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
					
					if (localConnection.writable) {
						if (!localConnection.write(buffer)) {
							return remoteConnection.pause();
						}
					}
					
					stage = 1;
					
					return;
				});
				
				remoteConnection.on("data", function(data) {
					if (localConnection.writable) {
						if (!localConnection.write(data)) {
							return remoteConnection.pause();
						}
					}
				});
				
				remoteConnection.on("end", function() {
					console.log("remoteConnection disconnected");
					console.log("concurrent connections: " + server.connections);
					return localConnection.end();
				});
				
				remoteConnection.on("error", function() {
					console.warn("remoteConnection error");
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
				if (!remoteConnection.write(data)) {
					localConnection.pause();
				}
				return;
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
			console.warn("server error");
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
	
	server.listen(configuration.REMOTE_PROXY_SERVER.PORT, function() {
		return console.log("server listening at port " + configuration.REMOTE_PROXY_SERVER.PORT);
	});
	
	server.on("error", function(e) {
		if (e.code === "EADDRINUSE") {
			return console.warn("address in use, aborting");
		}
	});
	
}).call(this);
