/*
JAP
Copyright (C) 2012 Jeroen Van Steirteghem

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
*/

var fs = require("fs");
var http = require("http");
var https = require("https");
var net = require("net");
var websocket = require("websocket");
var tunnel = require("./TUNNEL");

var setDefaultConfiguration = function(configuration) {
	configuration = configuration || {};
	configuration.LOCAL_PROXY_SERVER = configuration.LOCAL_PROXY_SERVER || {};
	configuration.LOCAL_PROXY_SERVER.ADDRESS = configuration.LOCAL_PROXY_SERVER.ADDRESS || "";
	configuration.LOCAL_PROXY_SERVER.PORT = configuration.LOCAL_PROXY_SERVER.PORT || 0;
	configuration.REMOTE_PROXY_SERVERS = configuration.REMOTE_PROXY_SERVERS || [];
	for(var i = 0; i < configuration.REMOTE_PROXY_SERVERS.length; i = i + 1) {
		configuration.REMOTE_PROXY_SERVERS[i].TYPE = configuration.REMOTE_PROXY_SERVERS[i].TYPE || "";
		configuration.REMOTE_PROXY_SERVERS[i].ADDRESS = configuration.REMOTE_PROXY_SERVERS[i].ADDRESS || "";
		configuration.REMOTE_PROXY_SERVERS[i].PORT = configuration.REMOTE_PROXY_SERVERS[i].PORT || 0;
		configuration.REMOTE_PROXY_SERVERS[i].AUTHENTICATION = configuration.REMOTE_PROXY_SERVERS[i].AUTHENTICATION || {};
		configuration.REMOTE_PROXY_SERVERS[i].AUTHENTICATION.USERNAME = configuration.REMOTE_PROXY_SERVERS[i].AUTHENTICATION.USERNAME || "";
		configuration.REMOTE_PROXY_SERVERS[i].AUTHENTICATION.PASSWORD = configuration.REMOTE_PROXY_SERVERS[i].AUTHENTICATION.PASSWORD || "";
		configuration.REMOTE_PROXY_SERVERS[i].CERTIFICATE = configuration.REMOTE_PROXY_SERVERS[i].CERTIFICATE || {};
		configuration.REMOTE_PROXY_SERVERS[i].CERTIFICATE.AUTHENTICATION = configuration.REMOTE_PROXY_SERVERS[i].CERTIFICATE.AUTHENTICATION || {};
		configuration.REMOTE_PROXY_SERVERS[i].CERTIFICATE.AUTHENTICATION.FILE = configuration.REMOTE_PROXY_SERVERS[i].CERTIFICATE.AUTHENTICATION.FILE || "";
	}
	configuration.PROXY_SERVER = configuration.PROXY_SERVER || {};
	configuration.PROXY_SERVER.ADDRESS = configuration.PROXY_SERVER.ADDRESS || "";
	configuration.PROXY_SERVER.PORT = configuration.PROXY_SERVER.PORT || 0;
	configuration.PROXY_SERVER.AUTHENTICATION = configuration.PROXY_SERVER.AUTHENTICATION || {};
	configuration.PROXY_SERVER.AUTHENTICATION.USERNAME = configuration.PROXY_SERVER.AUTHENTICATION.USERNAME || "";
	configuration.PROXY_SERVER.AUTHENTICATION.PASSWORD = configuration.PROXY_SERVER.AUTHENTICATION.PASSWORD || "";
	
	return configuration;
}

module.exports.setDefaultConfiguration = setDefaultConfiguration;

