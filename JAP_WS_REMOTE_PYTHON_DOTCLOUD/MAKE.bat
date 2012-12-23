set SEVENZIP_HOME="C:\Program Files\7-Zip"
set PYINSTALLER_HOME="C:\pyinstaller-2.0"
set VERSION=2.0.0-SNAPSHOT
if exist MAKE rmdir MAKE /s /q
mkdir MAKE
cd MAKE
mkdir JAP_WS_REMOTE_PYTHON_DOTCLOUD-%VERSION%
cd JAP_WS_REMOTE_PYTHON_DOTCLOUD-%VERSION%
copy ..\..\dotcloud.yml dotcloud.yml
copy ..\..\JAP_WS_REMOTE.json JAP_WS_REMOTE.json
copy ..\..\JAP_WS_REMOTE.py JAP_WS_REMOTE.py
copy ..\..\README.txt README.txt
copy ..\..\requirements.txt requirements.txt
mkdir JAP
cd JAP
copy ..\..\..\JAP\__init__.py __init__.py
copy ..\..\..\JAP\JAP_WS_REMOTE.py JAP_WS_REMOTE.py
cd ..
cd ..
%SEVENZIP_HOME%\7z.exe a -tzip JAP_WS_REMOTE_PYTHON_DOTCLOUD-%VERSION%.zip JAP_WS_REMOTE_PYTHON_DOTCLOUD-%VERSION%
cd ..