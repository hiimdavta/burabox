# Iskolai Fájlkezelő Rendszer - Telepítési Útmutató

> Ez a dokumentum a telepítési lépéseket tartalmazza Windows és macOS rendszereken. A teljes dokumentációért lásd a [fő README.md](README.md) fájlt.

## Verzió
Ez a dokumentum a v1.0.0 verzióhoz tartozik.

## Windows Telepítés

### Előfeltételek
1. Windows 10 operációs rendszer
2. Internet kapcsolat a Python és a függőségek letöltéséhez
3. Adminisztrátori jogosultságok a telepítéshez

### Telepítés lépései

1. Töltsd le a projektet:
   ```bash
   # Git használatával (ajánlott):
   git clone https://github.com/hiimdavta/burabox_v1.0.0.git
   cd burabox_v1.0.0
   
   # VAGY manuálisan:
   # Töltsd le és csomagold ki a ZIP fájlt
   ```

2. Python telepítése:
   - Dupla kattintás az `install_python.bat` fájlra
   - A script automatikusan:
     - Ellenőrzi, hogy van-e már Python telepítve
     - Letölti és telepíti a Python 3.11.6 verziót
     - Beállítja a PATH környezeti változót
     - Ellenőrzi a telepítést

3. Projekt beállítása:
   - Dupla kattintás a `setup_windows.bat` fájlra
   - Ez automatikusan:
     - Telepíti a szükséges Python csomagokat a `requirements.txt` alapján
     - Ellenőrzi a telepítést
     - Létrehozza a `start_server.bat` indító scriptet

4. Környezeti változók beállítása:
   - Másold le a `.env.example` fájlt `.env` néven
   - Módosítsd a `.env` fájlt a saját beállításaiddal
   - Fontos: változtasd meg az admin jelszót és a SECRET_KEY értékét!

### Szerver indítása Windows rendszeren

1. Dupla kattintás a `start_server.bat` fájlra
2. A script automatikusan:
   - Ellenőrzi, hogy fut-e már a szerver
   - Ha fut, leállítja
   - Ellenőrzi a Python és a szükséges csomagok telepítését
   - Ellenőrzi a `.env` fájl meglétét
   - Elindítja az új szervert
   - Megmutatja az elérhető címeket
   - Megnyitja a böngészőt

A szerver elérhető lesz:
- Lokálisan: http://localhost:5051
- Hálózaton: http://[WINDOWS_GEP_IP_CIME]:5051

## macOS Telepítés

### Előfeltételek
1. macOS 10.15 vagy újabb
2. Internet kapcsolat
3. Python 3 telepítve (ajánlott: Python 3.11)

### Telepítés lépései

1. Töltsd le a projektet:
   ```bash
   # Git használatával (ajánlott):
   git clone https://github.com/hiimdavta/burabox_v1.0.0.git
   cd burabox_v1.0.0
   
   # VAGY manuálisan:
   # Töltsd le és csomagold ki a ZIP fájlt
   ```

2. Python telepítése (ha még nincs):
   - Töltsd le a Python 3.11-et innen: https://www.python.org/downloads/macos/
   - Vagy használd a Homebrew-t: `brew install python@3.11`

3. Projekt beállítása:
   ```bash
   # Telepítsd a szükséges csomagokat
   pip3 install -r requirements.txt
   ```

4. Környezeti változók beállítása:
   ```bash
   # Másold le a .env.example fájlt
   cp .env.example .env
   # Módosítsd a .env fájlt a saját beállításaiddal
   ```

### Szerver indítása macOS rendszeren

1. Dupla kattintás a `start_app.command` fájlra
2. A script automatikusan:
   - Ellenőrzi, hogy fut-e már a szerver
   - Ha fut, leállítja
   - Ellenőrzi a Python és a szükséges csomagok telepítését
   - Ellenőrzi a `.env` fájl meglétét
   - Elindítja az új szervert
   - Megmutatja az elérhető címeket
   - Megnyitja a böngészőt

A szerver elérhető lesz:
- Lokálisan: http://localhost:5051
- Hálózaton: http://[MAC_GEP_IP_CIME]:5051

## Hálózati elérés

Ha más gépekről is szeretnéd elérni a szervert:

### Windows
1. Nyisd meg a Windows Tűzfalat
2. Kattints a "Speciális beállítások" linkre
3. Válaszd a "Bejövő szabályok" opciót
4. Kattints az "Új szabály..." gombra
5. Válaszd a "Port" opciót
6. Add meg a 5051-es portot
7. Engedélyezd a kapcsolatot
8. Válaszd a "Tartomány" hálózatot
9. Add meg a szabály nevét (pl. "BuraBox Server")

### macOS
1. Nyisd meg a Rendszerbeállítások > Biztonság és adatvédelem > Tűzfal
2. Kattints a "Tűzfal beállítások..." gombra
3. Kattints a "+" gombra
4. Válaszd a "Python" alkalmazást
5. Engedélyezd a bejövő kapcsolatokat

## Hibaelhárítás

### Python telepítési problémák
#### Windows
Ha az `install_python.bat` nem működik:
1. Töröld a jelenlegi Python telepítést a Windows Beállításokból
2. Töltsd le manuálisan a Python 3.11.6-ot: https://www.python.org/downloads/release/python-3116/
3. Telepítéskor jelöld be az "Add Python to PATH" opciót

#### macOS
Ha a Python nem található:
1. Telepítsd a Homebrew-t: `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
2. Telepítsd a Python-t: `brew install python@3.11`

### Szerver indítási problémák
Ha a szerver nem indul:
1. Ellenőrizd, hogy a Python telepítve van-e:
   - Windows: `python --version`
   - macOS: `python3 --version`
2. Ellenőrizd, hogy a 5051-es port szabad-e:
   - Windows: `netstat -ano | findstr :5051`
   - macOS: `lsof -i :5051`
3. Ellenőrizd a `.env` fájl beállításait
4. Ellenőrizd, hogy minden szükséges csomag telepítve van-e:
   - Windows: `pip list`
   - macOS: `pip3 list`

### További segítség
További hibaelhárítási tippekért és gyakori kérdésekért lásd a [fő README.md](README.md#gyakori-kérdések-faq) fájlt.

## Biztonsági beállítások

A teljes biztonsági ellenőrzőlistáért lásd a [fő README.md](README.md#biztonsági-ellenőrzőlista) fájlt.

Operációs rendszer specifikus biztonsági beállítások:
- [ ] Az `uploads` mappa jogosultságai korrekt beállítva
- [ ] Az adatbázis fájl jogosultságai korrekt beállítva
- [ ] A log fájlok jogosultságai korrekt beállítva
- [ ] Tűzfal szabályok megfelelően beállítva

## Fejlesztői környezet

### VS Code telepítése (ajánlott IDE)
1. Töltsd le innen: https://code.visualstudio.com/
2. Telepítsd a Python és Git bővítményeket

### Git beállítása
```bash
git config --global user.name "Az Ön neve"
git config --global user.email "az.on.email@pelda.com"
```

### Fejlesztői mód bekapcsolása
Módosítsd a `.env` fájlt:
```
FLASK_ENV=development
DEBUG=True
```

## Licenc
Ez a projekt az MIT licenc alatt áll. Lásd a [LICENSE](LICENSE) fájlt részletekért. 