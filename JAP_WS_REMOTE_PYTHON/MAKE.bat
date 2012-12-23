set SEVENZIP_HOME="C:\Program Files\7-Zip"
set PYINSTALLER_HOME="C:\pyinstaller-2.0"
set VERSION=2.0.0-SNAPSHOT
if exist MAKE rmdir MAKE /s /q
mkdir MAKE
cd MAKE
mkdir JAP_WS_REMOTE_PYTHON-%VERSION%
cd JAP_WS_REMOTE_PYTHON-%VERSION%
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
%SEVENZIP_HOME%\7z.exe a -tzip JAP_WS_REMOTE_PYTHON-%VERSION%.zip JAP_WS_REMOTE_PYTHON-%VERSION%
mkdir PYINSTALLER
cd PYINSTALLER
python %PYINSTALLER_HOME%\pyinstaller.py -c -F ..\..\JAP_WS_REMOTE.py
cd ..
mkdir JAP_WS_REMOTE_PYTHON_WINDOWS-%VERSION%
cd JAP_WS_REMOTE_PYTHON_WINDOWS-%VERSION%
copy ..\PYINSTALLER\dist\JAP_WS_REMOTE.exe JAP_WS_REMOTE.exe
copy ..\..\WINDOWS\JAP_WS_REMOTE.bat JAP_WS_REMOTE.bat
copy ..\..\WINDOWS\README.txt README.txt
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
%SEVENZIP_HOME%\7z.exe a -tzip JAP_WS_REMOTE_PYTHON_WINDOWS-%VERSION%.zip JAP_WS_REMOTE_PYTHON_WINDOWS-%VERSION%
cd ..