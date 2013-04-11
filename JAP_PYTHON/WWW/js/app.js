function Template(name, data) {
    var self = this;
    self.name = ko.observable(name);
    self.data = ko.observable(data);
}

function LOCAL_ViewModel(parent) {
    var self = this;
    self.parent = parent;
    self.defaultData = {
        "LOGGER":
        {
            "LEVEL": ""
        },
        "LOCAL_PROXY_SERVER":
        {
            "ADDRESS": "",
            "PORT": 0
        },
        "PROXY_SERVER":
        {
            "TYPE": "",
            "ADDRESS": "",
            "PORT": 0,
            "AUTHENTICATION":
            {
                "USERNAME": "",
                "PASSWORD": ""
            }
        }
    }
    self.data = ko.mapping.fromJS(self.defaultData);
    
    self.action_LOCAL_UPDATE = function() {
        var data = ko.mapping.toJS(self.data);
        
        if($.isNumeric(data.LOCAL_PROXY_SERVER.PORT)) {
            data.LOCAL_PROXY_SERVER.PORT = Number(data.LOCAL_PROXY_SERVER.PORT);
        } else {
            data.LOCAL_PROXY_SERVER.PORT = 0;
        }
        
        if($.isNumeric(data.PROXY_SERVER.PORT)) {
            data.PROXY_SERVER.PORT = Number(data.PROXY_SERVER.PORT);
        } else {
            data.PROXY_SERVER.PORT = 0;
        }
        
        $.ajax({
            "type": "POST",
            "url": "/API",
            "dataType": "",
            "data": {
                "action": "LOCAL_UPDATE",
                "data": ko.toJSON(data)
            }
        }).then(
            function(data, textStatus, jqXHR) {
                Alertify.log.success("LOCAL - UPDATE OK");
            }, 
            function(jqXHR, textStatus, errorThrown) {
                Alertify.log.error("LOCAL - UPDATE NOT OK");
            }
        )
    }
    
    $.ajax({
        "type": "GET",
        "url": "/API",
        "dataType": "JSON",
        "data": {
            "action": "LOCAL"
        }
    }).then(
        function(data, textStatus, jqXHR) {
            Alertify.log.success("LOCAL - OK");
            
            ko.mapping.fromJS(data, self.data);
        }, 
        function(jqXHR, textStatus, errorThrown) {
            Alertify.log.error("LOCAL - NOT OK");
        }
    );
}

