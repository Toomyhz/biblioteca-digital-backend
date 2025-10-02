import pytest
from app import create_app,db
@pytest.fixture
def client():
    app = create_app()