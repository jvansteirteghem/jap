PRE-INSTALLATION
----------------
- create OPENSHIFT account
- install OPENSHIFT CLI

INSTALLATION
------------
- unzip JAP_REMOTE_WS_NODE_OPENSHIFT-X.X.X.zip
- open JAP_REMOTE_WS_NODE_OPENSHIFT-X.X.X
- configure JAP_REMOTE_WS.json
- open CONSOLE
    - rhc app create -a application-id -t diy-0.1
    - cd application-id
    - xcopy ..\JAP_REMOTE_WS_NODE_OPENSHIFT-X.X.X\*.* /s /y
    - git update-index --add --chmod=+x .openshift/action_hooks/build
    - git update-index --add --chmod=+x .openshift/action_hooks/deploy
    - git update-index --add --chmod=+x .openshift/action_hooks/post_deploy
    - git update-index --add --chmod=+x .openshift/action_hooks/pre_build
    - git update-index --add --chmod=+x .openshift/action_hooks/start
    - git update-index --add --chmod=+x .openshift/action_hooks/stop
    - git add -A
    - git commit -m "JAP"
    - git push

IMPORTANT
---------
OPENSHIFT WEBSOCKET protocol support is EXPERIMENTAL
- WEBSOCKET protocol over HTTP
	- JAP_REMOTE_WS
		- configure JAP_REMOTE_WS.json
			- REMOTE_PROXY_SERVER/TYPE = HTTP
	- JAP_LOCAL_WS
		- configure JAP_LOCAL_WS.json
			- REMOTE_PROXY_SERVERS/TYPE = HTTP
			- REMOTE_PROXY_SERVERS/ADDRESS = YYY-ZZZ.rhcloud.com
			- REMOTE_PROXY_SERVERS/PORT = 8000
- WEBSOCKET protocol over HTTPS
	- JAP_REMOTE_WS
		- configure JAP_REMOTE_WS.json
			- REMOTE_PROXY_SERVER/TYPE = HTTPS
	- JAP_LOCAL_WS
		- configure JAP_LOCAL_WS.json
			- REMOTE_PROXY_SERVERS/TYPE = HTTPS
			- REMOTE_PROXY_SERVERS/ADDRESS = YYY-ZZZ.rhcloud.com
			- REMOTE_PROXY_SERVERS/PORT = 8443