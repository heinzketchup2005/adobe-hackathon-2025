# test_heading_extraction.py (UPDATED)
"""
Test the complete PDF parsing -> Heading extraction pipeline
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from round1a.pdf_parser import parse_pdf
from round1a.heading_extractor import HeadingExtractor
from utils.helpers import log, save_json, ensure_dir

def test_complete_pipeline():
    """Test the complete pipeline from PDF to outline"""
    pdf_path = "input/sample.pdf"
    
    # Ensure directories exist
    ensure_dir("input")
    ensure_dir("output")
    
    if not os.path.exists(pdf_path):
        print("❌ No PDF found! Please add a sample PDF to input/sample.pdf")
        print("   You can download any PDF and rename it to sample.pdf")
        return
    
    print("🚀 Testing Complete PDF -> Heading Extraction Pipeline...")
    
    try:
        # Step 1: Parse PDF
        print("\n📖 Step 1: Parsing PDF...")
        all_pages = parse_pdf(pdf_path)
        print(f"✅ Parsed {len(all_pages)} pages")
        
        # Step 2: Extract headings
        print("\n🎯 Step 2: Extracting headings...")
        extractor = HeadingExtractor()
        outline = extractor.extract_outline(all_pages)
        
        # Step 3: Display results
        print(f"\n📋 Results:")
        print(f"Title: '{outline['title']}'")
        print(f"Found {len(outline['outline'])} headings:")
        
        for i, heading in enumerate(outline['outline'], 1):
            indent = "  " if heading['level'] == 'H2' else "    " if heading['level'] == 'H3' else ""
            print(f"{i:2}. {indent}{heading['level']}: {heading['text']} (Page {heading['page']})")
        
        # Step 4: Save final JSON
        save_json(outline, "output/final_outline.json")
        print(f"\n💾 Saved final outline to output/final_outline.json")
        
        # Step 5: Validation
        print(f"\n✅ Validation:")
        print(f"   - Title extracted: {'✅' if outline['title'] != 'Untitled Document' else '❌'}")
        print(f"   - Has headings: {'✅' if outline['outline'] else '❌'}")
        print(f"   - Multiple levels: {'✅' if len(set(h['level'] for h in outline['outline'])) > 1 else '❌'}")
        
        return outline
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def analyze_heading_detection(all_pages):
    """Debug function to analyze how headings are detected"""
    print("\n🔍 Debugging Heading Detection...")
    
    # Flatten all spans
    all_spans = []
    for page_data in all_pages:
        all_spans.extend(page_data)
    
    # Analyze font sizes
    font_sizes = [span['size'] for span in all_spans if span['size'] > 0]
    unique_sizes = sorted(set(font_sizes), reverse=True)
    
    print(f"Font sizes found: {unique_sizes[:10]}...")  # Show top 10
    
    # Show text by font size
    for size in unique_sizes[:5]:  # Top 5 sizes
        texts = [span['text'][:50] + "..." if len(span['text']) > 50 else span['text'] 
                for span in all_spans if span['size'] == size][:3]  # First 3 examples
        print(f"Size {size}: {texts}")

if __name__ == "__main__":
    print("🔧 Setting up test environment...")
    outline = test_complete_pipeline()
    
    # Optional: Run debug analysis
    if outline:
        debug = input("\n🔍 Run debug analysis? (y/n): ")
        if debug.lower() == 'y':
            try:
                all_pages = parse_pdf("input/sample.pdf")
                analyze_heading_detection(all_pages)
            except Exception as e:
                print(f"Debug analysis failed: {e}")