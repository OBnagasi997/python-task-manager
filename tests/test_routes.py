import pytest
import json
from app.models import User, Task, TaskStatus, db
from datetime import datetime, timedelta

class TestRoutes:
    """Tests pour les routes de l'application"""
    
    def test_home_page(self, client):
        """Test que la page d'accueil se charge correctement"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'TaskManager' in response.data
        assert b'Gestion de t&#226;ches' in response.data
    
    def test_tasks_page_requires_login(self, client):
        """Test que la page des tâches nécessite une connexion"""
        response = client.get('/tasks', follow_redirects=True)
        # Doit rediriger vers la page de login
        assert b'Connexion' in response.data
    
    def test_health_check(self, client):
        """Test l'endpoint de santé"""
        response = client.get('/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
    
    def test_task_api_requires_auth(self, client):
        """Test que l'API tâches nécessite une authentification"""
        response = client.get('/api/tasks')
        assert response.status_code == 401  # Unauthorized
    
    def test_task_creation_authenticated(self, client, authenticated_user):
        """Test la création de tâche avec utilisateur authentifié"""
        response = client.post('/api/tasks', json={
            'title': 'Test Task API',
            'description': 'Description de test',
            'priority': 3
        })
        
        assert response.status_code == 201
        
        data = json.loads(response.data)
        assert data['title'] == 'Test Task API'
        assert data['status'] == 'pending'
        assert data['priority'] == 3
        assert data['user_id'] == authenticated_user.id
    
    def test_task_list_authenticated(self, client, authenticated_user):
        """Test la récupération des tâches avec utilisateur authentifié"""
        # Créer quelques tâches de test
        task1 = Task(title='Task 1', user_id=authenticated_user.id)
        task2 = Task(title='Task 2', user_id=authenticated_user.id)
        db.session.add_all([task1, task2])
        db.session.commit()
        
        response = client.get('/api/tasks')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert len(data) == 2
        assert data[0]['title'] == 'Task 2'  # Ordonné par date décroissante
    
    def test_task_update(self, client, authenticated_user):
        """Test la mise à jour d'une tâche"""
        # Créer une tâche
        task = Task(title='Original Task', user_id=authenticated_user.id)
        db.session.add(task)
        db.session.commit()
        
        # Mettre à jour
        response = client.put(f'/api/tasks/{task.id}', json={
            'title': 'Updated Task',
            'status': 'in_progress'
        })
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['title'] == 'Updated Task'
        assert data['status'] == 'in_progress'
    
    def test_task_deletion(self, client, authenticated_user):
        """Test la suppression d'une tâche"""
        # Créer une tâche
        task = Task(title='Task to delete', user_id=authenticated_user.id)
        db.session.add(task)
        db.session.commit()
        task_id = task.id
        
        # Supprimer
        response = client.delete(f'/api/tasks/{task_id}')
        assert response.status_code == 200
        
        # Vérifier qu'elle n'existe plus
        deleted_task = Task.query.get(task_id)
        assert deleted_task is None

@pytest.fixture
def authenticated_user(app):
    """Crée un utilisateur authentifié pour les tests"""
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            password_hash='hashed_password'
        )
        db.session.add(user)
        db.session.commit()
        
        # Ici, vous devriez normalement authentifier l'utilisateur
        # Pour les tests API, nous utiliserons des headers d'authentification
        yield user
        
        db.session.delete(user)
        db.session.commit()