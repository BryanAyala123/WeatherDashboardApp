import pytest

from app import create_app
from config import TestConfig
from weather.db import db

@pytest.fixture
def app():
    """
    Create and configure a new app instance for testing.
    """
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """
    A test client for the app.
    """
    return app.test_client()

@pytest.fixture
def session(app):
    """
    Provide a SQLAlchemy session for tests, rolled back after each test.
    """
    with app.app_context():
        yield db.session
