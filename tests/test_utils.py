import unittest
import sys
import os
import tempfile
import json
import shutil

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.helpers import save_json, load_json, log, ensure_dir, clean_text

class TestUtils(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method"""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up after each test method"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_save_json_success(self):
        """Test successful JSON saving"""
        test_data = {
            "title": "Test Document",
            "headings": ["1. Introduction", "2. Methodology"],
            "nested": {"key": "value", "numbers": [1, 2, 3]},
            "boolean": True,
            "null_value": None
        }
        
        test_file = os.path.join(self.temp_dir, "test_save.json")
        
        # Save JSON
        save_json(test_data, test_file)
        
        # Verify file exists
        self.assertTrue(os.path.exists(test_file))
        
        # Verify content
        with open(test_file, 'r', encoding='utf-8') as f:
            saved_content = json.load(f)
        
        self.assertEqual(saved_content, test_data)

    def test_save_json_unicode(self):
        """Test JSON saving with Unicode characters"""
        test_data = {
            "title": "Test Document with Unicode: 测试文档",
            "headings": ["1. Introduction", "2. 方法论"],
            "special_chars": "áéíóú ñ ç ß"
        }
        
        test_file = os.path.join(self.temp_dir, "test_unicode.json")
        
        # Save JSON
        save_json(test_data, test_file)
        
        # Verify content
        with open(test_file, 'r', encoding='utf-8') as f:
            saved_content = json.load(f)
        
        self.assertEqual(saved_content, test_data)

    def test_save_json_directory_creation(self):
        """Test that save_json creates directories if they don't exist"""
        nested_dir = os.path.join(self.temp_dir, "nested", "deep", "directory")
        test_file = os.path.join(nested_dir, "test.json")
        
        test_data = {"key": "value"}
        
        # This should create the directory structure
        save_json(test_data, test_file)
        
        # Verify directory and file exist
        self.assertTrue(os.path.exists(nested_dir))
        self.assertTrue(os.path.exists(test_file))

    def test_load_json_success(self):
        """Test successful JSON loading"""
        test_data = {
            "title": "Test Document",
            "headings": ["1. Introduction", "2. Methodology"]
        }
        
        test_file = os.path.join(self.temp_dir, "test_load.json")
        
        # Create test file
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)
        
        # Load JSON
        loaded_data = load_json(test_file)
        
        # Verify content
        self.assertEqual(loaded_data, test_data)

    def test_load_json_file_not_found(self):
        """Test JSON loading when file doesn't exist"""
        non_existent_file = os.path.join(self.temp_dir, "nonexistent.json")
        
        # Should raise FileNotFoundError
        with self.assertRaises(FileNotFoundError):
            load_json(non_existent_file)

    def test_load_json_invalid_json(self):
        """Test JSON loading with invalid JSON content"""
        test_file = os.path.join(self.temp_dir, "invalid.json")
        
        # Create file with invalid JSON
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write('{"key": "value", "incomplete": }')
        
        # Should raise JSONDecodeError
        with self.assertRaises(json.JSONDecodeError):
            load_json(test_file)

    def test_clean_text_basic(self):
        """Test basic text cleaning functionality"""
        test_cases = [
            ("  hello   world  ", "hello world"),
            ("\n\ttest\n\ttext\n", "test text"),
            ("", ""),
            ("   ", ""),
            ("single", "single"),
            ("multiple    spaces", "multiple spaces"),
            ("\r\nwindows\r\nlinebreaks\r\n", "windows linebreaks"),
            ("\t\t\ttabs\t\t\t", "tabs"),
            ("  mixed  \t  whitespace  \n  ", "mixed whitespace")
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=repr(input_text)):
                result = clean_text(input_text)
                self.assertEqual(result, expected)

    def test_clean_text_unicode(self):
        """Test text cleaning with Unicode characters"""
        test_cases = [
            ("  hello   world  ", "hello world"),
            ("  testé   español  ", "testé español"),
            ("  测试  文档  ", "测试 文档"),
            ("\n\táéíóú\n\t", "áéíóú"),
            ("  ñ ç ß  ", "ñ ç ß")
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=repr(input_text)):
                result = clean_text(input_text)
                self.assertEqual(result, expected)

    def test_clean_text_special_characters(self):
        """Test text cleaning with special characters"""
        test_cases = [
            ("  text with !@#$%^&*()  ", "text with !@#$%^&*()"),
            ("  numbers 123 456  ", "numbers 123 456"),
            ("  punctuation . , ; : ! ?  ", "punctuation . , ; : ! ?"),
            ("  quotes \" ' `  ", "quotes \" ' `"),
            ("  brackets [ ] { } ( )  ", "brackets [ ] { } ( )")
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=repr(input_text)):
                result = clean_text(input_text)
                self.assertEqual(result, expected)

    def test_ensure_dir_basic(self):
        """Test basic directory creation"""
        test_dir = os.path.join(self.temp_dir, "test_directory")
        
        # Directory shouldn't exist initially
        self.assertFalse(os.path.exists(test_dir))
        
        # Create directory
        ensure_dir(test_dir)
        
        # Directory should exist now
        self.assertTrue(os.path.exists(test_dir))
        self.assertTrue(os.path.isdir(test_dir))

    def test_ensure_dir_nested(self):
        """Test nested directory creation"""
        nested_dir = os.path.join(self.temp_dir, "level1", "level2", "level3")
        
        # Nested directories shouldn't exist initially
        self.assertFalse(os.path.exists(nested_dir))
        
        # Create nested directories
        ensure_dir(nested_dir)
        
        # All levels should exist now
        self.assertTrue(os.path.exists(nested_dir))
        self.assertTrue(os.path.isdir(nested_dir))
        
        # Check intermediate directories
        level1 = os.path.join(self.temp_dir, "level1")
        level2 = os.path.join(level1, "level2")
        
        self.assertTrue(os.path.exists(level1))
        self.assertTrue(os.path.exists(level2))

    def test_ensure_dir_already_exists(self):
        """Test directory creation when directory already exists"""
        test_dir = os.path.join(self.temp_dir, "existing_directory")
        
        # Create directory first
        os.makedirs(test_dir)
        self.assertTrue(os.path.exists(test_dir))
        
        # Try to create again (should not fail)
        ensure_dir(test_dir)
        
        # Directory should still exist
        self.assertTrue(os.path.exists(test_dir))

    def test_ensure_dir_with_file(self):
        """Test directory creation when a file with same name exists"""
        test_path = os.path.join(self.temp_dir, "test_path")
        
        # Create a file
        with open(test_path, 'w') as f:
            f.write("test content")
        
        self.assertTrue(os.path.exists(test_path))
        self.assertTrue(os.path.isfile(test_path))
        
        # This should raise an error since we can't create a directory where a file exists
        with self.assertRaises(OSError):
            ensure_dir(test_path)

    def test_log_function(self):
        """Test the log function (basic functionality)"""
        # Capture stdout to test log output
        import io
        from contextlib import redirect_stdout
        
        test_message = "Test log message"
        
        with io.StringIO() as buf, redirect_stdout(buf):
            log(test_message)
            output = buf.getvalue()
        
        # Check that log message contains the expected content
        self.assertIn("[INFO]", output)
        self.assertIn(test_message, output)

    def test_log_function_empty_message(self):
        """Test log function with empty message"""
        import io
        from contextlib import redirect_stdout
        
        with io.StringIO() as buf, redirect_stdout(buf):
            log("")
            output = buf.getvalue()
        
        # Should still output [INFO] prefix
        self.assertIn("[INFO]", output)

    def test_log_function_special_characters(self):
        """Test log function with special characters"""
        import io
        from contextlib import redirect_stdout
        
        test_messages = [
            "Test with unicode: 测试",
            "Test with special chars: !@#$%^&*()",
            "Test with newlines:\nline1\nline2",
            "Test with quotes: \"hello\" 'world'"
        ]
        
        for message in test_messages:
            with self.subTest(message=message):
                with io.StringIO() as buf, redirect_stdout(buf):
                    log(message)
                    output = buf.getvalue()
                
                self.assertIn("[INFO]", output)
                self.assertIn(message, output)

    def test_integration_save_and_load(self):
        """Test integration between save_json and load_json"""
        test_data = {
            "title": "Integration Test",
            "data": {
                "numbers": [1, 2, 3, 4, 5],
                "strings": ["hello", "world"],
                "boolean": True,
                "null": None
            },
            "metadata": {
                "version": "1.0",
                "author": "Test User"
            }
        }
        
        test_file = os.path.join(self.temp_dir, "integration_test.json")
        
        # Save data
        save_json(test_data, test_file)
        
        # Load data
        loaded_data = load_json(test_file)
        
        # Verify data integrity
        self.assertEqual(loaded_data, test_data)
        
        # Verify nested structures
        self.assertEqual(loaded_data["data"]["numbers"], [1, 2, 3, 4, 5])
        self.assertEqual(loaded_data["metadata"]["version"], "1.0")

    def test_file_permissions(self):
        """Test file permissions for saved JSON files"""
        test_data = {"key": "value"}
        test_file = os.path.join(self.temp_dir, "permissions_test.json")
        
        # Save JSON
        save_json(test_data, test_file)
        
        # Check file permissions (should be readable and writable)
        self.assertTrue(os.access(test_file, os.R_OK))
        self.assertTrue(os.access(test_file, os.W_OK))

if __name__ == '__main__':
    unittest.main() 