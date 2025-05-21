import os
from datetime import datetime, timedelta, timezone
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory, jsonify, send_file
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from config import Config
from class_manager import ClassManager
import jwt
from functools import wraps
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import json
import humanize
import re
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import mimetypes
import time
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect
import flask_wtf.csrf
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField
from wtforms.validators import DataRequired
from sqlalchemy import inspect
import logging
import zipfile
from io import BytesIO
import shutil
import hashlib
from dotenv import load_dotenv
import pytz

# Környezeti változók betöltése
load_dotenv()

# Naplózás beállítása
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Debug: környezeti változók ellenőrzése
logger.debug("Environment variables after load_dotenv():")
logger.debug(f"ADMIN_USERNAME: {os.environ.get('ADMIN_USERNAME')}")
logger.debug(f"ADMIN_PASSWORD: {'*' * len(os.environ.get('ADMIN_PASSWORD', '')) if os.environ.get('ADMIN_PASSWORD') else 'None'}")
logger.debug(f"SECRET_KEY: {os.environ.get('SECRET_KEY')}")
logger.debug(f"DATABASE_URL: {os.environ.get('DATABASE_URL')}")

# Flask alkalmazás inicializálása
app = Flask(__name__)
app.config.from_object(Config)
Config.init_app(app)

# Debug mód és naplózás beállítása
app.debug = False
app.logger.setLevel(logging.DEBUG)

# Alapvető konfigurációk
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or os.urandom(32)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///school.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')

# Session és login beállítások
app.config['SESSION_COOKIE_SECURE'] = False  # Development módban False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)
app.config['MAX_CONTENT_LENGTH'] = 15 * 1024 * 1024  # 15MB max file size

# Login manager beállítások
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'  # Visszaállítva: admin_login
login_manager.login_message = 'Kérjük, jelentkezzen be a folytatáshoz.'
login_manager.login_message_category = 'info'
login_manager.session_protection = None  # Kikapcsoljuk a session védelmet

# CSRF védelem kikapcsolása belső hálózati használatra
app.config['WTF_CSRF_ENABLED'] = False
app.config['WTF_CSRF_CHECK_DEFAULT'] = False
csrf = CSRFProtect()
csrf.init_app(app)

# Adatbázis inicializálása
db = SQLAlchemy(app)

# Rate limiting beállítások
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["1000 per day", "200 per hour", "50 per minute"],
    storage_uri="memory://",
    strategy="fixed-window"
)

# Fájl feltöltés beállítások
ALLOWED_EXTENSIONS = {
    # Documents
    'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'rtf',
    # Images
    'jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg',
    # Archives
    'zip', 'rar', '7z',
    # Audio/Video
    'mp3', 'mp4', 'avi', 'mov', 'wav',
    # Other
    'csv', 'json', 'xml'
}

FORBIDDEN_MIME_TYPES = {
    'application/x-executable',
    'application/x-msdownload',
    'application/x-msdos-program',
    'application/x-msdos-windows',
    'application/x-dosexec',
    'application/x-shockwave-flash',
    'application/x-shellscript',
    'text/x-shellscript',
    'application/x-python-code',
    'text/x-python',
    'application/x-javascript',
    'text/javascript',
    'application/x-php',
    'text/x-php',
    'application/x-perl',
    'text/x-perl',
    'application/x-ruby',
    'text/x-ruby'
}

