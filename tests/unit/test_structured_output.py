"""Tests for structured output processor."""
import pytest
from core.structured_output import (
    StructuredOutputProcessor,
    get_structured_processor,
    process_to_structured
)


class TestStructuredOutputProcessor:
    """Test structured output processing."""

    def setup_method(self):
        """Set up test fixtures."""
        self.processor = StructuredOutputProcessor()

    def test_process_invoice(self):
        """Test processing invoice text."""
        text = """
        SuperStore

        INVOICE
        # 16384

        Bill To:
        **Adam Hart**

        Ship To:
        **Nottingham, England, United Kingdom**

        Date: Dec 08 2012
        Ship Mode: Standard Class

        Balance Due: **$6,208.84**

        Subtotal: $6,118.14
        Shipping: $90.70
        Total: $6,208.84

        Notes:
        Thanks for your business!

        Terms:
        Order ID : ES-2012-AH10075139-41251
        """

        tables_html = [
            """<table>
            <thead>
            <tr><th>Item</th><th>Quantity</th><th>Rate</th><th>Amount</th></tr>
            </thead>
            <tbody>
            <tr>
            <td>Bush Stackable Bookrack, Pine\nBookcases, Furniture, FUR-BO-3647</td>
            <td>7</td>
            <td>$874.02</td>
            <td>$6,118.14</td>
            </tr>
            </tbody>
            </table>"""
        ]

        result = self.processor.process(text, tables_html)

        assert result["document_type"] == "invoice"
        assert result["confidence"] > 0
        assert result["language"] == "en"
        assert "extracted_fields" in result
        assert "line_items" in result
        assert "entities" in result
        assert "raw" in result

    def test_extract_invoice_fields(self):
        """Test field extraction from invoice."""
        text = """
        INVOICE # 12345
        Date: January 15, 2024
        Bill To: John Smith
        Ship To: 123 Main Street

        Subtotal: $100.00
        Shipping: $10.00
        Total: $110.00
        """

        result = self.processor.process(text)

        fields = result["extracted_fields"]
        assert "invoice_number" in fields
        assert fields["invoice_number"] == "12345"
        assert "date" in fields
        assert "total" in fields

    def test_extract_receipt_fields(self):
        """Test field extraction from receipt."""
        text = """
        RECEIPT
        Store: SuperMart
        Transaction # 98765
        Date: 01/15/2024

        Items purchased...

        Subtotal: $50.00
        Tax: $4.00
        Total: $54.00

        Paid by: Credit Card
        Cashier: Jane
        """

        result = self.processor.process(text)

        assert result["document_type"] == "receipt"
        assert "total" in result["extracted_fields"]

    def test_entity_extraction(self):
        """Test entity extraction."""
        text = """
        Invoice for John Smith
        Email: john@example.com
        Phone: (555) 123-4567
        Amount: $1,500.00
        Date: January 15, 2024
        """

        result = self.processor.process(text)

        entities = result["entities"]
        assert len(entities) > 0

        entity_types = [e["type"] for e in entities]
        # Should extract at least some entities
        assert any(t in entity_types for t in ["email", "phone", "money", "date"])

    def test_language_detection(self):
        """Test language detection in output."""
        # English text
        en_text = "This is an invoice for services rendered. The total amount due is $500."
        result = self.processor.process(en_text)
        assert result["language"] == "en"

        # Spanish text - use more characteristic Spanish words
        es_text = "Esta es una factura por los servicios prestados. El total que debe pagar es de quinientos dólares. Por favor realice el pago antes de la fecha límite."
        result = self.processor.process(es_text)
        assert result["language"] == "es"

    def test_line_item_parsing(self):
        """Test parsing line items from table."""
        text = "Invoice with items"
        tables_html = [
            """<table>
            <tr><th>Item</th><th>Qty</th><th>Price</th><th>Amount</th></tr>
            <tr><td>Widget A</td><td>5</td><td>$10.00</td><td>$50.00</td></tr>
            <tr><td>Widget B</td><td>3</td><td>$20.00</td><td>$60.00</td></tr>
            </table>"""
        ]

        result = self.processor.process(text, tables_html)

        assert len(result["line_items"]) == 2
        assert result["line_items"][0]["description"] == "Widget A"
        assert result["line_items"][0]["quantity"] == "5"

    def test_empty_text(self):
        """Test processing empty text."""
        result = self.processor.process("")

        assert result["document_type"] == "unknown"
        assert result["confidence"] == 0
        assert result["extracted_fields"] == {}

    def test_nested_field_structure(self):
        """Test nested field structuring."""
        text = """
        INVOICE
        Bill To: Jane Doe
        Ship To: 456 Oak Avenue
        Total: $200.00
        """

        result = self.processor.process(text)
        fields = result["extracted_fields"]

        # Should structure bill_to and ship_to as nested objects
        if "bill_to" in fields:
            assert isinstance(fields["bill_to"], dict)
            assert "name" in fields["bill_to"]

    def test_raw_data_included(self):
        """Test that raw data is included."""
        text = "Sample invoice text"
        result = self.processor.process(text)

        assert "raw" in result
        assert "text" in result["raw"]
        assert result["raw"]["text"] == text

    def test_singleton_instance(self):
        """Test singleton pattern."""
        processor1 = get_structured_processor()
        processor2 = get_structured_processor()

        assert processor1 is processor2

    def test_convenience_function(self):
        """Test convenience function."""
        text = "Invoice # 123, Total: $500"
        result = process_to_structured(text)

        assert "document_type" in result
        assert "extracted_fields" in result


class TestLineItemParsing:
    """Test line item parsing specifically."""

    def setup_method(self):
        """Set up test fixtures."""
        self.processor = StructuredOutputProcessor()

    def test_parse_with_sku(self):
        """Test parsing items with SKU codes."""
        tables_html = [
            """<table>
            <tr><th>Item</th><th>Quantity</th><th>Amount</th></tr>
            <tr><td>Product Name\nCategory, SKU-123-456</td><td>2</td><td>$100</td></tr>
            </table>"""
        ]

        result = self.processor.process("Invoice", tables_html)
        items = result["line_items"]

        if len(items) > 0:
            assert "description" in items[0]

    def test_empty_table(self):
        """Test parsing empty table."""
        tables_html = ["<table><tr><th>Item</th></tr></table>"]

        result = self.processor.process("Invoice", tables_html)
        assert result["line_items"] == []
