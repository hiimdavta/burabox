# Teszt Szerver Windows Telepítési Útmutató

## Előfeltételek
1. Windows 10 operációs rendszer
2. Python 3.11 vagy újabb verzió
   - Töltsd le innen: https://www.python.org/downloads/windows/
   - Telepítéskor **kérlek jelöld be** az "Add Python to PATH" opciót!

## Telepítés lépései

1. Másold át az összes projekt fájlt a Windows gépre egy mappába (pl. `C:\TesztSzerver`)

2. Futtasd a `setup_windows.bat` fájlt dupla kattintással
   - Ez automatikusan telepíti a szükséges Python csomagokat
   - Létrehozza a Windows-specifikus indító scriptet

3. A telepítés után a szervert a `start_server.bat` fájl futtatásával indíthatod

## Szerver indítása

1. Nyisd meg a projekt mappát
2. Kattints duplán a `start_server.bat` fájlra
3. A szerver elindul és elérhető lesz a böngészőben: http://127.0.0.1:5051

## Hálózati elérés

A szerver alapértelmezetten csak a localhost-on (127.0.0.1) érhető el. Ha más gépekről is szeretnéd elérni:

1. Nyisd meg a Windows Tűzfalat
2. Kattints a "Speciális beállítások" linkre
3. Válaszd a "Bejövő szabályok" opciót
4. Kattints az "Új szabály..." gombra
5. Válaszd a "Port" opciót
6. Add meg a 5051-es portot
7. Engedélyezd a kapcsolatot
8. Válaszd a "Tartomány" hálózatot
9. Add meg a szabály nevét (pl. "Teszt Szerver")

Ezután a szerver elérhető lesz a hálózaton a Windows gép IP címén keresztül:
http://[WINDOWS_GEP_IP_CIME]:5051

## Hibaelhárítás

Ha a szerver nem indul:
1. Ellenőrizd, hogy a Python telepítve van-e: nyiss egy Command Prompt-ot és írd: `python --version`
2. Ellenőrizd, hogy a 5051-es port szabad-e: `netstat -ano | findstr :5051`
3. Ha a port foglalt, állítsd le a folyamatot vagy módosítsd a portot az `app.py` fájlban

Ha más gépekről nem lehet elérni:
1. Ellenőrizd a Windows Tűzfal beállításait
2. Ellenőrizd, hogy a VLAN beállítások engedélyezik-e a kapcsolatot
3. Próbáld meg pingelni a Windows gépet a hálózatról 