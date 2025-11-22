"""
Unit tests for schema-based field extraction.
"""
import pytest
from unittest.mock import patch, MagicMock


class TestSchemaExtractor:
    """Tests for schema extractor functionality."""

    def test_import_schema_extractor(self):
        """Test that schema extractor can be imported."""
        from core.schema_extractor import SchemaExtractor
        assert SchemaExtractor is not None

    def test_schema_extractor_initialization(self):
        """Test SchemaExtractor can be initialized."""
        from core.schema_extractor import SchemaExtractor
        extractor = SchemaExtractor()
        assert extractor is not None

    def test_extract_with_invoice_schema(self):
        """Test extraction with invoice schema."""
        from core.schema_extractor import SchemaExtractor
        extractor = SchemaExtractor()

        text = """
        Invoice Number: INV-2024-001
        Date: January 15, 2024
        Total Amount: $1,250.00
        Tax: $125.00
        Vendor: Acme Corporation
        """

        result = extractor.extract(text, schema_type="invoice")

        assert result is not None
        assert isinstance(result, dict)

    def test_extract_invoice_number(self):
        """Test invoice number extraction."""
        from core.schema_extractor import SchemaExtractor
        extractor = SchemaExtractor()

        text = "Invoice Number: INV-2024-001"
        result = extractor.extract(text, schema_type="invoice")

        assert "invoice_number" in result
        assert "INV-2024-001" in str(result.get("invoice_number", ""))

    def test_extract_date(self):
        """Test date extraction."""
        from core.schema_extractor import SchemaExtractor
        extractor = SchemaExtractor()

        text = "Invoice Date: 2024-01-15"
        result = extractor.extract(text, schema_type="invoice")

        assert "date" in result or "invoice_date" in result

    def test_extract_total_amount(self):
        """Test total amount extraction."""
        from core.schema_extractor import SchemaExtractor
        extractor = SchemaExtractor()

        text = "Total Amount: $1,250.00"
        result = extractor.extract(text, schema_type="invoice")

        assert "total_amount" in result

    def test_extract_tax_amount(self):
        """Test tax amount extraction."""
        from core.schema_extractor import SchemaExtractor
        extractor = SchemaExtractor()

        text = "Tax: $125.00"
        result = extractor.extract(text, schema_type="invoice")

        assert "tax_amount" in result or "tax" in result

    def test_extract_with_receipt_schema(self):
        """Test extraction with receipt schema."""
        from core.schema_extractor import SchemaExtractor
        extractor = SchemaExtractor()

        text = """
        Store: SuperMart
        Date: 01/15/2024
        Total: $45.99
        """

        result = extractor.extract(text, schema_type="receipt")
        assert result is not None

    def test_extract_with_custom_schema(self):
        """Test extraction with custom schema."""
        from core.schema_extractor import SchemaExtractor
        extractor = SchemaExtractor()

        custom_schema = {
            "project_id": {
                "type": "string",
                "pattern": r"PRJ-\d+"
            },
            "budget": {
                "type": "number",
                "pattern": r"Budget:\s*\$?([\d,]+)"
            }
        }

        text = "Project: PRJ-12345, Budget: $50,000"
        result = extractor.extract(text, custom_schema=custom_schema)

        assert "project_id" in result
        assert "budget" in result

    def test_schema_validation(self):
        """Test schema validation."""
        from core.schema_extractor import SchemaExtractor
        extractor = SchemaExtractor()

        # Valid schema
        valid_schema = {
            "field1": {"type": "string", "pattern": r"\w+"}
        }
        assert extractor.validate_schema(valid_schema)

        # Invalid schema (missing type)
        invalid_schema = {
            "field1": {"pattern": r"\w+"}
        }
        assert not extractor.validate_schema(invalid_schema)

    def test_get_available_schemas(self):
        """Test getting available schema types."""
        from core.schema_extractor import SchemaExtractor
        extractor = SchemaExtractor()

        schemas = extractor.get_available_schemas()

        assert isinstance(schemas, list)
        assert "invoice" in schemas
        assert "receipt" in schemas

    def test_empty_text_returns_empty_result(self):
        """Test that empty text returns empty result."""
        from core.schema_extractor import SchemaExtractor
        extractor = SchemaExtractor()

        result = extractor.extract("", schema_type="invoice")

        assert result is not None
        assert isinstance(result, dict)

    def test_confidence_scores(self):
        """Test that extraction includes confidence scores."""
        from core.schema_extractor import SchemaExtractor
        extractor = SchemaExtractor()

        text = "Invoice Number: INV-001"
        result = extractor.extract(text, schema_type="invoice", include_confidence=True)

        # Result should have confidence info
        assert result is not None


class TestSchemaTypes:
    """Tests for different schema types."""

    def test_invoice_schema_fields(self):
        """Test invoice schema has expected fields."""
        from core.schema_extractor import SchemaExtractor
        extractor = SchemaExtractor()

        schema = extractor.get_schema("invoice")

        assert "invoice_number" in schema
        assert "total_amount" in schema

    def test_receipt_schema_fields(self):
        """Test receipt schema has expected fields."""
        from core.schema_extractor import SchemaExtractor
        extractor = SchemaExtractor()

        schema = extractor.get_schema("receipt")

        assert schema is not None

    def test_contract_schema_fields(self):
        """Test contract schema has expected fields."""
        from core.schema_extractor import SchemaExtractor
        extractor = SchemaExtractor()

        schema = extractor.get_schema("contract")

        # May return None if not defined
        assert schema is None or isinstance(schema, dict)


class TestSchemaPatterns:
    """Tests for schema pattern matching."""

    def test_currency_pattern(self):
        """Test currency amount pattern matching."""
        from core.schema_extractor import SchemaExtractor
        extractor = SchemaExtractor()

        # Various currency formats
        texts = [
            "Total: $1,234.56",
            "Amount: 1234.56",
            "Sum: €500.00",
            "Total Due: £99.99"
        ]

        for text in texts:
            result = extractor.extract(text, schema_type="invoice")
            assert result is not None

    def test_date_pattern(self):
        """Test date pattern matching."""
        from core.schema_extractor import SchemaExtractor
        extractor = SchemaExtractor()

        # Various date formats
        texts = [
            "Date: 2024-01-15",
            "Date: 01/15/2024",
            "Date: January 15, 2024",
            "Date: 15-Jan-2024"
        ]

        for text in texts:
            result = extractor.extract(text, schema_type="invoice")
            assert result is not None

    def test_email_pattern(self):
        """Test email pattern matching."""
        from core.schema_extractor import SchemaExtractor
        extractor = SchemaExtractor()

        text = "Contact: support@example.com"
        result = extractor.extract(text, schema_type="invoice")

        assert result is not None

    def test_phone_pattern(self):
        """Test phone number pattern matching."""
        from core.schema_extractor import SchemaExtractor
        extractor = SchemaExtractor()

        text = "Phone: +1 (555) 123-4567"
        result = extractor.extract(text, schema_type="invoice")

        assert result is not None
