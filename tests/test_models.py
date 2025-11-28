import pytest
from app.models import User, Task, TaskStatus
from datetime import datetime

class TestModels:
    """Tests pour les modèles"""
    
    def test_user_creation(self, app):
        """Test création utilisateur"""
        with app.app_context():
            user = User(
                username='testuser',
                email='test@example.com',
                password_hash='hashed_password'
            )
            assert user.username == 'testuser'
            assert user.email == 'test@example.com'
            assert user.is_active == True
    
    def test_task_creation(self, app):
        """Test création tâche"""
        with app.app_context():
            task = Task(
                title='Test Task',
                description='Test Description',
                priority=3,
                user_id=1
            )
            assert task.title == 'Test Task'
            assert task.status == TaskStatus.PENDING
            assert task.priority == 3
    
    def test_task_to_dict(self, app):
        """Test conversion tâche en dictionnaire"""
        with app.app_context():
            task = Task(
                title='Test Task',
                description='Test Description',
                priority=2,
                user_id=1
            )
            task_dict = task.to_dict()
            
            assert task_dict['title'] == 'Test Task'
            assert task_dict['status'] == 'pending'
            assert task_dict['priority'] == 2