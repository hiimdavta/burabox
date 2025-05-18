@echo off
echo Teszt Szerver Windows Telepito
echo ============================

REM Ellenőrizzük a Python telepítést
python --version > nul 2>&1
if errorlevel 1 (
    echo Hiba: Python nincs telepítve vagy nincs a PATH-ban!
    echo Kérlek telepítsd a Python-t innen: https://www.python.org/downloads/windows/
    echo Ne felejtsd el bejelölni az "Add Python to PATH" opciót!
    pause
    exit /b 1
)

REM Telepítsük a szükséges csomagokat
echo Telepítem a szükséges Python csomagokat...
python -m pip install --upgrade pip
pip install flask pillow

REM Készítsünk egy indító scriptet
echo @echo off > start_server.bat
echo echo Teszt Szerver Indito >> start_server.bat
echo echo =================== >> start_server.bat
echo echo. >> start_server.bat
echo echo Ellenőrzöm a szerver állapotát... >> start_server.bat
echo netstat -ano ^| findstr :5051 ^> nul >> start_server.bat
echo if not errorlevel 1 ( >> start_server.bat
echo     echo A szerver mar fut a 5051-es porton! >> start_server.bat
echo     echo Nyisd meg a bongeszoben: http://127.0.0.1:5051 >> start_server.bat
echo     echo. >> start_server.bat
echo     echo Nyomj egy billentyut a kilepeshez... >> start_server.bat
echo     pause ^> nul >> start_server.bat
echo     exit /b 1 >> start_server.bat
echo ) >> start_server.bat
echo. >> start_server.bat
echo echo Inditom a szervert... >> start_server.bat
echo echo Nyisd meg a bongeszoben: http://127.0.0.1:5051 >> start_server.bat
echo echo. >> start_server.bat
echo echo A szerver leallitasahoz zarja be ezt az ablakot (Ctrl+C) >> start_server.bat
echo echo. >> start_server.bat
echo python app.py >> start_server.bat
echo. >> start_server.bat
echo echo A szerver leallt. >> start_server.bat
echo echo Nyomj egy billentyut a kilepeshez... >> start_server.bat
echo pause ^> nul >> start_server.bat

echo.
echo Telepites befejezve!
echo A szervert a start_server.bat futtatasaval indithatod.
echo.
pause 