function LOCAL_SSH_ViewModel(parent) {
    var self = this;
    self.parent = parent;
    self.defaultData = {
        "LOGGER":
        {
            "LEVEL": ""
        },
        "LOCAL_PROXY_SERVER":
        {
            "ADDRESS": "",
            "PORT": 0,
            "KEYS": []
        },
        "REMOTE_PROXY_SERVERS":[],
        "PROXY_SERVER":
        {
            "TYPE": "",
            "ADDRESS": "",
            "PORT": 0,
            "AUTHENTICATION":
            {
                "USERNAME": "",
                "PASSWORD": ""
            }
        }
    }
    self.data = ko.mapping.fromJS(self.defaultData);
    
    self.action_LOCAL_SSH_UPDATE = function() {
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
        
        if($.isNumeric(data.PROXY_SERVER.PORT)) {
            data.PROXY_SERVER.PORT = Number(data.PROXY_SERVER.PORT);
        } else {
            data.PROXY_SERVER.PORT = 0;
        }
        
        $.ajax({
            "type": "POST",
            "url": "/API",
            "dataType": "",
            "data": {
                "action": "LOCAL_SSH_UPDATE",
                "data": ko.toJSON(data)
            }
        }).then(
            function(data, textStatus, jqXHR) {
                Alertify.log.success("LOCAL SSH - UPDATE OK");
            }, 
            function(jqXHR, textStatus, errorThrown) {
                Alertify.log.error("LOCAL SSH - UPDATE NOT OK");
            }
        )
    }
    
    self.action_LOCAL_SSH_LOCAL_PROXY_SERVER_KEYS_ADD = function(data) {
        self.data.LOCAL_PROXY_SERVER.KEYS.push(data);
    }
    
    self.action_LOCAL_SSH_LOCAL_PROXY_SERVER_KEYS_UPDATE = function(selectedData, data) {
        ko.mapping.fromJS(ko.mapping.toJS(data), selectedData);
    }
    
    self.action_LOCAL_SSH_LOCAL_PROXY_SERVER_KEYS_REMOVE = function(selectedData) {
        self.data.LOCAL_PROXY_SERVER.KEYS.remove(selectedData);
    }
    
    self.action_LOCAL_SSH_LOCAL_PROXY_SERVER_KEYS_REMOVE_ALL = function() {
        self.data.LOCAL_PROXY_SERVER.KEYS.removeAll();
    }
    
    self.action_LOCAL_SSH_REMOTE_PROXY_SERVERS_ADD = function(data) {
        self.data.REMOTE_PROXY_SERVERS.push(data);
    }
    
    self.action_LOCAL_SSH_REMOTE_PROXY_SERVERS_UPDATE = function(selectedData, data) {
        ko.mapping.fromJS(ko.mapping.toJS(data), selectedData);
    }
    
    self.action_LOCAL_SSH_REMOTE_PROXY_SERVERS_REMOVE = function(selectedData) {
        self.data.REMOTE_PROXY_SERVERS.remove(selectedData);
    }
    
    self.action_LOCAL_SSH_REMOTE_PROXY_SERVERS_REMOVE_ALL = function() {
        self.data.REMOTE_PROXY_SERVERS.removeAll();
    }
    
    self.load_LOCAL_SSH_LOCAL_PROXY_SERVER_KEYS_ADD = function() {
        self.template_LOCAL_SSH_LOCAL_PROXY_SERVER_KEYS(new Template("TEMPLATE_LOCAL_SSH_LOCAL_PROXY_SERVER_KEY", new LOCAL_SSH_LOCAL_PROXY_SERVER_KEYS_ADD_ViewModel(self)));
    }
    
    self.load_LOCAL_SSH_LOCAL_PROXY_SERVER_KEYS_UPDATE = function(data) {
        self.template_LOCAL_SSH_LOCAL_PROXY_SERVER_KEYS(new Template("TEMPLATE_LOCAL_SSH_LOCAL_PROXY_SERVER_KEY", new LOCAL_SSH_LOCAL_PROXY_SERVER_KEYS_UPDATE_ViewModel(self, data)));
    }
    
    self.load_LOCAL_SSH_REMOTE_PROXY_SERVERS_ADD = function() {
        self.template_LOCAL_SSH_REMOTE_PROXY_SERVERS(new Template("TEMPLATE_LOCAL_SSH_REMOTE_PROXY_SERVER", new LOCAL_SSH_REMOTE_PROXY_SERVERS_ADD_ViewModel(self)));
    }
    
    self.load_LOCAL_SSH_REMOTE_PROXY_SERVERS_UPDATE = function(data) {
        self.template_LOCAL_SSH_REMOTE_PROXY_SERVERS(new Template("TEMPLATE_LOCAL_SSH_REMOTE_PROXY_SERVER", new LOCAL_SSH_REMOTE_PROXY_SERVERS_UPDATE_ViewModel(self, data)));
    }
    
    self.template_LOCAL_SSH_LOCAL_PROXY_SERVER_KEYS = ko.observable();
    
    self.load_LOCAL_SSH_LOCAL_PROXY_SERVER_KEYS = function() {
        self.template_LOCAL_SSH_LOCAL_PROXY_SERVER_KEYS(new Template("TEMPLATE_LOCAL_SSH_LOCAL_PROXY_SERVER_KEYS", self));
    }
    
    self.load_LOCAL_SSH_LOCAL_PROXY_SERVER_KEYS();
    
    self.template_LOCAL_SSH_REMOTE_PROXY_SERVERS = ko.observable();
    
    self.load_LOCAL_SSH_REMOTE_PROXY_SERVERS = function() {
        self.template_LOCAL_SSH_REMOTE_PROXY_SERVERS(new Template("TEMPLATE_LOCAL_SSH_REMOTE_PROXY_SERVERS", self));
    }
    
    self.load_LOCAL_SSH_REMOTE_PROXY_SERVERS();
    
    $.ajax({
        "type": "GET",
        "url": "/API",
        "dataType": "JSON",
        "data": {
            "action": "LOCAL_SSH"
        }
    }).then(
        function(data, textStatus, jqXHR) {
            Alertify.log.success("LOCAL SSH - OK");
            
            ko.mapping.fromJS(data, self.data);
        }, 
        function(jqXHR, textStatus, errorThrown) {
            Alertify.log.error("LOCAL SSH - NOT OK");
        }
    );
}

