set SEVENZIP_HOME="C:\Program Files\7-Zip"
set PYINSTALLER_HOME="C:\pyinstaller-2.0"
set JAP_WS_LOCAL_NODE_VERSION=2.0.0-SNAPSHOT
if exist MAKE rmdir MAKE /s /q
mkdir MAKE
cd MAKE
rem JAP_WS_LOCAL_NODE
mkdir JAP_WS_LOCAL_NODE-%JAP_WS_LOCAL_NODE_VERSION%
cd JAP_WS_LOCAL_NODE-%JAP_WS_LOCAL_NODE_VERSION%
copy ..\..\JAP_WS_LOCAL.bat JAP_WS_LOCAL.bat
copy ..\..\JAP_WS_LOCAL.js JAP_WS_LOCAL.js
copy ..\..\JAP_WS_LOCAL.json JAP_WS_LOCAL.json
copy ..\..\CA.pem CA.pem
copy ..\..\NM.bat NM.bat
copy ..\..\README.txt README.txt
mkdir JAP
cd JAP
copy ..\..\..\JAP\TUNNEL.js TUNNEL.js
copy ..\..\..\JAP\JAP_WS_LOCAL.js JAP_WS_LOCAL.js
cd ..
cd ..
%SEVENZIP_HOME%\7z.exe a -tzip JAP_WS_LOCAL_NODE-%JAP_WS_LOCAL_NODE_VERSION%.zip JAP_WS_LOCAL_NODE-%JAP_WS_LOCAL_NODE_VERSION%
cd ..