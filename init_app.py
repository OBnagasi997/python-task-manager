#!/usr/bin/env python3
"""
Script d'initialisation de l'application TaskManager
"""
import os
import sys
import sqlite3
from ensure_dirs import ensure_directories

def initialize_application():
    """Initialise l'application avec tous les composants nécessaires"""
    print("🚀 Initialisation de l'application TaskManager...")
    
    # 1. Créer les dossiers nécessaires
    print("\n📁 Création des dossiers...")
    ensure_directories()
    
    # 2. Vérifier et installer les dépendances
    print("\n📦 Vérification des dépendances...")
    try:
        import flask
        print("✅ Flask est installé")
    except ImportError:
        print("❌ Flask n'est pas installé")
        print("Exécutez: pip install -r requirements.txt")
        return False
    
    try:
        import flask_sqlalchemy
        print("✅ Flask-SQLAlchemy est installé")
    except ImportError:
        print("❌ Flask-SQLAlchemy n'est pas installé")
        return False
    
    # 3. Créer la base de données de test
    print("\n🗄️ Initialisation de la base de données...")
    try:
        from app import create_app
        from config import DevelopmentConfig
        
        app = create_app(DevelopmentConfig)
        with app.app_context():
            from app.models import db
            db.create_all()
            print("✅ Base de données initialisée avec succès")
            
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation de la base de données: {e}")
        # Créer une base SQLite manuellement
        try:
            conn = sqlite3.connect('tasks.db')
            conn.close()
            print("✅ Base de données SQLite créée manuellement")
        except Exception as e2:
            print(f"❌ Impossible de créer la base de données: {e2}")
            return False
    
    # 4. Vérifier les templates
    print("\n📄 Vérification des templates...")
    templates = ['index.html', 'login.html', 'register.html', 'tasks.html']
    templates_dir = 'app/templates'
    
    for template in templates:
        template_path = os.path.join(templates_dir, template)
        if os.path.exists(template_path):
            print(f" {template} - Présent")
        else:
            print(f" {template} - Manquant")
    
    print("\n🎉 Initialisation terminée!")
    print("\nProchaines étapes:")
    print("1. Exécutez: python run.py")
    print("2. Ouvrez: http://localhost:8000")
    print("3. Créez un compte utilisateur")
    
    return True

if __name__ == '__main__':
    initialize_application()