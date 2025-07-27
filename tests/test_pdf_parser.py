import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
import tempfile
import json

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from round1a.pdf_parser import parse_pdf
from utils.helpers import clean_text, save_json, load_json

class TestPDFParser(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method"""
        # Create a temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        
        # Sample PDF data structure for mocking
        self.sample_pdf_data = {
            "blocks": [
                {
                    "type": 0,  # text block
                    "lines": [
                        {
                            "spans": [
                                {
                                    "text": "Sample Document Title",
                                    "font": "Arial-Bold",
                                    "size": 16.0,
                                    "flags": 1,
                                    "color": 0,
                                    "bbox": [50, 100, 300, 120]
                                }
                            ]
                        },
                        {
                            "spans": [
                                {
                                    "text": "1. Introduction",
                                    "font": "Arial-Bold",
                                    "size": 14.0,
                                    "flags": 1,
                                    "color": 0,
                                    "bbox": [50, 150, 200, 170]
                                }
                            ]
                        },
                        {
                            "spans": [
                                {
                                    "text": "This is a sample paragraph with regular text content.",
                                    "font": "Arial",
                                    "size": 12.0,
                                    "flags": 0,
                                    "color": 0,
                                    "bbox": [50, 200, 400, 220]
                                }
                            ]
                        }
                    ]
                }
            ]
        }

    def tearDown(self):
        """Clean up after each test method"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('fitz.open')
    def test_parse_pdf_success(self, mock_fitz_open):
        """Test successful PDF parsing"""
        # Mock the PDF document
        mock_doc = MagicMock()
        mock_page = MagicMock()
        
        # Configure the mock page to return our sample data
        mock_page.get_text.return_value = self.sample_pdf_data
        mock_doc.__iter__.return_value = [mock_page]
        mock_doc.__len__.return_value = 1
        
        mock_fitz_open.return_value = mock_doc
        
        # Test parsing
        result = parse_pdf("dummy_path.pdf")
        
        # Verify results
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)  # One page
        self.assertGreater(len(result[0]), 0)  # Has text spans
        
        # Check span structure
        span = result[0][0]
        self.assertIn('text', span)
        self.assertIn('font', span)
        self.assertIn('size', span)
        self.assertIn('flags', span)
        self.assertIn('color', span)
        self.assertIn('bbox', span)
        self.assertIn('page', span)

    @patch('fitz.open')
    def test_parse_pdf_multiple_pages(self, mock_fitz_open):
        """Test parsing PDF with multiple pages"""
        # Create mock data for two pages
        page1_data = {"blocks": [{"type": 0, "lines": [{"spans": [{"text": "Page 1", "font": "Arial", "size": 12.0, "flags": 0, "color": 0, "bbox": [0, 0, 100, 20]}]}]}]}
        page2_data = {"blocks": [{"type": 0, "lines": [{"spans": [{"text": "Page 2", "font": "Arial", "size": 12.0, "flags": 0, "color": 0, "bbox": [0, 0, 100, 20]}]}]}]}
        
        mock_doc = MagicMock()
        mock_page1 = MagicMock()
        mock_page2 = MagicMock()
        
        mock_page1.get_text.return_value = page1_data
        mock_page2.get_text.return_value = page2_data
        
        mock_doc.__iter__.return_value = [mock_page1, mock_page2]
        mock_doc.__len__.return_value = 2
        
        mock_fitz_open.return_value = mock_doc
        
        # Test parsing
        result = parse_pdf("multi_page.pdf")
        
        # Verify results
        self.assertEqual(len(result), 2)  # Two pages
        self.assertGreater(len(result[0]), 0)  # Page 1 has content
        self.assertGreater(len(result[1]), 0)  # Page 2 has content

    @patch('fitz.open')
    def test_parse_pdf_empty_pages(self, mock_fitz_open):
        """Test parsing PDF with empty pages"""
        empty_page_data = {"blocks": []}
        
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_text.return_value = empty_page_data
        mock_doc.__iter__.return_value = [mock_page]
        mock_doc.__len__.return_value = 1
        
        mock_fitz_open.return_value = mock_doc
        
        # Test parsing
        result = parse_pdf("empty.pdf")
        
        # Verify results
        self.assertEqual(len(result), 1)  # One page
        self.assertEqual(len(result[0]), 0)  # No text spans

    @patch('fitz.open')
    def test_parse_pdf_non_text_blocks(self, mock_fitz_open):
        """Test parsing PDF with non-text blocks (images, etc.)"""
        mixed_blocks_data = {
            "blocks": [
                {
                    "type": 1,  # Non-text block (e.g., image)
                    "lines": []
                },
                {
                    "type": 0,  # Text block
                    "lines": [
                        {
                            "spans": [
                                {
                                    "text": "Valid text content",
                                    "font": "Arial",
                                    "size": 12.0,
                                    "flags": 0,
                                    "color": 0,
                                    "bbox": [50, 100, 200, 120]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_text.return_value = mixed_blocks_data
        mock_doc.__iter__.return_value = [mock_page]
        mock_doc.__len__.return_value = 1
        
        mock_fitz_open.return_value = mock_doc
        
        # Test parsing
        result = parse_pdf("mixed_content.pdf")
        
        # Should only process text blocks (type 0)
        self.assertEqual(len(result), 1)
        self.assertEqual(len(result[0]), 1)  # Only one text span
        self.assertEqual(result[0][0]['text'], 'Valid text content')

    @patch('fitz.open')
    def test_parse_pdf_text_cleaning(self, mock_fitz_open):
        """Test that text is properly cleaned during parsing"""
        dirty_text_data = {
            "blocks": [
                {
                    "type": 0,
                    "lines": [
                        {
                            "spans": [
                                {
                                    "text": "  This   text   has   extra   spaces  ",
                                    "font": "Arial",
                                    "size": 12.0,
                                    "flags": 0,
                                    "color": 0,
                                    "bbox": [50, 100, 200, 120]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_text.return_value = dirty_text_data
        mock_doc.__iter__.return_value = [mock_page]
        mock_doc.__len__.return_value = 1
        
        mock_fitz_open.return_value = mock_doc
        
        # Test parsing
        result = parse_pdf("dirty_text.pdf")
        
        # Text should be cleaned
        self.assertEqual(result[0][0]['text'], 'This text has extra spaces')

    @patch('fitz.open')
    def test_parse_pdf_page_numbering(self, mock_fitz_open):
        """Test that page numbers are correctly assigned"""
        mock_doc = MagicMock()
        mock_page1 = MagicMock()
        mock_page2 = MagicMock()
        
        # Both pages return same data structure
        page_data = {"blocks": [{"type": 0, "lines": [{"spans": [{"text": "Content", "font": "Arial", "size": 12.0, "flags": 0, "color": 0, "bbox": [0, 0, 100, 20]}]}]}]}
        
        mock_page1.get_text.return_value = page_data
        mock_page2.get_text.return_value = page_data
        
        mock_doc.__iter__.return_value = [mock_page1, mock_page2]
        mock_doc.__len__.return_value = 2
        
        mock_fitz_open.return_value = mock_doc
        
        # Test parsing
        result = parse_pdf("numbered_pages.pdf")
        
        # Check page numbering
        self.assertEqual(result[0][0]['page'], 1)  # First page
        self.assertEqual(result[1][0]['page'], 2)  # Second page

    @patch('fitz.open')
    def test_parse_pdf_font_properties(self, mock_fitz_open):
        """Test that font properties are correctly extracted"""
        font_test_data = {
            "blocks": [
                {
                    "type": 0,
                    "lines": [
                        {
                            "spans": [
                                {
                                    "text": "Bold Text",
                                    "font": "Arial-Bold",
                                    "size": 14.0,
                                    "flags": 1,  # Bold flag
                                    "color": 16711680,  # Red color
                                    "bbox": [50, 100, 150, 120]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_text.return_value = font_test_data
        mock_doc.__iter__.return_value = [mock_page]
        mock_doc.__len__.return_value = 1
        
        mock_fitz_open.return_value = mock_doc
        
        # Test parsing
        result = parse_pdf("font_test.pdf")
        
        # Check font properties
        span = result[0][0]
        self.assertEqual(span['font'], 'Arial-Bold')
        self.assertEqual(span['size'], 14.0)
        self.assertEqual(span['flags'], 1)
        self.assertEqual(span['color'], 16711680)

    @patch('fitz.open')
    def test_parse_pdf_error_handling(self, mock_fitz_open):
        """Test error handling when PDF cannot be opened"""
        mock_fitz_open.side_effect = Exception("PDF file not found")
        
        # Should raise an exception
        with self.assertRaises(Exception):
            parse_pdf("nonexistent.pdf")

    def test_clean_text_helper(self):
        """Test the clean_text helper function"""
        test_cases = [
            ("  hello   world  ", "hello world"),
            ("\n\ttest\n\ttext\n", "test text"),
            ("", ""),
            ("   ", ""),
            ("single", "single"),
            ("multiple    spaces", "multiple spaces")
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                result = clean_text(input_text)
                self.assertEqual(result, expected)

    def test_json_helpers(self):
        """Test JSON save and load helper functions"""
        test_data = {
            "title": "Test Document",
            "headings": ["1. Introduction", "2. Methodology"],
            "pages": 2
        }
        
        test_file = os.path.join(self.temp_dir, "test.json")
        
        # Test saving
        save_json(test_data, test_file)
        self.assertTrue(os.path.exists(test_file))
        
        # Test loading
        loaded_data = load_json(test_file)
        self.assertEqual(loaded_data, test_data)

    @patch('fitz.open')
    def test_parse_pdf_complex_structure(self, mock_fitz_open):
        """Test parsing PDF with complex text structure"""
        complex_data = {
            "blocks": [
                {
                    "type": 0,
                    "lines": [
                        {
                            "spans": [
                                {"text": "Title", "font": "Arial-Bold", "size": 16.0, "flags": 1, "color": 0, "bbox": [50, 50, 100, 70]},
                                {"text": " ", "font": "Arial", "size": 16.0, "flags": 0, "color": 0, "bbox": [100, 50, 105, 70]},
                                {"text": "Part", "font": "Arial-Bold", "size": 16.0, "flags": 1, "color": 0, "bbox": [105, 50, 150, 70]}
                            ]
                        },
                        {
                            "spans": [
                                {"text": "1.1", "font": "Arial-Bold", "size": 14.0, "flags": 1, "color": 0, "bbox": [50, 100, 80, 120]},
                                {"text": " ", "font": "Arial", "size": 14.0, "flags": 0, "color": 0, "bbox": [80, 100, 85, 120]},
                                {"text": "Subsection", "font": "Arial-Bold", "size": 14.0, "flags": 1, "color": 0, "bbox": [85, 100, 180, 120]}
                            ]
                        }
                    ]
                }
            ]
        }
        
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_text.return_value = complex_data
        mock_doc.__iter__.return_value = [mock_page]
        mock_doc.__len__.return_value = 1
        
        mock_fitz_open.return_value = mock_doc
        
        # Test parsing
        result = parse_pdf("complex.pdf")
        
        # Should handle multiple spans per line
        self.assertEqual(len(result), 1)
        self.assertGreater(len(result[0]), 0)
        
        # Check that spans are properly processed
        for span in result[0]:
            self.assertIn('text', span)
            self.assertIn('font', span)
            self.assertIn('size', span)

if __name__ == '__main__':
    unittest.main() 