# Modellek
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='student')
    is_active = db.Column(db.Boolean, default=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Teacher(db.Model):
    __tablename__ = 'teachers'
    
    id = db.Column(db.Integer, primary_key=True)
    teacher_name = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    
    # Kapcsolatok
    classes = db.relationship('ClassTeacher', backref='teacher', lazy='joined')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(80), unique=True, nullable=False)
    class_name = db.Column(db.String(20), db.ForeignKey('classes.class_name'), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Kapcsolatok
    files = db.relationship('File', backref='student', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<Student {self.student_name}>'

class Class(db.Model):
    __tablename__ = 'classes'
    
    id = db.Column(db.Integer, primary_key=True)
    class_name = db.Column(db.String(20), unique=True, nullable=False)
    
    # Kapcsolatok
    students = db.relationship('Student', backref='class_ref', lazy='joined')
    teachers = db.relationship('ClassTeacher', backref='class_ref', lazy='joined')
    files = db.relationship('File', backref='class_ref', lazy='dynamic')

class ClassTeacher(db.Model):
    __tablename__ = 'class_teachers'
    
    id = db.Column(db.Integer, primary_key=True)
    class_name = db.Column(db.String(20), db.ForeignKey('classes.class_name'), nullable=False)
    teacher_name = db.Column(db.String(80), db.ForeignKey('teachers.teacher_name'), nullable=False)
    
    __table_args__ = (db.UniqueConstraint('class_name', 'teacher_name'),)

class File(db.Model):
    __tablename__ = 'files'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    student_name = db.Column(db.String(80), db.ForeignKey('students.student_name'), nullable=False)
    class_name = db.Column(db.String(20), db.ForeignKey('classes.class_name'), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    file_size = db.Column(db.Integer)
    file_type = db.Column(db.String(50))
    status = db.Column(db.String(20), default='active')

# Form osztályok
class LoginForm(FlaskForm):
    username = StringField('Felhasználónév', validators=[DataRequired()])
    password = PasswordField('Jelszó', validators=[DataRequired()])

# Segédfüggvények
def sanitize_filename(filename):
    """Fájlnév biztonságossá tétele."""
    base, ext = os.path.splitext(filename)
    base = re.sub(r'[^a-zA-Z0-9\-\_\.]', '_', base)
    if len(base) > 100:
        base = base[:100]
    return base + ext.lower()

def is_allowed_file(filename):
    """Engedélyezett fájltípus ellenőrzése."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_safe_mime_type(file_path):
    """Biztonságos MIME típus ellenőrzés."""
    try:
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type is None:
            ext = os.path.splitext(file_path)[1].lower()
            mime_type = mimetypes.types_map.get(ext, '')
        
        file_ext = os.path.splitext(file_path)[1].lower()
        FORBIDDEN_EXTENSIONS = {
            '.exe', '.dll', '.bat', '.cmd', '.sh', '.py', '.js', '.php', 
            '.pl', '.rb', '.vbs', '.ps1', '.msi', '.app', '.dmg'
        }
        
        if file_ext in FORBIDDEN_EXTENSIONS:
            return False
            
        return mime_type not in FORBIDDEN_MIME_TYPES
    except Exception:
        return False

def get_db_connection():
    """Adatbázis kapcsolat létrehozása."""
    conn = sqlite3.connect('school.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_user_role(username, user_type):
    """Felhasználó szerepkörének meghatározása."""
    if username == 'admin':
        return 'admin'
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if user_type == 'teacher':
        # Ellenőrizzük, hogy a felhasználó tanár-e
        cursor.execute('SELECT teacher_name FROM teachers WHERE teacher_name = ?', (username,))
        if cursor.fetchone():
            conn.close()
            return 'teacher'
    else:
        # Ellenőrizzük, hogy a felhasználó diák-e
        cursor.execute('SELECT student_name FROM students WHERE student_name = ?', (username,))
        if cursor.fetchone():
            conn.close()
            return 'student'
    
    conn.close()
    return None

def verify_password(username, password, user_type):
    """Jelszó ellenőrzése a felhasználó típusa alapján."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if user_type == 'teacher':
        # Admin és tanár jelszavak a teachers táblából
        cursor.execute('SELECT password FROM teachers WHERE teacher_name = ?', (username,))
    else:
        # Diák jelszavak a students táblából
        cursor.execute('SELECT password FROM students WHERE student_name = ?', (username,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result and check_password_hash(result['password'], password):
        return True
    return False

# Decoratorok
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Ellenőrizzük mind a session-t, mind a Flask-Login állapotot
        if not session.get('admin_logged_in') and (not current_user.is_authenticated or current_user.role != 'admin'):
            flash('Nincs megfelelő jogosultsága az oldal megtekintéséhez!', 'error')
            return redirect(url_for('simple_admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def teacher_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'teacher':
            app.logger.warning(f"Unauthorized access attempt to teacher-protected route by user: {getattr(current_user, 'username', None)} with role {getattr(current_user, 'role', None)}")
            flash('Nincs megfelelő jogosultsága az oldal megtekintéséhez!', 'error')
            return redirect(url_for('landing_page'))
        return f(*args, **kwargs)
    return decorated_function

def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'student':
            flash('Nincs megfelelő jogosultsága az oldal megtekintéséhez!', 'error')
            return redirect(url_for('landing_page'))
        return f(*args, **kwargs)
    return decorated_function

def class_auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Kérjük, jelentkezzen be a folytatáshoz!', 'error')
            return redirect(url_for('landing_page'))
        
        class_name = kwargs.get('class_name')
        if not class_name:
            class_name = request.form.get('class_name')
        
        if not class_name:
            flash('Hiányzó osztálynév!', 'error')
            return redirect(url_for('landing_page'))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if current_user.role == 'admin':
            cursor.execute('SELECT class_name FROM classes WHERE class_name = ?', (class_name,))
            if cursor.fetchone():
                conn.close()
                return f(*args, **kwargs)
        
        elif current_user.role == 'teacher':
            cursor.execute('''
                SELECT ct.teacher_name 
                FROM class_teachers ct 
                WHERE ct.teacher_name = ? AND ct.class_name = ?
            ''', (current_user.username, class_name))
            if cursor.fetchone():
                conn.close()
                return f(*args, **kwargs)
        
        elif current_user.role == 'student':
            cursor.execute('''
                SELECT s.student_name 
                FROM students s 
                WHERE s.student_name = ? AND s.class_name = ?
            ''', (current_user.username, class_name))
            if cursor.fetchone():
                conn.close()
                return f(*args, **kwargs)
        
        conn.close()
        flash('Nincs megfelelő jogosultsága az osztályhoz!', 'error')
        return redirect(url_for('landing_page'))
    
    return decorated_function

# User loader
@login_manager.user_loader
def load_user(user_id):
    try:
        user = User.query.get(int(user_id))
        if user:
            app.logger.debug(f"[user_loader] User loaded: {user.student_name}, role: {user.role}")
        else:
            app.logger.debug(f"[user_loader] No user found for ID: {user_id}")
        return user
    except Exception as e:
        app.logger.error(f"Error loading user {user_id}: {str(e)}")
        return None

# Error handlers
@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({
        'success': False,
        'message': 'A fájl mérete meghaladja a 15 MB-os limitet!'
    }), 413

@app.errorhandler(429)
def ratelimit_handler(error):
    return jsonify({
        'success': False,
        'message': 'Túl sok kérés! Kérjük, várjon egy kicsit!'
    }), 429

# Állítsuk be a magyar időzónát
HUNGARY_TZ = pytz.timezone('Europe/Budapest')

@app.template_filter('datetime')
def format_datetime(timestamp, format='%Y-%m-%d %H:%M:%S'):
    """Formázza az időbélyegot a megadott formátumban, magyar időzónára konvertálva"""
    if isinstance(timestamp, datetime):
        # Ha már datetime objektum, konvertáljuk UTC-ről magyar időzónára
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        local_time = timestamp.astimezone(HUNGARY_TZ)
    else:
        # Ha timestamp, konvertáljuk UTC-ről magyar időzónára
        dt = datetime.fromtimestamp(timestamp, timezone.utc)
        local_time = dt.astimezone(HUNGARY_TZ)
    return local_time.strftime(format)

@app.template_filter('humanize_datetime')
def humanize_datetime(timestamp):
    """Emberi olvasható formátumban jeleníti meg az időt, magyar időzónára konvertálva"""
    if isinstance(timestamp, datetime):
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        local_time = timestamp.astimezone(HUNGARY_TZ)
    else:
        dt = datetime.fromtimestamp(timestamp, timezone.utc)
        local_time = dt.astimezone(HUNGARY_TZ)
    return humanize.naturaltime(datetime.now(HUNGARY_TZ) - local_time)

def get_current_time():
    """Visszaadja az aktuális időt magyar időzónában"""
    return datetime.now(HUNGARY_TZ)

def get_student_files(student_name, class_name):
    """Diák fájljainak lekérése."""
    try:
        # SQLAlchemy ORM lekérdezés a közvetlen SQL helyett
        files_query = File.query.filter_by(
            student_name=student_name, 
            class_name=class_name
        ).order_by(File.uploaded_at.desc()).all()
        
        files = []
        for file in files_query:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], class_name, file.filename)
            if os.path.exists(file_path):
                files.append({
                    'id': file.id,
                    'filename': file.filename,
                    'original_filename': file.original_filename,
                    'uploaded_at': file.uploaded_at,
                    'size': os.path.getsize(file_path)
                })
        
        return files
    except Exception as e:
        app.logger.error(f"Hiba a fájlok lekérése közben: {str(e)}")
        return []

def ensure_upload_folder():
    """Upload mappa létrehozása, ha nem létezik."""
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

# Route-ok
@app.route('/')
@app.route('/landing_page')
def landing_page():
    """Bejelentkezési oldal."""
    app.logger.debug(f"Landing page accessed. Current user: {current_user.student_name if current_user.is_authenticated else 'Not authenticated'}")
    
    if current_user.is_authenticated:
        app.logger.info(f"User {current_user.student_name} is authenticated with role {current_user.role}")
        if current_user.role == 'admin':
            app.logger.debug(f"Redirecting admin user {current_user.student_name} to admin dashboard")
            return redirect(url_for('admin_dashboard'))
        elif current_user.role == 'teacher':
            app.logger.debug(f"Redirecting teacher user {current_user.student_name} to teacher dashboard")
            return redirect(url_for('teacher_dashboard'))
        elif current_user.role == 'student':
            app.logger.debug(f"Redirecting student user {current_user.student_name} to upload_page")
            return redirect(url_for('upload_page'))
    
    app.logger.debug("Rendering landing page for unauthenticated user")
    return render_template('landing.html', title='Bejelentkezés')

@app.route('/logout')
@login_required
def logout():
    """Kijelentkezés kezelése."""
    logout_user()
    session.clear()
    return redirect(url_for('landing_page'))

@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    app.logger.debug(f"[admin_dashboard] START - current_user.is_authenticated: {current_user.is_authenticated}")
    app.logger.debug(f"[admin_dashboard] current_user: {getattr(current_user, 'student_name', None)}, role: {getattr(current_user, 'role', None)}")
    
    if not current_user.is_authenticated or current_user.role != 'admin':
        app.logger.warning(f"Unauthorized access attempt to admin dashboard by user: {getattr(current_user, 'student_name', None)} with role {getattr(current_user, 'role', None)}")
        logout_user()
        flash('Nincs megfelelő jogosultsága az oldal megtekintéséhez!', 'error')
        return redirect(url_for('admin_login'))
    
    app.logger.debug(f"[admin_dashboard] User authenticated as admin: {current_user.student_name}")
    
    try:
        app.logger.debug("Fetching admin dashboard data")
        
        # Adatbázis kapcsolat létrehozása
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Osztályok lekérése
        cursor.execute('SELECT class_name FROM classes ORDER BY class_name')
        classes = [row[0] for row in cursor.fetchall()]
        
        # Tanárok lekérése
        cursor.execute('SELECT teacher_name FROM teachers ORDER BY teacher_name')
        teachers = [row[0] for row in cursor.fetchall()]
        
        # Diákok lekérése osztályonként
        cursor.execute('''
            SELECT student_name, class_name 
            FROM students 
            ORDER BY class_name, student_name
        ''')
        students = [{'name': row[0], 'class': row[1]} for row in cursor.fetchall()]
        
        # Osztályonkénti tanulószám
        class_student_counts = {}
        cursor.execute('''
            SELECT class_name, COUNT(*) as count 
            FROM students 
            GROUP BY class_name
        ''')
        for row in cursor.fetchall():
            class_student_counts[row[0]] = row[1]
        
        # Osztályokhoz rendelt tanárok
        class_teachers = {}
        cursor.execute('''
            SELECT class_name, teacher_name 
            FROM class_teachers
        ''')
        for row in cursor.fetchall():
            class_teachers[row[0]] = row[1]
        
        # Tanárok osztályai
        teacher_classes = {}
        cursor.execute('''
            SELECT teacher_name, GROUP_CONCAT(class_name) as classes
            FROM class_teachers
            GROUP BY teacher_name
        ''')
        for row in cursor.fetchall():
            teacher_classes[row[0]] = row[1].split(',') if row[1] else []
        
        # Feltöltések száma osztályonként
        class_upload_counts = {}
        cursor.execute('''
            SELECT class_name, COUNT(*) as count 
            FROM files 
            GROUP BY class_name
        ''')
        for row in cursor.fetchall():
            class_upload_counts[row[0]] = row[1]
        
        # Feltöltések száma diákonként
        student_upload_counts = {}
        file_counts = db.session.query(
            File.student_name, 
            db.func.count(File.id).label('count')
        ).group_by(File.student_name).all()
        
        for student_name, count in file_counts:
            student_upload_counts[student_name] = count
        
        conn.close()
        
        app.logger.info("Successfully loaded admin dashboard data")
        
        return render_template('simple_admin_dashboard.html',
                            title='Admin Vezérlőpult',
                            classes=classes,
                            teachers=teachers,
                            students=students,
                            class_student_counts=class_student_counts,
                            class_teachers=class_teachers,
                            teacher_classes=teacher_classes,
                            class_upload_counts=class_upload_counts,
                            student_upload_counts=student_upload_counts)
    except Exception as e:
        app.logger.error(f"Admin dashboard error: {str(e)}")
        flash(f'Hiba történt: {str(e)}', 'error')
        return redirect(url_for('admin_login'))

@app.route('/teacher_dashboard')
@app.route('/teacher_dashboard/<int:page>')
@teacher_required
def teacher_dashboard(page=1):
    """Tanár vezérlőpult."""
    app.logger.debug("Teacher dashboard accessed")
    
    try:
        teacher_name = current_user.student_name
        per_page = 20  # Egy oldalon megjelenő elemek száma
        
        # Frissítjük az utolsó bejelentkezés időpontját
        current_user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Ellenőrizzük, hogy a tanár létezik-e
        teacher = Teacher.query.filter_by(teacher_name=teacher_name).first()
        if not teacher:
            app.logger.error(f"Teacher not found in database: {teacher_name}")
            logout_user()
            flash('Hiba történt a tanár adatok betöltése közben!', 'error')
            return redirect(url_for('landing_page'))
        
        # Tanár osztályainak lekérése
        assigned_classes = [ct.class_name for ct in ClassTeacher.query.filter_by(teacher_name=teacher_name).all()]
        app.logger.debug(f"Assigned classes for teacher {teacher_name}: {assigned_classes}")
        
        if not assigned_classes:
            flash('Nincs hozzárendelt osztálya!', 'info')
            return render_template('teacher_dashboard.html',
                                title='Tanár Vezérlőpult',
                                teacher_name=teacher_name,
                                class_files={},
                                last_login=current_user.last_login)
        
        # Keresési és szűrési paraméterek
        search_query = request.args.get('search', '')
        sort_by = request.args.get('sort_by', 'uploaded_at')
        sort_order = request.args.get('sort_order', 'desc')
        student_filter = request.args.get('student', '')
        date_filter = request.args.get('date', '')
        
        class_files = {}
        total_pages = {}
        class_students = {}
        
        for class_name in assigned_classes:
            try:
                # Alap lekérdezés építése
                query = File.query.filter_by(class_name=class_name)
                
                # Keresés alkalmazása
                if search_query:
                    query = query.filter(
                        (File.original_filename.ilike(f'%{search_query}%')) |
                        (File.student_name.ilike(f'%{search_query}%'))
                    )
                
                # Diák szűrő
                if student_filter:
                    query = query.filter(File.student_name == student_filter)
                
                # Dátum szűrő
                if date_filter:
                    try:
                        filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
                        next_day = filter_date + timedelta(days=1)
                        query = query.filter(
                            File.uploaded_at >= filter_date,
                            File.uploaded_at < next_day
                        )
                    except ValueError:
                        app.logger.error(f"Invalid date format: {date_filter}")
                
                # Fájlok lekérése és méret hozzáadása
                files_query = query.all()
                files = []
                for file in files_query:
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], class_name, file.filename)
                    if os.path.exists(file_path):
                        file_size = os.path.getsize(file_path)
                        file_extension = os.path.splitext(file.original_filename)[1].lower()
                        files.append({
                            'id': file.id,
                            'filename': file.filename,
                            'original_filename': file.original_filename,
                            'student_name': file.student_name,
                            'uploaded_at': file.uploaded_at,
                            'size': file_size,
                            'file_extension': file_extension
                        })
                
                # Rendezés a memóriában
                if sort_by == 'filename':
                    files.sort(key=lambda x: x['original_filename'].lower(), reverse=(sort_order == 'desc'))
                elif sort_by == 'student':
                    files.sort(key=lambda x: x['student_name'].lower(), reverse=(sort_order == 'desc'))
                elif sort_by == 'size':
                    files.sort(key=lambda x: x['size'], reverse=(sort_order == 'desc'))
                elif sort_by == 'filetype':
                    files.sort(key=lambda x: x['file_extension'], reverse=(sort_order == 'desc'))
                else:  # default: uploaded_at
                    files.sort(key=lambda x: x['uploaded_at'], reverse=(sort_order == 'desc'))
                
                # Lapozás
                total_items = len(files)
                total_pages[class_name] = (total_items + per_page - 1) // per_page
                start_idx = (page - 1) * per_page
                end_idx = start_idx + per_page
                files = files[start_idx:end_idx]
                
                class_files[class_name] = files
                
                # Az osztály diákjainak lekérése
                students = Student.query.filter_by(class_name=class_name).all()
                class_students[class_name] = sorted([s.student_name for s in students])
                
            except Exception as e:
                app.logger.error(f'Error loading files for class {class_name}: {str(e)}')
                flash(f'Hiba történt a {class_name} osztály fájljainak betöltése közben: {str(e)}', 'error')
                continue
        
        return render_template('teacher_dashboard.html',
                            title='Tanár Vezérlőpult',
                            teacher_name=teacher_name,
                            class_files=class_files,
                            current_page=page,
                            total_pages=total_pages,
                            search_query=search_query,
                            sort_by=sort_by,
                            sort_order=sort_order,
                            student_filter=student_filter,
                            date_filter=date_filter,
                            class_students=class_students,
                            last_login=current_user.last_login)
                            
    except Exception as e:
        app.logger.error(f'Teacher dashboard error: {str(e)}')
        flash(f'Hiba történt: {str(e)}', 'error')
        return redirect(url_for('landing_page'))

# Új template filter a fájl kiterjesztés kezeléséhez
@app.template_filter('file_extension')
def file_extension(filename):
    """Visszaadja a fájl kiterjesztését."""
    ext = os.path.splitext(filename)[1].lower()
    if not ext:
        return 'Nincs'
    return ext[1:].upper()  # Eltávolítjuk a pontot és nagybetűssé alakítjuk

@app.route('/upload_page')
@student_required
def upload_page():
    """Fájl feltöltési oldal."""
    try:
        student_name = current_user.student_name
        
        # Lekérjük a diák osztályát
        student = Student.query.filter_by(student_name=student_name).first()
        if not student:
            flash('Nem található osztály a diákhoz!', 'error')
            return redirect(url_for('landing_page'))
        
        class_name = student.class_name
        files = get_student_files(student_name, class_name)
        
        # Ellenőrizzük, hogy a template létezik-e
        try:
            app.logger.debug(f"Rendering upload_page.html for student {student_name}, class {class_name}")
            return render_template('upload_page.html',
                                title='Fájl Feltöltés',
                                student_name=student_name,
                                class_name=class_name,
                                files=files)
        except Exception as template_error:
            app.logger.error(f"Template error: {str(template_error)}")
            flash(f'Hiba a sablon betöltése közben: {str(template_error)}', 'error')
            return redirect(url_for('landing_page'))
            
    except Exception as e:
        app.logger.error(f'Upload page error: {str(e)}')
        flash(f'Hiba történt: {str(e)}', 'error')
        return redirect(url_for('landing_page'))

@app.route('/upload_file', methods=['POST'])
@student_required
@limiter.limit("120 per minute")
def upload_file():
    """Fájl feltöltése."""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'Nincs kiválasztott fájl!'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'Nincs kiválasztott fájl!'}), 400
        
        if not is_allowed_file(file.filename):
            return jsonify({'success': False, 'message': 'Nem engedélyezett fájltípus!'}), 400
        
        student_name = current_user.student_name
        
        # Lekérjük a diák osztályát
        student = Student.query.filter_by(student_name=student_name).first()
        if not student:
            return jsonify({'success': False, 'message': 'Nem található osztály a diákhoz!'}), 400
        
        class_name = student.class_name
        
        # Fájl mentése
        filename = secure_filename(file.filename)
        timestamp = int(time.time())
        safe_filename = f"{timestamp}_{sanitize_filename(filename)}"
        
        upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], class_name)
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, safe_filename)
        file.save(file_path)
        
        if not is_safe_mime_type(file_path):
            os.remove(file_path)
            return jsonify({'success': False, 'message': 'Nem biztonságos fájltípus!'}), 400
        
        # Fájl adatok mentése az adatbázisba
        new_file = File(
            filename=safe_filename,
            original_filename=filename,
            student_name=student_name,
            class_name=class_name,
            uploaded_at=datetime.now(HUNGARY_TZ)  # Módosítva: magyar időzóna
        )
        db.session.add(new_file)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'A fájl sikeresen feltöltve!',
            'filename': filename,
            'timestamp': timestamp
        })
    except Exception as e:
        app.logger.error(f'File upload error: {str(e)}')
        return jsonify({'success': False, 'message': f'Hiba történt: {str(e)}'}), 500

