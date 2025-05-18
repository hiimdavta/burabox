import sqlite3
import logging
from werkzeug.security import generate_password_hash

def migrate_database():
    """Adatbázis séma frissítése és adatok migrálása."""
    logging.info("Starting database migration...")
    
    try:
        # Kapcsolódás az adatbázishoz
        conn = sqlite3.connect('school.db')
        cursor = conn.cursor()
        
        # Ellenőrizzük, hogy létezik-e a students tábla
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='students'")
        students_exists = cursor.fetchone() is not None
        
        # Ellenőrizzük, hogy létezik-e a files tábla
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='files'")
        files_exists = cursor.fetchone() is not None
        
        # Adatok mentése
        existing_students = []
        existing_files = []
        
        if students_exists:
            # Lekérjük a jelenlegi diákokat
            cursor.execute('SELECT id, student_name, class_name, password_hash FROM students')
            existing_students = cursor.fetchall()
            
            # Töröljük a régi táblát
            cursor.execute('DROP TABLE IF EXISTS students')
        
        if files_exists:
            # Lekérjük a fájl adatokat
            cursor.execute('SELECT id, filename, original_filename, student_name, class_name, uploaded_at FROM files')
            existing_files = cursor.fetchall()
            
            # Töröljük a régi táblát
            cursor.execute('DROP TABLE IF EXISTS files')
        
        # Létrehozzuk az új students táblát
        cursor.execute('''
            CREATE TABLE students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                last_name VARCHAR(40) NOT NULL,
                first_name VARCHAR(40) NOT NULL,
                username VARCHAR(80) UNIQUE NOT NULL,
                class_name VARCHAR(20) NOT NULL,
                password_hash VARCHAR(128) NOT NULL,
                FOREIGN KEY (class_name) REFERENCES classes (class_name)
            )
        ''')
        
        # Létrehozzuk az új files táblát
        cursor.execute('''
            CREATE TABLE files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename VARCHAR(255) NOT NULL,
                original_filename VARCHAR(255) NOT NULL,
                username VARCHAR(80) NOT NULL,
                class_name VARCHAR(20) NOT NULL,
                uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (username) REFERENCES students (username),
                FOREIGN KEY (class_name) REFERENCES classes (class_name)
            )
        ''')
        
        # Adatok visszatöltése
        for student in existing_students:
            student_id, student_name, class_name, password_hash = student
            # A student_name-et használjuk vezetéknévként és a felhasználónévként is
            cursor.execute('''
                INSERT INTO students (id, last_name, first_name, username, class_name, password_hash)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (student_id, student_name, student_name, student_name, class_name, password_hash))
        
        for file in existing_files:
            file_id, filename, original_filename, student_name, class_name, uploaded_at = file
            cursor.execute('''
                INSERT INTO files (id, filename, original_filename, username, class_name, uploaded_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (file_id, filename, original_filename, student_name, class_name, uploaded_at))
        
        # Commitoljuk a változtatásokat
        conn.commit()
        logging.info("Database migration completed successfully!")
        
    except Exception as e:
        logging.error(f"Error during migration: {str(e)}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_database() 