# PDF Outline Extractor - Adobe Hackathon 2025

## Challenge Overview
This project extracts structured outlines from PDF documents, identifying the title and hierarchical headings (H1, H2, H3) with their corresponding page numbers.

## Project Structure
```
├── src/
│   ├── round1a/          # Core extraction logic
│   │   ├── main.py       # Processing logic
│   │   ├── pdf_parser.py # PDF text extraction
│   │   └── heading_extractor.py # Heading detection
│   └── utils/            # Utilities
│       └── helpers.py    # Helper functions
├── input/                # Place your PDFs here
├── output/               # JSON outputs appear here
├── Dockerfile           # Docker configuration
├── main.py              # Main entry point
└── requirements.txt     # Dependencies
```

## Features

- Extracts document title from PDF files
- Identifies headings using font properties and content patterns
- Organizes headings into hierarchical levels (H1, H2, H3)
- Creates clean JSON output with title and outline
- Fast processing (handles 50-page PDFs in under 10 seconds)
- Works offline without internet connection
- Supports scanned PDFs through OCR technology

## How to Use

### Input and Output
1. Place your PDF files in the `input/` folder
2. Run the program (see below)
3. Find the generated JSON files in the `output/` folder (same filename as input but with .json extension)

### Local Development (without Docker)
```bash
# Install dependencies
pip install -r requirements.txt

# Run the program
python main.py
```

### Using Docker
Docker is a platform that packages the application and all its dependencies into a container that can run consistently on any system. The Docker image includes Tesseract OCR for processing scanned PDFs.

```bash
# Build the Docker image
docker build --platform linux/amd64 -t pdf-extractor .

# Run the container
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none pdf-extractor
```

The `-v` flag maps your local input and output folders to the container's folders, so files can be shared between your computer and the Docker container.

## Output Format

The solution generates a JSON file with the following structure:

```json
{
  "title": "Understanding AI",
  "outline": [
    { "level": "H1", "text": "Introduction", "page": 1 },
    { "level": "H2", "text": "What is AI?", "page": 2 },
    { "level": "H3", "text": "History of AI", "page": 3 }
  ]
}
```

## Technical Details

### How It Works
- Uses font size, formatting, and position to identify headings
- Analyzes text patterns to recognize heading structures
- Groups similar headings into hierarchical levels
- Extracts the most prominent text as the document title
- For scanned PDFs, employs OCR technology to first convert images to text before applying heading extraction algorithms

### Libraries Used
- PyMuPDF (fitz): PDF parsing
- NumPy: Data analysis
- scikit-learn: Pattern recognition
- Tesseract OCR: Text extraction from scanned documents

## Notes
- For large PDFs, processing may take longer but should still be under 10 seconds
- For OCR functionality, Tesseract OCR must be installed on your system
  - On macOS: `brew install tesseract`
  - On Ubuntu/Debian: `apt-get install tesseract-ocr`
  - On Windows: Download installer from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)