# adobe-hackathon-2025
# README.md
# Adobe India Hackathon 2025 - Connecting the Dots

## Challenge Overview
Building an intelligent PDF experience that extracts structured outlines and provides persona-driven document intelligence.

## Project Structure
```
├── src/
│   ├── round1a/          # PDF outline extraction
│   ├── round1b/          # Persona-driven intelligence
│   └── utils/            # Shared utilities
├── input/                # Input PDFs
├── output/               # Generated JSON outputs
├── tests/                # Unit tests
├── Dockerfile           # Container configuration
└── requirements.txt     # Python dependencies
```

## Development Setup

### Local Development
```bash
pip install -r requirements.txt
python src/round1a/main.py
python src/round1b/main.py
```

### Docker Build & Run
```bash
# Build image
docker build --platform linux/amd64 -t adobe-solution:latest .

# Run container
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none adobe-solution:latest
```

## Approach

### Round 1A: PDF Structure Extraction
- **Strategy**: [Your approach here]
- **Libraries**: PyMuPDF, pdfplumber
- **Key Features**: Multi-signal heading detection, robust parsing

### Round 1B: Persona-Driven Intelligence
- **Strategy**: [Your approach here]
- **Libraries**: sentence-transformers, scikit-learn
- **Key Features**: Semantic matching, relevance ranking

## Team
[Your team details]

## Timeline
- Week 1: Experimentation & Round 1A
- Week 2: Round 1B development  
- Week 3: Integration & optimization