@app.route('/student-login', methods=['GET', 'POST'])
def student_login():
    form = LoginForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        try:
            # Ellenőrizzük a diák létezését és jelszavát
            student = Student.query.filter_by(student_name=username).first()
            
            if student is None:
                flash('Hibás felhasználónév vagy jelszó!', 'error')
                return render_template('student_login.html', title='Diák bejelentkezés', form=form)
            
            if not student.check_password(password):
                flash('Hibás felhasználónév vagy jelszó!', 'error')
                return render_template('student_login.html', title='Diák bejelentkezés', form=form)
            
            # Sikeres bejelentkezés
            session['logged_in'] = True
            session['student_name'] = username
            session['role'] = 'student'
            session['class_name'] = student.class_name
            
            # User objektum létrehozása vagy frissítése a Flask-Login számára
            user = User.query.filter_by(student_name=username).first()
            if not user:
                user = User(
                    student_name=username,
                    email=f"{username}@student.school.com",
                    role='student'
                )
                user.password_hash = student.password_hash
                db.session.add(user)
                db.session.commit()
            
            # Bejelentkeztetjük a felhasználót
            login_user(user)
            
            # Átirányítás a fájlfeltöltő oldalra
            return redirect(url_for('upload_page'))
            
        except Exception as e:
            app.logger.error(f"Error during student login: {str(e)}")
            flash('Hiba történt a bejelentkezés során!', 'error')
            return render_template('student_login.html', title='Diák bejelentkezés', form=form)
    
    # GET kérés vagy sikertelen form validáció esetén
    return render_template('student_login.html', title='Diák bejelentkezés', form=form)

