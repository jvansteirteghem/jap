PRE-INSTALLATION
----------------
- create HEROKU account
- install HEROKU CLI

INSTALLATION
------------
- unzip JAP_REMOTE_WS_NODE_HEROKU-X.X.X.zip
- open JAP_REMOTE_WS_NODE_HEROKU-X.X.X
- configure JAP_REMOTE_WS.json
- open CONSOLE
	- cd JAP_REMOTE_WS_NODE_HEROKU-X.X.X
	- heroku login
	- git init
	- git add .
	- git commit -m "init"
	- heroku create --stack cedar
	- heroku labs:enable websockets
	- git push heroku master

IMPORTANT
---------