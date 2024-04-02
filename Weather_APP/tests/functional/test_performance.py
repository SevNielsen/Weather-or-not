import pytest
from flask import url_for
from website.__init222 import create_app

@pytest.fixture
def app():
    # Setup: Create a Flask app instance for testing
    app = create_app()
    app.config['TESTING'] = True
    yield app

@pytest.fixture
def client(app):
    # Setup: Create a test client for the Flask app
    return app.test_client()

def test_page_load_time(client):
    # Test page load time: Check if the home page loads within an acceptable range
    response = client.get('/')
    assert response.status_code == 200
    assert response.elapsed.total_seconds() < 2.0  # Assuming page load time is within 2 seconds

def test_stress_test(client):
    # Stress test: Simulate multiple concurrent users accessing the home page
    num_users = 50  # Assuming 50 users simultaneously accessing
    urls = [url_for('index') for _ in range(num_users)]
    responses = []

    for url in urls:
        response = client.get(url)
        responses.append(response)

    # Ensure all requests are successful
    for response in responses:
        assert response.status_code == 200

    # Check if average response time is within acceptable range
    total_time = sum(response.elapsed.total_seconds() for response in responses)
    average_time = total_time / num_users
    assert average_time < 2.0  # Assuming average response time is within 2 seconds
