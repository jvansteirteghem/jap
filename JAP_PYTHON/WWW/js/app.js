function Template(name, data) {
    var self = this;
    self.name = ko.observable(name);
    self.data = ko.observable(data);
}

function JAP_ViewModel(parent) {
    var self = this;
    self.parent = parent;
    self.defaultData = {
        "LOGGER": {
            "LEVEL": ""
        },
        "DNS_RESOLVER": {
            "HOSTS": {
                "FILE": ""
            },
            "SERVERS": []
        },
        "LOCAL_SERVER": {
            "ADDRESS": "",
            "PORT": 0,
            "AUTHENTICATION": {
                "USERNAME": "",
                "PASSWORD": ""
            }
        }
    }
    self.data = ko.mapping.fromJS(self.defaultData);
    
    self.action_JAP_UPDATE = function() {
        var data = ko.mapping.toJS(self.data);
        
        for(var i = 0; i < data.DNS_RESOLVER.SERVERS.length; i = i + 1) {
            if($.isNumeric(data.DNS_RESOLVER.SERVERS[i].PORT)) {
                data.DNS_RESOLVER.SERVERS[i].PORT = Number(data.DNS_RESOLVER.SERVERS[i].PORT);
            } else {
                data.DNS_RESOLVER.SERVERS[i].PORT = 0;
            }
        }
        
        $.ajax({
            "type": "POST",
            "url": "/API",
            "dataType": "",
            "data": {
                "action": "JAP_UPDATE",
                "data": ko.toJSON(data)
            }
        }).then(
            function(data, textStatus, jqXHR) {
                Alertify.log.success("JAP - UPDATE OK");
            }, 
            function(jqXHR, textStatus, errorThrown) {
                Alertify.log.error("JAP - UPDATE NOT OK");
            }
        )
    }
    
    self.action_JAP_DNS_RESOLVER_SERVERS_ADD = function(data) {
        self.data.DNS_RESOLVER.SERVERS.push(data);
    }
    
    self.action_JAP_DNS_RESOLVER_SERVERS_UPDATE = function(selectedData, data) {
        ko.mapping.fromJS(ko.mapping.toJS(data), {}, selectedData);
    }
    
    self.action_JAP_DNS_RESOLVER_SERVERS_REMOVE = function(selectedData) {
        self.data.DNS_RESOLVER.SERVERS.remove(selectedData);
    }
    
    self.action_JAP_DNS_RESOLVER_SERVERS_REMOVE_ALL = function() {
        self.data.DNS_RESOLVER.SERVERS.removeAll();
    }
    
    self.load_JAP_DNS_RESOLVER_SERVERS_ADD = function() {
        self.template_JAP_DNS_RESOLVER_SERVERS(new Template("TEMPLATE_JAP_DNS_RESOLVER_SERVER", new JAP_DNS_RESOLVER_SERVERS_ADD_ViewModel(self)));
    }
    
    self.load_JAP_DNS_RESOLVER_SERVERS_UPDATE = function(data) {
        self.template_JAP_DNS_RESOLVER_SERVERS(new Template("TEMPLATE_JAP_DNS_RESOLVER_SERVER", new JAP_DNS_RESOLVER_SERVERS_UPDATE_ViewModel(self, data)));
    }
    
    self.template_JAP_DNS_RESOLVER_SERVERS = ko.observable();
    
    self.load_JAP_DNS_RESOLVER_SERVERS = function() {
        self.template_JAP_DNS_RESOLVER_SERVERS(new Template("TEMPLATE_JAP_DNS_RESOLVER_SERVERS", self));
    }
    
    self.load_JAP_DNS_RESOLVER_SERVERS();
    
    $.ajax({
        "type": "GET",
        "url": "/API",
        "dataType": "JSON",
        "data": {
            "action": "JAP"
        }
    }).then(
        function(data, textStatus, jqXHR) {
            Alertify.log.success("JAP - OK");
            
            ko.mapping.fromJS(data, self.data);
        }, 
        function(jqXHR, textStatus, errorThrown) {
            Alertify.log.error("JAP - NOT OK");
        }
    );
}

function JAP_DNS_RESOLVER_SERVERS_ADD_ViewModel(parent) {
    var self = this;
    self.parent = parent;
    self.defaultData = {
        "ADDRESS": "",
        "PORT": 0
    }
    self.data = ko.mapping.fromJS(self.defaultData);
    self.action = "JAP_DNS_RESOLVER_SERVERS_ADD";
    
    self.action_JAP_DNS_RESOLVER_SERVERS_ADD = function() {
        self.parent.action_JAP_DNS_RESOLVER_SERVERS_ADD(self.data);
        self.parent.load_JAP_DNS_RESOLVER_SERVERS();
    }
    
    self.cancel = function() {
        self.parent.load_JAP_DNS_RESOLVER_SERVERS();
    }
}

function JAP_DNS_RESOLVER_SERVERS_UPDATE_ViewModel(parent, data) {
    var self = this;
    self.parent = parent;
    self.selectedData = data;
    self.data = ko.mapping.fromJS(ko.mapping.toJS(self.selectedData));
    self.action = "JAP_DNS_RESOLVER_SERVERS_UPDATE";
    
    self.action_JAP_DNS_RESOLVER_SERVERS_UPDATE = function() {
        self.parent.action_JAP_DNS_RESOLVER_SERVERS_UPDATE(self.selectedData, self.data);
        self.parent.load_JAP_DNS_RESOLVER_SERVERS();
    }
    
    self.cancel = function() {
        self.parent.load_JAP_DNS_RESOLVER_SERVERS();
    }
}

function JAP_LOCAL_ViewModel(parent) {
    var self = this;
    self.parent = parent;
    self.defaultData = {
        "LOGGER": {
            "LEVEL": ""
        },
        "LOCAL_PROXY_SERVER": {
            "ADDRESS": "",
            "PORT": 0
        },
        "PROXY_SERVERS": []
    }
    self.data = ko.mapping.fromJS(self.defaultData);
    
    self.action_JAP_LOCAL_UPDATE = function() {
        var data = ko.mapping.toJS(self.data);
        
        if($.isNumeric(data.LOCAL_PROXY_SERVER.PORT)) {
            data.LOCAL_PROXY_SERVER.PORT = Number(data.LOCAL_PROXY_SERVER.PORT);
        } else {
            data.LOCAL_PROXY_SERVER.PORT = 0;
        }
        
        for(var i = 0; i < data.PROXY_SERVERS.length; i = i + 1) {
            if($.isNumeric(data.PROXY_SERVERS[i].PORT)) {
                data.PROXY_SERVERS[i].PORT = Number(data.PROXY_SERVERS[i].PORT);
            } else {
                data.PROXY_SERVERS[i].PORT = 0;
            }
        }
        
        $.ajax({
            "type": "POST",
            "url": "/API",
            "dataType": "",
            "data": {
                "action": "JAP_LOCAL_UPDATE",
                "data": ko.toJSON(data)
            }
        }).then(
            function(data, textStatus, jqXHR) {
                Alertify.log.success("JAP LOCAL - UPDATE OK");
            }, 
            function(jqXHR, textStatus, errorThrown) {
                Alertify.log.error("JAP LOCAL - UPDATE NOT OK");
            }
        )
    }
    
    self.action_JAP_LOCAL_PROXY_SERVERS_ADD = function(data) {
        self.data.PROXY_SERVERS.push(data);
    }
    
    self.action_JAP_LOCAL_PROXY_SERVERS_UPDATE = function(selectedData, data) {
        ko.mapping.fromJS(ko.mapping.toJS(data), {}, selectedData);
    }
    
    self.action_JAP_LOCAL_PROXY_SERVERS_REMOVE = function(selectedData) {
        self.data.PROXY_SERVERS.remove(selectedData);
    }
    
    self.action_JAP_LOCAL_PROXY_SERVERS_REMOVE_ALL = function() {
        self.data.PROXY_SERVERS.removeAll();
    }
    
    self.load_JAP_LOCAL_PROXY_SERVERS_ADD = function() {
        self.template_JAP_LOCAL_PROXY_SERVERS(new Template("TEMPLATE_JAP_LOCAL_PROXY_SERVER", new JAP_LOCAL_PROXY_SERVERS_ADD_ViewModel(self)));
    }
    
    self.load_JAP_LOCAL_PROXY_SERVERS_UPDATE = function(data) {
        self.template_JAP_LOCAL_PROXY_SERVERS(new Template("TEMPLATE_JAP_LOCAL_PROXY_SERVER", new JAP_LOCAL_PROXY_SERVERS_UPDATE_ViewModel(self, data)));
    }
    
    self.template_JAP_LOCAL_PROXY_SERVERS = ko.observable();
    
    self.load_JAP_LOCAL_PROXY_SERVERS = function() {
        self.template_JAP_LOCAL_PROXY_SERVERS(new Template("TEMPLATE_JAP_LOCAL_PROXY_SERVERS", self));
    }
    
    self.load_JAP_LOCAL_PROXY_SERVERS();
    
    $.ajax({
        "type": "GET",
        "url": "/API",
        "dataType": "JSON",
        "data": {
            "action": "JAP_LOCAL"
        }
    }).then(
        function(data, textStatus, jqXHR) {
            Alertify.log.success("JAP LOCAL - OK");
            
            ko.mapping.fromJS(data, self.data);
        }, 
        function(jqXHR, textStatus, errorThrown) {
            Alertify.log.error("JAP LOCAL - NOT OK");
        }
    );
}

