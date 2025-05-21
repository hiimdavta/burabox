# BuraBox - Iskolai Fájlkezelő Rendszer v1.0.4

## Leírás
BuraBox egy modern, biztonságos és felhasználóbarát iskolai fájlkezelő rendszer. A rendszer lehetővé teszi a tanárok és diákok számára a fájlok hatékony kezelését, feltöltését és megosztását osztályonként. A legújabb verzió (1.0.4) jelentős biztonsági és funkcionális fejlesztéseket tartalmaz.

## 🚀 Főbb funkciók
- 🔐 Többfaktoros bejelentkezési rendszer (admin, tanár, diák)
- 👥 Fejlett felhasználókezelés és szerepkörök
- 📁 Osztályonkénti fájlkezelés és megosztás
- ⬆️ Többfunkciós fájlműveletek:
  * Egyszeri és tömeges feltöltés
  * Biztonságos letöltés
  * Intelligens törlés
  * Automatikus fájlnév kezelés
- 🔍 Fejlett keresés és szűrés:
  * Fájlnév alapján
  * Feltöltési dátum szerint
  * Fájltípus szerint
  * Feltöltő szerint
- 📱 Modern, reszponzív felület:
  * Bootstrap 5 alapú design
  * Mobilbarát felület
  * Sötét/világos téma támogatás
- 🌐 Többnyelvű támogatás (Flask-Babel)
- 📧 Email értesítések (Flask-Mail)
- ⚡ Teljesítmény optimalizáció (Flask-Caching)

## 🛡️ Biztonsági funkciók
- 🔐 Fejlett felhasználókezelés:
  * Flask-Login integráció
  * Biztonságos session kezelés
  * Jelszó visszaállítás
- 🔑 Erős jelszókezelés:
  * bcrypt hashelés
  * Jelszó komplexitás ellenőrzés
  * Jelszó lejárat
- 📝 Fájlbiztonság:
  * MIME típus ellenőrzés
  * Fájlnév sanitizálás
  * Vírusellenőrzés integráció
- ⏱️ Rate limiting és DDoS védelem:
  * 120 kérés/percenként limit
  * IP alapú korlátozás
  * Brute force védelem
- 🔒 Adatbiztonság:
  * SQL injection védelem
  * XSS védelem
  * CSRF védelem
- 🛡️ Környezeti biztonság:
  * Környezeti változók használata
  * Biztonságos cookie kezelés
  * HTTPS kényszerítés

## 💻 Telepítés

### Előfeltételek
- Python 3.11 vagy újabb
- pip (Python csomagkezelő)
- libmagic (a python-magic csomaghoz)

### Rendszerkövetelmények
- macOS: `brew install libmagic`
- Linux: `apt-get install libmagic1` vagy `yum install file-libs`
- Windows: Automatikus telepítés a `setup_windows.bat` segítségével

### Telepítési lépések

#### Windows
1. Futtasd a `setup_windows.bat` fájlt
2. Kövesd a telepítő útmutatását
3. A telepítés után indítsd el a `start_server.bat` fájlt

#### macOS/Linux
1. Klónozd a repository-t:
```bash
git clone https://github.com/hiimdavta/burabox.git
cd burabox
```

2. Futtasd a telepítő szkriptet:
```bash
# macOS
chmod +x start_app.command
./start_app.command

# Linux
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Állítsd be a környezeti változókat:
```bash
cp .env.example .env
# Módosítsd a .env fájlt a saját beállításaiddal
```

4. Indítsd el a szervert:
```bash
python app.py
```

## ⚙️ Környezeti változók
A rendszer a következő környezeti változókat használja (`.env` fájlban):

### Kötelező beállítások
- `ADMIN_USERNAME`: Admin felhasználónév
- `ADMIN_PASSWORD`: Admin jelszó (kötelező megváltoztatni!)
- `SECRET_KEY`: Flask alkalmazás titkos kulcs
- `MAIL_SERVER`: SMTP szerver címe
- `MAIL_PORT`: SMTP szerver portja
- `MAIL_USERNAME`: SMTP felhasználónév
- `MAIL_PASSWORD`: SMTP jelszó

### Opcionális beállítások
- `FLASK_ENV`: Környezet típusa ('development' vagy 'production')
- `DATABASE_URL`: Adatbázis kapcsolati URL
- `MAX_CONTENT_LENGTH`: Maximális fájlméret (alapértelmezett: 15MB)
- `SESSION_COOKIE_SECURE`: Biztonságos cookie-k
- `PERMANENT_SESSION_LIFETIME`: Session élettartam
- `CACHE_TYPE`: Cache típusa (alapértelmezett: 'simple')
- `BABEL_DEFAULT_LOCALE`: Alapértelmezett nyelv
- `RATELIMIT_STORAGE_URL`: Rate limit tároló URL

## 🛠️ Fejlesztői információk

### Használt technológiák
- 🚀 Flask 3.0.2
- 🗄️ SQLAlchemy 2.0.27
- 👤 Flask-Login 0.6.3
- 📦 Flask-Migrate 4.0.5
- ⏱️ Flask-Limiter 3.5.0
- 🔍 python-magic 0.4.27
- 🎨 Bootstrap 5
- 🌐 Flask-Babel 4.0.0
- 📧 Flask-Mail 0.9.1
- ⚡ Flask-Caching 2.1.0
- 🛡️ Flask-Talisman 1.1.0

### Fejlesztői eszközök
- 🧪 Unit tesztek (unittest)
- 📝 Kód formázás (black)
- 🔍 Linting (flake8)
- 📊 Kód lefedettség (coverage)

## 📚 Dokumentáció
- [Telepítési útmutató](docs/INSTALL.md)
- [Fejlesztői dokumentáció](docs/DEVELOPMENT.md)
- [API dokumentáció](docs/API.md)
- [Biztonsági útmutató](docs/SECURITY.md)

## 🤝 Közreműködés
A projekt nyitott a közreműködésre! Kérjük, olvasd el a [közreműködési útmutatót](CONTRIBUTING.md) a részletekért.

## 📄 Licenc
Ez a projekt az MIT licenc alatt áll. Lásd a [LICENSE](LICENSE) fájlt részletekért.

## 📞 Kapcsolat
- Email: [email protected]
- GitHub Issues: [Problémák jelentése](https://github.com/hiimdavta/burabox/issues)
- Discord: [Közösségi szerver](https://discord.gg/burabox)

## 🙏 Köszönet
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
git clone https://github.com/hiimdavta/burabox.git /opt/burabox
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

### v1.0.4 (2024.03.21)
- Fájl feltöltési időpontok megjelenítésének módosítása (év.hónap.nap óra:perc formátum)
- Rendszer optimalizálások és hibajavítások
- Dokumentáció frissítése

### v1.0.3 (2024.03.20)
- Tanár vezérlőpult fejlesztése
- Fájl feltöltési időpontok megjelenítése
- Rendszer optimalizálások

### v1.0.0 (2024-03-XX)
- 🎉 Első stabil verzió
- 🔐 Környezeti változók bevezetése
- 🛡️ Biztonsági fejlesztések
- 📝 Dokumentáció bővítése

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
