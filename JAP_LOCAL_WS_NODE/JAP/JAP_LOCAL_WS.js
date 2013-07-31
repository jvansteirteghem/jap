/*
JAP
Copyright (C) 2012 Jeroen Van Steirteghem

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
*/

var fs = require("fs");
var http = require("http");
var net = require("net");
var websocket = require("streamws");
var util = require("util");
var events = require("events");
var tls = require("tls");

function HTTPAgent(configuration) {
	events.EventEmitter.call(this);
	
	var self = this;
	self.configuration = configuration;
	
	self.createConnection = function(options, cb) {
		var requestOptions = {};
		requestOptions.host = self.configuration.PROXY_SERVER.ADDRESS;
		requestOptions.port = self.configuration.PROXY_SERVER.PORT;
		requestOptions.method = "CONNECT";
		requestOptions.path = options.host + ":" + options.port;
		requestOptions.headers = {};
		requestOptions.headers["Proxy-Authorization"] = "Basic " + new Buffer(self.configuration.PROXY_SERVER.AUTHENTICATION.USERNAME + ":" + self.configuration.PROXY_SERVER.AUTHENTICATION.PASSWORD).toString("base64");
		requestOptions.agent = false;
		
		var request = http.request(requestOptions);
		
		request.on("connect", function(response, socket, head) {
			cb(socket);
		});
		
		request.on("error", function(error) {
			options.request.emit("error", error);
		});
		
		request.end();
	}
}

util.inherits(HTTPAgent, events.EventEmitter);

HTTPAgent.prototype.addRequest = function(request, host, port, localAddress) {
	var self = this;
	
	var options = {};
	options.request = request;
	options.host = host;
	options.port = port;
	options.localAddress = localAddress;
	
	self.createSocket(options, function(socket) {
		request.onSocket(socket);
	});
};

HTTPAgent.prototype.createSocket = function(options, cb) {
	var self = this;
	
	self.createConnection(options, function(socket) {
		cb(socket);
	});
};

function HTTPSAgent(options)
{
	HTTPAgent.call(this, options);
};

util.inherits(HTTPSAgent, HTTPAgent);

HTTPSAgent.prototype.createSocket = function(options, cb) {
	var self = this;
	
	self.createConnection(options, function(socket) {
		options.socket = socket;
		socket = tls.connect(options);
		
		cb(socket);
	});
};

var setDefaultConfiguration = function(configuration) {
	configuration = configuration || {};
	configuration.PROXY_SERVER = configuration.PROXY_SERVER || {};
	configuration.PROXY_SERVER.ADDRESS = configuration.PROXY_SERVER.ADDRESS || "";
	configuration.PROXY_SERVER.PORT = configuration.PROXY_SERVER.PORT || 0;
	configuration.PROXY_SERVER.AUTHENTICATION = configuration.PROXY_SERVER.AUTHENTICATION || {};
	configuration.PROXY_SERVER.AUTHENTICATION.USERNAME = configuration.PROXY_SERVER.AUTHENTICATION.USERNAME || "";
	configuration.PROXY_SERVER.AUTHENTICATION.PASSWORD = configuration.PROXY_SERVER.AUTHENTICATION.PASSWORD || "";
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
	
	return configuration;
}

module.exports.setDefaultConfiguration = setDefaultConfiguration;

