import pytest
from website.__init222 import create_app, db
from website.models import Member
from datetime import datetime

@pytest.fixture(scope='module')
def new_member():
    # Setup a new Member instance
    member = Member(
        username='testuser', 
        password='testpassword', 
        email='testuser@example.com', 
        city='TestCity', 
        first_name='Test', 
        last_name='User',
        # Assume `date` needs to be manually set for testing
        date=datetime.utcnow()
    )
    return member

@pytest.fixture(scope='module')
def test_app():
    # Configure the app for testing
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False
    })
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='module')
def test_db(test_app):
    # Provide the DB instance
    return db

def test_new_member_created(new_member):
    # Test the member attributes
    assert new_member.username == 'testuser'
    assert new_member.password == 'testpassword'
    assert new_member.email == 'testuser@example.com'
    assert new_member.city == 'TestCity'
    assert new_member.first_name == 'Test'
    assert new_member.last_name == 'User'
    assert not new_member.notifications
    assert isinstance(new_member.date, datetime)

def test_member_save_to_db(test_db, new_member):
    # Save the new member to the database and verify
    test_db.session.add(new_member)
    test_db.session.commit()
    member_in_db = Member.query.filter_by(username='testuser').first()
    assert member_in_db is not None
    assert member_in_db.username == 'testuser'
    assert member_in_db.email == 'testuser@example.com'
    assert member_in_db.city == 'TestCity'
    assert not member_in_db.notifications
    assert isinstance(member_in_db.date, datetime)
    # Cleanup after test
    test_db.session.delete(member_in_db)
    test_db.session.commit()
