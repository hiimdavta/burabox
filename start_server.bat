@echo off
setlocal enabledelayedexpansion

:: Ellenőrizzük, hogy fut-e már a szerver a 5051-es porton
netstat -ano | findstr :5051 > nul
if %errorlevel% equ 0 (
    echo A szerver mar fut a 5051-es porton. Leallitom...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5051') do (
        taskkill /F /PID %%a
    )
    timeout /t 2 /nobreak > nul
)

:: Ellenőrizzük, hogy a Python telepítve van-e
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Hiba: A Python nincs telepítve vagy nincs a PATH-ban!
    echo Kérlek telepítsd a Python 3.11 vagy újabb verziót: https://www.python.org/downloads/windows/
    pause
    exit /b 1
)

:: Ellenőrizzük, hogy létezik-e a .env fájl
if not exist ".env" (
    echo Hiba: A .env fájl nem található!
    echo Kérlek másold le a .env.example fájlt .env néven és állítsd be a szükséges értékeket!
    pause
    exit /b 1
)

:: Ellenőrizzük, hogy telepítve vannak-e a szükséges csomagok
python -c "import flask" > nul 2>&1
if %errorlevel% neq 0 (
    echo Hiba: A Flask nincs telepítve!
    echo Kérlek futtasd először a setup_windows.bat fájlt!
    pause
    exit /b 1
)

:: Elindítjuk a szervert a háttérben
start /B python app.py

:: Várunk egy kicsit, hogy a szerver biztosan elinduljon
timeout /t 3 /nobreak > nul

:: Ellenőrizzük, hogy a szerver tényleg elindult-e
netstat -ano | findstr :5051 > nul
if %errorlevel% neq 0 (
    echo Hiba: A szerver nem indult el megfelelően!
    pause
    exit /b 1
)

:: Megkeressük a gép IP címét
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /R /C:"IPv4 Address"') do (
    set IP=%%a
    set IP=!IP:~1!
    goto :found_ip
)
:found_ip

:: Kiírjuk az elérhető URL-eket
echo.
echo A szerver elindult és elérhető a következő címeken:
echo - Lokális: http://localhost:5051
echo - Hálózat: http://%IP%:5051
echo.

:: Megnyitjuk a böngészőt
start http://localhost:5051

echo A szerver fut a háttérben. A bezáráshoz nyomj Ctrl+C-t a konzol ablakban.
echo.
pause 