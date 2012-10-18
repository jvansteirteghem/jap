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
	var tunnel = require("./NODE/tunnel");
	
	var configuration = JSON.parse(fs.readFileSync("JAP_LOCAL_NODE.json"));
	
	server = net.createServer(function(connection) {
		console.log("local connected");
		console.log("concurrent connections: " + server.connections);
		
		var stage = 0;
		var request = null;
		var localConnection = null;
		var remoteConnection = null;
		var destinationAddress = null;
		var destinationPort = null;
		
		localConnection = connection;
		
		localConnection.on("data", function(data) {
			if (stage === 0) {
				// response
				var buffer = new Buffer(2);
				//   field 1: SOCKS protocol version, 1 byte (0x05 for this version)
				buffer.write("\u0005", 0, 1, "binary");
				//   field 2: status, 1 byte:
				//     0x00 = request granted
				buffer.write("\u0000", 1, 1, "binary");
				
				localConnection.write(buffer);
				
				stage = 1;
				
				return;
			}
			
			if (stage === 1) {
				// request
				//   field 2: command code, 1 byte:
				//     0x02 = establish a TCP/IP port binding
				if (data[1] === 2) {
					console.log("unsupported command code: 0x02 (establish a TCP/IP port binding)");
					
					// response
					var buffer = new Buffer(2);
					//  field 1: SOCKS protocol version, 1 byte (0x05 for this version)
					buffer.write("\u0005", 0, 1, "binary");
					//  field 2: status, 1 byte:
					//   0x07 = command not supported / protocol error
					buffer.write("\u0007", 1, 1, "binary");
					
					localConnection.end(buffer);
					
					return;
				}
				
				// request
				//   field 2: command code, 1 byte:
				//     0x03 = associate a UDP port
				if (data[1] === 3) {
					console.log("unsupported command code: 0x03 (associate a UDP port)");
					
					// response
					var buffer = new Buffer(2);
					//   field 1: SOCKS protocol version, 1 byte (0x05 for this version)
					buffer.write("\u0005", 0, 1, "binary");
					//   field 2: status, 1 byte:
					//     0x07 = command not supported / protocol error
					buffer.write("\u0007", 1, 1, "binary");
					
					localConnection.end(buffer);
					
					return;
				}
				
				// request
				//   field 4: address type, 1 byte:
				//     0x04 = IPv6 address
				if (data[3] === 4) {
					console.log("unsupported address type: 0x04 (IPv6 address)");
					
					// response
					var buffer = new Buffer(2);
					//   field 1: SOCKS protocol version, 1 byte (0x05 for this version)
					buffer.write("\u0005", 0, 1, "binary");
					//   field 2: status, 1 byte:
					//     0x08 = address type not supported
					buffer.write("\u0008", 1, 1, "binary");
					
					localConnection.end(buffer);
					
					return;
				}
				
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
				
				var i = Math.floor(Math.random() * configuration.REMOTE_PROXY_SERVERS.length);
				
				var requestOptions = {};
				requestOptions.host = configuration.REMOTE_PROXY_SERVERS[i].ADDRESS;
				requestOptions.port = configuration.REMOTE_PROXY_SERVERS[i].PORT;
				requestOptions.headers = {
				  'Connection': 'Upgrade',
				  'Upgrade': 'WebSocket'
				};
				
				if(configuration.PROXY_SERVER.ADDRESS !== '') {
					var agentOptions = {};
					agentOptions.maxSockets = 100;
					agentOptions.proxy = {};
					agentOptions.proxy.host = configuration.PROXY_SERVER.ADDRESS;
					agentOptions.proxy.port = configuration.PROXY_SERVER.PORT;
					
					if(configuration.PROXY_SERVER.AUTHORIZATION.USERNAME !== '') {
						agentOptions.proxy.proxyAuth = configuration.PROXY_SERVER.AUTHORIZATION.USERNAME + ':' + configuration.PROXY_SERVER.AUTHORIZATION.PASSWORD;
					}
					
					if(configuration.REMOTE_PROXY_SERVERS[i].TYPE === 'HTTP') {
						requestOptions.agent = tunnel.httpOverHttp(agentOptions);
					} else {
						requestOptions.agent = tunnel.httpsOverHttp(agentOptions);
					}
				}
				
				if(configuration.REMOTE_PROXY_SERVERS[i].AUTHORIZATION.USERNAME !== '') {
					requestOptions.auth = configuration.REMOTE_PROXY_SERVERS[i].AUTHORIZATION.USERNAME + ':' + configuration.REMOTE_PROXY_SERVERS[i].AUTHORIZATION.PASSWORD;
				}
				
				if(configuration.REMOTE_PROXY_SERVERS[i].TYPE === 'HTTP') {
					request = http.request(requestOptions);
				} else {
					request = https.request(requestOptions);
				}
				
				request.setNoDelay(true);
				request.end();
				request.setTimeout(60000, function() {
					request.abort();
					return localConnection.end();
				});
				
				request.on('error', function() {
					console.log('request error');
					request.abort();
					return localConnection.end();
				});
				
				request.on('upgrade', function(res, conn, upgradeHead) {
					remoteConnection = conn;
					console.log("remoteConnection got upgrade");
					
					remoteConnection.on("data", function(data) {
						if (stage === 1) {
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
							
							localConnection.write(buffer);
							
							stage = 2;
							
							return;
						}
						
						if (localConnection.writable) {
							if (!localConnection.write(data)) {
								return remoteConnection.pause();
							}
						}
					});
					
					remoteConnection.on("end", function() {
					  console.log("remoteConnection disconnected");
					  localConnection.end();
					  return console.log("concurrent connections: " + server.connections);
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
					
					remoteConnection.write(data);
					
					return;
				});
			}
			
			if (stage === 2) {
				if (remoteConnection.writable) {
					if (!remoteConnection.write(data)) {
						localConnection.pause();
					}
				}
				
				return;
			}
		});
		
		localConnection.on("end", function() {
			console.log("local disconnected");
			if (remoteConnection) {
				console.log("remoteConnection.end()");
				remoteConnection.end();
			} else if (request) {
				console.log("request.abort()");
				request.abort();
			}
			
			return console.log("concurrent connections: " + server.connections);
		});
		
		localConnection.on("error", function() {
			console.log("local error");
			
			if (request) {
				request.abort();
			}
			
			if (remoteConnection) {
				remoteConnection.end();
			}
			
			return console.log("concurrent connections: " + server.connections);
		});
		
		localConnection.on("drain", function() {
			if (stage === 2 && remoteConnection) {
				return remoteConnection.resume();
			}
		});
		
		return localConnection.setTimeout(60000, function() {
			if (request) {
				request.abort();
			}
			if (remoteConnection) {
				remoteConnection.end();
			}
			return localConnection.end();
		});
	});
	
	server.listen(configuration.LOCAL_PROXY_SERVER.PORT, function() {
		return console.log("server listening at port " + configuration.LOCAL_PROXY_SERVER.PORT);
	});
	
	server.on("error", function(e) {
		if (e.code === "EADDRINUSE") {
			return console.log("address in use, aborting");
		}
	});
}).call(this);
