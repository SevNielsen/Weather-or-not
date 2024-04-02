import pytest
from flask_testing import TestCase
from website import create_app, db
from website.models import User

class TestUserCRUD(TestCase):
    def create_app(self):
        app = create_app()
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_create_user(self):
        response = self.client.post('/register', data={'username': 'new_user', 'email': 'new_user@example.com', 'password': 'password'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        user = User.query.filter_by(username='new_user').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'new_user@example.com')

    def test_read_user_profile(self):
        user = User(username='john_doe', email='john_doe@example.com')
        db.session.add(user)
        db.session.commit()

        response = self.client.get('/user/john_doe')
        self.assert200(response)
        self.assertIn('john_doe@example.com', response.data.decode())

if __name__ == '__main__':
    pytest.main()
