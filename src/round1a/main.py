# src/round1a/main.py
#!/usr/bin/env python3
"""
Round 1A: PDF Structure Extraction
Extract structured outlines from PDFs
"""

import os
import json
from pathlib import Path
from .pdf_parser import PDFParser
from .heading_extractor import HeadingExtractor

def process_pdf(input_path: str, output_path: str):
    """Process a single PDF and extract outline"""
    parser = PDFParser()
    extractor = HeadingExtractor()
    
    # Parse PDF
    document = parser.parse(input_path)
    
    # Extract outline
    outline = extractor.extract_outline(document)
    
    # Save result
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(outline, f, indent=2, ensure_ascii=False)

def main():
    """Main execution function"""
    input_dir = Path("/app/input")
    output_dir = Path("/app/output")
    
    # Process all PDFs in input directory
    for pdf_file in input_dir.glob("*.pdf"):
        output_file = output_dir / f"{pdf_file.stem}.json"
        print(f"Processing {pdf_file.name}...")
        process_pdf(str(pdf_file), str(output_file))
        print(f"Generated {output_file.name}")

if __name__ == "__main__":
    main()
