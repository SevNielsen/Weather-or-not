import pytest
from flask_login import current_user
from website import create_app, db
from website.models import Member

@pytest.fixture(scope='module')
def test_client():
    flask_app = create_app('testing')
    testing_client = flask_app.test_client()
    ctx = flask_app.app_context()
    ctx.push()
    yield testing_client
    ctx.pop()

@pytest.fixture(scope='module')
def init_database():
    db.create_all()
    user1 = Member(username='testuser', email='test@example.com', password='testpassword', city='TestCity')
    db.session.add(user1)
    db.session.commit()
    yield db
    db.drop_all()

def test_sign_up(test_client, init_database):
    response = test_client.post('/signup', data={
        'First_Name': 'Test',
        'Last_Name': 'User',
        'email': 'test@example.com',
        'username': 'testuser',
        'password': 'testpassword',
        'city': 'TestCity'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"dashboard" in response.data

def test_login(test_client, init_database):
    response = test_client.post('/login2', data={
        'username': 'testuser',
        'password2': 'testpassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"dashboard" in response.data
    assert current_user.username == 'testuser'

def test_logout(test_client, init_database):
    test_client.get('/logout', follow_redirects=True)
    assert current_user.is_anonymous
