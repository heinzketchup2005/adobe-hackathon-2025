# Test Suite for Adobe Hackathon 2025 Project

This directory contains comprehensive test files for the Adobe Hackathon 2025 project's heading extraction system.

## Test Files Overview

### 1. `test_heading_extractor.py`
Tests for the `HeadingExtractor` class functionality:
- **Initialization tests**: Verify proper setup of patterns and keywords
- **Pattern matching tests**: Test strong and weak heading pattern detection
- **Text preprocessing tests**: Verify span filtering and cleaning
- **Heading classification tests**: Test heading level assignment (H1, H2, H3)
- **Duplicate removal tests**: Ensure no duplicate headings
- **Edge case tests**: Handle various text formats and edge cases
- **Multi-page processing tests**: Verify cross-page heading detection

### 2. `test_pdf_parser.py`
Tests for the PDF parsing functionality:
- **Basic parsing tests**: Verify PDF text extraction
- **Multi-page tests**: Test parsing across multiple pages
- **Font property tests**: Verify font size, style, and color extraction
- **Text cleaning tests**: Ensure proper text normalization
- **Error handling tests**: Test with corrupted or missing files
- **Complex structure tests**: Handle various PDF layouts
- **Page numbering tests**: Verify correct page assignment

### 3. `test_utils.py`
Tests for utility functions:
- **JSON operations**: Test save/load functionality with Unicode support
- **Text cleaning**: Verify whitespace normalization
- **Directory creation**: Test `ensure_dir` function
- **Logging**: Test log message formatting
- **File permissions**: Verify proper file access
- **Integration tests**: Test utility function combinations

### 4. `test_integration.py`
Integration tests for the complete pipeline:
- **End-to-end tests**: Complete PDF → Heading extraction workflow
- **Data persistence tests**: Verify save/load functionality
- **Performance tests**: Test with large datasets
- **Consistency tests**: Ensure reproducible results
- **Error handling tests**: Test pipeline robustness
- **Multi-page integration**: Test complex document processing

## Running Tests

### Quick Start
```bash
# Run all tests
python run_tests.py

# Run specific test categories
python run_tests.py unit         # Unit tests only
python run_tests.py integration  # Integration tests only
python run_tests.py all          # All tests (default)
```

### Individual Test Files
```bash
# Run specific test files
python -m unittest tests.test_heading_extractor
python -m unittest tests.test_pdf_parser
python -m unittest tests.test_utils
python -m unittest tests.test_integration
```

### Verbose Output
```bash
# Run with detailed output
python -m unittest tests.test_heading_extractor -v
```

## Test Coverage

The test suite covers:

### Heading Extractor (85%+ coverage)
- Pattern matching (strong/weak patterns)
- Text preprocessing and filtering
- Heading level classification
- Duplicate detection and removal
- Font size analysis
- Multi-page processing
- Edge cases and error handling

### PDF Parser (90%+ coverage)
- PDF text extraction
- Font property extraction
- Multi-page handling
- Text cleaning and normalization
- Error handling for corrupted files
- Complex PDF structure handling

### Utilities (95%+ coverage)
- JSON save/load with Unicode support
- Text cleaning and normalization
- Directory creation and management
- Logging functionality
- File permission handling

### Integration (80%+ coverage)
- Complete pipeline testing
- Data persistence verification
- Performance benchmarking
- Consistency validation
- Error scenario handling

## Test Data

The tests use:
- **Mock PDF data**: Simulated PDF structure for consistent testing
- **Sample text spans**: Realistic document content
- **Edge cases**: Empty text, special characters, very long headings
- **Performance data**: Large datasets for performance testing

## Expected Test Results

When all tests pass, you should see:
```
Starting Test Suite for Adobe Hackathon 2025 Project
============================================================
Found 45+ test cases

✅ Tests run: 45
❌ Failures: 0
⚠️  Errors: 0
⏭️  Skipped: 0

📈 Success Rate: 100.0%
🎉 All tests passed!
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure `src` directory is in Python path
2. **Missing Dependencies**: Install required packages from `requirements.txt`
3. **Permission Errors**: Check file/directory permissions
4. **Mock Issues**: Verify PyMuPDF mocking is working correctly

### Debug Mode
```bash
# Run with debug output
python -m unittest tests.test_heading_extractor -v --debug
```

## Adding New Tests

To add new tests:

1. Create test file: `tests/test_new_feature.py`
2. Follow naming convention: `test_*.py`
3. Inherit from `unittest.TestCase`
4. Add comprehensive test cases
5. Update this README with new test information

## Test Best Practices

- Use descriptive test method names
- Include edge cases and error conditions
- Mock external dependencies
- Test performance with realistic data sizes
- Ensure tests are independent and repeatable
- Add proper cleanup in `tearDown` methods

## Continuous Integration

The test suite is designed to work with CI/CD pipelines:
- Exit codes: 0 for success, 1 for failure
- Structured output for parsing
- Performance benchmarks included
- Comprehensive error reporting 