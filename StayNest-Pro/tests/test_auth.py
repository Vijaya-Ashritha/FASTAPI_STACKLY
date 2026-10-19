"""Authentication integration tests should run against a dedicated test database.
These tests verify the stable validation contract without requiring a live MySQL server.
"""
import pytest
from pydantic import ValidationError
from app.schemas.auth import RegisterRequest, LoginRequest

def test_registration_rejects_short_password():
    with pytest.raises(ValidationError): RegisterRequest(full_name="Test User",email="test@example.com",password="short")
def test_login_requires_email():
    with pytest.raises(ValidationError): LoginRequest(email="not-an-email",password="secret")