var createServer = function(configuration) {
	server = net.createServer(function(connection) {
		console.log("server.connect");
		
		var state = 0;
		var localConnection = null;
		var localConnectionState = 0;
		var remoteConnection = null;
		var remoteAddress = null;
		var remotePort = null;
		
		localConnection = connection;
		localConnectionState = 1;
		
		localConnection.on("data", function(data) {
			if(state == 0) {
				var buffer = new Buffer(2);
				buffer.write("\u0005", 0, 1, "binary");
				buffer.write("\u0000", 1, 1, "binary");
				
				localConnection.write(buffer);
				
				state = 1;
				
				return;
			}
			
			if(state == 1) {
				if(data[1] == 2) {
					console.log("error: unsupported command code: 0x02 (establish a TCP/IP port binding)");
					
					var buffer = new Buffer(10);
					buffer.write("\u0005", 0, 1, "binary");
					buffer.write("\u0007", 1, 1, "binary");
					buffer.write("\u0000", 2, 1, "binary");
					buffer.write("\u0001", 3, 1, "binary");
					buffer.write("\u0000", 4, 1, "binary");
					buffer.write("\u0000", 5, 1, "binary");
					buffer.write("\u0000", 6, 1, "binary");
					buffer.write("\u0000", 7, 1, "binary");
					buffer.write("\u0000", 8, 1, "binary");
					buffer.write("\u0000", 9, 1, "binary");
					
					localConnection.end(buffer);
					
					return;
				}
				
				if(data[1] == 3) {
					console.log("error: unsupported command code: 0x03 (associate a UDP port)");
					
					var buffer = new Buffer(10);
					buffer.write("\u0005", 0, 1, "binary");
					buffer.write("\u0007", 1, 1, "binary");
					buffer.write("\u0000", 2, 1, "binary");
					buffer.write("\u0001", 3, 1, "binary");
					buffer.write("\u0000", 4, 1, "binary");
					buffer.write("\u0000", 5, 1, "binary");
					buffer.write("\u0000", 6, 1, "binary");
					buffer.write("\u0000", 7, 1, "binary");
					buffer.write("\u0000", 8, 1, "binary");
					buffer.write("\u0000", 9, 1, "binary");
					
					localConnection.end(buffer);
					
					return;
				}
				
				if(data[3] == 4) {
					console.log("error: unsupported address type: 0x04 (IPv6 address)");
					
					var buffer = new Buffer(10);
					buffer.write("\u0005", 0, 1, "binary");
					buffer.write("\u0008", 1, 1, "binary");
					buffer.write("\u0000", 2, 1, "binary");
					buffer.write("\u0001", 3, 1, "binary");
					buffer.write("\u0000", 4, 1, "binary");
					buffer.write("\u0000", 5, 1, "binary");
					buffer.write("\u0000", 6, 1, "binary");
					buffer.write("\u0000", 7, 1, "binary");
					buffer.write("\u0000", 8, 1, "binary");
					buffer.write("\u0000", 9, 1, "binary");
					
					localConnection.end(buffer);
					
					return;
				}
				
				if(data[3] == 1) {
					remoteAddress = data[4] + "." + data[5] + "." + data[6] + "." + data[7];
					remotePort = data.readUInt16BE(8);
				}
				
				if(data[3] == 3) {
					var remoteAddressLength = data[4];
					remoteAddress = data.slice(5, 5 + remoteAddressLength).toString("binary");
					remotePort = data.readUInt16BE(5 + remoteAddressLength);
				}
				
				console.log("localConnection.remoteAddress: " + remoteAddress);
				console.log("localConnection.remotePort: " + remotePort);
				
				var i = Math.floor(Math.random() * configuration.REMOTE_PROXY_SERVERS.length);
				
				var requestUrl = configuration.REMOTE_PROXY_SERVERS[i].ADDRESS + ":" + configuration.REMOTE_PROXY_SERVERS[i].PORT + "/";
				var requestOptions = {};
				
				if(configuration.REMOTE_PROXY_SERVERS[i].TYPE == "HTTP") {
					if(configuration.PROXY_SERVER.ADDRESS == "") {
						requestOptions.agent = false;
					} else {
						requestOptions.agent = new HTTPAgent(configuration);
					}
					
					requestUrl = "ws://" + requestUrl;
				} else {
					if(configuration.REMOTE_PROXY_SERVERS[i].CERTIFICATE.AUTHENTICATION.FILE !== "") {
						certificates = [];
						
						certificatesData = fs.readFileSync(configuration.REMOTE_PROXY_SERVERS[i].CERTIFICATE.AUTHENTICATION.FILE, "utf8");
						certificatesData = certificatesData.split("\n");
						
						certificateData = [];
						
						for(j = 0; j < certificatesData.length; j = j + 1) {
							data = certificatesData[j];
							
							if(data.length !== 0) {
								certificateData.push(data);
								
								if(data.match(/-END CERTIFICATE-/)) {
									certificates.push(certificateData.join("\n"));
									
									certificateData = [];
								}
							}
						}
						
						requestOptions.ca = certificates;
						requestOptions.rejectUnauthorized = true;
					} else {
						requestOptions.ca = [];
						requestOptions.rejectUnauthorized = false;
					}
					
					if(configuration.PROXY_SERVER.ADDRESS == "") {
						requestOptions.agent = false;
					} else {
						requestOptions.agent = new HTTPSAgent(configuration);
					}
					
					requestUrl = "wss://" + requestUrl;
				}
				
				remoteConnection = new websocket(requestUrl, requestOptions);
				
				remoteConnection.on("open", function() {
					console.log("remoteConnection.open");
					
					var request = {};
					request["REMOTE_PROXY_SERVER"] = {};
					request["REMOTE_PROXY_SERVER"]["AUTHENTICATION"] = {};
					request["REMOTE_PROXY_SERVER"]["AUTHENTICATION"]["USERNAME"] = configuration.REMOTE_PROXY_SERVERS[i].AUTHENTICATION.USERNAME;
					request["REMOTE_PROXY_SERVER"]["AUTHENTICATION"]["PASSWORD"] = configuration.REMOTE_PROXY_SERVERS[i].AUTHENTICATION.PASSWORD;
					request["REMOTE_ADDRESS"] = remoteAddress
					request["REMOTE_PORT"] = remotePort
					
					var message = JSON.stringify(request);
					
					remoteConnection.send(message, {binary: false});
				});
				
				remoteConnection.on("message", function(message) {
					console.log("remoteConnection.message");
					
					if(state == 1) {
						var response = JSON.parse(message);
						
						var buffer = new Buffer(10);
						buffer.write("\u0005", 0, 1, "binary");
						buffer.write("\u0000", 1, 1, "binary");
						buffer.write("\u0000", 2, 1, "binary");
						buffer.write("\u0001", 3, 1, "binary");
						buffer.write("\u0000", 4, 1, "binary");
						buffer.write("\u0000", 5, 1, "binary");
						buffer.write("\u0000", 6, 1, "binary");
						buffer.write("\u0000", 7, 1, "binary");
						buffer.write("\u0000", 8, 1, "binary");
						buffer.write("\u0000", 9, 1, "binary");
						
						if(localConnectionState == 1) {
							localConnection.write(buffer);
						}
						
						state = 2;
						
						return;
					}
					
					if(state == 2) {
						console.log("remoteConnection.message: messageLength=" + message.length);
						
						if(message.length == 0) {
							if(localConnectionState == 1) {
								localConnection.resume();
							}
							
							return;
						}
						
						remoteConnection.send("", {binary: true});
						
						if(localConnectionState == 1) {
							if(!localConnection.write(message)) {
								remoteConnection.pause();
							}
						}
						
						return;
					}
				});
				
				remoteConnection.on("close", function() {
					console.log("remoteConnection.close");
					
					if(localConnectionState == 1) {
						localConnection.end();
					}
				});
				
				remoteConnection.on("error", function(error) {
					console.log("remoteConnection.error");
					console.log("error: " + error.toString());
				});
			}
			
			if(state == 2) {
				localConnection.pause();
				
				if(remoteConnection.readyState == websocket.OPEN) {
					remoteConnection.send(data, {binary: true});
				}
			}
		});
		
		localConnection.on("end", function() {
			console.log("localConnection.end");
			
			localConnectionState = 2;
			
			if(remoteConnection && remoteConnection.readyState == websocket.OPEN) {
				remoteConnection.close();
			}
		});
		
		localConnection.on("close", function(hadError) {
			console.log("localConnection.close");
			
			localConnectionState = 2;
			
			if(hadError) {
				if(remoteConnection && remoteConnection.readyState == websocket.OPEN) {
					remoteConnection.terminate();
				}
			} else {
				if(remoteConnection && remoteConnection.readyState == websocket.OPEN) {
					remoteConnection.close();
				}
			}
		});
		
		localConnection.on("error", function(error) {
			console.log("localConnection.error");
			console.log("error: " + error.toString());
		});
		
		localConnection.on("drain", function() {
			console.log("localConnection.drain");
			
			if(remoteConnection && remoteConnection.readyState == websocket.OPEN) {
				remoteConnection.resume();
			}
		});
	});
	
	server.on("error", function(error) {
		console.log("server.error");
		console.log("error: " + error.toString());
	});
	
	return server;
};

module.exports.createServer = createServer;