function LOCAL_SSH_LOCAL_PROXY_SERVER_KEYS_ADD_ViewModel(parent) {
    var self = this;
    self.parent = parent;
    self.defaultData = {
        "PUBLIC": 
        {
            "FILE": ""
        },
        "PRIVATE": 
        {
            "FILE": "",
            "PASSPHRASE": ""
        }
    }
    self.data = ko.mapping.fromJS(self.defaultData);
    self.action = "LOCAL_SSH_LOCAL_PROXY_SERVER_KEYS_ADD";
    
    self.action_LOCAL_SSH_LOCAL_PROXY_SERVER_KEYS_ADD = function() {
        self.parent.action_LOCAL_SSH_LOCAL_PROXY_SERVER_KEYS_ADD(self.data);
        self.parent.load_LOCAL_SSH_LOCAL_PROXY_SERVER_KEYS();
    }
    
    self.cancel = function() {
        self.parent.load_LOCAL_SSH_LOCAL_PROXY_SERVER_KEYS();
    }
}

function LOCAL_SSH_LOCAL_PROXY_SERVER_KEYS_UPDATE_ViewModel(parent, selectedData) {
    var self = this;
    self.parent = parent;
    self.selectedData = selectedData;
    self.data = ko.mapping.fromJS(ko.mapping.toJS(self.selectedData));
    self.action = "LOCAL_SSH_LOCAL_PROXY_SERVER_KEYS_UPDATE";
    
    self.action_LOCAL_SSH_LOCAL_PROXY_SERVER_KEYS_UPDATE = function() {
        self.parent.action_LOCAL_SSH_LOCAL_PROXY_SERVER_KEYS_UPDATE(self.selectedData, self.data);
        self.parent.load_LOCAL_SSH_LOCAL_PROXY_SERVER_KEYS();
    }
    
    self.cancel = function() {
        self.parent.load_LOCAL_SSH_LOCAL_PROXY_SERVER_KEYS();
    }
}

function LOCAL_SSH_REMOTE_PROXY_SERVERS_ADD_ViewModel(parent) {
    var self = this;
    self.parent = parent;
    self.defaultData = {
        "ADDRESS": "",
        "PORT": 0,
        "AUTHENTICATION":
        {
            "USERNAME": "",
            "PASSWORD": ""
        },
        "CERTIFICATE": 
        {
            "AUTHENTICATION": 
            {
                "FINGERPRINT": ""
            }
        }
    }
    self.data = ko.mapping.fromJS(self.defaultData);
    self.action = "LOCAL_SSH_REMOTE_PROXY_SERVERS_ADD";
    
    self.action_LOCAL_SSH_REMOTE_PROXY_SERVERS_ADD = function() {
        self.parent.action_LOCAL_SSH_REMOTE_PROXY_SERVERS_ADD(self.data);
        self.parent.load_LOCAL_SSH_REMOTE_PROXY_SERVERS();
    }
    
    self.cancel = function() {
        self.parent.load_LOCAL_SSH_REMOTE_PROXY_SERVERS();
    }
}

function LOCAL_SSH_REMOTE_PROXY_SERVERS_UPDATE_ViewModel(parent, data) {
    var self = this;
    self.parent = parent;
    self.selectedData = data;
    self.data = ko.mapping.fromJS(ko.mapping.toJS(self.selectedData));
    self.action = "LOCAL_SSH_REMOTE_PROXY_SERVERS_UPDATE";
    
    self.action_LOCAL_SSH_REMOTE_PROXY_SERVERS_UPDATE = function() {
        self.parent.action_LOCAL_SSH_REMOTE_PROXY_SERVERS_UPDATE(self.selectedData, self.data);
        self.parent.load_LOCAL_SSH_REMOTE_PROXY_SERVERS();
    }
    
    self.cancel = function() {
        self.parent.load_LOCAL_SSH_REMOTE_PROXY_SERVERS();
    }
}

