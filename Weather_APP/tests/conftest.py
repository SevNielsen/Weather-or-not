import pytest
from website import create_app
from website import db as _db

@pytest.fixture(scope='session')
def app():
    """Session-wide test Flask application."""
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SECRET_KEY': 'test',
        'WTF_CSRF_ENABLED': False
    })

    # Establish an application context before running the tests.
    with app.app_context():
        _db.create_all()

    yield app

    with app.app_context():
        _db.drop_all()

@pytest.fixture(scope='function')
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture(scope='session')
def db(app):
    """Session-wide test database."""
    # Ensure the app is associated with this context
    _db.app = app
    
    # Create all tables
    _db.create_all()
    
    yield _db
    
    # Drop all tables
    _db.drop_all()

@pytest.fixture(scope='function')
def session(db, request):
    """Creates a new database transaction for a test."""
    transaction = db.engine.begin()
    options = dict(bind=db.engine, binds={})
    session = db.create_scoped_session(options=options)
    
    db.session = session

    def teardown():
        transaction.rollback()
        session.remove()
    
    request.addfinalizer(teardown)
    return session

