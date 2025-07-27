# src/round1a/main.py
#!/usr/bin/env python3
"""
PDF Outline Extraction
"""

import os
import json
import time
from pathlib import Path
from .pdf_parser import PDFParser
from .heading_extractor import HeadingExtractor
from ..utils.helpers import log, ensure_dir

# Create singleton instances for reuse
_parser = PDFParser()
_extractor = HeadingExtractor()

def process_pdf(input_path: str, output_path: str):
    """Process a single PDF and extract outline"""
    start_time = time.time()
    
    # Ensure output directory exists
    output_dir = os.path.dirname(output_path)
    ensure_dir(output_dir)
    
    log("Starting PDF processing...")
    
    # Check if this is a text file (for testing)
    if input_path.endswith('.txt'):
        log(f"Processing text file: {os.path.basename(input_path)}")
        # Create a simple test document structure
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Create a mock document with a single page and span
        document = [[
            {
                "text": "Test Document",
                "font": "Helvetica",
                "size": 16,
                "flags": 16,  # Bold
                "bbox": [50, 50, 200, 70],
                "page": 1
            },
            {
                "text": content,
                "font": "Helvetica",
                "size": 12,
                "flags": 0,
                "bbox": [50, 100, 500, 120],
                "page": 1
            }
        ]]
        parse_time = time.time() - start_time
        log(f"✓ Text file processing completed in {parse_time:.2f} seconds")
    else:
        # Parse PDF (with page limit for very large PDFs)
        log(f"Step 1: Parsing PDF: {os.path.basename(input_path)}...")
        document = _parser.parse(input_path)
        parse_time = time.time() - start_time
        log(f"✓ PDF parsing completed in {parse_time:.2f} seconds")
    
    # Extract outline
    
    # Extract outline
    log("Step 2: Analyzing document structure and extracting headings...")
    extract_start = time.time()
    outline = _extractor.extract_outline(document)
    extract_time = time.time() - extract_start
    log(f"✓ Heading extraction completed in {extract_time:.2f} seconds")
    
    # Save result
    
    # Save result
    log("Step 3: Saving extracted outline...")
    save_start = time.time()
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(outline, f, indent=2, ensure_ascii=False)
    save_time = time.time() - save_start
    log(f"✓ Outline saved successfully in {save_time:.2f} seconds")
    
    total_time = time.time() - start_time
    log(f"✓ Total processing time: {total_time:.2f} seconds")
    
    return outline

def main():
    """Main execution function"""
    input_dir = Path("/app/input")
    output_dir = Path("/app/output")
    ensure_dir(str(output_dir))
    
    # Process all PDFs in input directory
    for pdf_file in input_dir.glob("*.pdf"):
        output_file = output_dir / f"{pdf_file.stem}.json"
        log(f"Processing {pdf_file.name}...")
        try:
            process_pdf(str(pdf_file), str(output_file))
            log(f"Generated {output_file.name}")
        except Exception as e:
            log(f"Error processing {pdf_file.name}: {str(e)}")

if __name__ == "__main__":
    main()
