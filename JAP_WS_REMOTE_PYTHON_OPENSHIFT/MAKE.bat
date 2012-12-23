set SEVENZIP_HOME="C:\Program Files\7-Zip"
set PYINSTALLER_HOME="C:\pyinstaller-2.0"
set VERSION=2.0.0-SNAPSHOT
if exist MAKE rmdir MAKE /s /q
mkdir MAKE
cd MAKE
mkdir JAP_WS_REMOTE_PYTHON_OPENSHIFT-%VERSION%
cd JAP_WS_REMOTE_PYTHON_OPENSHIFT-%VERSION%
copy ..\..\app.tac app.tac
copy ..\..\JAP_WS_REMOTE.json JAP_WS_REMOTE.json
copy ..\..\JAP_WS_REMOTE.py JAP_WS_REMOTE.py
copy ..\..\README.txt README.txt
copy ..\..\requirements.txt requirements.txt
mkdir JAP
cd JAP
copy ..\..\..\JAP\__init__.py __init__.py
copy ..\..\..\JAP\JAP_WS_REMOTE.py JAP_WS_REMOTE.py
cd ..
mkdir .openshift
cd .openshift
mkdir action_hooks
cd action_hooks
copy ..\..\..\..\.openshift\action_hooks\build build
copy ..\..\..\..\.openshift\action_hooks\deploy deploy
copy ..\..\..\..\.openshift\action_hooks\post_deploy post_deploy
copy ..\..\..\..\.openshift\action_hooks\pre_build pre_build
copy ..\..\..\..\.openshift\action_hooks\start start
copy ..\..\..\..\.openshift\action_hooks\stop stop
copy ..\..\..\..\.openshift\action_hooks\vars vars
cd ..
cd ..
cd ..
%SEVENZIP_HOME%\7z.exe a -tzip JAP_WS_REMOTE_PYTHON_OPENSHIFT-%VERSION%.zip JAP_WS_REMOTE_PYTHON_OPENSHIFT-%VERSION%
cd ..