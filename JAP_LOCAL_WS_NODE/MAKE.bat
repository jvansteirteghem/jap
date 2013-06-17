set SEVENZIP_HOME="C:\Program Files\7-Zip"
set JAP_LOCAL_WS_NODE_VERSION=3.0.0-SNAPSHOT
if exist MAKE rmdir MAKE /s /q
mkdir MAKE
cd MAKE
rem JAP_LOCAL_WS_NODE
mkdir JAP_LOCAL_WS_NODE-%JAP_LOCAL_WS_NODE_VERSION%
cd JAP_LOCAL_WS_NODE-%JAP_LOCAL_WS_NODE_VERSION%
copy ..\..\JAP_LOCAL_WS.bat JAP_LOCAL_WS.bat
copy ..\..\JAP_LOCAL_WS.js JAP_LOCAL_WS.js
copy ..\..\JAP_LOCAL_WS.json JAP_LOCAL_WS.json
copy ..\..\CA.pem CA.pem
copy ..\..\CA_DEFAULT.pem CA_DEFAULT.pem
copy ..\..\NM.bat NM.bat
copy ..\..\README.txt README.txt
mkdir JAP
cd JAP
copy ..\..\..\JAP\JAP_LOCAL_WS.js JAP_LOCAL_WS.js
cd ..
cd ..
%SEVENZIP_HOME%\7z.exe a -tzip JAP_LOCAL_WS_NODE-%JAP_LOCAL_WS_NODE_VERSION%.zip JAP_LOCAL_WS_NODE-%JAP_LOCAL_WS_NODE_VERSION%
cd ..