import pytest

from website import create_app, db

@pytest.fixture()
def app():
    app = create_app("sqlite://")

    with app.app_context():
        db.create_al_all()

    yield app 
    