#!/usr/bin/env python3
"""
PDF Outline Extractor - Main Entry Point
"""

import os
import sys
import time
import traceback
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.round1a.main import process_pdf
from src.utils.helpers import log, ensure_dir

def process_single_pdf(pdf_path, output_dir):
    """Process a single PDF file"""
    start_time = time.time()
    output_file = output_dir / f"{pdf_path.stem}.json"
    
    try:
        log(f"Processing {pdf_path.name}...")
        process_pdf(str(pdf_path), str(output_file))
        elapsed = time.time() - start_time
        log(f"Successfully generated {output_file.name} in {elapsed:.2f} seconds")
        return True
    except Exception as e:
        log(f"Error processing {pdf_path.name}: {str(e)}")
        traceback.print_exc()
        return False

def main():
    """Main execution function"""
    overall_start = time.time()
    
    # Check if running in Docker or locally
    if os.path.exists("/app"):
        input_dir = Path("/app/input")
        output_dir = Path("/app/output")
    else:
        input_dir = Path("input")
        output_dir = Path("output")
    
    # Ensure output directory exists
    ensure_dir(str(output_dir))
    
    # Find all PDF files in input directory
    pdf_files = list(input_dir.glob("*.pdf"))
    
    # Also check for text files during testing
    if not pdf_files:
        pdf_files = list(input_dir.glob("*.txt"))
    
    if not pdf_files:
        log("No PDF files found in input directory!")
        return
    
    log(f"Found {len(pdf_files)} PDF files to process")
    
    # Process PDFs sequentially
    success_count = 0
    total_files = len(pdf_files)
    
    for i, pdf_file in enumerate(pdf_files, 1):
        filename = pdf_file.name if hasattr(pdf_file, 'name') else os.path.basename(str(pdf_file))
        log(f"Processing file {i}/{total_files}: {filename}")
        if process_single_pdf(pdf_file, output_dir):
            success_count += 1
    
    # Report statistics
    total_elapsed = time.time() - overall_start
    log(f"Processing complete! Successfully processed {success_count}/{total_files} files")
    log(f"Total execution time: {total_elapsed:.2f} seconds")

if __name__ == "__main__":
    main()