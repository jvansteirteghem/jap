/*
JAP
Copyright (C) 2012 Jeroen Van Steirteghem

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
*/

var util = require("util");
var events = require("events");
var http = require("http");
var tls = require("tls");

function HTTPAgent(options) {
	events.EventEmitter.call(this);
	
	var self = this;
	self.options = options || {};
	
	self.createConnection = function(options, cb) {
		var requestOptions = {};
		requestOptions.host = options.proxy.host;
		requestOptions.port = options.proxy.port;
		requestOptions.method = "CONNECT";
		requestOptions.path = options.host + ":" + options.port;
		requestOptions.headers = {};
		requestOptions.headers["Proxy-Authorization"] = "Basic " + new Buffer(options.proxy.auth).toString("base64");
		requestOptions.agent = http.globalAgent;
		
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
	
	var options = util._extend({}, self.options);
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

module.exports.HTTPAgent = HTTPAgent;
module.exports.HTTPSAgent = HTTPSAgent;