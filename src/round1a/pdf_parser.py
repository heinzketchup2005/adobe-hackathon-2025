# src/round1a/pdf_parser.py
"""
PDF parsing utilities
"""

import fitz  # PyMuPDF
import sys
import os
import time

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.helpers import log, clean_text

class PDFParser:
    def __init__(self):
        """Initialize the PDF parser"""
        # Minimum text length to consider (for filtering noise)
        self.min_text_length = 2
        # Skip these characters as standalone text
        self.skip_chars = {'•', '○', '-', '–', '—', '>', '<', '*'}
        
    def parse(self, pdf_path):
        """Parse a PDF file and return structured data"""
        start_time = time.time()
        log(f"Opening PDF: {pdf_path}")
        
        # Open the PDF document
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        all_pages = []
        
        # Process each page
        for page_num, page in enumerate(doc, start=1):
            # Log progress
            if page_num % 5 == 0 or page_num == 1 or page_num == total_pages:
                log(f"Parsing page {page_num}/{total_pages}")
                
            page_data = []
            # Extract text blocks from the page
            blocks = page.get_text("dict")["blocks"]
            
            # Process each text block
            for block in blocks:
                if block["type"] == 0:  # text block
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text = clean_text(span["text"])
                            
                            # Skip very short text or standalone special characters
                            if len(text) < self.min_text_length or text in self.skip_chars or text.isdigit():
                                continue
                                
                            # Create span data with only necessary attributes
                            span_data = {
                                "text": text,
                                "font": span["font"],
                                "size": span["size"],
                                "flags": span["flags"],
                                "bbox": span["bbox"],
                                "page": page_num
                            }
                            page_data.append(span_data)
                            
            all_pages.append(page_data)
        
        # Close the document to free resources
        doc.close()
        
        total_spans = sum(len(p) for p in all_pages)
        elapsed_time = time.time() - start_time
        log(f"Extracted {total_spans} text spans from {pdf_path} in {elapsed_time:.2f} seconds")
        
        return all_pages

# For backward compatibility with existing code
def parse_pdf(pdf_path):
    parser = PDFParser()
    return parser.parse(pdf_path)