function JAP_LOCAL_PROXY_SERVERS_ADD_ViewModel(parent) {
    var self = this;
    self.parent = parent;
    self.defaultData = {
        "TYPE": "",
        "ADDRESS": "",
        "PORT": 0,
        "AUTHENTICATION": {
            "USERNAME": "",
            "PASSWORD": ""
        }
    }
    self.data = ko.mapping.fromJS(self.defaultData);
    self.action = "JAP_LOCAL_PROXY_SERVERS_ADD";
    
    self.action_JAP_LOCAL_PROXY_SERVERS_ADD = function() {
        self.parent.action_JAP_LOCAL_PROXY_SERVERS_ADD(self.data);
        self.parent.load_JAP_LOCAL_PROXY_SERVERS();
    }
    
    self.cancel = function() {
        self.parent.load_JAP_LOCAL_PROXY_SERVERS();
    }
}

function JAP_LOCAL_PROXY_SERVERS_UPDATE_ViewModel(parent, data) {
    var self = this;
    self.parent = parent;
    self.selectedData = data;
    self.data = ko.mapping.fromJS(ko.mapping.toJS(self.selectedData));
    self.action = "JAP_LOCAL_PROXY_SERVERS_UPDATE";
    
    self.action_JAP_LOCAL_PROXY_SERVERS_UPDATE = function() {
        self.parent.action_JAP_LOCAL_PROXY_SERVERS_UPDATE(self.selectedData, self.data);
        self.parent.load_JAP_LOCAL_PROXY_SERVERS();
    }
    
    self.cancel = function() {
        self.parent.load_JAP_LOCAL_PROXY_SERVERS();
    }
}

function JAP_LOCAL_SSH_ViewModel(parent) {
    var self = this;
    self.parent = parent;
    self.defaultData = {
        "LOGGER": {
            "LEVEL": ""
        },
        "LOCAL_PROXY_SERVER": {
            "ADDRESS": "",
            "PORT": 0,
            "KEYS": []
        },
        "REMOTE_PROXY_SERVERS":[],
        "PROXY_SERVERS": []
    }
    self.data = ko.mapping.fromJS(self.defaultData);
    
    self.action_JAP_LOCAL_SSH_UPDATE = function() {
        var data = ko.mapping.toJS(self.data);
        
        if($.isNumeric(data.LOCAL_PROXY_SERVER.PORT)) {
            data.LOCAL_PROXY_SERVER.PORT = Number(data.LOCAL_PROXY_SERVER.PORT);
        } else {
            data.LOCAL_PROXY_SERVER.PORT = 0;
        }
        
        for(var i = 0; i < data.REMOTE_PROXY_SERVERS.length; i = i + 1) {
            if($.isNumeric(data.REMOTE_PROXY_SERVERS[i].PORT)) {
                data.REMOTE_PROXY_SERVERS[i].PORT = Number(data.REMOTE_PROXY_SERVERS[i].PORT);
            } else {
                data.REMOTE_PROXY_SERVERS[i].PORT = 0;
            }
        }
        
        for(var i = 0; i < data.PROXY_SERVERS.length; i = i + 1) {
            if($.isNumeric(data.PROXY_SERVERS[i].PORT)) {
                data.PROXY_SERVERS[i].PORT = Number(data.PROXY_SERVERS[i].PORT);
            } else {
                data.PROXY_SERVERS[i].PORT = 0;
            }
        }
        
        $.ajax({
            "type": "POST",
            "url": "/API",
            "dataType": "",
            "data": {
                "action": "JAP_LOCAL_SSH_UPDATE",
                "data": ko.toJSON(data)
            }
        }).then(
            function(data, textStatus, jqXHR) {
                Alertify.log.success("JAP LOCAL SSH - UPDATE OK");
            }, 
            function(jqXHR, textStatus, errorThrown) {
                Alertify.log.error("JAP LOCAL SSH - UPDATE NOT OK");
            }
        )
    }
    
    self.action_JAP_LOCAL_SSH_LOCAL_PROXY_SERVER_KEYS_ADD = function(data) {
        self.data.LOCAL_PROXY_SERVER.KEYS.push(data);
    }
    
    self.action_JAP_LOCAL_SSH_LOCAL_PROXY_SERVER_KEYS_UPDATE = function(selectedData, data) {
        ko.mapping.fromJS(ko.mapping.toJS(data), {}, selectedData);
    }
    
    self.action_JAP_LOCAL_SSH_LOCAL_PROXY_SERVER_KEYS_REMOVE = function(selectedData) {
        self.data.LOCAL_PROXY_SERVER.KEYS.remove(selectedData);
    }
    
    self.action_JAP_LOCAL_SSH_LOCAL_PROXY_SERVER_KEYS_REMOVE_ALL = function() {
        self.data.LOCAL_PROXY_SERVER.KEYS.removeAll();
    }
    
    self.action_JAP_LOCAL_SSH_REMOTE_PROXY_SERVERS_ADD = function(data) {
        self.data.REMOTE_PROXY_SERVERS.push(data);
    }
    
    self.action_JAP_LOCAL_SSH_REMOTE_PROXY_SERVERS_UPDATE = function(selectedData, data) {
        ko.mapping.fromJS(ko.mapping.toJS(data), {}, selectedData);
    }
    
    self.action_JAP_LOCAL_SSH_REMOTE_PROXY_SERVERS_REMOVE = function(selectedData) {
        self.data.REMOTE_PROXY_SERVERS.remove(selectedData);
    }
    
    self.action_JAP_LOCAL_SSH_REMOTE_PROXY_SERVERS_REMOVE_ALL = function() {
        self.data.REMOTE_PROXY_SERVERS.removeAll();
    }
    
    self.action_JAP_LOCAL_SSH_PROXY_SERVERS_ADD = function(data) {
        self.data.PROXY_SERVERS.push(data);
    }
    
    self.action_JAP_LOCAL_SSH_PROXY_SERVERS_UPDATE = function(selectedData, data) {
        ko.mapping.fromJS(ko.mapping.toJS(data), {}, selectedData);
    }
    
    self.action_JAP_LOCAL_SSH_PROXY_SERVERS_REMOVE = function(selectedData) {
        self.data.PROXY_SERVERS.remove(selectedData);
    }
    
    self.action_JAP_LOCAL_SSH_PROXY_SERVERS_REMOVE_ALL = function() {
        self.data.PROXY_SERVERS.removeAll();
    }
    
    self.load_JAP_LOCAL_SSH_LOCAL_PROXY_SERVER_KEYS_ADD = function() {
        self.template_JAP_LOCAL_SSH_LOCAL_PROXY_SERVER_KEYS(new Template("TEMPLATE_JAP_LOCAL_SSH_LOCAL_PROXY_SERVER_KEY", new JAP_LOCAL_SSH_LOCAL_PROXY_SERVER_KEYS_ADD_ViewModel(self)));
    }
    
    self.load_JAP_LOCAL_SSH_LOCAL_PROXY_SERVER_KEYS_UPDATE = function(data) {
        self.template_JAP_LOCAL_SSH_LOCAL_PROXY_SERVER_KEYS(new Template("TEMPLATE_JAP_LOCAL_SSH_LOCAL_PROXY_SERVER_KEY", new JAP_LOCAL_SSH_LOCAL_PROXY_SERVER_KEYS_UPDATE_ViewModel(self, data)));
    }
    
    self.load_JAP_LOCAL_SSH_REMOTE_PROXY_SERVERS_ADD = function() {
        self.template_JAP_LOCAL_SSH_REMOTE_PROXY_SERVERS(new Template("TEMPLATE_JAP_LOCAL_SSH_REMOTE_PROXY_SERVER", new JAP_LOCAL_SSH_REMOTE_PROXY_SERVERS_ADD_ViewModel(self)));
    }
    
    self.load_JAP_LOCAL_SSH_REMOTE_PROXY_SERVERS_UPDATE = function(data) {
        self.template_JAP_LOCAL_SSH_REMOTE_PROXY_SERVERS(new Template("TEMPLATE_JAP_LOCAL_SSH_REMOTE_PROXY_SERVER", new JAP_LOCAL_SSH_REMOTE_PROXY_SERVERS_UPDATE_ViewModel(self, data)));
    }
    
    self.load_JAP_LOCAL_SSH_PROXY_SERVERS_ADD = function() {
        self.template_JAP_LOCAL_SSH_PROXY_SERVERS(new Template("TEMPLATE_JAP_LOCAL_SSH_PROXY_SERVER", new JAP_LOCAL_SSH_PROXY_SERVERS_ADD_ViewModel(self)));
    }
    
    self.load_JAP_LOCAL_SSH_PROXY_SERVERS_UPDATE = function(data) {
        self.template_JAP_LOCAL_SSH_PROXY_SERVERS(new Template("TEMPLATE_JAP_LOCAL_SSH_PROXY_SERVER", new JAP_LOCAL_SSH_PROXY_SERVERS_UPDATE_ViewModel(self, data)));
    }
    
    self.template_JAP_LOCAL_SSH_LOCAL_PROXY_SERVER_KEYS = ko.observable();
    
    self.load_JAP_LOCAL_SSH_LOCAL_PROXY_SERVER_KEYS = function() {
        self.template_JAP_LOCAL_SSH_LOCAL_PROXY_SERVER_KEYS(new Template("TEMPLATE_JAP_LOCAL_SSH_LOCAL_PROXY_SERVER_KEYS", self));
    }
    
    self.load_JAP_LOCAL_SSH_LOCAL_PROXY_SERVER_KEYS();
    
    self.template_JAP_LOCAL_SSH_REMOTE_PROXY_SERVERS = ko.observable();
    
    self.load_JAP_LOCAL_SSH_REMOTE_PROXY_SERVERS = function() {
        self.template_JAP_LOCAL_SSH_REMOTE_PROXY_SERVERS(new Template("TEMPLATE_JAP_LOCAL_SSH_REMOTE_PROXY_SERVERS", self));
    }
    
    self.load_JAP_LOCAL_SSH_REMOTE_PROXY_SERVERS();
    
    self.template_JAP_LOCAL_SSH_PROXY_SERVERS = ko.observable();
    
    self.load_JAP_LOCAL_SSH_PROXY_SERVERS = function() {
        self.template_JAP_LOCAL_SSH_PROXY_SERVERS(new Template("TEMPLATE_JAP_LOCAL_SSH_PROXY_SERVERS", self));
    }
    
    self.load_JAP_LOCAL_SSH_PROXY_SERVERS();
    
    $.ajax({
        "type": "GET",
        "url": "/API",
        "dataType": "JSON",
        "data": {
            "action": "JAP_LOCAL_SSH"
        }
    }).then(
        function(data, textStatus, jqXHR) {
            Alertify.log.success("JAP LOCAL SSH - OK");
            
            ko.mapping.fromJS(data, self.data);
        }, 
        function(jqXHR, textStatus, errorThrown) {
            Alertify.log.error("JAP LOCAL SSH - NOT OK");
        }
    );
}

