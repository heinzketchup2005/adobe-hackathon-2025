# src/utils/helpers.py
"""
Shared utility functions
"""

import json
import os
import time
import re
from datetime import datetime

# Precompile regex for text cleaning
_whitespace_pattern = re.compile(r'\s+')

def save_json(data, path):
    """Save data to a JSON file"""
    try:
        # Ensure directory exists
        ensure_dir(os.path.dirname(path))
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        log(f"Error saving JSON to {path}: {str(e)}", level="ERROR")
        return False

def load_json(path):
    """Load data from a JSON file"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        log(f"Error loading JSON from {path}: {str(e)}", level="ERROR")
        return None
        
def log(msg, level="INFO"):
    """Log a message with timestamp and level"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {msg}")

def ensure_dir(path):
    """Ensure a directory exists"""
    if path:
        os.makedirs(path, exist_ok=True)
    
def clean_text(text):
    """Clean text by removing extra whitespace"""
    if not text:
        return ""
    return _whitespace_pattern.sub(' ', text.strip())

def timer(func):
    """Decorator to time function execution"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start_time
        log(f"{func.__name__} completed in {elapsed:.2f} seconds")
        return result
    return wrapper