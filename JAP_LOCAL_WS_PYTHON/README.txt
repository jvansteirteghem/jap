PRE-INSTALLATION
----------------
- install PYTHON >= 2.7.0
- install TWISTED
- install PYOPENSSL
- install AUTOBAHN

INSTALLATION
------------
- unzip JAP_LOCAL_WS_PYTHON-X.X.X.zip
- open JAP_LOCAL_WS_PYTHON-X.X.X
- configure JAP_LOCAL_WS.json
- execute JAP_LOCAL_WS.bat
- open
	- FIREFOX
		- configure PROXY SERVER
			- click TOOLS, OPTIONS
			- click ADVANCED, NETWORK, SETTINGS
			- check MANUAL PROXY CONFIGURATION
			- in SOCKS write 127.0.0.1 and LOCAL_PROXY_SERVER.PORT
			- check SOCKS v5
			- click OK
			- click OK
		- configure PROXY SERVER DNS
			- open about:config
			- click I'LL BE CAREFUL, I PROMISE!
			- set NETWORK.PROXY.SOCKS_REMOTE_DNS to TRUE
			- close

IMPORTANT
---------