function LOCAL_WS_ViewModel(parent) {
    var self = this;
    self.parent = parent;
    self.defaultData = {
        "LOGGER":
        {
            "LEVEL": ""
        },
        "LOCAL_PROXY_SERVER":
        {
            "ADDRESS": "",
            "PORT": 0
        },
        "REMOTE_PROXY_SERVERS": [],
        "PROXY_SERVER":
        {
            "TYPE": "",
            "ADDRESS": "",
            "PORT": 0,
            "AUTHENTICATION":
            {
                "USERNAME": "",
                "PASSWORD": ""
            }
        }
    }
    self.data = ko.mapping.fromJS(self.defaultData);
    
    self.action_LOCAL_WS_UPDATE = function() {
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
        
        if($.isNumeric(data.PROXY_SERVER.PORT)) {
            data.PROXY_SERVER.PORT = Number(data.PROXY_SERVER.PORT);
        } else {
            data.PROXY_SERVER.PORT = 0;
        }
        
        $.ajax({
            "type": "POST",
            "url": "/API",
            "dataType": "",
            "data": {
                "action": "LOCAL_WS_UPDATE",
                "data": ko.toJSON(data)
            }
        }).then(
            function(data, textStatus, jqXHR) {
                Alertify.log.success("LOCAL WS - UPDATE OK");
            }, 
            function(jqXHR, textStatus, errorThrown) {
                Alertify.log.error("LOCAL WS - UPDATE NOT OK");
            }
        )
    }
    
    self.action_LOCAL_WS_REMOTE_PROXY_SERVERS_ADD = function(data) {
        self.data.REMOTE_PROXY_SERVERS.push(data);
    }
    
    self.action_LOCAL_WS_REMOTE_PROXY_SERVERS_UPDATE = function(selectedData, data) {
        ko.mapping.fromJS(ko.mapping.toJS(data), selectedData);
    }
    
    self.action_LOCAL_WS_REMOTE_PROXY_SERVERS_REMOVE = function(selectedData) {
        self.data.REMOTE_PROXY_SERVERS.remove(selectedData);
    }
    
    self.action_LOCAL_WS_REMOTE_PROXY_SERVERS_REMOVE_ALL = function() {
        self.data.REMOTE_PROXY_SERVERS.removeAll();
    }
    
    self.load_LOCAL_WS_REMOTE_PROXY_SERVERS_ADD = function() {
        self.template_LOCAL_WS_REMOTE_PROXY_SERVERS(new Template("TEMPLATE_LOCAL_WS_REMOTE_PROXY_SERVER", new LOCAL_WS_REMOTE_PROXY_SERVERS_ADD_ViewModel(self)));
    }
    
    self.load_LOCAL_WS_REMOTE_PROXY_SERVERS_UPDATE = function(data) {
        self.template_LOCAL_WS_REMOTE_PROXY_SERVERS(new Template("TEMPLATE_LOCAL_WS_REMOTE_PROXY_SERVER", new LOCAL_WS_REMOTE_PROXY_SERVERS_UPDATE_ViewModel(self, data)));
    }
    
    self.template_LOCAL_WS_REMOTE_PROXY_SERVERS = ko.observable();
    
    self.load_LOCAL_WS_REMOTE_PROXY_SERVERS = function() {
        self.template_LOCAL_WS_REMOTE_PROXY_SERVERS(new Template("TEMPLATE_LOCAL_WS_REMOTE_PROXY_SERVERS", self));
    }
    
    self.load_LOCAL_WS_REMOTE_PROXY_SERVERS();
    
    $.ajax({
        "type": "GET",
        "url": "/API",
        "dataType": "JSON",
        "data": {
            "action": "LOCAL_WS"
        }
    }).then(
        function(data, textStatus, jqXHR) {
            Alertify.log.success("LOCAL WS - OK");
            
            ko.mapping.fromJS(data, self.data);
        }, 
        function(jqXHR, textStatus, errorThrown) {
            Alertify.log.error("LOCAL WS - NOT OK");
        }
    );
}

function LOCAL_WS_REMOTE_PROXY_SERVERS_ADD_ViewModel(parent) {
    var self = this;
    self.parent = parent;
    self.defaultData = {
        "TYPE": "",
        "ADDRESS": "",
        "PORT": 0,
        "AUTHENTICATION":
        {
            "USERNAME": "",
            "PASSWORD": ""
        },
        "CERTIFICATE":
        {
            "AUTHENTICATION":
            {
                "FILE": ""
            }
        }
    }
    self.data = ko.mapping.fromJS(self.defaultData);
    self.action = "LOCAL_WS_REMOTE_PROXY_SERVERS_ADD";
    
    self.action_LOCAL_WS_REMOTE_PROXY_SERVERS_ADD = function() {
        self.parent.action_LOCAL_WS_REMOTE_PROXY_SERVERS_ADD(self.data);
        self.parent.load_LOCAL_WS_REMOTE_PROXY_SERVERS();
    }
    
    self.cancel = function() {
        self.parent.load_LOCAL_WS_REMOTE_PROXY_SERVERS();
    }
}

