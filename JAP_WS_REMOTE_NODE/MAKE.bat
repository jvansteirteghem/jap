set SEVENZIP_HOME="C:\Program Files\7-Zip"
set PYINSTALLER_HOME="C:\pyinstaller-2.0"
set JAP_WS_REMOTE_NODE_VERSION=2.0.0-SNAPSHOT
set JAP_WS_REMOTE_NODE_DOTCLOUD_VERSION=2.0.0-SNAPSHOT
if exist MAKE rmdir MAKE /s /q
mkdir MAKE
cd MAKE
rem JAP_WS_REMOTE_NODE
mkdir JAP_WS_REMOTE_NODE-%JAP_WS_REMOTE_NODE_VERSION%
cd JAP_WS_REMOTE_NODE-%JAP_WS_REMOTE_NODE_VERSION%
copy ..\..\JAP_WS_REMOTE.bat JAP_WS_REMOTE.bat
copy ..\..\JAP_WS_REMOTE.js JAP_WS_REMOTE.js
copy ..\..\JAP_WS_REMOTE.json JAP_WS_REMOTE.json
copy ..\..\C.bat C.bat
copy ..\..\C.ini C.ini
copy ..\..\C.pem C.pem
copy ..\..\CA.bat CA.bat
copy ..\..\CA.ini CA.ini
copy ..\..\CA.pem CA.pem
copy ..\..\CA.srl CA.srl
copy ..\..\CAK.pem CAK.pem
copy ..\..\CK.pem CK.pem
copy ..\..\CR.pem CR.pem
copy ..\..\NM.bat NM.bat
copy ..\..\README.txt README.txt
mkdir JAP
cd JAP
copy ..\..\..\JAP\JAP_WS_REMOTE.js JAP_WS_REMOTE.js
cd ..
cd ..
%SEVENZIP_HOME%\7z.exe a -tzip JAP_WS_REMOTE_NODE-%JAP_WS_REMOTE_NODE_VERSION%.zip JAP_WS_REMOTE_NODE-%JAP_WS_REMOTE_NODE_VERSION%
rem JAP_WS_REMOTE_NODE_DOTCLOUD
mkdir JAP_WS_REMOTE_NODE_DOTCLOUD-%JAP_WS_REMOTE_NODE_DOTCLOUD_VERSION%
cd JAP_WS_REMOTE_NODE_DOTCLOUD-%JAP_WS_REMOTE_NODE_DOTCLOUD_VERSION%
copy ..\..\JAP_WS_REMOTE_NODE_DOTCLOUD\dotcloud.yml dotcloud.yml
copy ..\..\JAP_WS_REMOTE_NODE_DOTCLOUD\JAP_WS_REMOTE.js JAP_WS_REMOTE.js
copy ..\..\JAP_WS_REMOTE_NODE_DOTCLOUD\JAP_WS_REMOTE.json JAP_WS_REMOTE.json
copy ..\..\JAP_WS_REMOTE_NODE_DOTCLOUD\package.json package.json
copy ..\..\JAP_WS_REMOTE_NODE_DOTCLOUD\Procfile Procfile
copy ..\..\JAP_WS_REMOTE_NODE_DOTCLOUD\README.txt README.txt
copy ..\..\JAP_WS_REMOTE_NODE_DOTCLOUD\supervisord.conf supervisord.conf
mkdir JAP
cd JAP
copy ..\..\..\JAP\JAP_WS_REMOTE.js JAP_WS_REMOTE.js
cd ..
cd ..
%SEVENZIP_HOME%\7z.exe a -tzip JAP_WS_REMOTE_NODE_DOTCLOUD-%JAP_WS_REMOTE_NODE_DOTCLOUD_VERSION%.zip JAP_WS_REMOTE_NODE_DOTCLOUD-%JAP_WS_REMOTE_NODE_DOTCLOUD_VERSION%
cd ..