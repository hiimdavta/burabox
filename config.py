import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-please-change-in-production'
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 15 * 1024 * 1024  # 15MB max file size
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # Admin credentials (in production, these should be in environment variables)
    ADMIN_USERNAME = 'admin'
    ADMIN_PASSWORD = 'admin123'  # Change this in production!
    
    # Ensure upload directory exists
    @staticmethod
    def init_app(app):
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True) 