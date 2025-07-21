# test_pdf_parser.py (create this in your root directory)
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import the functions
from src.round1a.pdf_parser import parse_pdf
from src.utils.helpers import log, save_json

def test_pdf_parser():
    # Test with a sample PDF (you'll need to add one)
    pdf_path = "input/sample.pdf"  # Put a test PDF here
    
    if not os.path.exists(pdf_path):
        print("❌ No PDF found! Please add a sample PDF to input/sample.pdf")
        return
    
    print("🚀 Testing PDF Parser...")
    
    try:
        # Parse the PDF
        all_pages = parse_pdf(pdf_path)
        
        # Print some results
        print(f"✅ Successfully parsed PDF!")
        print(f"📊 Total pages: {len(all_pages)}")
        print(f"📝 Total text spans: {sum(len(page) for page in all_pages)}")
        
        # Show first few text spans
        if all_pages and all_pages[0]:
            print("\n🔍 First 5 text spans:")
            for i, span in enumerate(all_pages[0][:5]):
                print(f"  {i+1}. '{span['text']}' (size: {span['size']}, font: {span['font']})")
        
        # Save results to see full output
        save_json(all_pages, "output/test_parsed_output.json")
        print("💾 Saved full results to output/test_parsed_output.json")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pdf_parser()