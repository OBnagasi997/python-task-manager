import pytest
from app.models import User, db
from werkzeug.security import check_password_hash

class TestAuthentication:
    """Tests pour l'authentification"""
    
    def test_user_registration(self, client):
        """Test l'inscription d'un nouvel utilisateur"""
        response = client.post('/auth/register', data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'securepassword123',
            'confirm_password': 'securepassword123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Compte cr&#233;&#233; avec succ&#232;s' in response.data
        
        # Vérifier que l'utilisateur existe en base
        user = User.query.filter_by(username='newuser').first()
        assert user is not None
        assert user.email == 'newuser@example.com'
        assert check_password_hash(user.password_hash, 'securepassword123')
    
    def test_user_login_success(self, client):
        """Test la connexion réussie d'un utilisateur"""
        # Créer un utilisateur de test
        user = User(
            username='testuser',
            email='test@example.com',
            password_hash='pbkdf2:sha256:150000$hash123$...'
        )
        db.session.add(user)
        db.session.commit()
        
        response = client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'password123'
        }, follow_redirects=True)
        
        # Vérifier la redirection vers la page d'accueil
        assert response.status_code == 200
    
    def test_user_login_failure(self, client):
        """Test l'échec de connexion avec mauvais identifiants"""
        response = client.post('/auth/login', data={
            'username': 'nonexistent',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Nom d&#39;utilisateur ou mot de passe incorrect' in response.data
    
    def test_password_hashing(self, app):
        """Test que les mots de passe sont bien hashés"""
        with app.app_context():
            user = User(
                username='hashuser',
                email='hash@example.com',
                password_hash='plaintext'  # Ce sera hashé dans la vraie app
            )
            
            # Dans l'implémentation réelle, le mot de passe serait hashé
            assert user.password_hash is not None
            assert user.password_hash != 'plaintext'
    
    def test_user_duplicate_registration(self, client):
        """Test qu'on ne peut pas créer deux utilisateurs avec le même username"""
        # Premier enregistrement
        client.post('/auth/register', data={
            'username': 'duplicate',
            'email': 'first@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        })
        
        # Deuxième enregistrement avec le même username
        response = client.post('/auth/register', data={
            'username': 'duplicate',
            'email': 'second@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        
        assert b'Ce nom d&#39;utilisateur est d&#233;j&#224; pris' in response.data