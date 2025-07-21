# src/utils/.ipynb_checkpoints/helpers-checkpoint.py
"""
Shared utility functions
"""

import json
import os

def save_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
        
def log(msg):
    print(f"[INFO] {msg}")

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)
    
def clean_text(text):
    return " ".join(text.strip().split())