function JAP_LOCAL_SSH_LOCAL_PROXY_SERVER_KEYS_ADD_ViewModel(parent) {
    var self = this;
    self.parent = parent;
    self.defaultData = {
        "PUBLIC": {
            "FILE": "",
            "PASSPHRASE": ""
        },
        "PRIVATE": {
            "FILE": "",
            "PASSPHRASE": ""
        }
    }
    self.data = ko.mapping.fromJS(self.defaultData);
    self.action = "JAP_LOCAL_SSH_LOCAL_PROXY_SERVER_KEYS_ADD";
    
    self.action_JAP_LOCAL_SSH_LOCAL_PROXY_SERVER_KEYS_ADD = function() {
        self.parent.action_JAP_LOCAL_SSH_LOCAL_PROXY_SERVER_KEYS_ADD(self.data);
        self.parent.load_JAP_LOCAL_SSH_LOCAL_PROXY_SERVER_KEYS();
    }
    
    self.cancel = function() {
        self.parent.load_JAP_LOCAL_SSH_LOCAL_PROXY_SERVER_KEYS();
    }
}

function JAP_LOCAL_SSH_LOCAL_PROXY_SERVER_KEYS_UPDATE_ViewModel(parent, selectedData) {
    var self = this;
    self.parent = parent;
    self.selectedData = selectedData;
    self.data = ko.mapping.fromJS(ko.mapping.toJS(self.selectedData));
    self.action = "JAP_LOCAL_SSH_LOCAL_PROXY_SERVER_KEYS_UPDATE";
    
    self.action_JAP_LOCAL_SSH_LOCAL_PROXY_SERVER_KEYS_UPDATE = function() {
        self.parent.action_JAP_LOCAL_SSH_LOCAL_PROXY_SERVER_KEYS_UPDATE(self.selectedData, self.data);
        self.parent.load_JAP_LOCAL_SSH_LOCAL_PROXY_SERVER_KEYS();
    }
    
    self.cancel = function() {
        self.parent.load_JAP_LOCAL_SSH_LOCAL_PROXY_SERVER_KEYS();
    }
}

function JAP_LOCAL_SSH_REMOTE_PROXY_SERVERS_ADD_ViewModel(parent) {
    var self = this;
    self.parent = parent;
    self.defaultData = {
        "ADDRESS": "",
        "PORT": 0,
        "AUTHENTICATION": {
            "USERNAME": "",
            "PASSWORD": ""
        },
        "KEY": {
            "AUTHENTICATION": {
                "FINGERPRINT": ""
            }
        }
    }
    self.data = ko.mapping.fromJS(self.defaultData);
    self.action = "JAP_LOCAL_SSH_REMOTE_PROXY_SERVERS_ADD";
    
    self.action_JAP_LOCAL_SSH_REMOTE_PROXY_SERVERS_ADD = function() {
        self.parent.action_JAP_LOCAL_SSH_REMOTE_PROXY_SERVERS_ADD(self.data);
        self.parent.load_JAP_LOCAL_SSH_REMOTE_PROXY_SERVERS();
    }
    
    self.cancel = function() {
        self.parent.load_JAP_LOCAL_SSH_REMOTE_PROXY_SERVERS();
    }
}

function JAP_LOCAL_SSH_REMOTE_PROXY_SERVERS_UPDATE_ViewModel(parent, data) {
    var self = this;
    self.parent = parent;
    self.selectedData = data;
    self.data = ko.mapping.fromJS(ko.mapping.toJS(self.selectedData));
    self.action = "JAP_LOCAL_SSH_REMOTE_PROXY_SERVERS_UPDATE";
    
    self.action_JAP_LOCAL_SSH_REMOTE_PROXY_SERVERS_UPDATE = function() {
        self.parent.action_JAP_LOCAL_SSH_REMOTE_PROXY_SERVERS_UPDATE(self.selectedData, self.data);
        self.parent.load_JAP_LOCAL_SSH_REMOTE_PROXY_SERVERS();
    }
    
    self.cancel = function() {
        self.parent.load_JAP_LOCAL_SSH_REMOTE_PROXY_SERVERS();
    }
}

function JAP_LOCAL_SSH_PROXY_SERVERS_ADD_ViewModel(parent) {
    var self = this;
    self.parent = parent;
    self.defaultData = {
        "TYPE": "",
        "ADDRESS": "",
        "PORT": 0,
        "AUTHENTICATION": {
            "USERNAME": "",
            "PASSWORD": ""
        }
    }
    self.data = ko.mapping.fromJS(self.defaultData);
    self.action = "JAP_LOCAL_SSH_PROXY_SERVERS_ADD";
    
    self.action_JAP_LOCAL_SSH_PROXY_SERVERS_ADD = function() {
        self.parent.action_JAP_LOCAL_SSH_PROXY_SERVERS_ADD(self.data);
        self.parent.load_JAP_LOCAL_SSH_PROXY_SERVERS();
    }
    
    self.cancel = function() {
        self.parent.load_JAP_LOCAL_SSH_PROXY_SERVERS();
    }
}

