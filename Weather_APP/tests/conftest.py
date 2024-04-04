import pytest
from website import create_app
from website  import db

@pytest.fixture
def test_app():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'})
    with app.app_context():
        db.create_all()
    yield app
    with app.app_context():
        db.drop_all()

@pytest.fixture
def test_client(test_app):
    """A test client for the app."""
    return test_app.test_client()

@pytest.fixture(scope='session')
def test_db(test_app):
    """Session-wide test database."""
    # Ensure the app is associated with this context
    db.app = test_app
    
    # Create all tables
    db.create_all()
    
    yield db
    
    # Drop all tables
    db.drop_all()

@pytest.fixture
def test_session(test_db, request):
    """Creates a new database transaction for a test."""
    transaction = test_db.engine.begin()
    options = dict(bind=test_db.engine, binds={})
    session = test_db.create_scoped_session(options=options)
    
    test_db.session = session

    def teardown():
        transaction.rollback()
        session.remove()
    
    request.addfinalizer(teardown)
    return session