@app.route('/teacher-login', methods=['GET', 'POST'])
def teacher_login():
    app.logger.debug("Teacher login route accessed")
    
    # Ha már be van jelentkezve és tanár, akkor irányítsuk át a dashboardra
    if current_user.is_authenticated and current_user.role == 'teacher':
        return redirect(url_for('teacher_dashboard'))
    elif current_user.is_authenticated:
        logout_user()
        return redirect(url_for('landing_page'))
    
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        try:
            # Ellenőrizzük a tanár létezését és jelszavát
            teacher = Teacher.query.filter_by(teacher_name=username).first()
            
            if teacher is None:
                app.logger.error(f"Teacher not found: {username}")
                flash('Hibás felhasználónév vagy jelszó!', 'error')
                return render_template('teacher_login.html', form=form)
            
            if not teacher.check_password(password):
                app.logger.error(f"Invalid password for teacher: {username}")
                flash('Hibás felhasználónév vagy jelszó!', 'error')
                return render_template('teacher_login.html', form=form)
            
            # Ha idáig eljutottunk, akkor sikeres a bejelentkezés
            # Keressük meg vagy hozzuk létre a User objektumot
            user = User.query.filter_by(student_name=username).first()
            if not user:
                user = User(
                    student_name=username,
                    email=f"{username}@school.com",
                    role='teacher'
                )
                user.password_hash = teacher.password_hash  # Használjuk ugyanazt a jelszó hash-t
                db.session.add(user)
                db.session.commit()
            
            # Bejelentkeztetjük a felhasználót
            login_user(user)
            app.logger.info(f"Successful teacher login: {username}")
            return redirect(url_for('teacher_dashboard'))
            
        except Exception as e:
            app.logger.error(f'Teacher login error: {str(e)}')
            flash('Bejelentkezési hiba történt! Kérjük, próbálja újra később.', 'error')
    
    return render_template('teacher_login.html', form=form)

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    """Átirányítás az egyszerű admin bejelentkezésre."""
    return redirect(url_for('simple_admin_login'))

