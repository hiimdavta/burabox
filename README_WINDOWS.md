# Iskolai Fájlkezelő Rendszer - Windows Telepítési Útmutató

> Ez a dokumentum a Windows-specifikus telepítési lépéseket tartalmazza. A teljes dokumentációért lásd a [fő README.md](README.md) fájlt.

## Verzió
Ez a dokumentum a v1.0.0 verzióhoz tartozik.

## Előfeltételek
1. Windows 10 operációs rendszer
2. Python 3.11 vagy újabb verzió
   - Töltsd le innen: https://www.python.org/downloads/windows/
   - Telepítéskor **kérlek jelöld be** az "Add Python to PATH" opciót!
3. Git for Windows (opcionális, de ajánlott)
   - Töltsd le innen: https://git-scm.com/download/win

## Telepítés lépései

1. Töltsd le a projektet:
   ```bash
   # Git használatával (ajánlott):
   git clone https://github.com/hiimdavta/burabox_v1.0.0.git
   cd burabox_v1.0.0
   
   # VAGY manuálisan:
   # Töltsd le és csomagold ki a ZIP fájlt
   ```

2. Futtasd a `setup_windows.bat` fájlt dupla kattintással
   - Ez automatikusan:
     - Létrehozza a virtuális környezetet
     - Telepíti a szükséges Python csomagokat
     - Létrehozza a Windows-specifikus indító scriptet
     - Beállítja a környezeti változókat

3. Állítsd be a környezeti változókat:
   - Másold le a `.env.example` fájlt `.env` néven
   - Módosítsd a `.env` fájlt a saját beállításaiddal
   - Fontos: változtasd meg az admin jelszót és a SECRET_KEY értékét!

4. Futtasd az adatbázis migrációt:
   ```bash
   python migrations.py
   ```

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
9. Add meg a szabály nevét (pl. "BuraBox Server")

Ezután a szerver elérhető lesz a hálózaton a Windows gép IP címén keresztül:
http://[WINDOWS_GEP_IP_CIME]:5051

## Biztonsági beállítások

A teljes biztonsági ellenőrzőlistáért lásd a [fő README.md](README.md#biztonsági-ellenőrzőlista) fájlt.

Windows-specifikus biztonsági beállítások:
- [ ] A `uploads` mappa jogosultságai korrekt beállítva
- [ ] Az adatbázis fájl jogosultságai korrekt beállítva
- [ ] A log fájlok jogosultságai korrekt beállítva
- [ ] Windows Tűzfal szabályok megfelelően beállítva

## Hibaelhárítás

### Szerver indítási problémák
Ha a szerver nem indul:
1. Ellenőrizd, hogy a Python telepítve van-e: nyiss egy Command Prompt-ot és írd: `python --version`
2. Ellenőrizd, hogy a 5051-es port szabad-e: `netstat -ano | findstr :5051`
3. Ha a port foglalt, állítsd le a folyamatot vagy módosítsd a portot az `app.py` fájlban
4. Ellenőrizd a `.env` fájl beállításait

### Hálózati problémák
Ha más gépekről nem lehet elérni:
1. Ellenőrizd a Windows Tűzfal beállításait
2. Ellenőrizd, hogy a VLAN beállítások engedélyezik-e a kapcsolatot
3. Próbáld meg pingelni a Windows gépet a hálózatról
4. Ellenőrizd, hogy a `app.py` fájlban a host beállítás megfelelő-e

### További segítség
További hibaelhárítási tippekért és gyakori kérdésekért lásd a [fő README.md](README.md#gyakori-kérdések-faq) fájlt.

## Fejlesztői környezet

Windows-specifikus fejlesztői beállítások:
1. VS Code telepítése (ajánlott IDE):
   - Töltsd le innen: https://code.visualstudio.com/
   - Telepítsd a Python és Git bővítményeket

2. Git beállítása:
   ```bash
   git config --global user.name "Az Ön neve"
   git config --global user.email "az.on.email@pelda.com"
   ```

3. Fejlesztői mód bekapcsolása:
   - Módosítsd a `.env` fájlt:
   ```
   FLASK_ENV=development
   DEBUG=True
   ```

## Licenc
Ez a projekt az MIT licenc alatt áll. Lásd a [LICENSE](LICENSE) fájlt részletekért. 