function JAP_LOCAL_SSH_PROXY_SERVERS_UPDATE_ViewModel(parent, data) {
    var self = this;
    self.parent = parent;
    self.selectedData = data;
    self.data = ko.mapping.fromJS(ko.mapping.toJS(self.selectedData));
    self.action = "JAP_LOCAL_SSH_PROXY_SERVERS_UPDATE";
    
    self.action_JAP_LOCAL_SSH_PROXY_SERVERS_UPDATE = function() {
        self.parent.action_JAP_LOCAL_SSH_PROXY_SERVERS_UPDATE(self.selectedData, self.data);
        self.parent.load_JAP_LOCAL_SSH_PROXY_SERVERS();
    }
    
    self.cancel = function() {
        self.parent.load_JAP_LOCAL_SSH_PROXY_SERVERS();
    }
}

function JAP_LOCAL_WS_ViewModel(parent) {
    var self = this;
    self.parent = parent;
    self.defaultData = {
        "LOGGER": {
            "LEVEL": ""
        },
        "LOCAL_PROXY_SERVER": {
            "ADDRESS": "",
            "PORT": 0
        },
        "REMOTE_PROXY_SERVERS": [],
        "PROXY_SERVERS": []
    }
    self.data = ko.mapping.fromJS(self.defaultData);
    
    self.action_JAP_LOCAL_WS_UPDATE = function() {
        var data = ko.mapping.toJS(self.data);
        
        if($.isNumeric(data.LOCAL_PROXY_SERVER.PORT)) {
            data.LOCAL_PROXY_SERVER.PORT = Number(data.LOCAL_PROXY_SERVER.PORT);
        } else {
            data.LOCAL_PROXY_SERVER.PORT = 0;
        }
        
        for(var i = 0; i < data.REMOTE_PROXY_SERVERS.length; i = i + 1) {
            if($.isNumeric(data.REMOTE_PROXY_SERVERS[i].PORT)) {
                data.REMOTE_PROXY_SERVERS[i].PORT = Number(data.REMOTE_PROXY_SERVERS[i].PORT);
            } else {
                data.REMOTE_PROXY_SERVERS[i].PORT = 0;
            }
        }
        
        for(var i = 0; i < data.PROXY_SERVERS.length; i = i + 1) {
            if($.isNumeric(data.PROXY_SERVERS[i].PORT)) {
                data.PROXY_SERVERS[i].PORT = Number(data.PROXY_SERVERS[i].PORT);
            } else {
                data.PROXY_SERVERS[i].PORT = 0;
            }
        }
        
        $.ajax({
            "type": "POST",
            "url": "/API",
            "dataType": "",
            "data": {
                "action": "JAP_LOCAL_WS_UPDATE",
                "data": ko.toJSON(data)
            }
        }).then(
            function(data, textStatus, jqXHR) {
                Alertify.log.success("JAP LOCAL WS - UPDATE OK");
            }, 
            function(jqXHR, textStatus, errorThrown) {
                Alertify.log.error("JAP LOCAL WS - UPDATE NOT OK");
            }
        )
    }
    
    self.action_JAP_LOCAL_WS_REMOTE_PROXY_SERVERS_ADD = function(data) {
        self.data.REMOTE_PROXY_SERVERS.push(data);
    }
    
    self.action_JAP_LOCAL_WS_REMOTE_PROXY_SERVERS_UPDATE = function(selectedData, data) {
        ko.mapping.fromJS(ko.mapping.toJS(data), {}, selectedData);
    }
    
    self.action_JAP_LOCAL_WS_REMOTE_PROXY_SERVERS_REMOVE = function(selectedData) {
        self.data.REMOTE_PROXY_SERVERS.remove(selectedData);
    }
    
    self.action_JAP_LOCAL_WS_REMOTE_PROXY_SERVERS_REMOVE_ALL = function() {
        self.data.REMOTE_PROXY_SERVERS.removeAll();
    }
    
    self.action_JAP_LOCAL_WS_PROXY_SERVERS_ADD = function(data) {
        self.data.PROXY_SERVERS.push(data);
    }
    
    self.action_JAP_LOCAL_WS_PROXY_SERVERS_UPDATE = function(selectedData, data) {
        ko.mapping.fromJS(ko.mapping.toJS(data), {}, selectedData);
    }
    
    self.action_JAP_LOCAL_WS_PROXY_SERVERS_REMOVE = function(selectedData) {
        self.data.PROXY_SERVERS.remove(selectedData);
    }
    
    self.action_JAP_LOCAL_WS_PROXY_SERVERS_REMOVE_ALL = function() {
        self.data.PROXY_SERVERS.removeAll();
    }
    
    self.load_JAP_LOCAL_WS_REMOTE_PROXY_SERVERS_ADD = function() {
        self.template_JAP_LOCAL_WS_REMOTE_PROXY_SERVERS(new Template("TEMPLATE_JAP_LOCAL_WS_REMOTE_PROXY_SERVER", new JAP_LOCAL_WS_REMOTE_PROXY_SERVERS_ADD_ViewModel(self)));
    }
    
    self.load_JAP_LOCAL_WS_REMOTE_PROXY_SERVERS_UPDATE = function(data) {
        self.template_JAP_LOCAL_WS_REMOTE_PROXY_SERVERS(new Template("TEMPLATE_JAP_LOCAL_WS_REMOTE_PROXY_SERVER", new JAP_LOCAL_WS_REMOTE_PROXY_SERVERS_UPDATE_ViewModel(self, data)));
    }
    
    self.load_JAP_LOCAL_WS_PROXY_SERVERS_ADD = function() {
        self.template_JAP_LOCAL_WS_PROXY_SERVERS(new Template("TEMPLATE_JAP_LOCAL_WS_PROXY_SERVER", new JAP_LOCAL_WS_PROXY_SERVERS_ADD_ViewModel(self)));
    }
    
    self.load_JAP_LOCAL_WS_PROXY_SERVERS_UPDATE = function(data) {
        self.template_JAP_LOCAL_WS_PROXY_SERVERS(new Template("TEMPLATE_JAP_LOCAL_WS_PROXY_SERVER", new JAP_LOCAL_WS_PROXY_SERVERS_UPDATE_ViewModel(self, data)));
    }
    
    self.template_JAP_LOCAL_WS_REMOTE_PROXY_SERVERS = ko.observable();
    
    self.load_JAP_LOCAL_WS_REMOTE_PROXY_SERVERS = function() {
        self.template_JAP_LOCAL_WS_REMOTE_PROXY_SERVERS(new Template("TEMPLATE_JAP_LOCAL_WS_REMOTE_PROXY_SERVERS", self));
    }
    
    self.load_JAP_LOCAL_WS_REMOTE_PROXY_SERVERS();
    
    self.template_JAP_LOCAL_WS_PROXY_SERVERS = ko.observable();
    
    self.load_JAP_LOCAL_WS_PROXY_SERVERS = function() {
        self.template_JAP_LOCAL_WS_PROXY_SERVERS(new Template("TEMPLATE_JAP_LOCAL_WS_PROXY_SERVERS", self));
    }
    
    self.load_JAP_LOCAL_WS_PROXY_SERVERS();
    
    $.ajax({
        "type": "GET",
        "url": "/API",
        "dataType": "JSON",
        "data": {
            "action": "JAP_LOCAL_WS"
        }
    }).then(
        function(data, textStatus, jqXHR) {
            Alertify.log.success("JAP LOCAL WS - OK");
            
            ko.mapping.fromJS(data, self.data);
        }, 
        function(jqXHR, textStatus, errorThrown) {
            Alertify.log.error("JAP LOCAL WS - NOT OK");
        }
    );
}

function JAP_LOCAL_WS_REMOTE_PROXY_SERVERS_ADD_ViewModel(parent) {
    var self = this;
    self.parent = parent;
    self.defaultData = {
        "TYPE": "",
        "ADDRESS": "",
        "PORT": 0,
        "AUTHENTICATION": {
            "USERNAME": "",
            "PASSWORD": ""
        },
        "CERTIFICATE": {
            "AUTHENTICATION": {
                "FILE": ""
            }
        }
    }
    self.data = ko.mapping.fromJS(self.defaultData);
    self.action = "JAP_LOCAL_WS_REMOTE_PROXY_SERVERS_ADD";
    
    self.action_JAP_LOCAL_WS_REMOTE_PROXY_SERVERS_ADD = function() {
        self.parent.action_JAP_LOCAL_WS_REMOTE_PROXY_SERVERS_ADD(self.data);
        self.parent.load_JAP_LOCAL_WS_REMOTE_PROXY_SERVERS();
    }
    
    self.cancel = function() {
        self.parent.load_JAP_LOCAL_WS_REMOTE_PROXY_SERVERS();
    }
}

