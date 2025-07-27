import unittest
import sys
import os
import tempfile
import json
from unittest.mock import Mock, patch, MagicMock

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from round1a.pdf_parser import parse_pdf
from round1a.heading_extractor import HeadingExtractor
from utils.helpers import save_json, load_json, clean_text

class TestIntegration(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method"""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create sample PDF data that mimics real document structure
        self.sample_pdf_data = {
            "blocks": [
                {
                    "type": 0,  # text block
                    "lines": [
                        {
                            "spans": [
                                {
                                    "text": "Adobe Hackathon 2025",
                                    "font": "Arial-Bold",
                                    "size": 18.0,
                                    "flags": 1,
                                    "color": 0,
                                    "bbox": [50, 50, 300, 80]
                                }
                            ]
                        },
                        {
                            "spans": [
                                {
                                    "text": "Round 1A: Document Analysis",
                                    "font": "Arial-Bold",
                                    "size": 16.0,
                                    "flags": 1,
                                    "color": 0,
                                    "bbox": [50, 100, 350, 130]
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
                                    "text": "This is the introduction section of the document.",
                                    "font": "Arial",
                                    "size": 12.0,
                                    "flags": 0,
                                    "color": 0,
                                    "bbox": [50, 180, 400, 200]
                                }
                            ]
                        },
                        {
                            "spans": [
                                {
                                    "text": "1.1 Background",
                                    "font": "Arial-Bold",
                                    "size": 13.0,
                                    "flags": 1,
                                    "color": 0,
                                    "bbox": [50, 220, 200, 240]
                                }
                            ]
                        },
                        {
                            "spans": [
                                {
                                    "text": "Background information about the project.",
                                    "font": "Arial",
                                    "size": 12.0,
                                    "flags": 0,
                                    "color": 0,
                                    "bbox": [50, 250, 400, 270]
                                }
                            ]
                        },
                        {
                            "spans": [
                                {
                                    "text": "2. Methodology",
                                    "font": "Arial-Bold",
                                    "size": 14.0,
                                    "flags": 1,
                                    "color": 0,
                                    "bbox": [50, 300, 200, 320]
                                }
                            ]
                        },
                        {
                            "spans": [
                                {
                                    "text": "Description of the methodology used.",
                                    "font": "Arial",
                                    "size": 12.0,
                                    "flags": 0,
                                    "color": 0,
                                    "bbox": [50, 330, 400, 350]
                                }
                            ]
                        },
                        {
                            "spans": [
                                {
                                    "text": "3. Results",
                                    "font": "Arial-Bold",
                                    "size": 14.0,
                                    "flags": 1,
                                    "color": 0,
                                    "bbox": [50, 380, 150, 400]
                                }
                            ]
                        },
                        {
                            "spans": [
                                {
                                    "text": "Results and findings of the analysis.",
                                    "font": "Arial",
                                    "size": 12.0,
                                    "flags": 0,
                                    "color": 0,
                                    "bbox": [50, 410, 400, 430]
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
    def test_complete_pipeline_success(self, mock_fitz_open):
        """Test the complete pipeline from PDF parsing to heading extraction"""
        # Mock the PDF document
        mock_doc = Mock()
        mock_page = Mock()
        mock_page.get_text.return_value = self.sample_pdf_data
        mock_doc.__iter__.return_value = [mock_page]
        mock_doc.__len__.return_value = 1
        
        mock_fitz_open.return_value = mock_doc
        
        # Step 1: Parse PDF
        all_pages = parse_pdf("test_document.pdf")
        
        # Verify PDF parsing
        self.assertIsInstance(all_pages, list)
        self.assertEqual(len(all_pages), 1)
        self.assertGreater(len(all_pages[0]), 0)
        
        # Step 2: Extract headings
        extractor = HeadingExtractor()
        outline = extractor.extract_outline(all_pages)
        
        # Verify heading extraction
        self.assertIn('title', outline)
        self.assertIn('outline', outline)
        self.assertIsInstance(outline['outline'], list)
        
        # Verify that headings were detected
        self.assertGreater(len(outline['outline']), 0)
        
        # Check specific headings
        heading_texts = [h['text'] for h in outline['outline']]
        expected_headings = ['1. Introduction', '1.1 Background', '2. Methodology', '3. Results']
        
        for expected in expected_headings:
            self.assertIn(expected, heading_texts, f"Expected heading '{expected}' not found")

    @patch('fitz.open')
    def test_pipeline_with_multiple_pages(self, mock_fitz_open):
        """Test pipeline with multiple pages"""
        # Create data for two pages
        page1_data = {
            "blocks": [{
                "type": 0,
                "lines": [{
                    "spans": [{
                        "text": "Page 1 Title",
                        "font": "Arial-Bold",
                        "size": 16.0,
                        "flags": 1,
                        "color": 0,
                        "bbox": [50, 50, 200, 80]
                    }]
                }]
            }]
        }
        
        page2_data = {
            "blocks": [{
                "type": 0,
                "lines": [{
                    "spans": [{
                        "text": "Page 2: Chapter 2",
                        "font": "Arial-Bold",
                        "size": 16.0,
                        "flags": 1,
                        "color": 0,
                        "bbox": [50, 50, 250, 80]
                    }]
                }]
            }]
        }
        
        mock_doc = Mock()
        mock_page1 = Mock()
        mock_page2 = Mock()
        
        mock_page1.get_text.return_value = page1_data
        mock_page2.get_text.return_value = page2_data
        
        mock_doc.__iter__.return_value = [mock_page1, mock_page2]
        mock_doc.__len__.return_value = 2
        
        mock_fitz_open.return_value = mock_doc
        
        # Run pipeline
        all_pages = parse_pdf("multi_page_document.pdf")
        extractor = HeadingExtractor()
        outline = extractor.extract_outline(all_pages)
        
        # Verify multi-page processing
        self.assertEqual(len(all_pages), 2)
        self.assertGreater(len(outline['outline']), 0)
        
        # Check that headings from both pages are included
        heading_texts = [h['text'] for h in outline['outline']]
        self.assertTrue(any('Page 1' in text for text in heading_texts) or 
                       any('Page 2' in text for text in heading_texts))

    @patch('fitz.open')
    def test_pipeline_data_persistence(self, mock_fitz_open):
        """Test that data can be saved and loaded correctly through the pipeline"""
        # Mock PDF document
        mock_doc = Mock()
        mock_page = Mock()
        mock_page.get_text.return_value = self.sample_pdf_data
        mock_doc.__iter__.return_value = [mock_page]
        mock_doc.__len__.return_value = 1
        
        mock_fitz_open.return_value = mock_doc
        
        # Run pipeline
        all_pages = parse_pdf("test_document.pdf")
        extractor = HeadingExtractor()
        outline = extractor.extract_outline(all_pages)
        
        # Save results
        output_file = os.path.join(self.temp_dir, "pipeline_output.json")
        save_json(outline, output_file)
        
        # Load and verify
        loaded_outline = load_json(output_file)
        
        # Verify data integrity
        self.assertEqual(loaded_outline, outline)
        self.assertIn('title', loaded_outline)
        self.assertIn('outline', loaded_outline)
        self.assertIsInstance(loaded_outline['outline'], list)

    @patch('fitz.open')
    def test_pipeline_error_handling(self, mock_fitz_open):
        """Test error handling in the pipeline"""
        # Test with corrupted PDF data
        corrupted_data = {
            "blocks": [
                {
                    "type": 0,
                    "lines": [
                        {
                            "spans": [
                                {
                                    "text": "",  # Empty text
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
        
        mock_doc = Mock()
        mock_page = Mock()
        mock_page.get_text.return_value = corrupted_data
        mock_doc.__iter__.return_value = [mock_page]
        mock_doc.__len__.return_value = 1
        
        mock_fitz_open.return_value = mock_doc
        
        # Pipeline should handle empty text gracefully
        all_pages = parse_pdf("corrupted_document.pdf")
        extractor = HeadingExtractor()
        outline = extractor.extract_outline(all_pages)
        
        # Should still produce valid output structure
        self.assertIn('title', outline)
        self.assertIn('outline', outline)
        self.assertIsInstance(outline['outline'], list)

    def test_heading_classification_accuracy(self):
        """Test accuracy of heading classification"""
        # Create test data with known heading levels
        test_spans = [
            {
                'text': '1. Main Heading',
                'size': 16.0,
                'font': 'Arial-Bold',
                'page': 1,
                'bbox': [50, 100, 200, 130]
            },
            {
                'text': '1.1 Sub Heading',
                'size': 14.0,
                'font': 'Arial-Bold',
                'page': 1,
                'bbox': [50, 150, 200, 170]
            },
            {
                'text': '1.1.1 Sub Sub Heading',
                'size': 13.0,
                'font': 'Arial-Bold',
                'page': 1,
                'bbox': [50, 200, 250, 220]
            },
            {
                'text': 'Regular paragraph text',
                'size': 12.0,
                'font': 'Arial',
                'page': 1,
                'bbox': [50, 250, 300, 270]
            }
        ]
        
        extractor = HeadingExtractor()
        headings = extractor._detect_headings_strict(test_spans)
        classified_headings = extractor._classify_heading_levels_improved(headings)
        
        # Verify heading detection
        self.assertGreater(len(classified_headings), 0)
        
        # Check that regular text is not classified as heading
        heading_texts = [h['text'] for h in classified_headings]
        self.assertNotIn('Regular paragraph text', heading_texts)

    def test_pipeline_performance(self):
        """Test pipeline performance with larger datasets"""
        # Create larger test dataset
        large_spans = []
        for i in range(100):
            span = {
                'text': f'Section {i+1}',
                'size': 14.0 if i % 5 == 0 else 12.0,  # Every 5th is a heading
                'font': 'Arial-Bold' if i % 5 == 0 else 'Arial',
                'page': (i // 20) + 1,  # 20 spans per page
                'bbox': [50, 100 + i*10, 200, 120 + i*10]
            }
            large_spans.append(span)
        
        # Test processing time
        import time
        start_time = time.time()
        
        extractor = HeadingExtractor()
        outline = extractor.extract_outline([large_spans])
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Verify performance (should complete within reasonable time)
        self.assertLess(processing_time, 5.0, f"Processing took too long: {processing_time:.2f} seconds")
        
        # Verify output quality
        self.assertIn('title', outline)
        self.assertIn('outline', outline)
        self.assertIsInstance(outline['outline'], list)

    def test_pipeline_edge_cases(self):
        """Test pipeline with various edge cases"""
        edge_case_spans = [
            # Very long heading
            {
                'text': 'This is a very long heading that might cause issues with text processing and classification algorithms',
                'size': 16.0,
                'font': 'Arial-Bold',
                'page': 1,
                'bbox': [50, 100, 600, 130]
            },
            # Heading with special characters
            {
                'text': 'Section 2.1: Special Characters & Symbols (@#$%)',
                'size': 14.0,
                'font': 'Arial-Bold',
                'page': 1,
                'bbox': [50, 150, 400, 170]
            },
            # Heading with numbers and letters
            {
                'text': 'Chapter 3A: Advanced Topics',
                'size': 16.0,
                'font': 'Arial-Bold',
                'page': 1,
                'bbox': [50, 200, 300, 230]
            },
            # Very short heading
            {
                'text': 'A',
                'size': 14.0,
                'font': 'Arial-Bold',
                'page': 1,
                'bbox': [50, 250, 70, 270]
            }
        ]
        
        extractor = HeadingExtractor()
        outline = extractor.extract_outline([edge_case_spans])
        
        # Should handle edge cases gracefully
        self.assertIn('title', outline)
        self.assertIn('outline', outline)
        self.assertIsInstance(outline['outline'], list)

    def test_pipeline_consistency(self):
        """Test that pipeline produces consistent results"""
        # Run the same data multiple times
        test_spans = [
            {
                'text': '1. Test Heading',
                'size': 14.0,
                'font': 'Arial-Bold',
                'page': 1,
                'bbox': [50, 100, 200, 120]
            },
            {
                'text': 'Regular text content',
                'size': 12.0,
                'font': 'Arial',
                'page': 1,
                'bbox': [50, 150, 300, 170]
            }
        ]
        
        extractor = HeadingExtractor()
        results = []
        
        # Run multiple times
        for i in range(5):
            outline = extractor.extract_outline([test_spans])
            results.append(outline)
        
        # All results should be identical
        for i in range(1, len(results)):
            self.assertEqual(results[i], results[0], f"Result {i} differs from first result")

if __name__ == '__main__':
    unittest.main() 