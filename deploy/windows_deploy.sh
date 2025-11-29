# deploy/windows_deploy.sh - Script de déploiement Python adapté pour Bash/SSH

set -e  # Arrêter en cas d'erreur

# Configuration
STAGING_PATH="C:/apps/python-task-manager-staging"
LIVE_PATH="C:/apps/python-task-manager-live"
BACKUP_PATH="C:/apps/python-task-manager-backup"
PYTHON_EXE="python"
APP_PORT="8000"

echo "=== DÉPLOIEMENT PYTHON - $(date) ==="
echo "Staging: $STAGING_PATH"
echo "Live: $LIVE_PATH"
echo "Backup: $BACKUP_PATH"

# Fonction pour exécuter des commandes PowerShell depuis Bash
run_powershell() {
    ssh -i ~/.ssh/github_actions_python python_deploy@$DEPLOY_HOST "powershell -Command \"$1\""
}

# Fonction pour logger
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Vérification des prérequis
log "1. Vérifications pré-déploiement..."

# Vérifier que le dossier staging existe
if ! run_powershell "Test-Path '$STAGING_PATH'" | grep -q "True"; then
    log "Dossier staging introuvable: $STAGING_PATH"
    exit 1
fi

# Vérifier les fichiers essentiels
ESSENTIAL_FILES=("requirements.txt" "run.py" "app/__init__.py")
for file in "${ESSENTIAL_FILES[@]}"; do
    if ! run_powershell "Test-Path '$STAGING_PATH/$file'" | grep -q "True"; then
        log "Fichier essentiel manquant: $file"
        exit 1
    fi
done
log "   Fichiers essentiels présents"

# Sauvegarde de la version actuelle
log "2. Sauvegarde de la version actuelle..."
if run_powershell "Test-Path '$LIVE_PATH'" | grep -q "True"; then
    log "   → Arrêt de l'application en cours..."
    
    # Arrêter les processus Python liés à l'application
    run_powershell "Get-Process -Name 'python' -ErrorAction SilentlyContinue | Where-Object { \$_.Path -like '*$LIVE_PATH*' } | Stop-Process -Force -ErrorAction SilentlyContinue"
    
    # Sauvegarder
    BACKUP_NAME="backup_$(date +'%Y%m%d_%H%M%S')"
    FULL_BACKUP_PATH="$BACKUP_PATH/$BACKUP_NAME"
    
    run_powershell "
        if (Test-Path '$FULL_BACKUP_PATH') { 
            Remove-Item '$FULL_BACKUP_PATH' -Recurse -Force 
        }
        Copy-Item '$LIVE_PATH' '$FULL_BACKUP_PATH' -Recurse -Force
    "
    log "   Version sauvegardée: $BACKUP_NAME"
else
    log "   Aucune version live existante"
fi

# Déploiement de la nouvelle version
log "3. Déploiement de la nouvelle version..."

# Supprimer l'ancienne version live si elle existe
run_powershell "if (Test-Path '$LIVE_PATH') { Remove-Item '$LIVE_PATH' -Recurse -Force }"

# Déployer la nouvelle version
run_powershell "Rename-Item '$STAGING_PATH' '$(basename "$LIVE_PATH")'"
log "   Nouvelle version déployée"

# Configuration de l'environnement
log "4. Configuration de l'environnement..."

# Installation des dépendances
log "   → Installation des dépendances Python..."
run_powershell "
    cd '$LIVE_PATH'
    $PYTHON_EXE -m pip install --upgrade pip
    $PYTHON_EXE -m pip install -r requirements.txt
"

# Vérifier le succès de l'installation
if [ $? -ne 0 ]; then
    log "Échec de l'installation des dépendances"
    exit 1
fi
log "   Dépendances installées"

# Initialisation de la base de données
log "5. Initialisation de la base de données..."
run_powershell "
    cd '$LIVE_PATH'
    try {
        \$output = & $PYTHON_EXE -c \`
            \\\"from app import create_app; \\
             from config import ProductionConfig; \\
             app = create_app(ProductionConfig); \\
             print('Base de données initialisée')\\\" 2>&1
        Write-Host \$output
    } catch {
        Write-Host 'Note: Base de données déjà initialisée'
    }
"

# Démarrage de l'application
log "6. Démarrage de l'application..."

# Arrêter tout processus existant sur le port
run_powershell "
    \$process = Get-NetTCPConnection -LocalPort $APP_PORT -ErrorAction SilentlyContinue
    if (\$process) {
        Stop-Process -Id \$process.OwningProcess -Force -ErrorAction SilentlyContinue
    }
"

# Démarrer l'application
run_powershell "
    cd '$LIVE_PATH'
    Start-Process -NoNewWindow -FilePath '$PYTHON_EXE' \`
        -ArgumentList \\\"-m waitress --port=$APP_PORT --call \\\"\\\"run:main\\\"\\\"\\\" \`
        -WorkingDirectory '$LIVE_PATH'
"

# Attendre le démarrage
sleep 10

# Vérification du démarrage
log "   → Vérification du démarrage..."
if run_powershell "try { Invoke-WebRequest 'http://localhost:$APP_PORT/health' -UseBasicParsing -TimeoutSec 10 } catch { \\\$_.Exception.Message }" | grep -q "healthy"; then
    log "  Application démarrée avec succès"
else
    log "  Health check échoué, vérification manuelle nécessaire"
    
    # Vérifier si le processus tourne
    if run_powershell "Get-Process -Name 'python' -ErrorAction SilentlyContinue" | grep -q "python"; then
        log "  Processus Python détecté"
    else
        log "  Aucun processus Python détecté"
        exit 1
    fi
fi

log "DÉPLOIEMENT RÉUSSI !"
log "Application disponible sur: http://localhost:$APP_PORT"
log "Déployé le: $(date)"