@app.route('/simple-admin-login', methods=['GET', 'POST'])
def simple_admin_login():
    app.logger.debug("Simple admin login route accessed")
    
    # Ha már be van jelentkezve és admin, akkor irányítsuk át a dashboardra
    if session.get('admin_logged_in'):
        return redirect(url_for('simple_admin_dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        app.logger.debug(f"Login attempt with username: {username}")
        
        # Egyszerű admin bejelentkezés
        admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
        admin_password = os.environ.get('ADMIN_PASSWORD')
        if username == admin_username and password == admin_password:
            # Sikeres bejelentkezés - beállítjuk a session változót
            session['admin_logged_in'] = True
            session['student_name'] = username
            
            # Admin user létrehozása vagy betöltése Flask-Login számára
            user = User.query.filter_by(student_name=admin_username).first()
            if not user:
                user = User(student_name=admin_username, email='admin@school.com', role='admin')
                user.set_password(admin_password)
                db.session.add(user)
                db.session.commit()
            
            # Admin bejelentkeztetése Flask-Login-nal
            login_user(user)
            
            flash('Sikeres bejelentkezés!', 'success')
            return redirect(url_for('simple_admin_dashboard'))
        else:
            flash('Hibás felhasználónév vagy jelszó!', 'error')
    
    return render_template('admin_login.html')

@app.route('/simple-admin-dashboard')
def simple_admin_dashboard():
    app.logger.debug("Simple admin dashboard route accessed")
    app.logger.debug(f"Session: {session}")
    
    # Ellenőrizzük, hogy admin be van-e jelentkezve
    if not session.get('admin_logged_in'):
        flash('Kérjük, jelentkezzen be admin jogosultsággal!', 'error')
        return redirect(url_for('simple_admin_login'))
    
    try:
        # Egyszerű statisztikák az adatbázisból
        with app.app_context():
            teacher_count = Teacher.query.count()
            class_count = Class.query.count()
            student_count = Student.query.count()
            
            # Osztályok lekérése
            classes = Class.query.all()
            class_data = [{'id': c.id, 'class_name': c.class_name} for c in classes]
            
            # Tanárok lekérése
            teachers = Teacher.query.all()
            teacher_data = [{'id': t.id, 'teacher_name': t.teacher_name} for t in teachers]
            
            # Diákok lekérése
            students = Student.query.all()
            student_data = [{'id': s.id, 'student_name': s.student_name, 'class_name': s.class_name} for s in students]
            
            # Osztály-tanár kapcsolatok
            class_teachers = {}
            for ct in ClassTeacher.query.all():
                class_teachers[ct.class_name] = ct.teacher_name
            
            # Osztályonkénti diákok száma
            class_student_counts = {}
            for s in students:
                class_student_counts[s.class_name] = class_student_counts.get(s.class_name, 0) + 1
            
            # Osztályonkénti feltöltések száma
            class_upload_counts = {}
            for f in File.query.all():
                class_upload_counts[f.class_name] = class_upload_counts.get(f.class_name, 0) + 1
            
            # Diákonkénti feltöltések száma
            student_upload_counts = {}
            for f in File.query.all():
                student_upload_counts[f.student_name] = student_upload_counts.get(f.student_name, 0) + 1
        
        return render_template('simple_admin_dashboard.html',
                           title='Admin Vezérlőpult',
                           teachers=teacher_data,
                           classes=class_data,
                           students=student_data,
                           class_student_counts=class_student_counts,
                           class_teachers=class_teachers,
                           class_upload_counts=class_upload_counts,
                           student_upload_counts=student_upload_counts,
                           teacher_count=teacher_count,
                           class_count=class_count,
                           student_count=student_count)
                           
    except Exception as e:
        app.logger.error(f"Simple admin dashboard error: {str(e)}")
        flash(f'Hiba történt: {str(e)}', 'error')
        return redirect(url_for('simple_admin_login'))

@app.route('/simple-logout')
def simple_logout():
    session.pop('admin_logged_in', None)
    session.pop('student_name', None)
    logout_user()
    return redirect(url_for('landing_page'))

# Főoldal átirányítása az egyszerű admin bejelentkezésre
@app.route('/')
def index():
    """Főoldal - átirányít az egyszerű admin bejelentkezésre."""
    return redirect(url_for('simple_admin_login'))

# Törlés route-ok
@app.route('/delete_class', methods=['POST'])
@admin_required
def delete_class():
    """Osztály törlése az adatbázisból és a fájlrendszerből."""
    app.logger.debug("Delete class request: %s", request.form)
    
    # Támogatjuk mind a class_id, mind a class_name paramétert
    class_id = request.form.get('class_id')
    class_name = request.form.get('class_name')
    confirmed = request.form.get('confirmed') == 'true'
    
    if not class_id and not class_name:
        return jsonify({
            'success': False,
            'message': 'Hiányzó osztály azonosító!'
        })
    
    try:
        # Ha class_id van megadva, az alapján keressük meg az osztályt
        if class_id:
            class_obj = Class.query.get(class_id)
        else:
            class_obj = Class.query.filter_by(class_name=class_name).first()
            
        if not class_obj:
            return jsonify({
                'success': False,
                'message': f'Az osztály nem található!'
            })
            
        class_name = class_obj.class_name  # Használjuk az osztály tényleges nevét
            
        # Ellenőrizzük, hogy vannak-e diákok az osztályban
        student_count = Student.query.filter_by(class_name=class_name).count()
        if student_count > 0 and not confirmed:
            return jsonify({
                'warning': True,
                'message': f'Az osztályban {student_count} diák van. Biztosan törölni szeretné az osztályt és a hozzá tartozó összes diákot?'
            })

        # Ha megerősítették a törlést vagy nincs diák, töröljük az osztályt
        # Először töröljük a kapcsolódó fájlokat
        files = File.query.filter_by(class_name=class_name).all()
        for file in files:
            try:
                # Töröljük a fájlt a fájlrendszerből
                if hasattr(file, 'file_path') and file.file_path:
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.file_path)
                    if os.path.exists(file_path):
                        os.remove(file_path)
                # Töröljük a fájl rekordot az adatbázisból
                db.session.delete(file)
            except Exception as e:
                app.logger.error(f"Hiba a fájl törlése közben: {str(e)}")
                raise
        
        # Töröljük a diákokat
        Student.query.filter_by(class_name=class_name).delete()
        
        # Töröljük a tanár-osztály kapcsolatokat
        ClassTeacher.query.filter_by(class_name=class_name).delete()
        
        # Töröljük az osztályt
        db.session.delete(class_obj)
        
        # Töröljük a mappát
        class_folder = os.path.join(app.config['UPLOAD_FOLDER'], class_name)
        if os.path.exists(class_folder):
            try:
                shutil.rmtree(class_folder)
            except Exception as e:
                app.logger.error(f"Hiba a mappa törlése közben: {str(e)}")
        
        db.session.commit()
        return jsonify({
            'success': True,
            'message': f'Az osztály ({class_name}) sikeresen törölve!'
        })
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Hiba az osztály törlése közben: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Hiba történt: {str(e)}'
        })

