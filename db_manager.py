from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app import app, db
import sqlite3
from datetime import datetime
import os

migrate = Migrate(app, db)

def create_database():
    """Create the database and all tables."""
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")

def init_migrations():
    """Initialize the migration system."""
    try:
        if not os.path.exists('migrations'):
            os.makedirs('migrations')
        
        with app.app_context():
            if not db.engine.dialect.has_table(db.engine, 'user'):
                db.create_all()
            
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('user')]
            
            if 'is_teacher' not in columns:
                db.engine.execute('ALTER TABLE user ADD COLUMN is_teacher BOOLEAN DEFAULT FALSE')
            if 'is_admin' not in columns:
                db.engine.execute('ALTER TABLE user ADD COLUMN is_admin BOOLEAN DEFAULT FALSE')
            
            print("Database migration initialized successfully!")
            return True
    except Exception as e:
        print(f"Error during migration initialization: {str(e)}")
        return False

def reset_database():
    """Reset the database to its initial state."""
    try:
        with app.app_context():
            db.drop_all()
            db.create_all()
            print("Database reset successfully!")
            return True
    except Exception as e:
        print(f"Error during database reset: {str(e)}")
        return False

def fix_database():
    """Fix common database issues."""
    try:
        conn = sqlite3.connect('school.db')
        cursor = conn.cursor()

        # Fix any NULL values in required fields
        cursor.execute('''
            UPDATE students 
            SET status = 'active' 
            WHERE status IS NULL
        ''')

        # Fix any missing foreign key references
        cursor.execute('''
            DELETE FROM files 
            WHERE student_name NOT IN (SELECT student_name FROM students)
        ''')

        # Fix any missing timestamps
        cursor.execute('''
            UPDATE students 
            SET created_at = CURRENT_TIMESTAMP 
            WHERE created_at IS NULL
        ''')

        conn.commit()
        print("Database fixes applied successfully!")
        return True
    except Exception as e:
        print(f"Error during database fixes: {str(e)}")
        conn.rollback()
        return False
    finally:
        conn.close()

def migrate_database():
    """Migrate the database to use student_name instead of username, first_name, and last_name."""
    try:
        conn = sqlite3.connect('school.db')
        cursor = conn.cursor()

        # Create backup of students table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students_backup AS 
            SELECT id, first_name || ' ' || last_name as student_name, 
                   class_name, password_hash, 'active' as status,
                   CURRENT_TIMESTAMP as created_at, CURRENT_TIMESTAMP as last_active
            FROM students
        ''')

        # Update students table
        cursor.execute('DROP TABLE IF EXISTS students')
        cursor.execute('''
            CREATE TABLE students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_name TEXT UNIQUE NOT NULL,
                class_name TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (class_name) REFERENCES classes(class_name) ON DELETE CASCADE
            )
        ''')

        # Copy data from backup
        cursor.execute('''
            INSERT INTO students (student_name, class_name, password_hash, status, created_at, last_active)
            SELECT student_name, class_name, password_hash, status, created_at, last_active
            FROM students_backup
        ''')

        # Update files table
        cursor.execute('''
            CREATE TABLE files_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                original_filename TEXT NOT NULL,
                student_name TEXT NOT NULL,
                class_name TEXT NOT NULL,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                file_size INTEGER,
                file_type TEXT,
                status TEXT DEFAULT 'active',
                FOREIGN KEY (student_name) REFERENCES students(student_name) ON DELETE CASCADE,
                FOREIGN KEY (class_name) REFERENCES classes(class_name) ON DELETE CASCADE
            )
        ''')

        cursor.execute('''
            INSERT INTO files_new (id, filename, original_filename, student_name, class_name, uploaded_at)
            SELECT id, filename, original_filename, username, class_name, uploaded_at
            FROM files
        ''')

        cursor.execute('DROP TABLE IF EXISTS files')
        cursor.execute('ALTER TABLE files_new RENAME TO files')

        # Update users table
        cursor.execute('''
            CREATE TABLE users_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_name TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT,
                role TEXT DEFAULT 'student',
                is_active BOOLEAN DEFAULT 1
            )
        ''')

        cursor.execute('''
            INSERT INTO users_new (id, student_name, email, password_hash, role, is_active)
            SELECT id, username, email, password_hash, role, is_active
            FROM users
        ''')

        cursor.execute('DROP TABLE IF EXISTS users')
        cursor.execute('ALTER TABLE users_new RENAME TO users')

        # Cleanup
        cursor.execute('DROP TABLE IF EXISTS students_backup')
        conn.commit()
        print("Database migration completed successfully!")
        return True

    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python db_manager.py [create|init|reset|fix|migrate]")
        sys.exit(1)
        
    command = sys.argv[1].lower()
    
    if command == 'create':
        create_database()
    elif command == 'init':
        init_migrations()
    elif command == 'reset':
        reset_database()
    elif command == 'fix':
        fix_database()
    elif command == 'migrate':
        migrate_database()
    else:
        print("Invalid command. Use: create, init, reset, fix, or migrate") 