from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

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
    from website.auth import auth
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
