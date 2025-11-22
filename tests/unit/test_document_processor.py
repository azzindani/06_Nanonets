"""
Unit tests for document processor.
"""
import pytest
from PIL import Image
from core.document_processor import DocumentProcessor


class TestDocumentProcessor:
    """Tests for DocumentProcessor class."""

    @pytest.fixture
    def processor(self):
        return DocumentProcessor()

    @pytest.mark.unit
    def test_validate_nonexistent_file(self, processor):
        """Test validation of nonexistent file."""
        result = processor.validate_file("/nonexistent/file.pdf")

        assert not result.is_valid
        assert "not found" in result.error_message.lower()

    @pytest.mark.unit
    def test_validate_unsupported_extension(self, processor, tmp_path):
        """Test validation of unsupported file type."""
        unsupported = tmp_path / "file.xyz"
        unsupported.touch()

        result = processor.validate_file(str(unsupported))

        assert not result.is_valid
        assert "unsupported" in result.error_message.lower()

    @pytest.mark.unit
    def test_validate_pdf_extension(self, processor, temp_pdf):
        """Test validation of PDF file."""
        result = processor.validate_file(temp_pdf)

        assert result.is_valid
        assert result.file_type == "pdf"

    @pytest.mark.unit
    def test_validate_image_extension(self, processor, temp_image):
        """Test validation of image file."""
        result = processor.validate_file(temp_image)

        assert result.is_valid
        assert result.file_type == "image"

    @pytest.mark.unit
    def test_preprocess_image_no_resize_needed(self, processor):
        """Test that small images are not resized."""
        small_image = Image.new('RGB', (800, 600), color='white')
        result = processor.preprocess_image(small_image, max_size=1536)

        assert result.size == (800, 600)

    @pytest.mark.unit
    def test_preprocess_image_resize_width(self, processor):
        """Test resizing image by width."""
        large_image = Image.new('RGB', (3000, 2000), color='white')
        result = processor.preprocess_image(large_image, max_size=1536)

        assert result.size[0] == 1536
        assert result.size[1] == 1024  # Maintains aspect ratio

    @pytest.mark.unit
    def test_preprocess_image_resize_height(self, processor):
        """Test resizing image by height."""
        tall_image = Image.new('RGB', (1000, 3000), color='white')
        result = processor.preprocess_image(tall_image, max_size=1536)

        assert result.size[1] == 1536
        assert result.size[0] == 512  # Maintains aspect ratio

    @pytest.mark.unit
    def test_get_file_metadata_image(self, processor, temp_image):
        """Test getting metadata for image file."""
        metadata = processor.get_file_metadata(temp_image)

        assert metadata.filename == "test.png"
        assert metadata.file_type == "PNG"
        assert metadata.total_pages == 1
        assert metadata.dimensions == (800, 600)

    @pytest.mark.unit
    def test_get_file_metadata_pdf(self, processor, temp_pdf):
        """Test getting metadata for PDF file."""
        metadata = processor.get_file_metadata(temp_pdf)

        assert metadata.filename == "test.pdf"
        assert metadata.file_type == "PDF"
        assert metadata.total_pages == 1

    @pytest.mark.unit
    def test_extract_pdf_pages(self, processor, temp_pdf):
        """Test extracting pages from PDF."""
        images = processor.extract_pdf_pages(temp_pdf)

        assert len(images) == 1
        assert isinstance(images[0], Image.Image)
