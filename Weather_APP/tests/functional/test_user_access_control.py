import pytest
from flask_login import login_user, logout_user, current_user
from website.models import Member
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
        normal_user = Member(username='normal_user', email='normal@example.com', is_admin=False)
        admin_user = Member(username='admin_user', email='admin@example.com', is_admin=True)
        db.session.add(normal_user)
        db.session.add(admin_user)
        db.session.commit()
    yield
    with app.app_context():
        db.session.remove()
        Member.query.delete()

def test_admin_access(client, init_database):
    with client:
        response = client.post('/login', data=dict(username='normal_user', password='password'), follow_redirects=True)
        assert current_user.is_admin is False
        response = client.get('/admin_page')
        assert response.status_code == 403          
        logout_user()
        
        response = client.post('/login', data=dict(username='admin_user', password='password'), follow_redirects=True)
        assert current_user.is_admin is True
        response = client.get('/admin_dashboard')
        assert response.status_code == 200  

def test_normal_user_cannot_access_admin_page(client, init_database):
    # Log in with a normal user
    response = client.post('/login', data={'username': 'normal_user', 'password': 'password'}, follow_redirects=True)
    assert b'Welcome' in response.data  # Assuming a successful login will display "Welcome" on the page

    # Try to access the admin page
    response = client.get('/admin_dashboard', follow_redirects=True)
    assert response.status_code == 403  # Assuming non-admin users attempting to access the admin page will receive a 403 error
    assert b'Access denied' in response.data  # Assuming the page will display "Access denied"


def test_access_dashboard_post_logout(client, init_database):
    # User logs in
    client.post('/login', data={'username': 'normal_user', 'password': 'password'}, follow_redirects=True)

    # User logs out
    client.get('/logout', follow_redirects=True)

    # Attempt to access the dashboard page
    response = client.get('/dashboard', follow_redirects=True)
    assert b'Please log in' in response.data
