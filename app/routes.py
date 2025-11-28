from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models import db, Task, TaskStatus
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Page d'accueil"""
    if current_user.is_authenticated:
        return redirect(url_for('main.tasks'))
    return render_template('index.html')

@main_bp.route('/tasks')
@login_required
def tasks():
    """Page des tâches"""
    return render_template('tasks.html')

@main_bp.route('/api/tasks', methods=['GET'])
@login_required
def get_tasks():
    """API: Récupérer les tâches de l'utilisateur"""
    status_filter = request.args.get('status')
    query = Task.query.filter_by(user_id=current_user.id)
    
    if status_filter:
        query = query.filter_by(status=TaskStatus(status_filter))
    
    tasks = query.order_by(Task.priority.desc(), Task.created_at.desc()).all()
    return jsonify([task.to_dict() for task in tasks])

@main_bp.route('/api/tasks', methods=['POST'])
@login_required
def create_task():
    """API: Créer une nouvelle tâche"""
    data = request.get_json()
    
    if not data or not data.get('title'):
        return jsonify({'error': 'Le titre est requis'}), 400
    
    # Gestion de la date d'échéance
    due_date = None
    if data.get('due_date'):
        try:
            due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'error': 'Format de date invalide'}), 400
    
    task = Task(
        title=data['title'],
        description=data.get('description', ''),
        priority=data.get('priority', 1),
        due_date=due_date,
        user_id=current_user.id
    )
    
    db.session.add(task)
    db.session.commit()
    
    return jsonify(task.to_dict()), 201

@main_bp.route('/api/tasks/<int:task_id>', methods=['PUT'])
@login_required
def update_task(task_id):
    """API: Mettre à jour une tâche"""
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    data = request.get_json()
    
    if 'title' in data:
        task.title = data['title']
    if 'description' in data:
        task.description = data['description']
    if 'priority' in data:
        task.priority = data['priority']
    if 'status' in data:
        task.status = TaskStatus(data['status'])
    if 'due_date' in data:
        if data['due_date']:
            task.due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
        else:
            task.due_date = None
    
    task.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify(task.to_dict())

@main_bp.route('/api/tasks/<int:task_id>', methods=['DELETE'])
@login_required
def delete_task(task_id):
    """API: Supprimer une tâche"""
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    
    db.session.delete(task)
    db.session.commit()
    
    return jsonify({'message': 'Tâche supprimée avec succès'})

@main_bp.route('/health')
def health_check():
    """Endpoint de santé pour le monitoring"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'database': 'connected' if db.engine else 'disconnected'
    })