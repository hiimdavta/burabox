import os
import json
from werkzeug.security import generate_password_hash
import sqlite3

class ClassManager:
    def __init__(self, uploads_dir):
        """Inicializálja a ClassManager-t az uploads könyvtárral"""
        self.uploads_dir = uploads_dir
        os.makedirs(uploads_dir, exist_ok=True)

    def get_class_students(self, class_name):
        """Betölti az osztály diákjainak adatait az adatbázisból"""
        try:
            # Ellenőrizzük, hogy létezik-e az osztály
            conn = sqlite3.connect('school.db')
            cursor = conn.cursor()
            cursor.execute('SELECT class_name FROM classes WHERE class_name = ?', (class_name,))
            if not cursor.fetchone():
                conn.close()
                raise ValueError(f"Az osztály nem található: {class_name}")
            
            # Diákok lekérése
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT student_name, password, last_name, first_name 
                FROM students 
                WHERE class_name = ?
                ORDER BY last_name, first_name
            ''', (class_name,))
            
            students = []
            for row in cursor.fetchall():
                students.append({
                    'student_name': row['student_name'],
                    'password': '',  # Ne küldjük vissza a jelszót
                    'last_name': row['last_name'],
                    'first_name': row['first_name']
                })
            conn.close()
            return students
            
        except sqlite3.Error as e:
            print(f"Adatbázis hiba a diákok betöltése közben: {str(e)}")
            raise Exception(f"Adatbázis hiba: {str(e)}")
        except Exception as e:
            print(f"Hiba a diákok betöltése közben: {str(e)}")
            raise

    def add_students(self, class_name, last_names, first_names, student_names, passwords):
        """Új diákok hozzáadása az osztályhoz"""
        try:
            conn = sqlite3.connect('school.db')
            cursor = conn.cursor()
            
            # Ellenőrizzük, hogy létezik-e az osztály
            cursor.execute('SELECT class_name FROM classes WHERE class_name = ?', (class_name,))
            if not cursor.fetchone():
                conn.close()
                return False
            
            # Diákok hozzáadása
            for i in range(len(student_names)):
                if student_names[i] and passwords[i]:  # Csak akkor adjuk hozzá, ha van adat
                    hashed_password = generate_password_hash(passwords[i])
                    try:
                        cursor.execute('''
                            INSERT INTO students (student_name, password, last_name, first_name, class_name)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (student_names[i], hashed_password, last_names[i], first_names[i], class_name))
                    except sqlite3.IntegrityError:
                        # Ha már létezik a diák, frissítjük az adatait
                        cursor.execute('''
                            UPDATE students 
                            SET password = ?, last_name = ?, first_name = ?
                            WHERE student_name = ? AND class_name = ?
                        ''', (hashed_password, last_names[i], first_names[i], student_names[i], class_name))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Hiba a diákok hozzáadása közben: {str(e)}")
            return False

    def get_all_classes(self):
        """Visszaadja az összes osztályt"""
        try:
            conn = sqlite3.connect('school.db')
            cursor = conn.cursor()
            cursor.execute('SELECT class_name FROM classes ORDER BY class_name')
            classes = [row[0] for row in cursor.fetchall()]
            conn.close()
            return classes
        except Exception as e:
            print(f"Hiba az osztályok lekérése közben: {str(e)}")
            return []

    def create_class(self, class_name):
        """Új osztály létrehozása"""
        try:
            os.makedirs(os.path.join(self.uploads_dir, class_name), exist_ok=True)
            return True
        except Exception as e:
            print(f"Hiba az osztály létrehozása közben: {str(e)}")
            return False

    def delete_class(self, class_name):
        """Osztály törlése"""
        try:
            class_dir = os.path.join(self.uploads_dir, class_name)
            if os.path.exists(class_dir):
                import shutil
                shutil.rmtree(class_dir)
            return True
        except Exception as e:
            print(f"Hiba az osztály törlése közben: {str(e)}")
            return False

    def get_class_files(self, class_name):
        """Visszaadja az osztály fájljait"""
        try:
            class_dir = os.path.join(self.uploads_dir, class_name)
            if not os.path.exists(class_dir):
                return []
            
            files = []
            for filename in os.listdir(class_dir):
                if filename.endswith('.meta'):
                    continue
                    
                file_path = os.path.join(class_dir, filename)
                if os.path.isfile(file_path):
                    # Try to get original filename from metadata
                    metadata_path = os.path.join(class_dir, f"{filename}.meta")
                    original_filename = filename
                    uploaded_at = os.path.getmtime(file_path)
                    
                    if os.path.exists(metadata_path):
                        try:
                            with open(metadata_path, 'r') as f:
                                metadata = json.load(f)
                                original_filename = metadata.get('original_filename', filename)
                                uploaded_at = metadata.get('uploaded_at', uploaded_at)
                        except:
                            pass
                    
                    files.append({
                        'name': original_filename,
                        'secure_name': filename,
                        'size': os.path.getsize(file_path),
                        'uploaded_at': uploaded_at
                    })
            
            return sorted(files, key=lambda x: x['uploaded_at'], reverse=True)
        except Exception as e:
            print(f"Hiba a fájlok lekérése közben: {str(e)}")
            return [] 