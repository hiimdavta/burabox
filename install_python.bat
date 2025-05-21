@echo off
setlocal enabledelayedexpansion

echo Python 3.11 telepitese Windows 10-re...
echo.

:: Ellenőrizzük, hogy fut-e már Python
python --version > nul 2>&1
if %errorlevel% equ 0 (
    echo A Python mar telepitve van a rendszeren.
    python --version
    echo.
    set /p "valasz=Szeretned folytatni a Python 3.11 telepiteset? (i/n): "
    if /i "!valasz!" neq "i" exit /b 0
)

:: Letöltési URL és fájlnév
set "PYTHON_URL=https://www.python.org/ftp/python/3.11.6/python-3.11.6-amd64.exe"
set "INSTALLER=python-3.11.6-amd64.exe"

echo Python 3.11.6 letoltese...
echo.

:: PowerShell parancs a letöltéshez
powershell -Command "& {Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%INSTALLER%'}"

if not exist "%INSTALLER%" (
    echo Hiba: A letoltes sikertelen!
    pause
    exit /b 1
)

echo.
echo Python 3.11.6 telepitese...
echo Fontos: A telepites soran jelold be az "Add Python to PATH" opciot!
echo.

:: Telepítés indítása
start /wait "" "%INSTALLER%" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

:: Telepítő törlése
del "%INSTALLER%"

:: Ellenőrizzük a telepítést
echo.
echo Telepites ellenorzese...
python --version
if %errorlevel% equ 0 (
    echo.
    echo A Python 3.11 sikeresen telepult!
    echo.
    echo Most mar futtathatod a setup_windows.bat fajlt.
) else (
    echo.
    echo Hiba: A Python telepitese nem sikerult megfeleloen!
    echo Kerdlek telepitsd manuálisan a Python 3.11-et:
    echo https://www.python.org/downloads/release/python-3116/
)

echo.
pause 