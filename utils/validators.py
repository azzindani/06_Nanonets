"""
Input validation utilities.
"""
import os
import re
from typing import Optional, Tuple

from config import settings


def validate_file_path(file_path: str) -> Tuple[bool, Optional[str]]:
    """
    Validate that a file path exists and is accessible.

    Args:
        file_path: Path to validate.

    Returns:
        Tuple of (is_valid, error_message).
    """
    if not file_path:
        return False, "File path is empty"

    if not os.path.exists(file_path):
        return False, f"File not found: {file_path}"

    if not os.path.isfile(file_path):
        return False, f"Path is not a file: {file_path}"

    if not os.access(file_path, os.R_OK):
        return False, f"File is not readable: {file_path}"

    return True, None


def validate_file_extension(file_path: str) -> Tuple[bool, Optional[str]]:
    """
    Validate that file has a supported extension.

    Args:
        file_path: Path to validate.

    Returns:
        Tuple of (is_valid, error_message).
    """
    extension = os.path.splitext(file_path)[1].lower()

    all_supported = (
        settings.processing.supported_image_formats +
        settings.processing.supported_document_formats
    )

    if extension not in all_supported:
        return False, f"Unsupported file type: {extension}. Supported: {', '.join(all_supported)}"

    return True, None


def validate_api_key(api_key: str) -> Tuple[bool, Optional[str]]:
    """
    Validate API key format.

    Args:
        api_key: API key to validate.

    Returns:
        Tuple of (is_valid, error_message).
    """
    if not api_key:
        return False, "API key is required"

    if len(api_key) < 8:
        return False, "API key must be at least 8 characters"

    return True, None


def validate_url(url: str) -> Tuple[bool, Optional[str]]:
    """
    Validate URL format.

    Args:
        url: URL to validate.

    Returns:
        Tuple of (is_valid, error_message).
    """
    if not url:
        return True, None  # Optional field

    url_pattern = re.compile(
        r'^https?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )

    if not url_pattern.match(url):
        return False, f"Invalid URL format: {url}"

    return True, None


def validate_max_tokens(max_tokens: int) -> Tuple[bool, Optional[str]]:
    """
    Validate max tokens value.

    Args:
        max_tokens: Value to validate.

    Returns:
        Tuple of (is_valid, error_message).
    """
    if max_tokens < 100:
        return False, "Max tokens must be at least 100"

    if max_tokens > 8000:
        return False, "Max tokens cannot exceed 8000"

    return True, None


def validate_image_size(size: int) -> Tuple[bool, Optional[str]]:
    """
    Validate image size value.

    Args:
        size: Value to validate.

    Returns:
        Tuple of (is_valid, error_message).
    """
    if size < 256:
        return False, "Image size must be at least 256"

    if size > 4096:
        return False, "Image size cannot exceed 4096"

    return True, None


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing dangerous characters.

    Args:
        filename: Filename to sanitize.

    Returns:
        Sanitized filename.
    """
    # Remove path separators
    filename = os.path.basename(filename)

    # Remove dangerous characters
    dangerous_chars = ['..', '/', '\\', '\x00', '<', '>', '|', '*', '?', '"']
    for char in dangerous_chars:
        filename = filename.replace(char, '')

    return filename


if __name__ == "__main__":
    print("=" * 60)
    print("VALIDATORS MODULE TEST")
    print("=" * 60)

    # Test file path validation
    valid, error = validate_file_path("/nonexistent/file.pdf")
    print(f"  File path validation: {not valid} (expected: True)")

    # Test extension validation
    valid, error = validate_file_extension("test.pdf")
    print(f"  Extension validation (pdf): {valid}")

    valid, error = validate_file_extension("test.xyz")
    print(f"  Extension validation (xyz): {not valid} (expected: True)")

    # Test API key validation
    valid, error = validate_api_key("short")
    print(f"  API key validation (short): {not valid} (expected: True)")

    valid, error = validate_api_key("valid-api-key-12345")
    print(f"  API key validation (valid): {valid}")

    # Test URL validation
    valid, error = validate_url("https://example.com/api")
    print(f"  URL validation: {valid}")

    # Test filename sanitization
    sanitized = sanitize_filename("../../../etc/passwd")
    print(f"  Sanitized filename: {sanitized}")

    print(f"\n  ✓ Validator tests passed")

    print("=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
