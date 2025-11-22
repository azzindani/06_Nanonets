"""
Document processor for handling file input, validation, and preprocessing.
"""
import os
from dataclasses import dataclass
from typing import List, Tuple, Optional

from PIL import Image
import fitz  # PyMuPDF

from config import settings


@dataclass
class ValidationResult:
    """Result of file validation."""
    is_valid: bool
    file_type: str
    error_message: Optional[str] = None


@dataclass
class FileMetadata:
    """Metadata about a processed file."""
    filename: str
    file_size_mb: float
    file_type: str
    total_pages: int
    dimensions: Optional[Tuple[int, int]] = None


class DocumentProcessor:
    """
    Handles document input, validation, and preprocessing.
    """

    def __init__(self, max_image_size: int = None):
        """
        Initialize the document processor.

        Args:
            max_image_size: Maximum dimension for image resizing.
        """
        self.max_image_size = max_image_size or settings.processing.max_image_size
        self.supported_images = settings.processing.supported_image_formats
        self.supported_docs = settings.processing.supported_document_formats

    def validate_file(self, file_path: str) -> ValidationResult:
        """
        Validate that a file exists and is supported.

        Args:
            file_path: Path to the file to validate.

        Returns:
            ValidationResult with validation status.
        """
        if not os.path.exists(file_path):
            return ValidationResult(
                is_valid=False,
                file_type="unknown",
                error_message=f"File not found: {file_path}"
            )

        extension = os.path.splitext(file_path)[1].lower()

        if extension in self.supported_images:
            return ValidationResult(is_valid=True, file_type="image")
        elif extension in self.supported_docs:
            return ValidationResult(is_valid=True, file_type="pdf")
        else:
            return ValidationResult(
                is_valid=False,
                file_type="unknown",
                error_message=f"Unsupported file type: {extension}"
            )

    def preprocess_image(self, image: Image.Image, max_size: int = None) -> Image.Image:
        """
        Resize image if it exceeds maximum dimensions.

        Args:
            image: PIL Image to process.
            max_size: Maximum dimension (width or height).

        Returns:
            Processed PIL Image.
        """
        max_dimension = max_size or self.max_image_size
        width, height = image.size

        if width > max_dimension or height > max_dimension:
            if width > height:
                new_width = max_dimension
                new_height = int(height * (max_dimension / width))
            else:
                new_height = max_dimension
                new_width = int(width * (max_dimension / height))

            return image.resize((new_width, new_height), Image.Resampling.LANCZOS)

        return image

    def extract_pdf_pages(self, pdf_path: str, dpi: int = None) -> List[Image.Image]:
        """
        Extract all pages from a PDF as images.

        Args:
            pdf_path: Path to the PDF file.
            dpi: Resolution for rendering (default from settings).

        Returns:
            List of PIL Images, one per page.
        """
        dpi = dpi or settings.processing.default_dpi
        images = []

        doc = fitz.open(pdf_path)
        try:
            for page_num in range(doc.page_count):
                page = doc.load_page(page_num)
                # Convert DPI to matrix scale (72 DPI is default)
                matrix = fitz.Matrix(dpi / 72, dpi / 72)
                pix = page.get_pixmap(matrix=matrix)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                images.append(img)
        finally:
            doc.close()

        return images

    def get_file_metadata(self, file_path: str) -> FileMetadata:
        """
        Get metadata about a file.

        Args:
            file_path: Path to the file.

        Returns:
            FileMetadata with file information.
        """
        filename = os.path.basename(file_path)
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        extension = os.path.splitext(file_path)[1].lower()

        total_pages = 1
        dimensions = None

        if extension in self.supported_images:
            file_type = extension.upper().replace('.', '')
            with Image.open(file_path) as img:
                dimensions = img.size
        elif extension == '.pdf':
            file_type = "PDF"
            doc = fitz.open(file_path)
            total_pages = doc.page_count
            doc.close()
        else:
            file_type = extension.upper().replace('.', '')

        return FileMetadata(
            filename=filename,
            file_size_mb=round(file_size_mb, 2),
            file_type=file_type,
            total_pages=total_pages,
            dimensions=dimensions
        )

    def load_image(self, file_path: str) -> Image.Image:
        """
        Load and preprocess an image file.

        Args:
            file_path: Path to the image file.

        Returns:
            Preprocessed PIL Image.
        """
        image = Image.open(file_path).convert("RGB")
        return self.preprocess_image(image)

    def process_file(self, file_path: str) -> Tuple[List[Image.Image], FileMetadata]:
        """
        Process a file and return images and metadata.

        Args:
            file_path: Path to the file to process.

        Returns:
            Tuple of (list of images, file metadata).

        Raises:
            ValueError: If file is invalid or unsupported.
        """
        validation = self.validate_file(file_path)
        if not validation.is_valid:
            raise ValueError(validation.error_message)

        metadata = self.get_file_metadata(file_path)
        images = []

        if validation.file_type == "image":
            image = self.load_image(file_path)
            images.append(image)
        elif validation.file_type == "pdf":
            pdf_images = self.extract_pdf_pages(file_path)
            for img in pdf_images:
                images.append(self.preprocess_image(img))

        return images, metadata


if __name__ == "__main__":
    print("=" * 60)
    print("DOCUMENT PROCESSOR MODULE TEST")
    print("=" * 60)

    processor = DocumentProcessor()

    # Test validation
    result = processor.validate_file("test.pdf")
    print(f"  Validation (test.pdf): is_valid={result.is_valid}")

    result = processor.validate_file("test.jpg")
    print(f"  Validation (test.jpg): is_valid={result.is_valid}")

    result = processor.validate_file("test.xyz")
    print(f"  Validation (test.xyz): is_valid={result.is_valid}")

    # Test image preprocessing
    test_image = Image.new('RGB', (3000, 2000), color='white')
    processed = processor.preprocess_image(test_image, 1536)
    print(f"  Image resize: {test_image.size} -> {processed.size}")

    print(f"\n  ✓ Document processor tests passed")

    print("=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