function LOCAL_WS_REMOTE_PROXY_SERVERS_UPDATE_ViewModel(parent, data) {
    var self = this;
    self.parent = parent;
    self.selectedData = data;
    self.data = ko.mapping.fromJS(ko.mapping.toJS(self.selectedData));
    self.action = "LOCAL_WS_REMOTE_PROXY_SERVERS_UPDATE";
    
    self.action_LOCAL_WS_REMOTE_PROXY_SERVERS_UPDATE = function() {
        self.parent.action_LOCAL_WS_REMOTE_PROXY_SERVERS_UPDATE(self.selectedData, self.data);
        self.parent.load_LOCAL_WS_REMOTE_PROXY_SERVERS();
    }
    
    self.cancel = function() {
        self.parent.load_LOCAL_WS_REMOTE_PROXY_SERVERS();
    }
}

function REMOTE_WS_ViewModel(parent) {
    var self = this;
    self.parent = parent;
    self.defaultData = {
        "LOGGER":
        {
            "LEVEL": "DEBUG"
        },
        "REMOTE_PROXY_SERVER":
        {
            "TYPE": "",
            "ADDRESS": "",
            "PORT": 0,
            "AUTHENTICATION": [],
            "CERTIFICATE":
            {
                "KEY":
                {
                    "FILE": ""
                },
                "FILE": ""
            }
        }
    }
    self.data = ko.mapping.fromJS(self.defaultData);
    
    self.action_REMOTE_WS_UPDATE = function() {
        var data = ko.mapping.toJS(self.data);
        
        if($.isNumeric(data.REMOTE_PROXY_SERVER.PORT)) {
            data.REMOTE_PROXY_SERVER.PORT = Number(data.REMOTE_PROXY_SERVER.PORT);
        } else {
            data.REMOTE_PROXY_SERVER.PORT = 0;
        }
        
        $.ajax({
            "type": "POST",
            "url": "/API",
            "dataType": "",
            "data": {
                "action": "REMOTE_WS_UPDATE",
                "data": ko.toJSON(data)
            }
        }).then(
            function(data, textStatus, jqXHR) {
                Alertify.log.success("REMOTE WS - UPDATE OK");
            }, 
            function(jqXHR, textStatus, errorThrown) {
                Alertify.log.error("REMOTE WS - UPDATE NOT OK");
            }
        )
    }
    
    self.action_REMOTE_WS_REMOTE_PROXY_SERVER_AUTHENTICATIONS_ADD = function(data) {
        self.data.REMOTE_PROXY_SERVER.AUTHENTICATION.push(data);
    }
    
    self.action_REMOTE_WS_REMOTE_PROXY_SERVER_AUTHENTICATIONS_UPDATE = function(selectedData, data) {
        ko.mapping.fromJS(ko.mapping.toJS(data), selectedData);
    }
    
    self.action_REMOTE_WS_REMOTE_PROXY_SERVER_AUTHENTICATIONS_REMOVE = function(selectedData) {
        self.data.REMOTE_PROXY_SERVER.AUTHENTICATION.remove(selectedData);
    }
    
    self.action_REMOTE_WS_REMOTE_PROXY_SERVER_AUTHENTICATIONS_REMOVE_ALL = function() {
        self.data.REMOTE_PROXY_SERVER.AUTHENTICATION.removeAll();
    }
    
    self.load_REMOTE_WS_REMOTE_PROXY_SERVER_AUTHENTICATIONS_ADD = function() {
        self.template_REMOTE_WS_REMOTE_PROXY_SERVER_AUTHENTICATIONS(new Template("TEMPLATE_REMOTE_WS_REMOTE_PROXY_SERVER_AUTHENTICATION", new REMOTE_WS_REMOTE_PROXY_SERVER_AUTHENTICATIONS_ADD_ViewModel(self)));
    }
    
    self.load_REMOTE_WS_REMOTE_PROXY_SERVER_AUTHENTICATIONS_UPDATE = function(data) {
        self.template_REMOTE_WS_REMOTE_PROXY_SERVER_AUTHENTICATIONS(new Template("TEMPLATE_REMOTE_WS_REMOTE_PROXY_SERVER_AUTHENTICATION", new REMOTE_WS_REMOTE_PROXY_SERVER_AUTHENTICATIONS_UPDATE_ViewModel(self, data)));
    }
    
    self.template_REMOTE_WS_REMOTE_PROXY_SERVER_AUTHENTICATIONS = ko.observable();
    
    self.load_REMOTE_WS_REMOTE_PROXY_SERVER_AUTHENTICATIONS = function() {
        self.template_REMOTE_WS_REMOTE_PROXY_SERVER_AUTHENTICATIONS(new Template("TEMPLATE_REMOTE_WS_REMOTE_PROXY_SERVER_AUTHENTICATIONS", self));
    }
    
    self.load_REMOTE_WS_REMOTE_PROXY_SERVER_AUTHENTICATIONS();
    
    $.ajax({
        "type": "GET",
        "url": "/API",
        "dataType": "JSON",
        "data": {
            "action": "REMOTE_WS"
        }
    }).then(
        function(data, textStatus, jqXHR) {
            Alertify.log.success("REMOTE WS - OK");
            
            ko.mapping.fromJS(data, self.data);
        }, 
        function(jqXHR, textStatus, errorThrown) {
            Alertify.log.error("REMOTE WS - NOT OK");
        }
    );
}

