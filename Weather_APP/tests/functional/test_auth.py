import pytest
from werkzeug.security import generate_password_hash
from website.models import Member, db
from website import create_app


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # create a temporary app with common test config
    app = create_app()
    with app.app_context():
        db.create_all()
    yield app
    with app.app_context():
        db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()

@pytest.fixture
def init_database(app):
    with app.app_context():
        user = Member(username='testuser', email='test@example.com', password=generate_password_hash('testpassword', method='pbkdf2:sha256'), city='TestCity')
        db.session.add(user)
        db.session.commit()
        yield db
        db.session.remove()

def test_signup(client, init_database):
    response = client.post('/signup', data={
        'First_Name': 'Test',
        'Last_Name': 'User',
        'email': 'test@example.com',
        'username': 'newuser',
        'password': 'newpassword',
        'city': 'NewCity'
    }, follow_redirects=True)
    assert b'Account created successfully' in response.data

def test_login(client, init_database):
    response = client.post('/login2', data={
        'username': 'testuser',
        'password2': 'testpassword'
    }, follow_redirects=True)
    assert b'dashboard' in response.data

def test_logout(client, init_database):
    # First login
    client.post('/login2', data={
        'username': 'testuser',
        'password2': 'testpassword'
    }, follow_redirects=True)
    response = client.get('/logout', follow_redirects=True)
    assert b'login' in response.data

def test_dashboard_access_without_login(client):
    response = client.get('/dashboard', follow_redirects=True)
    assert b'login' in response.data

def test_profile_access_without_login(client):
    response = client.get('/profile', follow_redirects=True)
    assert b'login' in response.data

def test_leafletMap_access_without_login(client):
    response = client.get('/leafletMap', follow_redirects=True)
    assert b'login' in response.data

def test_config_endpoint(client):
    response = client.get('/config')
    assert response.status_code == 200
    assert b'API key' in response.data
