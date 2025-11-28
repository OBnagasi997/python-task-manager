from flask import Flask
from flask_login import LoginManager
from app.models import db, User
from config import Config
import os

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app(config_class=Config):
    """Factory d'application Flask"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # S'assurer que le dossier instance existe
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass
    
    # Initialisation des extensions
    db.init_app(app)
    login_manager.init_app(app)
    
    # Enregistrement des blueprints
    from app.routes import main_bp
    from app.auth import auth_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    # Création des tables avec gestion d'erreur
    with app.app_context():
        try:
            db.create_all()
            print(" Tables de base de données créées avec succès")
        except Exception as e:
            print(f" Erreur lors de la création des tables: {e}")
            # Créer une base de données de secours
            import sqlite3
            backup_path = os.path.join(app.instance_path, 'backup_tasks.db')
            conn = sqlite3.connect(backup_path)
            conn.close()
            app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{backup_path}'
            db.create_all()
            print("✅ Base de données de secours créée")
    
    return app