var createServer = function(configuration) {
	server = net.createServer(function(connection) {
		console.log("server.connect");
		console.log("server.connections: " + server.connections);
		
		var state = 0;
		var localConnection = null;
		var localConnectionState = 0;
		var remoteConnection = null;
		var remoteConnectionState = 0;
		var remoteAddress = null;
		var remotePort = null;
		
		localConnection = connection;
		localConnectionState = 1;
		
		localConnection.on("data", function(data) {
			if(state === 0) {
				var buffer = new Buffer(2);
				buffer.write("\u0005", 0, 1, "binary");
				buffer.write("\u0000", 1, 1, "binary");
				
				if(localConnectionState == 1) {
					localConnection.write(buffer);
				}
				
				state = 1;
				
				return;
			}
			
			if(state === 1) {
				if(data[1] === 2) {
					console.log("error: unsupported command code: 0x02 (establish a TCP/IP port binding)");
					
					var buffer = new Buffer(2);
					buffer.write("\u0005", 0, 1, "binary");
					buffer.write("\u0007", 1, 1, "binary");
					buffer.write("\u0000", 2, 1, "binary");
					buffer.write("\u0001", 3, 1, "binary");
					buffer.write("\u0000", 4, 1, "binary");
					buffer.write("\u0000", 5, 1, "binary");
					
					localConnection.end(buffer);
					
					return;
				}
				
				if(data[1] === 3) {
					console.log("error: unsupported command code: 0x03 (associate a UDP port)");
					
					var buffer = new Buffer(2);
					buffer.write("\u0005", 0, 1, "binary");
					buffer.write("\u0007", 1, 1, "binary");
					buffer.write("\u0000", 2, 1, "binary");
					buffer.write("\u0001", 3, 1, "binary");
					buffer.write("\u0000", 4, 1, "binary");
					buffer.write("\u0000", 5, 1, "binary");
					
					localConnection.end(buffer);
					
					return;
				}
				
				if(data[3] === 4) {
					console.log("error: unsupported address type: 0x04 (IPv6 address)");
					
					var buffer = new Buffer(2);
					buffer.write("\u0005", 0, 1, "binary");
					buffer.write("\u0008", 1, 1, "binary");
					buffer.write("\u0000", 2, 1, "binary");
					buffer.write("\u0001", 3, 1, "binary");
					buffer.write("\u0000", 4, 1, "binary");
					buffer.write("\u0000", 5, 1, "binary");
					
					localConnection.end(buffer);
					
					return;
				}
				
				if(data[3] === 1) {
					remoteAddress = data[4] + "." + data[5] + "." + data[6] + "." + data[7];
					remotePort = data.readUInt16BE(8);
				}
				
				if(data[3] === 3) {
					var remoteAddressLength = data[4];
					remoteAddress = data.slice(5, 5 + remoteAddressLength).toString("binary");
					remotePort = data.readUInt16BE(5 + remoteAddressLength);
				}
				
				console.log("localConnection.remoteAddress: " + remoteAddress);
				console.log("localConnection.remotePort: " + remotePort);
				
				var i = Math.floor(Math.random() * configuration.REMOTE_PROXY_SERVERS.length);
				
				var requestUrl = configuration.REMOTE_PROXY_SERVERS[i].ADDRESS + ":" + configuration.REMOTE_PROXY_SERVERS[i].PORT + "/";
				var requestOptions = {};
				
				if(configuration.REMOTE_PROXY_SERVERS[i].TYPE === "HTTP") {
					if(configuration.PROXY_SERVER.ADDRESS === "") {
						requestOptions.agent = http.globalAgent;
					} else {
						requestOptions.proxy = {};
						requestOptions.proxy.host = configuration.PROXY_SERVER.ADDRESS;
						requestOptions.proxy.port = configuration.PROXY_SERVER.PORT;
						
						if(configuration.PROXY_SERVER.AUTHENTICATION.USERNAME !== "") {
							requestOptions.proxy.auth = configuration.PROXY_SERVER.AUTHENTICATION.USERNAME + ":" + configuration.PROXY_SERVER.AUTHENTICATION.PASSWORD;
						}
						
						requestOptions.agent = new tunnel.HTTPAgent(requestOptions);
					}
					
					requestUrl = "ws://" + requestUrl;
				} else {
					if(configuration.REMOTE_PROXY_SERVERS[i].CERTIFICATE.AUTHENTICATION.FILE !== "") {
						requestOptions.ca = fs.readFileSync(configuration.REMOTE_PROXY_SERVERS[i].CERTIFICATE.AUTHENTICATION.FILE);
					}
					
					//requestOptions.rejectUnauthorized = true;
					
					if(configuration.PROXY_SERVER.ADDRESS === "") {
						requestOptions.agent = https.globalAgent;
					} else {
						requestOptions.proxy = {};
						requestOptions.proxy.host = configuration.PROXY_SERVER.ADDRESS;
						requestOptions.proxy.port = configuration.PROXY_SERVER.PORT;
						
						if(configuration.PROXY_SERVER.AUTHENTICATION.USERNAME !== "") {
							requestOptions.proxy.auth = configuration.PROXY_SERVER.AUTHENTICATION.USERNAME + ":" + configuration.PROXY_SERVER.AUTHENTICATION.PASSWORD;
						}
						
						requestOptions.agent = new tunnel.HTTPSAgent(requestOptions);
					}
					
					requestUrl = "wss://" + requestUrl;
				}
				
				var client = new websocket.client();
				
				client.on("connectFailed", function(error) {
					console.log("client.connectFailed");
					console.log("error: " + error.toString());
					
					remoteConnectionState = 2;
					
					if(localConnectionState == 1) {
						localConnection.end();
					}
				});
				
				client.on("connect", function(connection) {
					console.log("client.connect");
					
					remoteConnection = connection;
					remoteConnectionState = 1;
					
					remoteConnection.on("error", function(error) {
						console.log("remoteConnection.error");
						console.log("error: " + error.toString());
						
						remoteConnectionState = 2;
						
						if(localConnectionState == 1) {
							localConnection.end();
						}
					});
					remoteConnection.on("close", function() {
						console.log("remoteConnection.close");
						
						remoteConnectionState = 2;
						
						if(localConnectionState == 1) {
							localConnection.end();
						}
					});
					remoteConnection.on("message", function(message) {
						console.log("remoteConnection.message");
						
						if(state === 1) {
							response = JSON.parse(message.utf8Data);
							
							var buffer = new Buffer(10);
							buffer.write("\u0005", 0, 1, "binary");
							buffer.write("\u0000", 1, 1, "binary");
							buffer.write("\u0000", 2, 1, "binary");
							buffer.write("\u0001", 3, 1, "binary");
							buffer.write("\u0000", 4, 1, "binary");
							buffer.write("\u0000", 5, 1, "binary");
							
							if(localConnectionState == 1) {
								localConnection.write(buffer);
							}
							
							state = 2;
							
							return;
						}
						
						if(localConnectionState == 1) {
							localConnection.write(message.binaryData);
						}
					});
					
					if(remoteConnectionState == 1) {
						var request = {};
						request["REMOTE_PROXY_SERVER"] = {};
						request["REMOTE_PROXY_SERVER"]["AUTHENTICATION"] = {};
						request["REMOTE_PROXY_SERVER"]["AUTHENTICATION"]["USERNAME"] = configuration.REMOTE_PROXY_SERVERS[i].AUTHENTICATION.USERNAME;
						request["REMOTE_PROXY_SERVER"]["AUTHENTICATION"]["PASSWORD"] = configuration.REMOTE_PROXY_SERVERS[i].AUTHENTICATION.PASSWORD;
						request["REMOTE_ADDRESS"] = remoteAddress
						request["REMOTE_PORT"] = remotePort
						
						message2 = JSON.stringify(request);
						
						remoteConnection.sendUTF(message2);
					}
				});
				
				client.connect(requestUrl, requestOptions);
			}
			
			if(state === 2) {
				if(remoteConnectionState == 1) {
					remoteConnection.sendBytes(data);
				}
			}
		});
		
		localConnection.on("end", function() {
			console.log("localConnection.end");
			
			localConnectionState = 2;
			
			if(remoteConnection && remoteConnectionState == 1) {
				remoteConnection.close();
			}
			
			console.log("server.connections: " + server.connections);
		});
		
		localConnection.on("error", function(error) {
			console.log("localConnection.error");
			console.log("error: " + error.toString());
			
			localConnectionState = 2;
			
			if(remoteConnection && remoteConnectionState == 1) {
				remoteConnection.close();
			}
			
			console.log("server.connections: " + server.connections);
		});
	});
	
	return server;
};

module.exports.createServer = createServer;