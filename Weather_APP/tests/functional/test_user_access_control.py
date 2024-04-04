import pytest
from flask_login import login_user, logout_user, current_user
from website.models import User
from website import create_app, db

@pytest.fixture
def app():
    app = create_app()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    with app.app_context():
        db.create_all()
    yield app
    with app.app_context():
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def init_database(app):
    with app.app_context():
        normal_user = User(username='normal_user', email='normal@example.com', is_admin=False)
        admin_user = User(username='admin_user', email='admin@example.com', is_admin=True)
        db.session.add(normal_user)
        db.session.add(admin_user)
        db.session.commit()
    yield
    with app.app_context():
        db.session.remove()
        User.query.delete()

def test_admin_access(client, init_database):
    with client:
        response = client.post('/login', data=dict(username='normal_user', password='password'), follow_redirects=True)
        assert current_user.is_admin is False
        response = client.get('/admin_page')
        assert response.status_code == 403          
        logout_user()
        
        response = client.post('/login', data=dict(username='admin_user', password='password'), follow_redirects=True)
        assert current_user.is_admin is True
        response = client.get('/admin_page')
        assert response.status_code == 200  