PRE-INSTALLATION
----------------
- create OPENSHIFT account
- install OPENSHIFT CLI

INSTALLATION
------------
- unzip JAP_WS_REMOTE_PYTHON_OPENSHIFT-X.X.X.zip
- open JAP_WS_REMOTE_PYTHON_OPENSHIFT-X.X.X
- configure JAP_WS_REMOTE.json
- open CONSOLE
	- WINDOWS
		- rhc app create -a application-id -t diy-0.1
		- cd application-id
		- xcopy ..\JAP_WS_REMOTE_PYTHON_OPENSHIFT-X.X.X\*.* /s /y
		- git add -A
		- git commit -m "JAP"
		- git push
	- LINUX
		- rhc app create -a application-id -t diy-0.1
		- cd application-id
		- cp -r ../JAP_WS_REMOTE_PYTHON_OPENSHIFT-X.X.X/* .
		- chmod -R +x ./.openshift/action_hooks
		- git add -A
		- git commit -m "JAP"
		- git push

IMPORTANT
---------
OPENSHIFT WEBSOCKET protocol support is EXPERIMENTAL
- WEBSOCKET protocol over HTTP
	- JAP_WS_REMOTE
		- configure JAP_WS_REMOTE.json
			- REMOTE_PROXY_SERVER/TYPE = HTTP
	- JAP_WS_LOCAL
		- configure JAP_WS_LOCAL.json
			- REMOTE_PROXY_SERVERS/TYPE = HTTP
			- REMOTE_PROXY_SERVERS/ADDRESS = YYY-ZZZ.rhcloud.com
			- REMOTE_PROXY_SERVERS/PORT = 8000
- WEBSOCKET protocol over HTTPS
	- JAP_WS_REMOTE
		- configure JAP_WS_REMOTE.json
			- REMOTE_PROXY_SERVER/TYPE = HTTPS
	- JAP_WS_LOCAL
		- download certificate (XXX.rhcloud.com)
			- open FIREFOX
			- open https://YYY-ZZZ.rhcloud.com:8443
			- click I UNDERSTAND THE RISKS
			- click ADD EXCEPTION
			- click VIEW
			- click DETAILS
			- click EXPORT
			- open JAP_WS_LOCAL
			- click SAVE
		- configure JAP_WS_LOCAL.json
			- REMOTE_PROXY_SERVERS/TYPE = HTTPS
			- REMOTE_PROXY_SERVERS/ADDRESS = YYY-ZZZ.rhcloud.com
			- REMOTE_PROXY_SERVERS/PORT = 8443
			- REMOTE_PROXY_SERVERS/CERTIFICATE/AUTHENTICATION/FILE = XXX.rhcloud.com