@app.route('/edit_class_post', methods=['POST'])
def edit_class_post():
    """Osztály nevének módosítása."""
    try:
        class_id = request.form.get('class_id')
        original_class_name = request.form.get('original_class_name')
        new_class_name = request.form.get('class_name')
        
        if not all([class_id, original_class_name, new_class_name]):
            return jsonify({
                'success': False,
                'message': 'Hiányzó adatok!'
            })
            
        # Osztály lekérése ID alapján
        class_record = Class.query.get(class_id)
        if not class_record:
            return jsonify({
                'success': False,
                'message': 'Az osztály nem található!'
            })
            
        # Ha a név nem változott, nincs teendő
        if original_class_name == new_class_name:
            return jsonify({
                'success': True,
                'message': 'Az osztály neve nem változott.'
            })
            
        # Ellenőrizzük, hogy az új név nem foglalt-e
        existing_class = Class.query.filter_by(class_name=new_class_name).first()
        if existing_class and existing_class.id != int(class_id):
            return jsonify({
                'success': False,
                'message': 'Ez az osztálynév már foglalt!'
            })
            
        # Mappa átnevezése
        old_folder = os.path.join(app.config['UPLOAD_FOLDER'], original_class_name)
        new_folder = os.path.join(app.config['UPLOAD_FOLDER'], new_class_name)
        
        try:
            if os.path.exists(old_folder):
                os.rename(old_folder, new_folder)
                app.logger.info(f"Mappa átnevezve: {old_folder} -> {new_folder}")
        except Exception as e:
            app.logger.error(f"Hiba a mappa átnevezése közben: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Hiba történt a mappa átnevezése közben: {str(e)}'
            })
            
        try:
            # Adatbázis tranzakció kezdése
            with db.session.begin_nested():
                # Osztály nevének frissítése
                class_record.class_name = new_class_name
                
                # Diákok frissítése
                Student.query.filter_by(class_name=original_class_name).update(
                    {Student.class_name: new_class_name},
                    synchronize_session=False
                )
                
                # Tanárok frissítése a ClassTeacher táblában
                ClassTeacher.query.filter_by(class_name=original_class_name).update(
                    {ClassTeacher.class_name: new_class_name},
                    synchronize_session=False
                )
                
                # Fájlok frissítése
                File.query.filter_by(class_name=original_class_name).update(
                    {File.class_name: new_class_name},
                    synchronize_session=False
                )
                
            # Tranzakció véglegesítése
            db.session.commit()
            app.logger.info(f"Osztály átnevezve: {original_class_name} -> {new_class_name}")
            
            return jsonify({
                'success': True,
                'message': f'Az osztály sikeresen átnevezve: {original_class_name} -> {new_class_name}'
            })
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Hiba az osztály frissítése közben: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Hiba történt: {str(e)}'
            })
            
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Hiba az osztály módosítása közben: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Hiba történt: {str(e)}'
        })

@app.route('/admin/classes')
@login_required
@admin_required
def admin_classes():
    app.logger.debug("Admin classes accessed")
    app.logger.debug(f"Session: {session}")
    
    # Ellenőrizzük, hogy admin be van-e jelentkezve
    if not session.get('admin_logged_in'):
        flash('Kérjük, jelentkezzen be admin jogosultsággal!', 'error')
        return redirect(url_for('simple_admin_login'))
    
    try:
        # Osztályok lekérése
        classes = Class.query.all()
        app.logger.debug(f"Classes: {classes}")
        
        class_data = []
        for class_obj in classes:
            class_data.append({
                'id': class_obj.id,
                'name': class_obj.class_name,
                'student_count': Student.query.filter_by(class_name=class_obj.class_name).count(),
                'teacher_count': ClassTeacher.query.filter_by(class_name=class_obj.class_name).count(),
                'upload_count': File.query.filter_by(class_name=class_obj.class_name).count()
            })
        
        return render_template('admin_classes.html',
                               title='Admin Osztályok',
                               classes=class_data)
    except Exception as e:
        app.logger.error(f"Admin classes error: {str(e)}")
        flash(f'Hiba történt: {str(e)}', 'error')
        return redirect(url_for('simple_admin_login'))

@app.route('/get_classes', methods=['GET'])
@login_required
@admin_required
def get_classes():
    try:
        classes = Class.query.all()
        return jsonify({
            'success': True,
            'classes': [{'class_name': c.class_name} for c in classes]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/create_class', methods=['POST'])
@login_required
@admin_required
def create_class():
    """Új osztály létrehozása."""
    try:
        class_name = request.form.get('class_name')
        
        if not class_name:
            return jsonify({
                'success': False,
                'message': 'Az osztály neve kötelező!'
            })
            
        # Ellenőrizzük, hogy az osztálynév nem foglalt-e
        existing_class = Class.query.filter_by(class_name=class_name).first()
        if existing_class:
            return jsonify({
                'success': False,
                'message': 'Ez az osztálynév már foglalt!'
            })
            
        # Létrehozzuk az osztályt az adatbázisban
        new_class = Class(class_name=class_name)
        db.session.add(new_class)
        
        # Létrehozzuk az osztály mappáját
        class_folder = os.path.join(app.config['UPLOAD_FOLDER'], class_name)
        try:
            os.makedirs(class_folder, exist_ok=True)
            app.logger.info(f"Osztály mappa létrehozva: {class_folder}")
        except Exception as e:
            app.logger.error(f"Hiba az osztály mappa létrehozása közben: {str(e)}")
            db.session.rollback()
            return jsonify({
                'success': False,
                'message': f'Hiba történt a mappa létrehozása közben: {str(e)}'
            })
        
        db.session.commit()
        app.logger.info(f"Új osztály létrehozva: {class_name}")
        
        return jsonify({
            'success': True,
            'message': f'Az osztály ({class_name}) sikeresen létrehozva!'
        })
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Hiba az osztály létrehozása közben: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Hiba történt: {str(e)}'
        })

@app.route('/create_teacher', methods=['POST'])
@login_required
@admin_required
def create_teacher():
    try:
        teacher_name = request.form.get('teacher_name')
        password = request.form.get('password')

        if not teacher_name or not password:
            return jsonify({
                'success': False,
                'message': 'A tanár neve és jelszava megadása kötelező'
            }), 400

        # Ellenőrizzük, hogy létezik-e már a tanár
        existing_teacher = Teacher.query.filter_by(teacher_name=teacher_name).first()
        if existing_teacher:
            return jsonify({
                'success': False,
                'message': 'Ez a tanár már létezik'
            }), 400

        # Új tanár létrehozása
        new_teacher = Teacher(teacher_name=teacher_name)
        new_teacher.set_password(password)
        db.session.add(new_teacher)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'A tanár sikeresen létrehozva'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/edit_teacher', methods=['POST'])
@login_required
@admin_required
def edit_teacher():
    try:
        teacher_id = request.form.get('teacher_id')
        teacher_name = request.form.get('teacher_name')
        password = request.form.get('password')

        if not teacher_id or not teacher_name:
            return jsonify({
                'success': False,
                'message': 'A tanár azonosítója és neve megadása kötelező'
            }), 400

        # Tanár keresése
        teacher = Teacher.query.get(teacher_id)
        if not teacher:
            return jsonify({
                'success': False,
                'message': 'A tanár nem található'
            }), 404

        # Ellenőrizzük, hogy a név nem foglalt-e
        if teacher_name != teacher.teacher_name:
            existing_teacher = Teacher.query.filter_by(teacher_name=teacher_name).first()
            if existing_teacher:
                return jsonify({
                    'success': False,
                    'message': 'Ez a tanárnév már foglalt'
                }), 400

        # Tanár adatainak frissítése
        teacher.teacher_name = teacher_name
        if password:
            teacher.set_password(password)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'A tanár adatai sikeresen frissítve'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/delete_teacher', methods=['POST'])
