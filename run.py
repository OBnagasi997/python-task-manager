import os
from app import create_app
from config import ProductionConfig, DevelopmentConfig
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

def main():
    """Point d'entrée de l'application"""
    # Déterminer l'environnement
    env = os.environ.get('FLASK_ENV', 'development')  # Défaut: développement
    
    print(f"🔧 Environnement détecté: {env}")
    
    if env == 'development':
        app = create_app(DevelopmentConfig)
        debug = True
        host = '127.0.0.1'
    else:
        app = create_app(ProductionConfig)
        debug = False
        host = '0.0.0.0'
    
    port = int(os.environ.get('PORT', 8000))
    
    print(f"🚀 Démarrage de l'application sur {host}:{port}")
    print(f"📊 Base de données: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    if env == 'production':
        # Utiliser Waitress pour la production
        try:
            from waitress import serve
            print(f"🎯 Mode production - Serveur Waitress")
            serve(app, host=host, port=port)
        except ImportError:
            print("⚠️ Waitress non installé, utilisation du serveur de développement")
            app.run(host=host, port=port, debug=debug)
    else:
        # Utiliser le serveur de développement Flask
        print(f"🔧 Mode développement - Serveur Flask")
        app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    main()