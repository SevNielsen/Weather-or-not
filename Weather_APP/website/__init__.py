from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from os import path
import os

# Initialize SQLAlchemy and LoginManager
db = SQLAlchemy()
login_manager = LoginManager()

DB_NAME = "database.db"

def create_app(test_config=None):
    app = Flask(__name__)

    # Initialize LoginManager with the app
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # Specify the login view
    login_manager.login_message = "Please log in to access this page."  # Custom login message

    # Configure the Flask app based on the provided test_config or the default settings
    if test_config is None:
        # Load the default configuration from a file, if it exists
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test configuration passed as a dictionary
        app.config.update(test_config)

    # Set up default configurations; these could be overridden by test_config
    app.config.setdefault('SECRET_KEY', 'Your secret key')
    app.config.setdefault('SQLALCHEMY_DATABASE_URI', f'sqlite:///{DB_NAME}')
    app.config.setdefault('SQLALCHEMY_TRACK_MODIFICATIONS', False)

    # Initialize database with the app
    db.init_app(app)

    # Import and register blueprints
    from .views import views
    from .auth import auth
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    # User loader callback for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        # Replace 'Member' with your actual User model class name
        # Ensure that 'Member' is imported from your models module
        from .models import Member
        return Member.query.get(int(user_id))

    # Create database if it does not exist
    if not path.exists('website/' + DB_NAME):
        with app.app_context():
            db.create_all()
            print('Created Database!')

    return app

# Initialize SQLAlchemy and LoginManager
db = SQLAlchemy()
login_manager = LoginManager()

def create_test_app(config_overrides=None):
    app = Flask(__name__, template_folder='Weather_APP/website/templates')
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF tokens in the forms for testing purposes.

    if config_overrides:
        app.config.update(config_overrides)
    # Initialize SQLAlchemy with the app
    db.init_app(app)

    # Initialize LoginManager with the app
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Register Blueprints
    from website.views import views
    from website.auth import auth
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    # Setup user loader for Flask-Login
    @login_manager.user_loader
    def load_member(user_id):
        from website.models import Member  # Import the Member model here to avoid circular imports
        return Member.query.get(int(user_id))

    # Create the database tables for our test data within the application context
    with app.app_context():
        db.create_all()

    return app

