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
- ⏱️ Rate limiting (120 kérés per perc)
- 📏 Fájlméret limit (15MB)
- 🔒 Biztonságos session kezelés
- 🛡️ SQL injection védelem
- 🔐 Környezeti változók használata bizalmas adatokhoz
- 🚫 Tiltott fájltípusok és MIME típusok ellenőrzése

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

## Fejlesztői környezet
A fejlesztéshez ajánlott beállítások:

1. Fejlesztői mód bekapcsolása:
```bash
# .env fájlban:
FLASK_ENV=development
DEBUG=True
```

2. Teszt adatbázis használata:
```bash
# .env fájlban:
DATABASE_URL=sqlite:///test.db
```

3. Fejlesztői eszközök:
- VS Code vagy PyCharm IDE
- Git verziókezelő
- Postman vagy hasonló API tesztelő eszköz
- SQLite Browser az adatbázis kezeléséhez

## Fejlesztői útmutató

### Környezeti változók tesztelése
1. Környezeti változók ellenőrzése:
```python
from app import app
print(app.config['ADMIN_USERNAME'])  # Ellenőrizd, hogy betöltődik-e
```

2. Környezeti változók tesztelése fejlesztői módban:
```bash
# .env.test fájl létrehozása teszteléshez
cp .env.example .env.test
# Módosítsd a .env.test fájlt teszt értékekkel
```

### Adatbázis migráció tesztelése
```bash
# Új migráció létrehozása
flask db migrate -m "migration message"
# Migráció alkalmazása
flask db upgrade
```

## Gyakori kérdések (FAQ)

### Környezeti változók
Q: Miért nem működik a bejelentkezés?
A: Ellenőrizd a `.env` fájlt:
- A fájl létezik-e a projekt gyökérkönyvtárában
- A `ADMIN_USERNAME` és `ADMIN_PASSWORD` helyesen van-e beállítva
- A `SECRET_KEY` be van-e állítva

Q: Hogyan generáljak biztonságos SECRET_KEY-t?
A: Használd a Python secrets modult:
```bash
python -c 'import secrets; print(secrets.token_hex(32))'
```

### Adatbázis
Q: Miért nem jelennek meg az adatok?
A: Ellenőrizd:
- Az adatbázis migráció sikeresen lefutott-e
- A `DATABASE_URL` helyesen van-e beállítva
- Az adatbázis fájl létezik-e és olvasható-e

### Fájlkezelés
Q: Miért nem működik a fájlfeltöltés?
A: Ellenőrizd:
- A `UPLOAD_FOLDER` létezik-e és írható-e
- A fájl mérete nem haladja-e meg a `MAX_CONTENT_LENGTH` értékét
- A fájl típusa engedélyezett-e

## Licenc
Ez a projekt az MIT licenc alatt áll. Lásd a LICENSE fájlt részletekért.

## Kapcsolat
Kérdések, javaslatok: [email protected]

## Köszönet
Köszönjük minden közreműködőnek és tesztelőnek a segítségüket a projekt fejlesztésében!

## Központi telepítés
A rendszer központi szerveren való telepítéséhez kövesd az alábbi lépéseket:

1. Szerver előkészítése:
```bash
# Rendszerfrissítés
sudo apt update && sudo apt upgrade  # Debian/Ubuntu
sudo yum update  # CentOS/RHEL

# Szükséges csomagok telepítése
sudo apt install python3.11 python3.11-venv nginx supervisor  # Debian/Ubuntu
sudo yum install python3.11 nginx supervisor  # CentOS/RHEL
```

2. Alkalmazás telepítése:
```bash
# Alkalmazás klónozása
git clone https://github.com/hiimdavta/burabox_v1.0.0.git /opt/burabox
cd /opt/burabox

# Virtuális környezet létrehozása
python3.11 -m venv venv
source venv/bin/activate

# Függőségek telepítése
pip install -r requirements.txt
pip install gunicorn  # WSGI szerver
```

3. Környezeti változók beállítása:
```bash
# Biztonságos értékek generálása
python -c 'import secrets; print(secrets.token_hex(32))'  # SECRET_KEY
python -c 'import secrets; print(secrets.token_urlsafe(16))'  # Admin jelszó

# .env fájl létrehozása
cp .env.example .env
# Módosítsd a .env fájlt a generált értékekkel
```

4. Nginx konfiguráció:
```nginx
# /etc/nginx/sites-available/burabox
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5051;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static {
        alias /opt/burabox/static;
    }
}
```

5. Supervisor konfiguráció:
```ini
# /etc/supervisor/conf.d/burabox.conf
[program:burabox]
directory=/opt/burabox
command=/opt/burabox/venv/bin/gunicorn -w 4 -b 127.0.0.1:5051 app:app
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/burabox.err.log
stdout_logfile=/var/log/burabox.out.log
```

6. SSL/TLS beállítása (Let's Encrypt):
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## Biztonsági ellenőrzőlista
A telepítés előtt ellenőrizd a következőket:

### Környezeti változók
- [ ] `SECRET_KEY` be van állítva és biztonságos
- [ ] `ADMIN_PASSWORD` megváltoztatva az alapértelmezett értékről
- [ ] `FLASK_ENV=production` be van állítva
- [ ] `SESSION_COOKIE_SECURE=True` be van állítva

### Rendszer beállítások
- [ ] A `uploads` mappa jogosultságai korrekt beállítva
- [ ] Az adatbázis fájl jogosultságai korrekt beállítva
- [ ] A log fájlok jogosultságai korrekt beállítva
- [ ] SSL/TLS tanúsítvány telepítve és érvényes

### Alkalmazás beállítások
- [ ] Rate limiting be van állítva
- [ ] Fájlméret limit be van állítva
- [ ] Tiltott fájltípusok listája frissítve
- [ ] Session timeout be van állítva

## Verziókövetés
A projekt verzióit a [Semantic Versioning](https://semver.org/) követi (MAJOR.MINOR.PATCH):

### v1.0.0 (2024-03-XX)
- 🎉 Első stabil verzió
- 🔐 Környezeti változók bevezetése
- 🛡️ Biztonsági fejlesztések
- 📝 Dokumentáció bővítése

### v0.9.0 (2024-03-XX)
- ⚠️ Béta verzió
- 🔐 Alapvető biztonsági funkciók
- 📁 Fájlkezelés implementálása
- 👥 Felhasználói szerepkörök

## Fejlesztői útmutató

### Kód stílus
A projekt a PEP 8 kódolási stílust követi. A kód formázásához használd a `black` formázót:

```bash
# Black telepítése
pip install black

# Kód formázása
black .
```

### Commit üzenetek
A commit üzenetek követik a [Conventional Commits](https://www.conventionalcommits.org/) formátumot:

- `feat:` új funkció
- `fix:` hiba javítása
- `docs:` dokumentáció változtatás
- `style:` kód stílus változtatás
- `refactor:` kód refaktorálás
- `test:` tesztek hozzáadása/módosítása
- `chore:` build folyamat vagy segédeszközök változtatása

Példa:
```bash
git commit -m "feat: add environment variables support"
git commit -m "fix: correct file upload size limit"
```

### Tesztelés
A tesztek futtatása:
```bash
# Unit tesztek
python -m pytest tests/

# Kód lefedettség ellenőrzése
python -m pytest --cov=app tests/
```
