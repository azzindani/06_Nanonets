"""
Unit tests for output parser.
"""
import pytest
from core.output_parser import OutputParser


class TestOutputParser:
    """Tests for OutputParser class."""

    @pytest.fixture
    def parser(self):
        return OutputParser()

    @pytest.mark.unit
    def test_parse_empty_text(self, parser):
        """Test parsing empty text."""
        result = parser.parse("")
        assert result.pages == []

    @pytest.mark.unit
    def test_parse_single_page(self, parser, sample_ocr_text):
        """Test parsing a single page."""
        result = parser.parse(sample_ocr_text)
        assert len(result.pages) == 1

    @pytest.mark.unit
    def test_extract_tables(self, parser):
        """Test table extraction from HTML."""
        content = "<table><tr><td>A</td><td>B</td></tr></table>"
        html_tables, csv_tables = parser.extract_tables(content)

        assert len(html_tables) == 1
        assert len(csv_tables) == 1
        assert "<table>" in html_tables[0]

    @pytest.mark.unit
    def test_extract_no_tables(self, parser):
        """Test when no tables present."""
        content = "Just plain text without tables."
        html_tables, csv_tables = parser.extract_tables(content)

        assert len(html_tables) == 0
        assert len(csv_tables) == 0

    @pytest.mark.unit
    def test_extract_equations_inline(self, parser):
        """Test inline equation extraction."""
        content = "The formula is $E = mc^2$ here."
        equations = parser.extract_equations(content)

        assert len(equations) == 1
        assert "E = mc^2" in equations[0]

    @pytest.mark.unit
    def test_extract_equations_display(self, parser):
        """Test display equation extraction."""
        content = "The formula is $$\\int_0^1 x dx$$ here."
        equations = parser.extract_equations(content)

        assert len(equations) >= 1

    @pytest.mark.unit
    def test_extract_images(self, parser):
        """Test image description extraction."""
        content = "<img>A beautiful sunset</img>"
        images = parser.extract_images(content)

        assert len(images) == 1
        assert "sunset" in images[0]

    @pytest.mark.unit
    def test_extract_watermarks(self, parser):
        """Test watermark extraction."""
        content = "<watermark>CONFIDENTIAL</watermark>"
        watermarks = parser.extract_watermarks(content)

        assert len(watermarks) == 1
        assert watermarks[0] == "CONFIDENTIAL"

    @pytest.mark.unit
    def test_extract_page_numbers(self, parser):
        """Test page number extraction."""
        content = "<page_number>5/10</page_number>"
        page_numbers = parser.extract_page_numbers(content)

        assert len(page_numbers) == 1
        assert page_numbers[0] == "5/10"

    @pytest.mark.unit
    def test_extract_checkboxes(self, parser):
        """Test checkbox extraction."""
        content = "☑ Task done\n☐ Task pending"
        checkboxes = parser.extract_checkboxes(content)

        assert len(checkboxes) == 2

        checked = [cb for cb in checkboxes if cb["checked"]]
        unchecked = [cb for cb in checkboxes if not cb["checked"]]

        assert len(checked) == 1
        assert len(unchecked) == 1

    @pytest.mark.unit
    def test_to_dict(self, parser, sample_ocr_text):
        """Test conversion to dictionary."""
        result = parser.parse(sample_ocr_text)
        data = parser.to_dict(result)

        assert "pages" in data
        assert isinstance(data["pages"], list)
