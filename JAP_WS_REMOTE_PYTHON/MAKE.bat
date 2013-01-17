set SEVENZIP_HOME="C:\Program Files\7-Zip"
set PYINSTALLER_HOME="C:\pyinstaller-2.0"
set JAP_WS_REMOTE_PYTHON_VERSION=2.0.0-SNAPSHOT-2
set JAP_WS_REMOTE_PYTHON_DOTCLOUD_VERSION=2.0.0-SNAPSHOT-3
set JAP_WS_REMOTE_PYTHON_OPENSHIFT_VERSION=2.0.0-SNAPSHOT-3
set JAP_WS_REMOTE_PYTHON_WINDOWS_VERSION=2.0.0-SNAPSHOT-2
if exist MAKE rmdir MAKE /s /q
mkdir MAKE
cd MAKE
rem JAP_WS_REMOTE_PYTHON
mkdir JAP_WS_REMOTE_PYTHON-%JAP_WS_REMOTE_PYTHON_VERSION%
cd JAP_WS_REMOTE_PYTHON-%JAP_WS_REMOTE_PYTHON_VERSION%
copy ..\..\JAP_WS_REMOTE.bat JAP_WS_REMOTE.bat
copy ..\..\JAP_WS_REMOTE.json JAP_WS_REMOTE.json
copy ..\..\JAP_WS_REMOTE.py JAP_WS_REMOTE.py
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
copy ..\..\README.txt README.txt
mkdir JAP
cd JAP
copy ..\..\..\JAP\__init__.py __init__.py
copy ..\..\..\JAP\JAP_WS_REMOTE.py JAP_WS_REMOTE.py
cd ..
cd ..
%SEVENZIP_HOME%\7z.exe a -tzip JAP_WS_REMOTE_PYTHON-%JAP_WS_REMOTE_PYTHON_VERSION%.zip JAP_WS_REMOTE_PYTHON-%JAP_WS_REMOTE_PYTHON_VERSION%
rem JAP_WS_REMOTE_PYTHON_DOTCLOUD
mkdir JAP_WS_REMOTE_PYTHON_DOTCLOUD-%JAP_WS_REMOTE_PYTHON_DOTCLOUD_VERSION%
cd JAP_WS_REMOTE_PYTHON_DOTCLOUD-%JAP_WS_REMOTE_PYTHON_DOTCLOUD_VERSION%
copy ..\..\JAP_WS_REMOTE_PYTHON_DOTCLOUD\dotcloud.yml dotcloud.yml
copy ..\..\JAP_WS_REMOTE_PYTHON_DOTCLOUD\JAP_WS_REMOTE.json JAP_WS_REMOTE.json
copy ..\..\JAP_WS_REMOTE_PYTHON_DOTCLOUD\JAP_WS_REMOTE.py JAP_WS_REMOTE.py
copy ..\..\JAP_WS_REMOTE_PYTHON_DOTCLOUD\README.txt README.txt
copy ..\..\JAP_WS_REMOTE_PYTHON_DOTCLOUD\requirements.txt requirements.txt
mkdir JAP
cd JAP
copy ..\..\..\JAP\__init__.py __init__.py
copy ..\..\..\JAP\JAP_WS_REMOTE.py JAP_WS_REMOTE.py
cd ..
cd ..
%SEVENZIP_HOME%\7z.exe a -tzip JAP_WS_REMOTE_PYTHON_DOTCLOUD-%JAP_WS_REMOTE_PYTHON_DOTCLOUD_VERSION%.zip JAP_WS_REMOTE_PYTHON_DOTCLOUD-%JAP_WS_REMOTE_PYTHON_DOTCLOUD_VERSION%
rem JAP_WS_REMOTE_PYTHON_OPENSHIFT
mkdir JAP_WS_REMOTE_PYTHON_OPENSHIFT-%JAP_WS_REMOTE_PYTHON_OPENSHIFT_VERSION%
cd JAP_WS_REMOTE_PYTHON_OPENSHIFT-%JAP_WS_REMOTE_PYTHON_OPENSHIFT_VERSION%
copy ..\..\JAP_WS_REMOTE_PYTHON_OPENSHIFT\app.tac app.tac
copy ..\..\JAP_WS_REMOTE_PYTHON_OPENSHIFT\JAP_WS_REMOTE.json JAP_WS_REMOTE.json
copy ..\..\JAP_WS_REMOTE_PYTHON_OPENSHIFT\README.txt README.txt
copy ..\..\JAP_WS_REMOTE_PYTHON_OPENSHIFT\requirements.txt requirements.txt
mkdir JAP
cd JAP
copy ..\..\..\JAP\__init__.py __init__.py
copy ..\..\..\JAP\JAP_WS_REMOTE.py JAP_WS_REMOTE.py
cd ..
mkdir .openshift
cd .openshift
mkdir action_hooks
cd action_hooks
copy ..\..\..\..\JAP_WS_REMOTE_PYTHON_OPENSHIFT\.openshift\action_hooks\build build
copy ..\..\..\..\JAP_WS_REMOTE_PYTHON_OPENSHIFT\.openshift\action_hooks\deploy deploy
copy ..\..\..\..\JAP_WS_REMOTE_PYTHON_OPENSHIFT\.openshift\action_hooks\post_deploy post_deploy
copy ..\..\..\..\JAP_WS_REMOTE_PYTHON_OPENSHIFT\.openshift\action_hooks\pre_build pre_build
copy ..\..\..\..\JAP_WS_REMOTE_PYTHON_OPENSHIFT\.openshift\action_hooks\start start
copy ..\..\..\..\JAP_WS_REMOTE_PYTHON_OPENSHIFT\.openshift\action_hooks\stop stop
copy ..\..\..\..\JAP_WS_REMOTE_PYTHON_OPENSHIFT\.openshift\action_hooks\vars vars
cd ..
cd ..
cd ..
%SEVENZIP_HOME%\7z.exe a -tzip JAP_WS_REMOTE_PYTHON_OPENSHIFT-%JAP_WS_REMOTE_PYTHON_OPENSHIFT_VERSION%.zip JAP_WS_REMOTE_PYTHON_OPENSHIFT-%JAP_WS_REMOTE_PYTHON_OPENSHIFT_VERSION%
rem JAP_WS_REMOTE_PYTHON_WINDOWS
mkdir PYINSTALLER
cd PYINSTALLER
python %PYINSTALLER_HOME%\pyinstaller.py -c -F ..\..\JAP_WS_REMOTE.py
cd ..
mkdir JAP_WS_REMOTE_PYTHON_WINDOWS-%JAP_WS_REMOTE_PYTHON_WINDOWS_VERSION%
cd JAP_WS_REMOTE_PYTHON_WINDOWS-%JAP_WS_REMOTE_PYTHON_WINDOWS_VERSION%
copy ..\PYINSTALLER\dist\JAP_WS_REMOTE.exe JAP_WS_REMOTE.exe
copy ..\..\JAP_WS_REMOTE_PYTHON_WINDOWS\JAP_WS_REMOTE.bat JAP_WS_REMOTE.bat
copy ..\..\JAP_WS_REMOTE_PYTHON_WINDOWS\README.txt README.txt
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
cd ..
%SEVENZIP_HOME%\7z.exe a -tzip JAP_WS_REMOTE_PYTHON_WINDOWS-%JAP_WS_REMOTE_PYTHON_WINDOWS_VERSION%.zip JAP_WS_REMOTE_PYTHON_WINDOWS-%JAP_WS_REMOTE_PYTHON_WINDOWS_VERSION%
cd ..