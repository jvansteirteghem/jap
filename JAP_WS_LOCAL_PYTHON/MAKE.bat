set SEVENZIP_HOME="C:\Program Files\7-Zip"
set PYINSTALLER_HOME="C:\pyinstaller-2.0"
set VERSION=1.0.0
if exist MAKE rmdir MAKE /s /q
mkdir MAKE
cd MAKE
mkdir JAP_WS_LOCAL_PYTHON-%VERSION%
cd JAP_WS_LOCAL_PYTHON-%VERSION%
copy ..\..\JAP_WS_LOCAL.bat JAP_WS_LOCAL.bat
copy ..\..\JAP_WS_LOCAL.json JAP_WS_LOCAL.json
copy ..\..\JAP_WS_LOCAL.py JAP_WS_LOCAL.py
copy ..\..\CA.pem CA.pem
copy ..\..\README.txt README.txt
mkdir JAP
cd JAP
copy ..\..\..\JAP\__init__.py __init__.py
copy ..\..\..\JAP\JAP_LOCAL.py JAP_LOCAL.py
copy ..\..\..\JAP\TUNNEL.py TUNNEL.py
copy ..\..\..\JAP\JAP_WS_LOCAL.py JAP_WS_LOCAL.py
cd ..
cd ..
%SEVENZIP_HOME%\7z.exe a -tzip JAP_WS_LOCAL_PYTHON-%VERSION%.zip JAP_WS_LOCAL_PYTHON-%VERSION%
mkdir PYINSTALLER
cd PYINSTALLER
python %PYINSTALLER_HOME%\pyinstaller.py -c -F ..\..\JAP_WS_LOCAL.py
cd ..
mkdir JAP_WS_LOCAL_PYTHON_WINDOWS-%VERSION%
cd JAP_WS_LOCAL_PYTHON_WINDOWS-%VERSION%
copy ..\PYINSTALLER\dist\JAP_WS_LOCAL.exe JAP_WS_LOCAL.exe
copy ..\..\WINDOWS\JAP_WS_LOCAL.bat JAP_WS_LOCAL.bat
copy ..\..\WINDOWS\README.txt README.txt
copy ..\..\JAP_WS_LOCAL.json JAP_WS_LOCAL.json
copy ..\..\CA.pem CA.pem
cd ..
%SEVENZIP_HOME%\7z.exe a -tzip JAP_WS_LOCAL_PYTHON_WINDOWS-%VERSION%.zip JAP_WS_LOCAL_PYTHON_WINDOWS-%VERSION%
cd ..