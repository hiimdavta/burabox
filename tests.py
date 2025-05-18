import unittest
from app import app, db, User
from flask import url_for
import os

class TestApp(unittest.TestCase):
    def setUp(self):
        """Teszt környezet beállítása."""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        """Teszt környezet takarítása."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        if os.path.exists('test.db'):
            os.remove('test.db')

    def test_login_page(self):
        """Teszteli a bejelentkezési oldal betöltését."""
        response = self.client.get('/bejelentkezes')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Bejelentkez\xc3\xa9s', response.data)

    def test_user_registration(self):
        """Teszteli a felhasználó regisztrációját."""
        response = self.client.post('/regisztracio', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        user = User.query.filter_by(username='testuser').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'test@example.com')

    def test_teacher_login(self):
        """Teszteli a tanári bejelentkezést."""
        # Először létrehozunk egy tanári felhasználót
        user = User(username='teacher', email='teacher@example.com', is_teacher=True)
        user.set_password('teacherpass')
        db.session.add(user)
        db.session.commit()

        # Teszteljük a bejelentkezést
        response = self.client.post('/bejelentkezes', data={
            'user_type': 'teacher',
            'username': 'teacher',
            'password': 'teacherpass'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'teacher_dashboard', response.data)

    def test_student_login(self):
        """Teszteli a diák bejelentkezést."""
        # Először létrehozunk egy diák felhasználót
        user = User(username='student', email='student@example.com', is_teacher=False)
        user.set_password('studentpass')
        db.session.add(user)
        db.session.commit()

        # Teszteljük a bejelentkezést
        response = self.client.post('/bejelentkezes', data={
            'user_type': 'student',
            'username': 'student',
            'password': 'studentpass'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'dashboard', response.data)

    def test_file_upload_security(self):
        """Teszteli a fájl feltöltés biztonságát."""
        # Teszteljük a tiltott fájltípusokat
        test_file = (b'fake executable content', 'test.exe')
        response = self.client.post('/upload_file/test_class', 
                                  data={'files[]': test_file},
                                  content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'nem enged\xc3\xa9lyezett', response.data)

if __name__ == '__main__':
    unittest.main() 