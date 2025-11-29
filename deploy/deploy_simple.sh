# deploy/deploy_simple.sh - Script de déploiement simplifié

set -e

echo "=== DÉPLOIEMENT SIMPLIFIÉ PYTHON ==="

# Configuration
HOST="$1"
STAGING="C:/apps/python-task-manager-staging"
LIVE="C:/apps/python-task-manager-live"
BACKUP="C:/apps/python-task-manager-backup"

if [ -z "$HOST" ]; then
    echo "Usage: $0 <192.168.1.6>"
    exit 1
fi

# Fonction SSH
ssh_cmd() {
    ssh -i ~/.ssh/github_actions_python python_deploy@$HOST "$1"
}

# 1. Sauvegarder l'ancienne version
echo "1. Sauvegarde..."
if ssh_cmd "Test-Path '$LIVE'" | grep -q "True"; then
    BACKUP_NAME="backup_$(date +%Y%m%d_%H%M%S)"
    ssh_cmd "
        # Arrêter l'app
        Get-Process -Name 'python' -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
        # Sauvegarder
        Copy-Item '$LIVE' '$BACKUP/$BACKUP_NAME' -Recurse -Force
        Remove-Item '$LIVE' -Recurse -Force
    "
    echo "Sauvegardé: $BACKUP_NAME"
fi

# 2. Déployer nouvelle version
echo "2. Déploiement..."
ssh_cmd "Rename-Item '$STAGING' 'python-task-manager-live'"

# 3. Installer dépendances
echo "3. Installation dépendances..."
ssh_cmd "
    cd '$LIVE'
    python -m pip install --upgrade pip
    pip install -r requirements.txt
"

# 4. Démarrer l'application
echo "4. Démarrage application..."
ssh_cmd "
    cd '$LIVE'
    Start-Process -NoNewWindow -FilePath 'python' \`
        -ArgumentList '-m waitress --port=8000 --call ""run:main""'
"

# 5. Vérification
echo "5. Vérification..."
sleep 5
if ssh_cmd "Invoke-WebRequest 'http://localhost:8000/health' -UseBasicParsing" | grep -q "healthy"; then
    echo "Déploiement réussi!"
else
    echo "Déploiement terminé, mais vérification health check échouée"
fi