function REMOTE_WS_REMOTE_PROXY_SERVER_AUTHENTICATIONS_ADD_ViewModel(parent) {
    var self = this;
    self.parent = parent;
    self.defaultData = {
        "USERNAME": "",
        "PASSWORD": ""
    }
    self.data = ko.mapping.fromJS(self.defaultData);
    self.action = "REMOTE_WS_REMOTE_PROXY_SERVER_AUTHENTICATIONS_ADD";
    
    self.action_REMOTE_WS_REMOTE_PROXY_SERVER_AUTHENTICATIONS_ADD = function() {
        self.parent.action_REMOTE_WS_REMOTE_PROXY_SERVER_AUTHENTICATIONS_ADD(self.data);
        self.parent.load_REMOTE_WS_REMOTE_PROXY_SERVER_AUTHENTICATIONS();
    }
    
    self.cancel = function() {
        self.parent.load_REMOTE_WS_REMOTE_PROXY_SERVER_AUTHENTICATIONS();
    }
}

function REMOTE_WS_REMOTE_PROXY_SERVER_AUTHENTICATIONS_UPDATE_ViewModel(parent, data) {
    var self = this;
    self.parent = parent;
    self.selectedData = data;
    self.data = ko.mapping.fromJS(ko.mapping.toJS(self.selectedData));
    self.action = "REMOTE_WS_REMOTE_PROXY_SERVER_AUTHENTICATIONS_UPDATE";
    
    self.action_REMOTE_WS_REMOTE_PROXY_SERVER_AUTHENTICATIONS_UPDATE = function() {
        self.parent.action_REMOTE_WS_REMOTE_PROXY_SERVER_AUTHENTICATIONS_UPDATE(self.selectedData, self.data);
        self.parent.load_REMOTE_WS_REMOTE_PROXY_SERVER_AUTHENTICATIONS();
    }
    
    self.cancel = function() {
        self.parent.load_REMOTE_WS_REMOTE_PROXY_SERVER_AUTHENTICATIONS();
    }
}

