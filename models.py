import json
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib

class ClassManager:
    def __init__(self, upload_folder):
        self.upload_folder = upload_folder
        self.classes_file = os.path.join(upload_folder, 'classes.json')
        self.teachers_file = os.path.join(upload_folder, 'teachers.json')
        self.teacher_classes_file = os.path.join(upload_folder, 'teacher_classes.json')
        self._ensure_files_exist()
        self._sync_with_database()

    def _ensure_files_exist(self):
        """Ensure all necessary directories and JSON files exist."""
        os.makedirs(self.upload_folder, exist_ok=True)
        
        default_data = {
            'classes.json': {},
            'teachers.json': {},
            'teacher_classes.json': {}
        }
        
        for filename, default in default_data.items():
            file_path = os.path.join(self.upload_folder, filename)
            if not os.path.exists(file_path):
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(default, f, indent=4, ensure_ascii=False)

    def _sync_with_database(self):
        """Synchronize JSON files with the database."""
        try:
            import sqlite3
            conn = sqlite3.connect('school.db')
            conn.row_factory = sqlite3.Row
            
            # Sync classes
            cursor = conn.cursor()
            cursor.execute('SELECT class_name FROM classes')
            classes = {row['class_name']: {'created_at': str(datetime.now())} 
                      for row in cursor.fetchall()}
            self._save_data(self.classes_file, classes)
            self.classes = classes
            
            # Sync teachers
            cursor.execute('SELECT teacher_name, password FROM teachers')
            teachers = {row['teacher_name']: {'password': row['password'], 'created_at': str(datetime.now())} 
                       for row in cursor.fetchall()}
            self._save_data(self.teachers_file, teachers)
            
            # Sync teacher-class assignments
            cursor.execute('SELECT teacher_name, class_name FROM class_teachers')
            teacher_classes = {}
            for row in cursor.fetchall():
                teacher = row['teacher_name']
                class_name = row['class_name']
                if teacher not in teacher_classes:
                    teacher_classes[teacher] = []
                teacher_classes[teacher].append(class_name)
            self._save_data(self.teacher_classes_file, teacher_classes)
            
            conn.close()
        except Exception as e:
            print(f"Error syncing with database: {e}")

    def _load_data(self, file_path):
        """Load data from a JSON file with proper error handling."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error loading {file_path}: {e}")
            return {}

    def _save_data(self, file_path, data):
        """Save data to a JSON file with proper error handling."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving {file_path}: {e}")

    def _hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def create_class(self, class_name):
        """Create a new class directory."""
        class_dir = os.path.join(self.upload_folder, class_name)
        if not os.path.exists(class_dir):
            os.makedirs(class_dir)
            return True
        return False

    def verify_class(self, class_name, password):
        if class_name not in self.classes:
            return False
        return check_password_hash(self.classes[class_name]['password_hash'], password)

    def delete_class(self, class_name):
        """Delete a class and all its files."""
        class_dir = os.path.join(self.upload_folder, class_name)
        if os.path.exists(class_dir):
            import shutil
            shutil.rmtree(class_dir)
            return True
        return False

    def get_all_classes(self):
        return list(self.classes.keys())

    def get_class_files(self, class_name):
        """Get all files for a class."""
        class_dir = os.path.join(self.upload_folder, class_name)
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

    # Teacher management methods
    def create_teacher(self, username, password):
        teachers = self._load_data(self.teachers_file)
        
        if username in teachers:
            return False, 'Ez a felhasználónév már foglalt!'
        
        teachers[username] = {
            'password': self._hash_password(password),
            'created_at': datetime.now().isoformat()
        }
        
        self._save_data(self.teachers_file, teachers)
        return True, 'Tanár sikeresen létrehozva!'

    def verify_teacher(self, username, password):
        teachers = self._load_data(self.teachers_file)
        teacher = teachers.get(username)
        
        if not teacher:
            return False
        
        return teacher['password'] == self._hash_password(password)

    def get_all_teachers(self):
        return list(self._load_data(self.teachers_file).keys())

    def delete_teacher(self, username):
        teachers = self._load_data(self.teachers_file)
        teacher_classes = self._load_data(self.teacher_classes_file)
        
        if username not in teachers:
            return False, 'A tanár nem található!'
        
        del teachers[username]
        if username in teacher_classes:
            del teacher_classes[username]
        
        self._save_data(self.teachers_file, teachers)
        self._save_data(self.teacher_classes_file, teacher_classes)
        return True, 'Tanár sikeresen törölve!'

    def assign_class_to_teacher(self, username, class_name):
        teachers = self._load_data(self.teachers_file)
        teacher_classes = self._load_data(self.teacher_classes_file)
        classes = self._load_data(self.classes_file)
        
        if username not in teachers:
            return False, 'A tanár nem található!'
        if class_name not in classes:
            return False, 'Az osztály nem található!'
        
        if username not in teacher_classes:
            teacher_classes[username] = []
        
        if class_name not in teacher_classes[username]:
            teacher_classes[username].append(class_name)
            self._save_data(self.teacher_classes_file, teacher_classes)
            return True, 'Osztály sikeresen hozzárendelve a tanárhoz!'
        
        return False, 'Az osztály már hozzá van rendelve a tanárhoz!'

    def remove_class_from_teacher(self, username, class_name):
        teacher_classes = self._load_data(self.teacher_classes_file)
        
        if username not in teacher_classes:
            return False, 'A tanár nem található!'
        
        if class_name in teacher_classes[username]:
            teacher_classes[username].remove(class_name)
            self._save_data(self.teacher_classes_file, teacher_classes)
            return True, 'Osztály sikeresen eltávolítva a tanártól!'
        
        return False, 'Az osztály nincs hozzárendelve a tanárhoz!'

    def get_teacher_classes(self, username):
        teacher_classes = self._load_data(self.teacher_classes_file)
        return teacher_classes.get(username, [])

    def get_teachers_for_class(self, class_name):
        teacher_classes = self._load_data(self.teacher_classes_file)
        return [teacher for teacher, classes in teacher_classes.items() if class_name in classes] 