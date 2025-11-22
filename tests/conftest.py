"""
Pytest configuration and fixtures.
"""
import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def sample_ocr_text():
    """Sample OCR output text for testing."""
    return """
    --- Page 1 ---
    Invoice Number: INV-2024-001
    Invoice Date: 2024-01-15
    Company Name: Acme Corporation

    <table>
        <tr><td>Item</td><td>Price</td></tr>
        <tr><td>Widget</td><td>$100</td></tr>
    </table>

    Total Amount: $1,234.56

    Equation: $E = mc^2$

    <img>Company logo image</img>

    <watermark>CONFIDENTIAL</watermark>

    <page_number>1</page_number>

    ☑ Approved
    ☐ Pending
    """


@pytest.fixture
def sample_image():
    """Create a sample test image."""
    from PIL import Image
    return Image.new('RGB', (800, 600), color='white')


@pytest.fixture
def temp_pdf(tmp_path):
    """Create a temporary PDF file for testing."""
    import fitz

    pdf_path = tmp_path / "test.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Test PDF content")
    doc.save(str(pdf_path))
    doc.close()

    return str(pdf_path)


@pytest.fixture
def temp_image(tmp_path):
    """Create a temporary image file for testing."""
    from PIL import Image

    img_path = tmp_path / "test.png"
    img = Image.new('RGB', (800, 600), color='white')
    img.save(str(img_path))

    return str(img_path)