function ViewModel() {
    var self = this;
    
    self.action_LOCAL_START = function() {
        $.ajax({
            "type": "POST",
            "url": "/API",
            "dataType": "",
            "data": {
                "action": "LOCAL_START"
            }
        }).then(
            function(data, textStatus, jqXHR) {
                Alertify.log.success("LOCAL - START OK");
            }, 
            function(jqXHR, textStatus, errorThrown) {
                Alertify.log.error("LOCAL - START NOT OK");
            }
        )
    }
    
    self.action_LOCAL_STOP = function() {
        $.ajax({
            "type": "POST",
            "url": "/API",
            "dataType": "",
            "data": {
                "action": "LOCAL_STOP"
            }
        }).then(
            function(data, textStatus, jqXHR) {
                Alertify.log.success("LOCAL - STOP OK");
            }, 
            function(jqXHR, textStatus, errorThrown) {
                Alertify.log.error("LOCAL - STOP NOT OK");
            }
        )
    }
    
    self.action_LOCAL_SSH_START = function() {
        $.ajax({
            "type": "POST",
            "url": "/API",
            "dataType": "",
            "data": {
                "action": "LOCAL_SSH_START"
            }
        }).then(
            function(data, textStatus, jqXHR) {
                Alertify.log.success("LOCAL SSH - START OK");
            }, 
            function(jqXHR, textStatus, errorThrown) {
                Alertify.log.error("LOCAL SSH - START NOT OK");
            }
        )
    }
    
    self.action_LOCAL_SSH_STOP = function() {
        $.ajax({
            "type": "POST",
            "url": "/API",
            "dataType": "",
            "data": {
                "action": "LOCAL_SSH_STOP"
            }
        }).then(
            function(data, textStatus, jqXHR) {
                Alertify.log.success("LOCAL SSH - STOP OK");
            }, 
            function(jqXHR, textStatus, errorThrown) {
                Alertify.log.error("LOCAL SSH - STOP NOT OK");
            }
        )
    }
    
    self.action_LOCAL_WS_START = function() {
        $.ajax({
            "type": "POST",
            "url": "/API",
            "dataType": "",
            "data": {
                "action": "LOCAL_WS_START"
            }
        }).then(
            function(data, textStatus, jqXHR) {
                Alertify.log.success("LOCAL WS - START OK");
            }, 
            function(jqXHR, textStatus, errorThrown) {
                Alertify.log.error("LOCAL WS - START NOT OK");
            }
        )
    }
    
    self.action_LOCAL_WS_STOP = function() {
        $.ajax({
            "type": "POST",
            "url": "/API",
            "dataType": "",
            "data": {
                "action": "LOCAL_WS_STOP"
            }
        }).then(
            function(data, textStatus, jqXHR) {
                Alertify.log.success("LOCAL WS - STOP OK");
            }, 
            function(jqXHR, textStatus, errorThrown) {
                Alertify.log.error("LOCAL WS - STOP NOT OK");
            }
        )
    }
    
    self.action_REMOTE_WS_START = function() {
        $.ajax({
            "type": "POST",
            "url": "/API",
            "dataType": "",
            "data": {
                "action": "REMOTE_WS_START"
            }
        }).then(
            function(data, textStatus, jqXHR) {
                Alertify.log.success("REMOTE WS - START OK");
            }, 
            function(jqXHR, textStatus, errorThrown) {
                Alertify.log.error("REMOTE WS - START NOT OK");
            }
        )
    }
    
    self.action_REMOTE_WS_STOP = function() {
        $.ajax({
            "type": "POST",
            "url": "/API",
            "dataType": "",
            "data": {
                "action": "REMOTE_WS_STOP"
            }
        }).then(
            function(data, textStatus, jqXHR) {
                Alertify.log.success("REMOTE WS - STOP OK");
            }, 
            function(jqXHR, textStatus, errorThrown) {
                Alertify.log.error("REMOTE WS - STOP NOT OK");
            }
        )
    }
    
    self.template_LOCAL = ko.observable();
    
    self.load_LOCAL = function() {
        self.template_LOCAL(new Template("TEMPLATE_LOCAL", new LOCAL_ViewModel(self)));
    }
    
    self.load_LOCAL();
    
    self.template_LOCAL_SSH = ko.observable();
    
    self.load_LOCAL_SSH = function() {
        self.template_LOCAL_SSH(new Template("TEMPLATE_LOCAL_SSH", new LOCAL_SSH_ViewModel(self)));
    }
    
    self.load_LOCAL_SSH();
    
    self.template_LOCAL_WS = ko.observable();
    
    self.load_LOCAL_WS = function() {
        self.template_LOCAL_WS(new Template("TEMPLATE_LOCAL_WS", new LOCAL_WS_ViewModel(self)));
    }
    
    self.load_LOCAL_WS();
    
    self.template_REMOTE_WS = ko.observable();
    
    self.load_REMOTE_WS = function() {
        self.template_REMOTE_WS(new Template("TEMPLATE_REMOTE_WS", new REMOTE_WS_ViewModel(self)));
    }
    
    self.load_REMOTE_WS();
}

ko.applyBindings(new ViewModel());