@login_required
@admin_required
def delete_teacher():
    try:
        teacher_id = request.form.get('teacher_id')
        if not teacher_id:
            return jsonify({
                'success': False,
                'message': 'A tanár azonosítója megadása kötelező'
            }), 400

        # Tanár keresése
        teacher = Teacher.query.get(teacher_id)
        if not teacher:
            return jsonify({
                'success': False,
                'message': 'A tanár nem található'
            }), 404

        # Tanár törlése
        db.session.delete(teacher)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'A tanár sikeresen törölve'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/create_student', methods=['POST'])
@login_required
@admin_required
def create_student():
    try:
        student_name = request.form.get('student_name')
        class_name = request.form.get('class_name')
        password = request.form.get('password')

        if not student_name or not class_name or not password:
            return jsonify({
                'success': False,
                'message': 'A diák neve, osztálya és jelszava megadása kötelező'
            }), 400

        # Ellenőrizzük, hogy létezik-e az osztály
        class_obj = Class.query.filter_by(class_name=class_name).first()
        if not class_obj:
            return jsonify({
                'success': False,
                'message': 'A megadott osztály nem létezik'
            }), 400

        # Ellenőrizzük, hogy létezik-e már a diák
        existing_student = Student.query.filter_by(student_name=student_name).first()
        if existing_student:
            return jsonify({
                'success': False,
                'message': 'Ez a diák már létezik'
            }), 400

        # Új diák létrehozása
        new_student = Student(
            student_name=student_name,
            class_name=class_name
        )
        new_student.set_password(password)
        db.session.add(new_student)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'A diák sikeresen létrehozva'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/edit_student', methods=['POST'])
@login_required
@admin_required
def edit_student():
    try:
        student_id = request.form.get('student_id')
        student_name = request.form.get('student_name')
        class_name = request.form.get('class_name')
        password = request.form.get('password')

        if not student_id or not student_name or not class_name:
            return jsonify({
                'success': False,
                'message': 'A diák azonosítója, neve és osztálya megadása kötelező'
            }), 400

        # Ellenőrizzük, hogy létezik-e az osztály
        class_obj = Class.query.filter_by(class_name=class_name).first()
        if not class_obj:
            return jsonify({
                'success': False,
                'message': 'A megadott osztály nem létezik'
            }), 400

        # Diák keresése
        student = Student.query.get(student_id)
        if not student:
            return jsonify({
                'success': False,
                'message': 'A diák nem található'
            }), 404

        # Ellenőrizzük, hogy a név nem foglalt-e
        if student_name != student.student_name:
            existing_student = Student.query.filter_by(student_name=student_name).first()
            if existing_student:
                return jsonify({
                    'success': False,
                    'message': 'Ez a diáknév már foglalt'
                }), 400

        # Diák adatainak frissítése
        student.student_name = student_name
        student.class_name = class_name
        if password:
            student.set_password(password)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'A diák adatai sikeresen frissítve'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/delete_student', methods=['POST'])
@login_required
@admin_required
def delete_student():
    try:
        student_id = request.form.get('student_id')
        if not student_id:
            return jsonify({
                'success': False,
                'message': 'A diák azonosítója megadása kötelező'
            }), 400

        # Diák keresése
        student = Student.query.get(student_id)
        if not student:
            return jsonify({
                'success': False,
                'message': 'A diák nem található'
            }), 404

        # Diák törlése
        db.session.delete(student)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'A diák sikeresen törölve'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/get_teacher_classes', methods=['GET'])
@login_required
@admin_required
def get_teacher_classes():
    """Tanár osztályainak lekérése."""
    try:
        teacher_id = request.args.get('teacher_id')
        if not teacher_id:
            return jsonify({
                'success': False,
                'message': 'Hiányzó tanár azonosító!'
            }), 400

        # Tanár osztályainak lekérése
        teacher_classes = ClassTeacher.query.filter_by(teacher_name=Teacher.query.get(teacher_id).teacher_name).all()
        assigned_classes = [ct.class_name for ct in teacher_classes]

        # Összes osztály lekérése
        all_classes = Class.query.all()
        available_classes = [{'id': c.id, 'class_name': c.class_name} for c in all_classes]

        return jsonify({
            'success': True,
            'assigned_classes': assigned_classes,
            'available_classes': available_classes
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/update_teacher_classes', methods=['POST'])
@login_required
@admin_required
def update_teacher_classes():
    """Tanár osztályainak frissítése."""
    try:
        teacher_id = request.form.get('teacher_id')
        selected_classes = request.form.getlist('classes[]')

        if not teacher_id:
            return jsonify({
                'success': False,
                'message': 'Hiányzó tanár azonosító!'
            }), 400

        # Tanár lekérése
        teacher = Teacher.query.get(teacher_id)
        if not teacher:
            return jsonify({
                'success': False,
                'message': 'A tanár nem található!'
            }), 404

        # Régi kapcsolatok törlése
        ClassTeacher.query.filter_by(teacher_name=teacher.teacher_name).delete()

        # Új kapcsolatok létrehozása
        for class_name in selected_classes:
            # Ellenőrizzük, hogy az osztály létezik-e
            if Class.query.filter_by(class_name=class_name).first():
                new_relation = ClassTeacher(
                    teacher_name=teacher.teacher_name,
                    class_name=class_name
                )
                db.session.add(new_relation)

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'A tanár osztályai sikeresen frissítve!'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/download_file/<int:file_id>')
@teacher_required
def download_file(file_id):
    """Fájl letöltése."""
    try:
        # Fájl lekérése az adatbázisból
        file = File.query.get_or_404(file_id)
        
        # Ellenőrizzük, hogy a tanár hozzáfér-e az osztályhoz
        teacher = Teacher.query.filter_by(teacher_name=current_user.student_name).first()
        if not teacher:
            flash('Nem található tanár!', 'error')
            return redirect(url_for('teacher_dashboard'))
            
        # Ellenőrizzük, hogy a tanár hozzá van-e rendelve az osztályhoz
        class_teacher = ClassTeacher.query.filter_by(
            teacher_name=teacher.teacher_name,
            class_name=file.class_name
        ).first()
        
        if not class_teacher:
            flash('Nincs jogosultsága a fájl letöltéséhez!', 'error')
            return redirect(url_for('teacher_dashboard'))
        
        # Fájl elérési út összeállítása
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.class_name, file.filename)
        
        if not os.path.exists(file_path):
            flash('A fájl nem található!', 'error')
            return redirect(url_for('teacher_dashboard'))
        
        # Fájl letöltése
        return send_file(
            file_path,
            as_attachment=True,
            download_name=file.original_filename
        )
        
    except Exception as e:
        app.logger.error(f'File download error: {str(e)}')
        flash(f'Hiba történt a fájl letöltése közben: {str(e)}', 'error')
        return redirect(url_for('teacher_dashboard'))

@app.route('/bulk_download', methods=['POST'])
@teacher_required
def bulk_download():
    """Több fájl letöltése ZIP formátumban."""
    try:
        file_ids = request.json.get('file_ids', [])
        if not file_ids:
            return jsonify({'success': False, 'message': 'Nincsenek kiválasztott fájlok!'}), 400

        # Ellenőrizzük, hogy a tanár hozzáfér-e a fájlokhoz
        teacher = Teacher.query.filter_by(teacher_name=current_user.student_name).first()
        if not teacher:
            return jsonify({'success': False, 'message': 'Nem található tanár!'}), 403

        # Fájlok lekérése és jogosultság ellenőrzése
        files = File.query.filter(File.id.in_(file_ids)).all()
        accessible_files = []
        
        for file in files:
            # Ellenőrizzük, hogy a tanár hozzá van-e rendelve az osztályhoz
            class_teacher = ClassTeacher.query.filter_by(
                teacher_name=teacher.teacher_name,
                class_name=file.class_name
            ).first()
            
            if class_teacher:
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.class_name, file.filename)
                if os.path.exists(file_path):
                    accessible_files.append((file, file_path))

        if not accessible_files:
            return jsonify({'success': False, 'message': 'Nem található letölthető fájl!'}), 404

        # ZIP fájl létrehozása
        memory_file = BytesIO()
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file, file_path in accessible_files:
                # Egyedi fájlnév létrehozása: osztály_diák_eredeti_fájlnév
                arcname = f"{file.class_name}_{file.student_name}_{file.original_filename}"
                zf.write(file_path, arcname)

        memory_file.seek(0)
        return send_file(
            memory_file,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'fajlok_{datetime.now(HUNGARY_TZ).strftime("%Y%m%d_%H%M%S")}.zip'
        )

    except Exception as e:
        app.logger.error(f'Bulk download error: {str(e)}')
        return jsonify({'success': False, 'message': f'Hiba történt: {str(e)}'}), 500

