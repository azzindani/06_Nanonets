"""
Unit tests for field extractor.
"""
import pytest
from core.field_extractor import FieldExtractor


class TestFieldExtractor:
    """Tests for FieldExtractor class."""

    @pytest.fixture
    def extractor(self):
        return FieldExtractor()

    @pytest.mark.unit
    def test_extract_invoice_number(self, extractor):
        """Test extraction of invoice number."""
        text = "Invoice Number: INV-2024-001"
        results = extractor.extract(text, enabled_fields=["Invoice Number"])

        assert "Invoice Number" in results
        assert results["Invoice Number"].found
        assert "INV-2024-001" in results["Invoice Number"].value

    @pytest.mark.unit
    def test_extract_multiple_fields(self, extractor, sample_ocr_text):
        """Test extraction of multiple fields."""
        fields = ["Invoice Number", "Invoice Date", "Company Name", "Total Amount"]
        results = extractor.extract(sample_ocr_text, enabled_fields=fields)

        assert len(results) == 4
        assert results["Invoice Number"].found
        assert results["Company Name"].found

    @pytest.mark.unit
    def test_extract_missing_field(self, extractor):
        """Test extraction when field is not present."""
        text = "Some random text without any fields."
        results = extractor.extract(text, enabled_fields=["Invoice Number"])

        assert "Invoice Number" in results
        assert not results["Invoice Number"].found
        assert results["Invoice Number"].value == ""

    @pytest.mark.unit
    def test_custom_fields(self, extractor):
        """Test extraction with custom fields."""
        text = "Tax ID: 123-45-6789\nVAT Number: VAT12345"
        results = extractor.extract(
            text,
            enabled_fields=[],
            custom_fields=["Tax ID", "VAT Number"]
        )

        assert "Tax ID" in results
        assert "VAT Number" in results

    @pytest.mark.unit
    def test_confidence_scores(self, extractor):
        """Test confidence score calculation."""
        text = "Invoice Number: INV-001"
        results = extractor.extract(text, enabled_fields=["Invoice Number"])

        confidence = results["Invoice Number"].confidence
        assert 0.0 <= confidence <= 1.0

    @pytest.mark.unit
    def test_get_statistics(self, extractor):
        """Test statistics generation."""
        text = "Invoice Number: INV-001\nTotal Amount: $100"
        results = extractor.extract(
            text,
            enabled_fields=["Invoice Number", "Total Amount", "Due Date"]
        )

        stats = extractor.get_statistics(results)

        assert stats["total_fields"] == 3
        assert stats["fields_found"] == 2
        assert stats["fields_empty"] == 1

    @pytest.mark.unit
    def test_to_dict(self, extractor):
        """Test conversion to simple dictionary."""
        text = "Invoice Number: INV-001"
        results = extractor.extract(text, enabled_fields=["Invoice Number"])

        data = extractor.to_dict(results)

        assert isinstance(data, dict)
        assert "Invoice Number" in data
        assert data["Invoice Number"] == "INV-001"

    @pytest.mark.unit
    def test_case_insensitive_extraction(self, extractor):
        """Test case-insensitive field matching."""
        text = "invoice number: INV-001"  # lowercase
        results = extractor.extract(text, enabled_fields=["Invoice Number"])

        assert results["Invoice Number"].found
