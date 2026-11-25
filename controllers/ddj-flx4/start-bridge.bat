@echo off
rem Starts the DDJ-FLX4 bridge on Windows: installs the Python dependencies on first run, then runs it.
rem Double-click this file. Leave the window open while you use B2B Studio.
setlocal
cd /d "%~dp0"

set PY=
where py >nul 2>nul && set PY=py -3
if not defined PY where python >nul 2>nul && set PY=python
if not defined PY (
    echo Python 3 was not found.
    echo Install it from https://www.python.org/downloads/ and tick "Add python.exe to PATH" in the installer.
    if not defined NOPAUSE pause
    exit /b 1
)

%PY% -m pip install --quiet --disable-pip-version-check -r requirements.txt
if errorlevel 1 (
    echo Could not install the dependencies. Check your internet connection and try again.
    if not defined NOPAUSE pause
    exit /b 1
)

%PY% flx4_bridge.py %*
echo.
if not defined NOPAUSE pause
