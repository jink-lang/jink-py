@echo off

echo Building an executable....

set /p specpath=Enter path of JINK directory:

pyinstaller --specpath=%specpath% jink.py

echo Executable built at %specpath%\build\jink