import pytest
from flask import url_for
from werkzeug.security import generate_password_hash
from website import create_app, db
from website.models import Member

@pytest.fixture(scope='module')
def test_client():
    flask_app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'})
    testing_client = flask_app.test_client()
    
    with flask_app.app_context():
        db.create_all()
        yield testing_client
        db.drop_all()

@pytest.fixture(scope='module')
def init_database():
    user = Member(username='testuser', email='test@example.com', password=generate_password_hash('testpassword', method='pbkdf2:sha256'), city='TestCity')
    db.session.add(user)
    db.session.commit()
    yield db
    db.session.remove()

def test_signup(test_client, init_database):
    response = test_client.post('/signup', data={
        'First_Name': 'Test',
        'Last_Name': 'User',
        'email': 'test@example.com',
        'username': 'newuser',
        'password': 'newpassword',
        'city': 'NewCity'
    }, follow_redirects=True)
    assert b'Account created successfully' in response.data

def test_login(test_client, init_database):
    response = test_client.post('/login2', data={
        'username': 'testuser',
        'password2': 'testpassword'
    }, follow_redirects=True)
    assert b'dashboard' in response.data

def test_logout(test_client, init_database):
    # First login
    test_client.post('/login2', data={
        'username': 'testuser',
        'password2': 'testpassword'
    }, follow_redirects=True)
    response = test_client.get('/logout', follow_redirects=True)
    assert b'login' in response.data

def test_dashboard_access_without_login(test_client):
    response = test_client.get('/dashboard', follow_redirects=True)
    assert b'login' in response.data

def test_profile_access_without_login(test_client):
    response = test_client.get('/profile', follow_redirects=True)
    assert b'login' in response.data

def test_leafletMap_access_without_login(test_client):
    response = test_client.get('/leafletMap', follow_redirects=True)
    assert b'login' in response.data

def test_config_endpoint(test_client):
    response = test_client.get('/config')
    assert response.status_code == 200
    assert b'API key' in response.data

# Add more tests for dashboard, profile, and leafletMap after login, simulating user interactions and verifying the outcomes.
