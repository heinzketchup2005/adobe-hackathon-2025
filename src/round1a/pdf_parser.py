# Fix 1: Update src/round1a/pdf_parser.py
"""
PDF parsing utilities
"""

import fitz  # PyMuPDF
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.helpers import log, clean_text

def parse_pdf(pdf_path):
    log(f"Opening PDF: {pdf_path}")
    doc = fitz.open(pdf_path)
    all_pages = []

    for page_num, page in enumerate(doc, start=1):
        log(f"Parsing page {page_num}/{len(doc)}")
        page_data = []
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if block["type"] == 0:  # text block
                for line in block["lines"]:
                    for span in line["spans"]:
                        span_data = {
                            "text": clean_text(span["text"]),
                            "font": span["font"],
                            "size": span["size"],
                            "flags": span["flags"],
                            "color": span["color"],
                            "bbox": span["bbox"],
                            "page": page_num
                        }
                        page_data.append(span_data)
        all_pages.append(page_data)
    log(f"Extracted {sum(len(p) for p in all_pages)} text spans from {pdf_path}")
    return all_pages