set SEVENZIP_HOME="C:\Program Files\7-Zip"
set PYINSTALLER_HOME="C:\pyinstaller-2.0"
set JAP_PYTHON_VERSION=2.0.0
set JAP_PYTHON_WINDOWS_VERSION=2.0.0
if exist MAKE rmdir MAKE /s /q
mkdir MAKE
cd MAKE
rem JAP_PYTHON
mkdir JAP_PYTHON-%JAP_PYTHON_VERSION%
cd JAP_PYTHON-%JAP_PYTHON_VERSION%
xcopy /E /I ..\..\WWW WWW
copy ..\..\JAP.bat JAP.bat
copy ..\..\JAP.json JAP.json
copy ..\..\JAP.py JAP.py
copy ..\..\JAP_LOCAL.json JAP_LOCAL.json
copy ..\..\JAP_LOCAL_SSH.json JAP_LOCAL_SSH.json
copy ..\..\JAP_LOCAL_WS.json JAP_LOCAL_WS.json
copy ..\..\JAP_REMOTE_SSH.json JAP_REMOTE_SSH.json
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
copy ..\..\KP.bat KP.bat
copy ..\..\KP.pem KP.pem
copy ..\..\README.txt README.txt
mkdir JAP
cd JAP
copy ..\..\..\JAP\__init__.py __init__.py
copy ..\..\..\JAP\JAP.py JAP.py
mkdir LOCAL
cd LOCAL
copy ..\..\..\..\JAP\LOCAL\__init__.py __init__.py
copy ..\..\..\..\JAP\LOCAL\JAP_LOCAL.py JAP_LOCAL.py
cd ..
mkdir LOCAL_SSH
cd LOCAL_SSH
copy ..\..\..\..\JAP\LOCAL_SSH\__init__.py __init__.py
copy ..\..\..\..\JAP\LOCAL_SSH\JAP_LOCAL.py JAP_LOCAL.py
copy ..\..\..\..\JAP\LOCAL_SSH\JAP_LOCAL_SSH.py JAP_LOCAL_SSH.py
cd ..
mkdir LOCAL_WS
cd LOCAL_WS
copy ..\..\..\..\JAP\LOCAL_WS\__init__.py __init__.py
copy ..\..\..\..\JAP\LOCAL_WS\JAP_LOCAL.py JAP_LOCAL.py
copy ..\..\..\..\JAP\LOCAL_WS\JAP_LOCAL_WS.py JAP_LOCAL_WS.py
cd ..
mkdir REMOTE_SSH
cd REMOTE_SSH
copy ..\..\..\..\JAP\REMOTE_SSH\__init__.py __init__.py
copy ..\..\..\..\JAP\REMOTE_SSH\JAP_LOCAL.py JAP_LOCAL.py
copy ..\..\..\..\JAP\REMOTE_SSH\JAP_REMOTE_SSH.py JAP_REMOTE_SSH.py
cd ..
mkdir REMOTE_WS
cd REMOTE_WS
copy ..\..\..\..\JAP\REMOTE_WS\__init__.py __init__.py
copy ..\..\..\..\JAP\REMOTE_WS\JAP_LOCAL.py JAP_LOCAL.py
copy ..\..\..\..\JAP\REMOTE_WS\JAP_REMOTE_WS.py JAP_REMOTE_WS.py
cd ..
cd ..
cd ..
%SEVENZIP_HOME%\7z.exe a -tzip JAP_PYTHON-%JAP_PYTHON_VERSION%.zip JAP_PYTHON-%JAP_PYTHON_VERSION%
rem JAP_PYTHON_WINDOWS
mkdir PYINSTALLER
cd PYINSTALLER
python %PYINSTALLER_HOME%\pyinstaller.py -c -F ..\..\JAP.py
cd ..
mkdir JAP_PYTHON_WINDOWS-%JAP_PYTHON_WINDOWS_VERSION%
cd JAP_PYTHON_WINDOWS-%JAP_PYTHON_WINDOWS_VERSION%
copy ..\PYINSTALLER\dist\JAP.exe JAP.exe
copy ..\..\JAP_PYTHON_WINDOWS\JAP.bat JAP.bat
copy ..\..\JAP_PYTHON_WINDOWS\README.txt README.txt
xcopy /E /I ..\..\WWW WWW
copy ..\..\JAP.json JAP.json
copy ..\..\JAP_LOCAL.json JAP_LOCAL.json
copy ..\..\JAP_LOCAL_SSH.json JAP_LOCAL_SSH.json
copy ..\..\JAP_LOCAL_WS.json JAP_LOCAL_WS.json
copy ..\..\JAP_REMOTE_SSH.json JAP_REMOTE_SSH.json
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
copy ..\..\KP.bat KP.bat
copy ..\..\KP.pem KP.pem
cd ..
%SEVENZIP_HOME%\7z.exe a -tzip JAP_PYTHON_WINDOWS-%JAP_PYTHON_WINDOWS_VERSION%.zip JAP_PYTHON_WINDOWS-%JAP_PYTHON_WINDOWS_VERSION%
cd ..