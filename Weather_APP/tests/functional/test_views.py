import pytest
from website import create_app

@pytest.fixture(scope='module')
def client():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
    })
    with app.test_client() as testing_client:
        with app.app_context():
            yield testing_client

def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Welcome to Weather or Not's Website!" in response.data
    assert b"Login" in response.data
    assert b"Signup" in response.data
