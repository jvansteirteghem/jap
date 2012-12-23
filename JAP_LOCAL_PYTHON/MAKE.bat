set SEVENZIP_HOME="C:\Program Files\7-Zip"
set PYINSTALLER_HOME="C:\pyinstaller-2.0"
set VERSION=2.0.0-SNAPSHOT
if exist MAKE rmdir MAKE /s /q
mkdir MAKE
cd MAKE
mkdir JAP_LOCAL_PYTHON-%VERSION%
cd JAP_LOCAL_PYTHON-%VERSION%
copy ..\..\JAP_LOCAL.bat JAP_LOCAL.bat
copy ..\..\JAP_LOCAL.json JAP_LOCAL.json
copy ..\..\JAP_LOCAL.py JAP_LOCAL.py
copy ..\..\README.txt README.txt
mkdir JAP
cd JAP
copy ..\..\..\JAP\__init__.py __init__.py
copy ..\..\..\JAP\JAP_LOCAL.py JAP_LOCAL.py
copy ..\..\..\JAP\TUNNEL.py TUNNEL.py
cd ..
cd ..
%SEVENZIP_HOME%\7z.exe a -tzip JAP_LOCAL_PYTHON-%VERSION%.zip JAP_LOCAL_PYTHON-%VERSION%
mkdir PYINSTALLER
cd PYINSTALLER
python %PYINSTALLER_HOME%\pyinstaller.py -c -F ..\..\JAP_LOCAL.py
cd ..
mkdir JAP_LOCAL_PYTHON_WINDOWS-%VERSION%
cd JAP_LOCAL_PYTHON_WINDOWS-%VERSION%
copy ..\PYINSTALLER\dist\JAP_LOCAL.exe JAP_LOCAL.exe
copy ..\..\WINDOWS\JAP_LOCAL.bat JAP_LOCAL.bat
copy ..\..\WINDOWS\README.txt README.txt
copy ..\..\JAP_LOCAL.json JAP_LOCAL.json
cd ..
%SEVENZIP_HOME%\7z.exe a -tzip JAP_LOCAL_PYTHON_WINDOWS-%VERSION%.zip JAP_LOCAL_PYTHON_WINDOWS-%VERSION%
cd ..