import os
import sys

def ensure_directories():
    """Crée les dossiers nécessaires pour l'application"""
    directories = [
        'instance',
        'app/templates',
        'tests',
        'migrations',
        'deploy',
        '.github/workflows'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Dossier créé/vérifié: {directory}")
    
    # Créer un fichier .gitkeep dans les dossiers vides
    empty_dirs = ['migrations', 'deploy', '.github/workflows']
    for empty_dir in empty_dirs:
        gitkeep_file = os.path.join(empty_dir, '.gitkeep')
        with open(gitkeep_file, 'w') as f:
            f.write('# Ce fichier permet de garder le dossier dans git\n')
        print(f"✅ Fichier .gitkeep créé dans: {empty_dir}")

if __name__ == '__main__':
    ensure_directories()