function JAP_LOCAL_WS_REMOTE_PROXY_SERVERS_UPDATE_ViewModel(parent, data) {
    var self = this;
    self.parent = parent;
    self.selectedData = data;
    self.data = ko.mapping.fromJS(ko.mapping.toJS(self.selectedData));
    self.action = "JAP_LOCAL_WS_REMOTE_PROXY_SERVERS_UPDATE";
    
    self.action_JAP_LOCAL_WS_REMOTE_PROXY_SERVERS_UPDATE = function() {
        self.parent.action_JAP_LOCAL_WS_REMOTE_PROXY_SERVERS_UPDATE(self.selectedData, self.data);
        self.parent.load_JAP_LOCAL_WS_REMOTE_PROXY_SERVERS();
    }
    
    self.cancel = function() {
        self.parent.load_JAP_LOCAL_WS_REMOTE_PROXY_SERVERS();
    }
}

function JAP_LOCAL_WS_PROXY_SERVERS_ADD_ViewModel(parent) {
    var self = this;
    self.parent = parent;
    self.defaultData = {
        "TYPE": "",
        "ADDRESS": "",
        "PORT": 0,
        "AUTHENTICATION": {
            "USERNAME": "",
            "PASSWORD": ""
        }
    }
    self.data = ko.mapping.fromJS(self.defaultData);
    self.action = "JAP_LOCAL_WS_PROXY_SERVERS_ADD";
    
    self.action_JAP_LOCAL_WS_PROXY_SERVERS_ADD = function() {
        self.parent.action_JAP_LOCAL_WS_PROXY_SERVERS_ADD(self.data);
        self.parent.load_JAP_LOCAL_WS_PROXY_SERVERS();
    }
    
    self.cancel = function() {
        self.parent.load_JAP_LOCAL_WS_PROXY_SERVERS();
    }
}

function JAP_LOCAL_WS_PROXY_SERVERS_UPDATE_ViewModel(parent, data) {
    var self = this;
    self.parent = parent;
    self.selectedData = data;
    self.data = ko.mapping.fromJS(ko.mapping.toJS(self.selectedData));
    self.action = "JAP_LOCAL_WS_PROXY_SERVERS_UPDATE";
    
    self.action_JAP_LOCAL_WS_PROXY_SERVERS_UPDATE = function() {
        self.parent.action_JAP_LOCAL_WS_PROXY_SERVERS_UPDATE(self.selectedData, self.data);
        self.parent.load_JAP_LOCAL_WS_PROXY_SERVERS();
    }
    
    self.cancel = function() {
        self.parent.load_JAP_LOCAL_WS_PROXY_SERVERS();
    }
}

function JAP_REMOTE_SSH_ViewModel(parent) {
    var self = this;
    self.parent = parent;
    self.defaultData = {
        "LOGGER": {
            "LEVEL": ""
        },
        "REMOTE_PROXY_SERVER": {
            "ADDRESS": "",
            "PORT": 0,
            "AUTHENTICATION": [],
            "KEY": {
                "PUBLIC": {
                    "FILE": "",
                    "PASSPHRASE": ""
                },
                "PRIVATE": {
                    "FILE": "",
                    "PASSPHRASE": ""
                }
            }
        },
        "PROXY_SERVERS": []
    }
    self.data = ko.mapping.fromJS(self.defaultData);
    
    self.action_JAP_REMOTE_SSH_UPDATE = function() {
        var data = ko.mapping.toJS(self.data);
        
        if($.isNumeric(data.REMOTE_PROXY_SERVER.PORT)) {
            data.REMOTE_PROXY_SERVER.PORT = Number(data.REMOTE_PROXY_SERVER.PORT);
        } else {
            data.REMOTE_PROXY_SERVER.PORT = 0;
        }
        
        for(var i = 0; i < data.PROXY_SERVERS.length; i = i + 1) {
            if($.isNumeric(data.PROXY_SERVERS[i].PORT)) {
                data.PROXY_SERVERS[i].PORT = Number(data.PROXY_SERVERS[i].PORT);
            } else {
                data.PROXY_SERVERS[i].PORT = 0;
            }
        }
        
        $.ajax({
            "type": "POST",
            "url": "/API",
            "dataType": "",
            "data": {
                "action": "JAP_REMOTE_SSH_UPDATE",
                "data": ko.toJSON(data)
            }
        }).then(
            function(data, textStatus, jqXHR) {
                Alertify.log.success("JAP REMOTE SSH - UPDATE OK");
            }, 
            function(jqXHR, textStatus, errorThrown) {
                Alertify.log.error("JAP REMOTE SSH - UPDATE NOT OK");
            }
        )
    }
    
    self.action_JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATIONS_ADD = function(data) {
        self.data.REMOTE_PROXY_SERVER.AUTHENTICATION.push(data);
    }
    
    self.action_JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATIONS_UPDATE = function(selectedData, data) {
        ko.mapping.fromJS(ko.mapping.toJS(data), {}, selectedData);
    }
    
    self.action_JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATIONS_REMOVE = function(selectedData) {
        self.data.REMOTE_PROXY_SERVER.AUTHENTICATION.remove(selectedData);
    }
    
    self.action_JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATIONS_REMOVE_ALL = function() {
        self.data.REMOTE_PROXY_SERVER.AUTHENTICATION.removeAll();
    }
    
    self.action_JAP_REMOTE_SSH_PROXY_SERVERS_ADD = function(data) {
        self.data.PROXY_SERVERS.push(data);
    }
    
    self.action_JAP_REMOTE_SSH_PROXY_SERVERS_UPDATE = function(selectedData, data) {
        ko.mapping.fromJS(ko.mapping.toJS(data), {}, selectedData);
    }
    
    self.action_JAP_REMOTE_SSH_PROXY_SERVERS_REMOVE = function(selectedData) {
        self.data.PROXY_SERVERS.remove(selectedData);
    }
    
    self.action_JAP_REMOTE_SSH_PROXY_SERVERS_REMOVE_ALL = function() {
        self.data.PROXY_SERVERS.removeAll();
    }
    
    self.load_JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATIONS_ADD = function() {
        self.template_JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATIONS(new Template("TEMPLATE_JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATION", new JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATIONS_ADD_ViewModel(self)));
    }
    
    self.load_JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATIONS_UPDATE = function(data) {
        self.template_JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATIONS(new Template("TEMPLATE_JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATION", new JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATIONS_UPDATE_ViewModel(self, data)));
    }
    
    self.load_JAP_REMOTE_SSH_PROXY_SERVERS_ADD = function() {
        self.template_JAP_REMOTE_SSH_PROXY_SERVERS(new Template("TEMPLATE_JAP_REMOTE_SSH_PROXY_SERVER", new JAP_REMOTE_SSH_PROXY_SERVERS_ADD_ViewModel(self)));
    }
    
    self.load_JAP_REMOTE_SSH_PROXY_SERVERS_UPDATE = function(data) {
        self.template_JAP_REMOTE_SSH_PROXY_SERVERS(new Template("TEMPLATE_JAP_REMOTE_SSH_PROXY_SERVER", new JAP_REMOTE_SSH_PROXY_SERVERS_UPDATE_ViewModel(self, data)));
    }
    
    self.template_JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATIONS = ko.observable();
    
    self.load_JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATIONS = function() {
        self.template_JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATIONS(new Template("TEMPLATE_JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATIONS", self));
    }
    
    self.load_JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATIONS();
    
    self.template_JAP_REMOTE_SSH_PROXY_SERVERS = ko.observable();
    
    self.load_JAP_REMOTE_SSH_PROXY_SERVERS = function() {
        self.template_JAP_REMOTE_SSH_PROXY_SERVERS(new Template("TEMPLATE_JAP_REMOTE_SSH_PROXY_SERVERS", self));
    }
    
    self.load_JAP_REMOTE_SSH_PROXY_SERVERS();
    
    $.ajax({
        "type": "GET",
        "url": "/API",
        "dataType": "JSON",
        "data": {
            "action": "JAP_REMOTE_SSH"
        }
    }).then(
        function(data, textStatus, jqXHR) {
            Alertify.log.success("JAP REMOTE SSH - OK");
            
            ko.mapping.fromJS(data, self.data);
        }, 
        function(jqXHR, textStatus, errorThrown) {
            Alertify.log.error("JAP REMOTE SSH - NOT OK");
        }
    );
}

function JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATIONS_ADD_ViewModel(parent) {
    var self = this;
    self.parent = parent;
    self.defaultData = {
        "USERNAME": "",
        "PASSWORD": "",
        "KEYS": []
    }
    self.data = ko.mapping.fromJS(self.defaultData);
    self.action = "JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATIONS_ADD";
    
    self.action_JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATIONS_ADD = function() {
        self.parent.action_JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATIONS_ADD(self.data);
        self.parent.load_JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATIONS();
    }
    
    self.cancel = function() {
        self.parent.load_JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATIONS();
    }
    
    self.action_JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATION_KEYS_ADD = function(data) {
        self.data.KEYS.push(data);
    }
    
    self.action_JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATION_KEYS_UPDATE = function(selectedData, data) {
        ko.mapping.fromJS(ko.mapping.toJS(data), {}, selectedData);
    }
    
    self.action_JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATION_KEYS_REMOVE = function(selectedData) {
        self.data.KEYS.remove(selectedData);
    }
    
    self.action_JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATION_KEYS_REMOVE_ALL = function() {
        self.data.KEYS.removeAll();
    }
    
    self.load_JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATION_KEYS_ADD = function() {
        self.template_JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATION_KEYS(new Template("TEMPLATE_JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATION_KEY", new JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATION_KEYS_ADD_ViewModel(self)));
    }
    
    self.load_JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATION_KEYS_UPDATE = function(data) {
        self.template_JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATION_KEYS(new Template("TEMPLATE_JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATION_KEY", new JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATION_KEYS_UPDATE_ViewModel(self, data)));
    }
    
    self.template_JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATION_KEYS = ko.observable();
    
    self.load_JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATION_KEYS = function() {
        self.template_JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATION_KEYS(new Template("TEMPLATE_JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATION_KEYS", self));
    }
    
    self.load_JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATION_KEYS();
}

function JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATIONS_UPDATE_ViewModel(parent, data) {
    var self = this;
    self.parent = parent;
    self.selectedData = data;
    self.data = ko.mapping.fromJS(ko.mapping.toJS(self.selectedData));
    self.action = "JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATIONS_UPDATE";
    
    self.action_JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATIONS_UPDATE = function() {
        self.parent.action_JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATIONS_UPDATE(self.selectedData, self.data);
        self.parent.load_JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATIONS();
    }
    
    self.cancel = function() {
        self.parent.load_JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATIONS();
    }
    
    self.action_JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATION_KEYS_ADD = function(data) {
        self.data.KEYS.push(data);
    }
    
    self.action_JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATION_KEYS_UPDATE = function(selectedData, data) {
        ko.mapping.fromJS(ko.mapping.toJS(data), {}, selectedData);
    }
    
    self.action_JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATION_KEYS_REMOVE = function(selectedData) {
        self.data.KEYS.remove(selectedData);
    }
    
    self.action_JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATION_KEYS_REMOVE_ALL = function() {
        self.data.KEYS.removeAll();
    }
    
    self.load_JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATION_KEYS_ADD = function() {
        self.template_JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATION_KEYS(new Template("TEMPLATE_JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATION_KEY", new JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATION_KEYS_ADD_ViewModel(self)));
    }
    
    self.load_JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATION_KEYS_UPDATE = function(data) {
        self.template_JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATION_KEYS(new Template("TEMPLATE_JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATION_KEY", new JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATION_KEYS_UPDATE_ViewModel(self, data)));
    }
    
    self.template_JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATION_KEYS = ko.observable();
    
    self.load_JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATION_KEYS = function() {
        self.template_JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATION_KEYS(new Template("TEMPLATE_JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATION_KEYS", self));
    }
    
    self.load_JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATION_KEYS();
}

function JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATION_KEYS_ADD_ViewModel(parent) {
    var self = this;
    self.parent = parent;
    self.defaultData = {
        "PUBLIC": {
            "FILE": "",
            "PASSPHRASE": ""
        }
    }
    self.data = ko.mapping.fromJS(self.defaultData);
    self.action = "JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATION_KEYS_ADD";
    
    self.action_JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATION_KEYS_ADD = function() {
        self.parent.action_JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATION_KEYS_ADD(self.data);
        self.parent.load_JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATION_KEYS();
    }
    
    self.cancel = function() {
        self.parent.load_JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATION_KEYS();
    }
}

function JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATION_KEYS_UPDATE_ViewModel(parent, data) {
    var self = this;
    self.parent = parent;
    self.selectedData = data;
    self.data = ko.mapping.fromJS(ko.mapping.toJS(self.selectedData));
    self.action = "JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATION_KEYS_UPDATE";
    
    self.action_JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATION_KEYS_UPDATE = function() {
        self.parent.action_JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATION_KEYS_UPDATE(self.selectedData, self.data);
        self.parent.load_JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATION_KEYS();
    }
    
    self.cancel = function() {
        self.parent.load_JAP_REMOTE_SSH_REMOTE_PROXY_SERVER_AUTHENTICATION_KEYS();
    }
}

function JAP_REMOTE_SSH_PROXY_SERVERS_ADD_ViewModel(parent) {
    var self = this;
    self.parent = parent;
    self.defaultData = {
        "TYPE": "",
        "ADDRESS": "",
        "PORT": 0,
        "AUTHENTICATION": {
            "USERNAME": "",
            "PASSWORD": ""
        }
    }
    self.data = ko.mapping.fromJS(self.defaultData);
    self.action = "JAP_REMOTE_SSH_PROXY_SERVERS_ADD";
    
    self.action_JAP_REMOTE_SSH_PROXY_SERVERS_ADD = function() {
        self.parent.action_JAP_REMOTE_SSH_PROXY_SERVERS_ADD(self.data);
        self.parent.load_JAP_REMOTE_SSH_PROXY_SERVERS();
    }
    
    self.cancel = function() {
        self.parent.load_JAP_REMOTE_SSH_PROXY_SERVERS();
    }
}

function JAP_REMOTE_SSH_PROXY_SERVERS_UPDATE_ViewModel(parent, data) {
    var self = this;
    self.parent = parent;
    self.selectedData = data;
    self.data = ko.mapping.fromJS(ko.mapping.toJS(self.selectedData));
    self.action = "JAP_REMOTE_SSH_PROXY_SERVERS_UPDATE";
    
    self.action_JAP_REMOTE_SSH_PROXY_SERVERS_UPDATE = function() {
        self.parent.action_JAP_REMOTE_SSH_PROXY_SERVERS_UPDATE(self.selectedData, self.data);
        self.parent.load_JAP_REMOTE_SSH_PROXY_SERVERS();
    }
    
    self.cancel = function() {
        self.parent.load_JAP_REMOTE_SSH_PROXY_SERVERS();
    }
}

