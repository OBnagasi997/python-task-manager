import os
from datetime import timedelta

class Config:
    """Configuration de base"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Chemin absolu pour la base de données SQLite
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATABASE_PATH = os.path.join(BASE_DIR, 'instance', 'tasks.db')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f'sqlite:///{DATABASE_PATH}'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuration sécurité
    SESSION_COOKIE_SECURE = False  # False pour le développement
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Temps de session
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)

class ProductionConfig(Config):
    """Configuration production"""
    DEBUG = False
    TESTING = False
    # Créer le dossier apps s'il n'existe pas
    PROD_DB_DIR = "C:\\apps\\python-task-manager\\instance"
    PROD_DB_PATH = os.path.join(PROD_DB_DIR, 'tasks.db')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f'sqlite:///{PROD_DB_PATH}'

class DevelopmentConfig(Config):
    """Configuration développement"""
    DEBUG = True
    DEVELOPMENT = True
    # Utiliser le chemin relatif pour le développement
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///tasks.db'

class TestingConfig(Config):
    """Configuration tests"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False