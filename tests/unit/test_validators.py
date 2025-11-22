"""
Unit tests for validators.
"""
import pytest
from utils.validators import (
    validate_file_path,
    validate_file_extension,
    validate_api_key,
    validate_url,
    validate_max_tokens,
    validate_image_size,
    sanitize_filename
)


class TestValidators:
    """Tests for validation utilities."""

    @pytest.mark.unit
    def test_validate_file_path_empty(self):
        """Test validation of empty file path."""
        valid, error = validate_file_path("")
        assert not valid
        assert "empty" in error.lower()

    @pytest.mark.unit
    def test_validate_file_path_nonexistent(self):
        """Test validation of nonexistent file."""
        valid, error = validate_file_path("/nonexistent/file.pdf")
        assert not valid
        assert "not found" in error.lower()

    @pytest.mark.unit
    def test_validate_file_extension_pdf(self):
        """Test validation of PDF extension."""
        valid, error = validate_file_extension("document.pdf")
        assert valid
        assert error is None

    @pytest.mark.unit
    def test_validate_file_extension_unsupported(self):
        """Test validation of unsupported extension."""
        valid, error = validate_file_extension("file.xyz")
        assert not valid
        assert "unsupported" in error.lower()

    @pytest.mark.unit
    def test_validate_api_key_empty(self):
        """Test validation of empty API key."""
        valid, error = validate_api_key("")
        assert not valid
        assert "required" in error.lower()

    @pytest.mark.unit
    def test_validate_api_key_short(self):
        """Test validation of short API key."""
        valid, error = validate_api_key("short")
        assert not valid
        assert "8 characters" in error.lower()

    @pytest.mark.unit
    def test_validate_api_key_valid(self):
        """Test validation of valid API key."""
        valid, error = validate_api_key("valid-api-key-12345")
        assert valid
        assert error is None

    @pytest.mark.unit
    def test_validate_url_empty(self):
        """Test validation of empty URL (optional)."""
        valid, error = validate_url("")
        assert valid  # Empty is okay for optional field

    @pytest.mark.unit
    def test_validate_url_valid(self):
        """Test validation of valid URL."""
        valid, error = validate_url("https://example.com/api")
        assert valid

    @pytest.mark.unit
    def test_validate_url_invalid(self):
        """Test validation of invalid URL."""
        valid, error = validate_url("not-a-url")
        assert not valid

    @pytest.mark.unit
    def test_validate_max_tokens_too_low(self):
        """Test validation of too low max tokens."""
        valid, error = validate_max_tokens(50)
        assert not valid
        assert "100" in error

    @pytest.mark.unit
    def test_validate_max_tokens_too_high(self):
        """Test validation of too high max tokens."""
        valid, error = validate_max_tokens(10000)
        assert not valid
        assert "8000" in error

    @pytest.mark.unit
    def test_validate_max_tokens_valid(self):
        """Test validation of valid max tokens."""
        valid, error = validate_max_tokens(2048)
        assert valid

    @pytest.mark.unit
    def test_validate_image_size_too_small(self):
        """Test validation of too small image size."""
        valid, error = validate_image_size(100)
        assert not valid

    @pytest.mark.unit
    def test_validate_image_size_too_large(self):
        """Test validation of too large image size."""
        valid, error = validate_image_size(5000)
        assert not valid

    @pytest.mark.unit
    def test_validate_image_size_valid(self):
        """Test validation of valid image size."""
        valid, error = validate_image_size(1536)
        assert valid

    @pytest.mark.unit
    def test_sanitize_filename_path_traversal(self):
        """Test sanitization removes path traversal."""
        result = sanitize_filename("../../../etc/passwd")
        assert ".." not in result
        assert "/" not in result

    @pytest.mark.unit
    def test_sanitize_filename_preserves_name(self):
        """Test sanitization preserves valid filename."""
        result = sanitize_filename("document.pdf")
        assert result == "document.pdf"