function JAP_REMOTE_WS_ViewModel(parent) {
    var self = this;
    self.parent = parent;
    self.defaultData = {
        "LOGGER": {
            "LEVEL": "DEBUG"
        },
        "REMOTE_PROXY_SERVER": {
            "TYPE": "",
            "ADDRESS": "",
            "PORT": 0,
            "AUTHENTICATION": [],
            "CERTIFICATE": {
                "KEY": {
                    "FILE": ""
                },
                "FILE": ""
            }
        },
        "PROXY_SERVERS": []
    }
    self.data = ko.mapping.fromJS(self.defaultData);
    
    self.action_JAP_REMOTE_WS_UPDATE = function() {
        var data = ko.mapping.toJS(self.data);
        
        if($.isNumeric(data.REMOTE_PROXY_SERVER.PORT)) {
            data.REMOTE_PROXY_SERVER.PORT = Number(data.REMOTE_PROXY_SERVER.PORT);
        } else {
            data.REMOTE_PROXY_SERVER.PORT = 0;
        }
        
        for(var i = 0; i < data.PROXY_SERVERS.length; i = i + 1) {
            if($.isNumeric(data.PROXY_SERVERS[i].PORT)) {
                data.PROXY_SERVERS[i].PORT = Number(data.PROXY_SERVERS[i].PORT);
            } else {
                data.PROXY_SERVERS[i].PORT = 0;
            }
        }
        
        $.ajax({
            "type": "POST",
            "url": "/API",
            "dataType": "",
            "data": {
                "action": "JAP_REMOTE_WS_UPDATE",
                "data": ko.toJSON(data)
            }
        }).then(
            function(data, textStatus, jqXHR) {
                Alertify.log.success("JAP REMOTE WS - UPDATE OK");
            }, 
            function(jqXHR, textStatus, errorThrown) {
                Alertify.log.error("JAP REMOTE WS - UPDATE NOT OK");
            }
        )
    }
    
    self.action_JAP_REMOTE_WS_REMOTE_PROXY_SERVER_AUTHENTICATIONS_ADD = function(data) {
        self.data.REMOTE_PROXY_SERVER.AUTHENTICATION.push(data);
    }
    
    self.action_JAP_REMOTE_WS_REMOTE_PROXY_SERVER_AUTHENTICATIONS_UPDATE = function(selectedData, data) {
        ko.mapping.fromJS(ko.mapping.toJS(data), {}, selectedData);
    }
    
    self.action_JAP_REMOTE_WS_REMOTE_PROXY_SERVER_AUTHENTICATIONS_REMOVE = function(selectedData) {
        self.data.REMOTE_PROXY_SERVER.AUTHENTICATION.remove(selectedData);
    }
    
    self.action_JAP_REMOTE_WS_REMOTE_PROXY_SERVER_AUTHENTICATIONS_REMOVE_ALL = function() {
        self.data.REMOTE_PROXY_SERVER.AUTHENTICATION.removeAll();
    }
    
    self.action_JAP_REMOTE_WS_PROXY_SERVERS_ADD = function(data) {
        self.data.PROXY_SERVERS.push(data);
    }
    
    self.action_JAP_REMOTE_WS_PROXY_SERVERS_UPDATE = function(selectedData, data) {
        ko.mapping.fromJS(ko.mapping.toJS(data), {}, selectedData);
    }
    
    self.action_JAP_REMOTE_WS_PROXY_SERVERS_REMOVE = function(selectedData) {
        self.data.PROXY_SERVERS.remove(selectedData);
    }
    
    self.action_JAP_REMOTE_WS_PROXY_SERVERS_REMOVE_ALL = function() {
        self.data.PROXY_SERVERS.removeAll();
    }
    
    self.load_JAP_REMOTE_WS_REMOTE_PROXY_SERVER_AUTHENTICATIONS_ADD = function() {
        self.template_JAP_REMOTE_WS_REMOTE_PROXY_SERVER_AUTHENTICATIONS(new Template("TEMPLATE_JAP_REMOTE_WS_REMOTE_PROXY_SERVER_AUTHENTICATION", new JAP_REMOTE_WS_REMOTE_PROXY_SERVER_AUTHENTICATIONS_ADD_ViewModel(self)));
    }
    
    self.load_JAP_REMOTE_WS_REMOTE_PROXY_SERVER_AUTHENTICATIONS_UPDATE = function(data) {
        self.template_JAP_REMOTE_WS_REMOTE_PROXY_SERVER_AUTHENTICATIONS(new Template("TEMPLATE_JAP_REMOTE_WS_REMOTE_PROXY_SERVER_AUTHENTICATION", new JAP_REMOTE_WS_REMOTE_PROXY_SERVER_AUTHENTICATIONS_UPDATE_ViewModel(self, data)));
    }
    
    self.load_JAP_REMOTE_WS_PROXY_SERVERS_ADD = function() {
        self.template_JAP_REMOTE_WS_PROXY_SERVERS(new Template("TEMPLATE_JAP_REMOTE_WS_PROXY_SERVER", new JAP_REMOTE_WS_PROXY_SERVERS_ADD_ViewModel(self)));
    }
    
    self.load_JAP_REMOTE_WS_PROXY_SERVERS_UPDATE = function(data) {
        self.template_JAP_REMOTE_WS_PROXY_SERVERS(new Template("TEMPLATE_JAP_REMOTE_WS_PROXY_SERVER", new JAP_REMOTE_WS_PROXY_SERVERS_UPDATE_ViewModel(self, data)));
    }
    
    self.template_JAP_REMOTE_WS_REMOTE_PROXY_SERVER_AUTHENTICATIONS = ko.observable();
    
    self.load_JAP_REMOTE_WS_REMOTE_PROXY_SERVER_AUTHENTICATIONS = function() {
        self.template_JAP_REMOTE_WS_REMOTE_PROXY_SERVER_AUTHENTICATIONS(new Template("TEMPLATE_JAP_REMOTE_WS_REMOTE_PROXY_SERVER_AUTHENTICATIONS", self));
    }
    
    self.load_JAP_REMOTE_WS_REMOTE_PROXY_SERVER_AUTHENTICATIONS();
    
    self.template_JAP_REMOTE_WS_PROXY_SERVERS = ko.observable();
    
    self.load_JAP_REMOTE_WS_PROXY_SERVERS = function() {
        self.template_JAP_REMOTE_WS_PROXY_SERVERS(new Template("TEMPLATE_JAP_REMOTE_WS_PROXY_SERVERS", self));
    }
    
    self.load_JAP_REMOTE_WS_PROXY_SERVERS();
    
    $.ajax({
        "type": "GET",
        "url": "/API",
        "dataType": "JSON",
        "data": {
            "action": "JAP_REMOTE_WS"
        }
    }).then(
        function(data, textStatus, jqXHR) {
            Alertify.log.success("JAP REMOTE WS - OK");
            
            ko.mapping.fromJS(data, self.data);
        }, 
        function(jqXHR, textStatus, errorThrown) {
            Alertify.log.error("JAP REMOTE WS - NOT OK");
        }
    );
}

function JAP_REMOTE_WS_REMOTE_PROXY_SERVER_AUTHENTICATIONS_ADD_ViewModel(parent) {
    var self = this;
    self.parent = parent;
    self.defaultData = {
        "USERNAME": "",
        "PASSWORD": ""
    }
    self.data = ko.mapping.fromJS(self.defaultData);
    self.action = "JAP_REMOTE_WS_REMOTE_PROXY_SERVER_AUTHENTICATIONS_ADD";
    
    self.action_JAP_REMOTE_WS_REMOTE_PROXY_SERVER_AUTHENTICATIONS_ADD = function() {
        self.parent.action_JAP_REMOTE_WS_REMOTE_PROXY_SERVER_AUTHENTICATIONS_ADD(self.data);
        self.parent.load_JAP_REMOTE_WS_REMOTE_PROXY_SERVER_AUTHENTICATIONS();
    }
    
    self.cancel = function() {
        self.parent.load_JAP_REMOTE_WS_REMOTE_PROXY_SERVER_AUTHENTICATIONS();
    }
}

function JAP_REMOTE_WS_REMOTE_PROXY_SERVER_AUTHENTICATIONS_UPDATE_ViewModel(parent, data) {
    var self = this;
    self.parent = parent;
    self.selectedData = data;
    self.data = ko.mapping.fromJS(ko.mapping.toJS(self.selectedData));
    self.action = "JAP_REMOTE_WS_REMOTE_PROXY_SERVER_AUTHENTICATIONS_UPDATE";
    
    self.action_JAP_REMOTE_WS_REMOTE_PROXY_SERVER_AUTHENTICATIONS_UPDATE = function() {
        self.parent.action_JAP_REMOTE_WS_REMOTE_PROXY_SERVER_AUTHENTICATIONS_UPDATE(self.selectedData, self.data);
        self.parent.load_JAP_REMOTE_WS_REMOTE_PROXY_SERVER_AUTHENTICATIONS();
    }
    
    self.cancel = function() {
        self.parent.load_JAP_REMOTE_WS_REMOTE_PROXY_SERVER_AUTHENTICATIONS();
    }
}

function JAP_REMOTE_WS_PROXY_SERVERS_ADD_ViewModel(parent) {
    var self = this;
    self.parent = parent;
    self.defaultData = {
        "TYPE": "",
        "ADDRESS": "",
        "PORT": 0,
        "AUTHENTICATION": {
            "USERNAME": "",
            "PASSWORD": ""
        }
    }
    self.data = ko.mapping.fromJS(self.defaultData);
    self.action = "JAP_REMOTE_WS_PROXY_SERVERS_ADD";
    
    self.action_JAP_REMOTE_WS_PROXY_SERVERS_ADD = function() {
        self.parent.action_JAP_REMOTE_WS_PROXY_SERVERS_ADD(self.data);
        self.parent.load_JAP_REMOTE_WS_PROXY_SERVERS();
    }
    
    self.cancel = function() {
        self.parent.load_JAP_REMOTE_WS_PROXY_SERVERS();
    }
}

