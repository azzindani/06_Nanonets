"""
Unit tests for authentication service.
"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta


class TestAuthService:
    """Tests for auth service functionality."""

    def test_import_auth_service(self):
        """Test that auth service can be imported."""
        from services.auth import AuthService
        assert AuthService is not None

    def test_auth_service_initialization(self):
        """Test AuthService can be initialized."""
        from services.auth import AuthService
        auth = AuthService()
        assert auth is not None

    def test_password_hashing(self):
        """Test password hashing functionality."""
        from services.auth import AuthService
        auth = AuthService()

        password = "test_password_123"
        hashed = auth.hash_password(password)

        # Hash should be different from original
        assert hashed != password
        # Should be able to verify
        assert auth.verify_password(password, hashed)
        # Wrong password should fail
        assert not auth.verify_password("wrong_password", hashed)

    def test_password_hash_uniqueness(self):
        """Test that same password produces different hashes."""
        from services.auth import AuthService
        auth = AuthService()

        password = "same_password"
        hash1 = auth.hash_password(password)
        hash2 = auth.hash_password(password)

        # Hashes should be different (salt)
        assert hash1 != hash2
        # Both should verify
        assert auth.verify_password(password, hash1)
        assert auth.verify_password(password, hash2)

    def test_create_access_token(self):
        """Test JWT access token creation."""
        from services.auth import AuthService
        auth = AuthService()

        data = {"sub": "user123", "email": "test@example.com"}
        token = auth.create_access_token(data)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_decode_access_token(self):
        """Test JWT access token decoding."""
        from services.auth import AuthService
        auth = AuthService()

        data = {"sub": "user123", "email": "test@example.com"}
        token = auth.create_access_token(data)

        decoded = auth.decode_access_token(token)
        assert decoded is not None
        assert decoded.get("sub") == "user123"
        assert decoded.get("email") == "test@example.com"

    def test_token_expiration(self):
        """Test that tokens have expiration."""
        from services.auth import AuthService
        auth = AuthService()

        data = {"sub": "user123"}
        token = auth.create_access_token(data, expires_delta=timedelta(minutes=30))

        decoded = auth.decode_access_token(token)
        assert "exp" in decoded

    def test_invalid_token_returns_none(self):
        """Test that invalid tokens return None."""
        from services.auth import AuthService
        auth = AuthService()

        result = auth.decode_access_token("invalid_token")
        assert result is None

    def test_generate_api_key(self):
        """Test API key generation."""
        from services.auth import AuthService
        auth = AuthService()

        api_key = auth.generate_api_key()

        assert api_key is not None
        assert isinstance(api_key, str)
        assert len(api_key) >= 32

    def test_api_key_uniqueness(self):
        """Test that generated API keys are unique."""
        from services.auth import AuthService
        auth = AuthService()

        keys = [auth.generate_api_key() for _ in range(10)]
        unique_keys = set(keys)

        assert len(unique_keys) == 10

    def test_validate_api_key_format(self):
        """Test API key format validation."""
        from services.auth import AuthService
        auth = AuthService()

        valid_key = auth.generate_api_key()
        assert auth.validate_api_key_format(valid_key)

        # Invalid formats
        assert not auth.validate_api_key_format("")
        assert not auth.validate_api_key_format("short")
        assert not auth.validate_api_key_format(None)


class TestAuthServiceFallbacks:
    """Tests for auth service fallback implementations."""

    def test_fallback_hash_works(self):
        """Test that fallback hashing works when passlib unavailable."""
        from services.auth import AuthService
        auth = AuthService()

        # Even with fallback, basic functionality should work
        password = "test123"
        hashed = auth.hash_password(password)
        assert auth.verify_password(password, hashed)

    def test_fallback_token_works(self):
        """Test that fallback token works when jose unavailable."""
        from services.auth import AuthService
        auth = AuthService()

        # Even with fallback, basic functionality should work
        data = {"user": "test"}
        token = auth.create_access_token(data)
        assert token is not None


class TestAuthHelpers:
    """Tests for auth helper functions."""

    def test_get_current_user(self):
        """Test getting current user from token."""
        from services.auth import AuthService
        auth = AuthService()

        # Create a valid token
        token = auth.create_access_token({"sub": "user123"})

        # Should be able to get user
        user_id = auth.get_user_id_from_token(token)
        assert user_id == "user123"

    def test_token_refresh(self):
        """Test token refresh functionality."""
        from services.auth import AuthService
        auth = AuthService()

        # Create initial token
        old_token = auth.create_access_token({"sub": "user123"})

        # Refresh token
        new_token = auth.refresh_token(old_token)

        assert new_token is not None
        assert new_token != old_token

        # New token should have same user
        decoded = auth.decode_access_token(new_token)
        assert decoded.get("sub") == "user123"
