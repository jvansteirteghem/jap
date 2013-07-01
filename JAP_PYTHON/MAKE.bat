set SEVENZIP_HOME="C:\Program Files\7-Zip"
set PYINSTALLER_HOME="C:\pyinstaller-SNAPSHOT"
set JAP_PYTHON_VERSION=3.0.0-SNAPSHOT-2
set JAP_PYTHON_WINDOWS_VERSION=3.0.0-SNAPSHOT-2
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
copy ..\..\CA_DEFAULT.pem CA_DEFAULT.pem
copy ..\..\CAK.pem CAK.pem
copy ..\..\CK.pem CK.pem
copy ..\..\CR.pem CR.pem
copy ..\..\H.txt H.txt
copy ..\..\KP.bat KP.bat
copy ..\..\KP.pem KP.pem
copy ..\..\README.txt README.txt
mkdir JAP
cd JAP
copy ..\..\..\JAP\__init__.py __init__.py
copy ..\..\..\JAP\JAP.py JAP.py
copy ..\..\..\JAP\JAP_LOCAL.py JAP_LOCAL.py
copy ..\..\..\JAP\JAP_LOCAL_SSH.py JAP_LOCAL_SSH.py
copy ..\..\..\JAP\JAP_LOCAL_WS.py JAP_LOCAL_WS.py
copy ..\..\..\JAP\JAP_REMOTE_SSH.py JAP_REMOTE_SSH.py
copy ..\..\..\JAP\JAP_REMOTE_WS.py JAP_REMOTE_WS.py
cd ..
cd ..
%SEVENZIP_HOME%\7z.exe a -tzip JAP_PYTHON-%JAP_PYTHON_VERSION%.zip JAP_PYTHON-%JAP_PYTHON_VERSION%
rem JAP_PYTHON_WINDOWS
mkdir PYINSTALLER
cd PYINSTALLER
python %PYINSTALLER_HOME%\pyinstaller.py -c -F ..\JAP_PYTHON-%JAP_PYTHON_VERSION%\JAP.py
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
copy ..\..\CA_DEFAULT.pem CA_DEFAULT.pem
copy ..\..\CAK.pem CAK.pem
copy ..\..\CK.pem CK.pem
copy ..\..\CR.pem CR.pem
copy ..\..\H.txt H.txt
copy ..\..\KP.bat KP.bat
copy ..\..\KP.pem KP.pem
cd ..
%SEVENZIP_HOME%\7z.exe a -tzip JAP_PYTHON_WINDOWS-%JAP_PYTHON_WINDOWS_VERSION%.zip JAP_PYTHON_WINDOWS-%JAP_PYTHON_WINDOWS_VERSION%
cd ..