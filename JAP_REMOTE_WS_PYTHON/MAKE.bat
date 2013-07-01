set SEVENZIP_HOME="C:\Program Files\7-Zip"
set PYINSTALLER_HOME="C:\pyinstaller-SNAPSHOT"
set JAP_REMOTE_WS_PYTHON_VERSION=3.0.0-SNAPSHOT-2
set JAP_REMOTE_WS_PYTHON_OPENSHIFT_VERSION=3.0.0-SNAPSHOT-2
set JAP_REMOTE_WS_PYTHON_WINDOWS_VERSION=3.0.0-SNAPSHOT-2
if exist MAKE rmdir MAKE /s /q
mkdir MAKE
cd MAKE
rem JAP_REMOTE_WS_PYTHON
mkdir JAP_REMOTE_WS_PYTHON-%JAP_REMOTE_WS_PYTHON_VERSION%
cd JAP_REMOTE_WS_PYTHON-%JAP_REMOTE_WS_PYTHON_VERSION%
copy ..\..\JAP_REMOTE_WS.bat JAP_REMOTE_WS.bat
copy ..\..\JAP_REMOTE_WS.json JAP_REMOTE_WS.json
copy ..\..\JAP_REMOTE_WS.py JAP_REMOTE_WS.py
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
copy ..\..\H.txt H.txt
copy ..\..\README.txt README.txt
mkdir JAP
cd JAP
copy ..\..\..\JAP\__init__.py __init__.py
copy ..\..\..\JAP\JAP_LOCAL.py JAP_LOCAL.py
copy ..\..\..\JAP\JAP_REMOTE_WS.py JAP_REMOTE_WS.py
cd ..
cd ..
%SEVENZIP_HOME%\7z.exe a -tzip JAP_REMOTE_WS_PYTHON-%JAP_REMOTE_WS_PYTHON_VERSION%.zip JAP_REMOTE_WS_PYTHON-%JAP_REMOTE_WS_PYTHON_VERSION%
rem JAP_REMOTE_WS_PYTHON_OPENSHIFT
mkdir JAP_REMOTE_WS_PYTHON_OPENSHIFT-%JAP_REMOTE_WS_PYTHON_OPENSHIFT_VERSION%
cd JAP_REMOTE_WS_PYTHON_OPENSHIFT-%JAP_REMOTE_WS_PYTHON_OPENSHIFT_VERSION%
copy ..\..\JAP_REMOTE_WS_PYTHON_OPENSHIFT\app.tac app.tac
copy ..\..\JAP_REMOTE_WS_PYTHON_OPENSHIFT\JAP_REMOTE_WS.json JAP_REMOTE_WS.json
copy ..\..\JAP_REMOTE_WS_PYTHON_OPENSHIFT\README.txt README.txt
copy ..\..\JAP_REMOTE_WS_PYTHON_OPENSHIFT\requirements.txt requirements.txt
mkdir JAP
cd JAP
copy ..\..\..\JAP\__init__.py __init__.py
copy ..\..\..\JAP\JAP_LOCAL.py JAP_LOCAL.py
copy ..\..\..\JAP\JAP_REMOTE_WS.py JAP_REMOTE_WS.py
cd ..
mkdir .openshift
cd .openshift
mkdir action_hooks
cd action_hooks
copy ..\..\..\..\JAP_REMOTE_WS_PYTHON_OPENSHIFT\.openshift\action_hooks\build build
copy ..\..\..\..\JAP_REMOTE_WS_PYTHON_OPENSHIFT\.openshift\action_hooks\deploy deploy
copy ..\..\..\..\JAP_REMOTE_WS_PYTHON_OPENSHIFT\.openshift\action_hooks\post_deploy post_deploy
copy ..\..\..\..\JAP_REMOTE_WS_PYTHON_OPENSHIFT\.openshift\action_hooks\pre_build pre_build
copy ..\..\..\..\JAP_REMOTE_WS_PYTHON_OPENSHIFT\.openshift\action_hooks\start start
copy ..\..\..\..\JAP_REMOTE_WS_PYTHON_OPENSHIFT\.openshift\action_hooks\stop stop
cd ..
cd ..
cd ..
%SEVENZIP_HOME%\7z.exe a -tzip JAP_REMOTE_WS_PYTHON_OPENSHIFT-%JAP_REMOTE_WS_PYTHON_OPENSHIFT_VERSION%.zip JAP_REMOTE_WS_PYTHON_OPENSHIFT-%JAP_REMOTE_WS_PYTHON_OPENSHIFT_VERSION%
rem JAP_REMOTE_WS_PYTHON_WINDOWS
mkdir PYINSTALLER
cd PYINSTALLER
python %PYINSTALLER_HOME%\pyinstaller.py -c -F ..\JAP_REMOTE_WS_PYTHON-%JAP_REMOTE_WS_PYTHON_VERSION%\JAP_REMOTE_WS.py
cd ..
mkdir JAP_REMOTE_WS_PYTHON_WINDOWS-%JAP_REMOTE_WS_PYTHON_WINDOWS_VERSION%
cd JAP_REMOTE_WS_PYTHON_WINDOWS-%JAP_REMOTE_WS_PYTHON_WINDOWS_VERSION%
copy ..\PYINSTALLER\dist\JAP_REMOTE_WS.exe JAP_REMOTE_WS.exe
copy ..\..\JAP_REMOTE_WS_PYTHON_WINDOWS\JAP_REMOTE_WS.bat JAP_REMOTE_WS.bat
copy ..\..\JAP_REMOTE_WS_PYTHON_WINDOWS\README.txt README.txt
copy ..\..\JAP_REMOTE_WS.json JAP_REMOTE_WS.json
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
copy ..\..\H.txt H.txt
cd ..
%SEVENZIP_HOME%\7z.exe a -tzip JAP_REMOTE_WS_PYTHON_WINDOWS-%JAP_REMOTE_WS_PYTHON_WINDOWS_VERSION%.zip JAP_REMOTE_WS_PYTHON_WINDOWS-%JAP_REMOTE_WS_PYTHON_WINDOWS_VERSION%
cd ..