# Iskolai Fájlkezelő Rendszer

## Leírás
Ez a webalkalmazás egy általános iskolai fájlkezelő rendszer. Lehetővé teszi a tanárok és diákok számára a fájlok feltöltését, kezelését és megosztását osztályonként. A rendszer biztonságos, felhasználóbarát és reszponzív felülettel rendelkezik.

## Főbb funkciók
- 🔐 Egységes bejelentkezési rendszer tanárok és diákok számára
- 👥 Felhasználói szerepkörök (admin, tanár, diák)
- 📁 Osztályonkénti fájlkezelés
- ⬆️ Fájlok feltöltése, letöltése és törlése
- 📦 Tömeges fájlműveletek (tömeges feltöltés, törlés, letöltés)
- 🔍 Fájlok szűrése és rendezése
- 🔒 Biztonságos fájlkezelés
- 📱 Reszponzív felhasználói felület

## Biztonsági funkciók
- 🔐 Egységes felhasználókezelés Flask-Login segítségével
- 🔑 Biztonságos jelszókezelés (bcrypt hashelés)
- 📝 Fájltípus korlátozások és MIME típus ellenőrzés
- 🧹 Fájlnév sanitizálás
- ⏱️ Rate limiting (10 feltöltés per perc)
- 📏 Fájlméret limit (10MB)
- 🔒 Biztonságos session kezelés
- 🛡️ SQL injection védelem

## Telepítés

### Előfeltételek
- Python 3.11 vagy újabb
- pip (Python csomagkezelő)
- libmagic (a python-magic csomaghoz)

### Rendszerkövetelmények
- macOS: `brew install libmagic`
- Linux: `apt-get install libmagic1` vagy `yum install file-libs`
- Windows: A python-magic-bin csomag automatikusan telepíti a szükséges DLL-t

### Telepítési lépések
1. Klónozd a repository-t:
```bash
git clone https://github.com/hiimdavta/burabox_v1.0.0.git
cd burabox_v1.0.0
```

2. Hozz létre és aktiválj egy virtuális környezetet:
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

3. Telepítsd a függőségeket:
```bash
pip install -r requirements.txt
```

4. Állítsd be a környezeti változókat:
```bash
# Másold le a .env.example fájlt .env néven
cp .env.example .env

# Módosítsd a .env fájlt a saját beállításaiddal
# Fontos: változtasd meg az admin jelszót és a SECRET_KEY értékét!
```

5. Futtasd az adatbázis migrációt:
```bash
python migrations.py
```

6. Indítsd el a szervert:
```bash
python app.py
```

## Környezeti változók
A rendszer a következő környezeti változókat használja (`.env` fájlban):

### Kötelező beállítások
- `ADMIN_USERNAME`: Admin felhasználónév (alapértelmezett: 'admin')
- `ADMIN_PASSWORD`: Admin jelszó (kötelező megváltoztatni!)
- `SECRET_KEY`: Flask alkalmazás titkos kulcs (kötelező megváltoztatni!)

### Opcionális beállítások
- `FLASK_ENV`: Környezet típusa ('development' vagy 'production')
- `DATABASE_URL`: Adatbázis kapcsolati URL (alapértelmezett: SQLite)
- `MAX_CONTENT_LENGTH`: Maximális fájlméret (alapértelmezett: 15MB)
- `SESSION_COOKIE_SECURE`: Biztonságos cookie-k (alapértelmezett: True)
- `PERMANENT_SESSION_LIFETIME`: Session élettartam (alapértelmezett: 24 óra)

További beállítások és részletek: lásd a `.env.example` fájlt.

## Használat
1. Nyisd meg a böngészőben: `http://localhost:5051`
2. Válaszd ki a felhasználó típusát (tanár/diák)
3. Jelentkezz be a megfelelő felhasználóval
4. Kezeld a fájlokat az osztályodban:
   - Fájlok feltöltése (egyszeri vagy tömeges)
   - Fájlok letöltése (egyszeri vagy tömeges)
   - Fájlok törlése (egyszeri vagy tömeges)
   - Fájlok szűrése és rendezése

## Fejlesztői információk
- 🚀 Flask web framework (3.0.2)
- 🗄️ SQLAlchemy ORM (2.0.27)
- 👤 Flask-Login felhasználókezelés
- 📦 Flask-Migrate adatbázis migráció
- ⏱️ Flask-Limiter rate limiting
- 🔍 python-magic MIME típus ellenőrzés
- 🎨 Bootstrap 5 UI framework
- 📱 Reszponzív design
- 🧪 Unit tesztek unittest framework-kal

## Hibaelhárítás
- Ha a statikus fájlok nem töltődnek be, ellenőrizd a Flask konfigurációt
- Ha a feltöltés nem működik, ellenőrizd a fájl jogosultságokat és a méretkorlátokat
- Ha az adatbázis kapcsolat nem működik, ellenőrizd a környezeti változókat
- Ha a bejelentkezés nem működik, ellenőrizd a `.env` fájl beállításait
- Ha a SECRET_KEY nincs beállítva, generálj egy újat: `python -c 'import secrets; print(secrets.token_hex(32))'`

## Licenc
Ez a projekt az MIT licenc alatt áll. Lásd a LICENSE fájlt részletekért.

## Kapcsolat
Kérdések, javaslatok: [email protected]

## Köszönet
Köszönjük minden közreműködőnek és tesztelőnek a segítségüket a projekt fejlesztésében!