@app.route('/delete_file/<int:file_id>', methods=['POST'])
@teacher_required
def delete_file(file_id):
    """Egy fájl törlése."""
    try:
        # Fájl lekérése az adatbázisból
        file = File.query.get_or_404(file_id)
        
        # Ellenőrizzük, hogy a tanár hozzáfér-e a fájlhoz
        teacher = Teacher.query.filter_by(teacher_name=current_user.student_name).first()
        if not teacher:
            return jsonify({'success': False, 'message': 'Nem található tanár!'}), 403
            
        # Ellenőrizzük, hogy a tanár hozzá van-e rendelve az osztályhoz
        class_teacher = ClassTeacher.query.filter_by(
            teacher_name=teacher.teacher_name,
            class_name=file.class_name
        ).first()
        
        if not class_teacher:
            return jsonify({'success': False, 'message': 'Nincs jogosultsága a fájl törléséhez!'}), 403
        
        # Fájl elérési út összeállítása
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.class_name, file.filename)
        
        # Fájl törlése a fájlrendszerből
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                app.logger.error(f"Error deleting file from filesystem: {str(e)}")
                return jsonify({'success': False, 'message': f'Hiba történt a fájl törlése közben: {str(e)}'}), 500
        
        # Fájl törlése az adatbázisból
        try:
            db.session.delete(file)
            db.session.commit()
            return jsonify({'success': True, 'message': 'A fájl sikeresen törölve!'})
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error deleting file from database: {str(e)}")
            return jsonify({'success': False, 'message': f'Hiba történt az adatbázis művelet közben: {str(e)}'}), 500
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'File delete error: {str(e)}')
        return jsonify({'success': False, 'message': f'Hiba történt: {str(e)}'}), 500

@app.route('/bulk_delete', methods=['POST'])
@teacher_required
def bulk_delete():
    """Több fájl törlése."""
    try:
        file_ids = request.json.get('file_ids', [])
        if not file_ids:
            return jsonify({'success': False, 'message': 'Nincsenek kiválasztott fájlok!'}), 400

        # Ellenőrizzük, hogy a tanár hozzáfér-e a fájlokhoz
        teacher = Teacher.query.filter_by(teacher_name=current_user.student_name).first()
        if not teacher:
            return jsonify({'success': False, 'message': 'Nem található tanár!'}), 403

        # Fájlok lekérése és jogosultság ellenőrzése
        files = File.query.filter(File.id.in_(file_ids)).all()
        deleted_count = 0
        errors = []

        for file in files:
            try:
                # Ellenőrizzük, hogy a tanár hozzá van-e rendelve az osztályhoz
                class_teacher = ClassTeacher.query.filter_by(
                    teacher_name=teacher.teacher_name,
                    class_name=file.class_name
                ).first()
                
                if class_teacher:
                    # Fájl törlése a fájlrendszerből
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.class_name, file.filename)
                    if os.path.exists(file_path):
                        try:
                            os.remove(file_path)
                        except Exception as e:
                            app.logger.error(f"Error deleting file from filesystem: {str(e)}")
                            errors.append(f"Hiba a fájl törlése közben ({file.original_filename}): {str(e)}")
                            continue
                    
                    # Fájl törlése az adatbázisból
                    try:
                        db.session.delete(file)
                        deleted_count += 1
                    except Exception as e:
                        app.logger.error(f"Error deleting file from database: {str(e)}")
                        errors.append(f"Hiba az adatbázis művelet közben ({file.original_filename}): {str(e)}")
                else:
                    errors.append(f"Nincs jogosultsága a fájl törléséhez: {file.original_filename}")
            except Exception as e:
                app.logger.error(f"Error processing file {file.original_filename}: {str(e)}")
                errors.append(f"Hiba a fájl feldolgozása közben ({file.original_filename}): {str(e)}")

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error committing bulk delete transaction: {str(e)}")
            return jsonify({'success': False, 'message': f'Hiba történt az adatbázis művelet közben: {str(e)}'}), 500

        if deleted_count > 0:
            message = f"{deleted_count} fájl sikeresen törölve."
            if errors:
                message += f" Hibák: {', '.join(errors)}"
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'message': 'Nem sikerült törölni egy fájlt sem!'}), 400

    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Bulk delete error: {str(e)}')
        return jsonify({'success': False, 'message': f'Hiba történt: {str(e)}'}), 500

# Statikus fájlok cache beállítása
@app.after_request
def add_cache_headers(response):
    """Cache headerek hozzáadása a statikus fájlokhoz."""
    if request.path.startswith('/static/'):
        # Cache-Control header beállítása
        response.headers['Cache-Control'] = 'public, max-age=31536000'  # 1 év
        
        # ETag header beállítása a fájl típusa alapján
        if not response.direct_passthrough:
            try:
                if response.data:
                    response.headers['ETag'] = hashlib.md5(response.data).hexdigest()
            except (RuntimeError, AttributeError):
                # Ha bármilyen hiba történik, egyszerűen hagyjuk figyelmen kívül az ETag beállítását
                pass
        else:
            # Direct passthrough módban csak a Cache-Control headert állítjuk be
            pass
            
    return response

# Alkalmazás indítása
if __name__ == '__main__':
    with app.app_context():
        try:
            app.logger.info("Starting application initialization...")
            
            # Táblák létrehozása
            app.logger.info("Creating database tables...")
            db.create_all()
            app.logger.info("Database tables created.")
            
            # Ellenőrizzük, hogy van-e admin felhasználó
            admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
            admin_password = os.environ.get('ADMIN_PASSWORD')
            admin = User.query.filter_by(student_name=admin_username).first()
            if not admin:
                app.logger.info("Creating admin user...")
                # Admin felhasználó létrehozása
                admin = User(student_name=admin_username, email='admin@school.com', role='admin')
                admin.set_password(admin_password)
                db.session.add(admin)
                db.session.commit()
                app.logger.info("Admin user created.")
            else:
                app.logger.info("Admin user already exists.")
            
            ensure_upload_folder()
            app.logger.info("Upload folder initialized successfully.")
            
        except Exception as e:
            app.logger.error(f"Initialization error: {str(e)}")
            db.session.rollback()
            raise

    app.run(host='0.0.0.0', port=5051, debug=False) # Debug mód kikapcsolva