function JAP_REMOTE_WS_PROXY_SERVERS_UPDATE_ViewModel(parent, data) {
    var self = this;
    self.parent = parent;
    self.selectedData = data;
    self.data = ko.mapping.fromJS(ko.mapping.toJS(self.selectedData));
    self.action = "JAP_REMOTE_WS_PROXY_SERVERS_UPDATE";
    
    self.action_JAP_REMOTE_WS_PROXY_SERVERS_UPDATE = function() {
        self.parent.action_JAP_REMOTE_WS_PROXY_SERVERS_UPDATE(self.selectedData, self.data);
        self.parent.load_JAP_REMOTE_WS_PROXY_SERVERS();
    }
    
    self.cancel = function() {
        self.parent.load_JAP_REMOTE_WS_PROXY_SERVERS();
    }
}

function ViewModel() {
    var self = this;
    
    self.action_JAP_LOCAL_START = function() {
        $.ajax({
            "type": "POST",
            "url": "/API",
            "dataType": "",
            "data": {
                "action": "JAP_LOCAL_START"
            }
        }).then(
            function(data, textStatus, jqXHR) {
                Alertify.log.success("JAP LOCAL - START OK");
            }, 
            function(jqXHR, textStatus, errorThrown) {
                Alertify.log.error("JAP LOCAL - START NOT OK");
            }
        )
    }
    
    self.action_JAP_LOCAL_STOP = function() {
        $.ajax({
            "type": "POST",
            "url": "/API",
            "dataType": "",
            "data": {
                "action": "JAP_LOCAL_STOP"
            }
        }).then(
            function(data, textStatus, jqXHR) {
                Alertify.log.success("JAP LOCAL - STOP OK");
            }, 
            function(jqXHR, textStatus, errorThrown) {
                Alertify.log.error("JAP LOCAL - STOP NOT OK");
            }
        )
    }
    
    self.action_JAP_LOCAL_SSH_START = function() {
        $.ajax({
            "type": "POST",
            "url": "/API",
            "dataType": "",
            "data": {
                "action": "JAP_LOCAL_SSH_START"
            }
        }).then(
            function(data, textStatus, jqXHR) {
                Alertify.log.success("JAP LOCAL SSH - START OK");
            }, 
            function(jqXHR, textStatus, errorThrown) {
                Alertify.log.error("JAP LOCAL SSH - START NOT OK");
            }
        )
    }
    
    self.action_JAP_LOCAL_SSH_STOP = function() {
        $.ajax({
            "type": "POST",
            "url": "/API",
            "dataType": "",
            "data": {
                "action": "JAP_LOCAL_SSH_STOP"
            }
        }).then(
            function(data, textStatus, jqXHR) {
                Alertify.log.success("JAP LOCAL SSH - STOP OK");
            }, 
            function(jqXHR, textStatus, errorThrown) {
                Alertify.log.error("JAP LOCAL SSH - STOP NOT OK");
            }
        )
    }
    
    self.action_JAP_LOCAL_WS_START = function() {
        $.ajax({
            "type": "POST",
            "url": "/API",
            "dataType": "",
            "data": {
                "action": "JAP_LOCAL_WS_START"
            }
        }).then(
            function(data, textStatus, jqXHR) {
                Alertify.log.success("JAP LOCAL WS - START OK");
            }, 
            function(jqXHR, textStatus, errorThrown) {
                Alertify.log.error("JAP LOCAL WS - START NOT OK");
            }
        )
    }
    
    self.action_JAP_LOCAL_WS_STOP = function() {
        $.ajax({
            "type": "POST",
            "url": "/API",
            "dataType": "",
            "data": {
                "action": "JAP_LOCAL_WS_STOP"
            }
        }).then(
            function(data, textStatus, jqXHR) {
                Alertify.log.success("JAP LOCAL WS - STOP OK");
            }, 
            function(jqXHR, textStatus, errorThrown) {
                Alertify.log.error("JAP LOCAL WS - STOP NOT OK");
            }
        )
    }
    
    self.action_JAP_REMOTE_SSH_START = function() {
        $.ajax({
            "type": "POST",
            "url": "/API",
            "dataType": "",
            "data": {
                "action": "JAP_REMOTE_SSH_START"
            }
        }).then(
            function(data, textStatus, jqXHR) {
                Alertify.log.success("JAP REMOTE SSH - START OK");
            }, 
            function(jqXHR, textStatus, errorThrown) {
                Alertify.log.error("JAP REMOTE SSH - START NOT OK");
            }
        )
    }
    
    self.action_JAP_REMOTE_SSH_STOP = function() {
        $.ajax({
            "type": "POST",
            "url": "/API",
            "dataType": "",
            "data": {
                "action": "JAP_REMOTE_SSH_STOP"
            }
        }).then(
            function(data, textStatus, jqXHR) {
                Alertify.log.success("JAP REMOTE SSH - STOP OK");
            }, 
            function(jqXHR, textStatus, errorThrown) {
                Alertify.log.error("JAP REMOTE SSH - STOP NOT OK");
            }
        )
    }
    
    self.action_JAP_REMOTE_WS_START = function() {
        $.ajax({
            "type": "POST",
            "url": "/API",
            "dataType": "",
            "data": {
                "action": "JAP_REMOTE_WS_START"
            }
        }).then(
            function(data, textStatus, jqXHR) {
                Alertify.log.success("JAP REMOTE WS - START OK");
            }, 
            function(jqXHR, textStatus, errorThrown) {
                Alertify.log.error("JAP REMOTE WS - START NOT OK");
            }
        )
    }
    
    self.action_JAP_REMOTE_WS_STOP = function() {
        $.ajax({
            "type": "POST",
            "url": "/API",
            "dataType": "",
            "data": {
                "action": "JAP_REMOTE_WS_STOP"
            }
        }).then(
            function(data, textStatus, jqXHR) {
                Alertify.log.success("JAP REMOTE WS - STOP OK");
            }, 
            function(jqXHR, textStatus, errorThrown) {
                Alertify.log.error("JAP REMOTE WS - STOP NOT OK");
            }
        )
    }
    
    self.template_JAP = ko.observable();
    
    self.load_JAP = function() {
        self.template_JAP(new Template("TEMPLATE_JAP", new JAP_ViewModel(self)));
    }
    
    self.load_JAP();
    
    self.template_JAP_LOCAL = ko.observable();
    
    self.load_JAP_LOCAL = function() {
        self.template_JAP_LOCAL(new Template("TEMPLATE_JAP_LOCAL", new JAP_LOCAL_ViewModel(self)));
    }
    
    self.load_JAP_LOCAL();
    
    self.template_JAP_LOCAL_SSH = ko.observable();
    
    self.load_JAP_LOCAL_SSH = function() {
        self.template_JAP_LOCAL_SSH(new Template("TEMPLATE_JAP_LOCAL_SSH", new JAP_LOCAL_SSH_ViewModel(self)));
    }
    
    self.load_JAP_LOCAL_SSH();
    
    self.template_JAP_LOCAL_WS = ko.observable();
    
    self.load_JAP_LOCAL_WS = function() {
        self.template_JAP_LOCAL_WS(new Template("TEMPLATE_JAP_LOCAL_WS", new JAP_LOCAL_WS_ViewModel(self)));
    }
    
    self.load_JAP_LOCAL_WS();
    
    self.template_JAP_REMOTE_SSH = ko.observable();
    
    self.load_JAP_REMOTE_SSH = function() {
        self.template_JAP_REMOTE_SSH(new Template("TEMPLATE_JAP_REMOTE_SSH", new JAP_REMOTE_SSH_ViewModel(self)));
    }
    
    self.load_JAP_REMOTE_SSH();
    
    self.template_JAP_REMOTE_WS = ko.observable();
    
    self.load_JAP_REMOTE_WS = function() {
        self.template_JAP_REMOTE_WS(new Template("TEMPLATE_JAP_REMOTE_WS", new JAP_REMOTE_WS_ViewModel(self)));
    }
    
    self.load_JAP_REMOTE_WS();
}

ko.applyBindings(new ViewModel());