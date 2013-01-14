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
	- rhc app create -a application-id -t diy-0.1
	- cd application-id
	- xcopy ..\JAP_WS_REMOTE_PYTHON_OPENSHIFT-X.X.X\*.* /s
	- git add -A
	- git commit -m "JAP"
	- git push

IMPORTANT
---------
OPENSHIFT websockets:
- HTTP port=8000
- HTTPS port=8443