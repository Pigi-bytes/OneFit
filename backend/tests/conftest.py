import pytest
from app import app


# https://docs.pytest.org/en/stable/explanation/fixtures.html
@pytest.fixture
def client():
    app.config["TESTING"] = True
    
    with app.test_client() as client:
        yield client
