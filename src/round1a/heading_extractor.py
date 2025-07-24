# src/round1a/heading_extractor.py (IMPROVED VERSION)
"""
Heading extraction and classification - Much more selective approach
"""

import re
import sys
import os
from collections import Counter

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.helpers import log, clean_text

class HeadingExtractor:
    def __init__(self):
        # Strong heading patterns (high confidence)
        self.strong_patterns = [
            r'^\d+\.?\s+[A-Z]',  # "1. Introduction" or "1 Introduction"
            r'^\d+\.\d+\.?\s+[A-Z]',  # "1.1 Overview" 
            r'^\d+\.\d+\.\d+\.?\s+[A-Z]',  # "1.1.1 Details"
            r'^[IVX]+\.?\s+[A-Z]',  # Roman numerals "I. Introduction"
            r'^Chapter\s+\d+',  # "Chapter 1"
            r'^Section\s+\d+',  # "Section 1"
        ]
        
        # Weaker patterns (need additional signals)
        self.weak_patterns = [
            r'^[A-Z][a-z]+\s+(Overview|Introduction|Conclusion|Summary|Background|Methodology)',
            r'(Introduction|Conclusion|Abstract|Summary|Overview|Background|Methodology|Results|Discussion|References)$',
            r'^Round\s+\d+[A-Z]?:',  # "Round 1A:"
            r'^What\s+(You|We|This)',  # "What You Need to Build"
            r'^Why\s+This\s+Matters',
        ]
        
        # Strong heading keywords
        self.strong_keywords = [
            'introduction', 'conclusion', 'abstract', 'summary', 'overview',
            'background', 'methodology', 'results', 'discussion', 'references',
            'chapter', 'section', 'appendix', 'bibliography', 'acknowledgments',
            'constraints', 'requirements', 'deliverables', 'scoring'
        ]
        
        # Words that are NOT headings
        self.blacklist_words = [
            'and', 'or', 'but', 'the', 'a', 'an', 'to', 'from', 'by', 'with',
            'for', 'of', 'in', 'on', 'at', 'is', 'are', 'was', 'were', 'be',
            'magic', 'context', 'allowed', 'seconds', 'points', 'criteria'
        ]

    def extract_outline(self, all_pages_data):
        """Extract hierarchical outline from parsed PDF data"""
        log("Starting improved heading extraction...")
        
        # Flatten all text spans
        all_spans = []
        for page_data in all_pages_data:
            all_spans.extend(page_data)
        
        # Filter out empty or very short text, and merge fragments
        text_spans = self._preprocess_spans(all_spans)
        
        log(f"Analyzing {len(text_spans)} processed text spans for headings")
        
        # Extract title
        title = self._extract_title_improved(text_spans)
        
        # Detect headings with much stricter criteria
        headings = self._detect_headings_strict(text_spans)
        
        # Classify heading levels
        classified_headings = self._classify_heading_levels_improved(headings)
        
        log(f"Found {len(classified_headings)} headings after strict filtering")
        
        return {
            "title": title,
            "outline": classified_headings
        }
    
    def _preprocess_spans(self, all_spans):
        """Preprocess spans to merge fragments and filter noise"""
        # Group spans by page and similar y-coordinate (same line)
        processed_spans = []
        
        for span in all_spans:
            text = span['text'].strip()
            if len(text) < 2:  # Skip very short text
                continue
                
            # Skip if text is just punctuation or numbers
            if text in ['•', '○', '-', '–', '—'] or text.isdigit():
                continue
                
            processed_spans.append(span)
        
        return processed_spans
    
    def _extract_title_improved(self, text_spans):
        """Extract document title with better fragment handling"""
        if not text_spans:
            return "Untitled Document"
        
        # Get spans from first few pages
        early_spans = [span for span in text_spans if span['page'] <= 2]
        
        if not early_spans:
            return "Untitled Document"
        
        # Find the largest font size in early pages
        max_size = max(span['size'] for span in early_spans)
        
        # Get all text with largest font size
        title_spans = [
            span for span in early_spans 
            if span['size'] == max_size and len(span['text'].strip()) > 3
        ]
        
        if not title_spans:
            return "Untitled Document"
        
        # Try to merge fragments that might be parts of the same title
        title_candidates = []
        current_candidate = ""
        
        # Sort by page, then by y-coordinate (top to bottom)
        title_spans.sort(key=lambda s: (s['page'], -s['bbox'][1]))
        
        for span in title_spans:
            text = span['text'].strip()
            
            # If this looks like a continuation (starts with lowercase or is short)
            if (current_candidate and 
                (text[0].islower() or len(text) < 10) and 
                len(current_candidate + " " + text) < 100):
                current_candidate += " " + text
            else:
                if current_candidate:
                    title_candidates.append(current_candidate)
                current_candidate = text
        
        if current_candidate:
            title_candidates.append(current_candidate)
        
        # Filter candidates
        valid_candidates = []
        for candidate in title_candidates:
            candidate = clean_text(candidate)
            # Must be reasonable length and not just fragments
            if 10 <= len(candidate) <= 200 and not candidate.lower().startswith('welcome'):
                valid_candidates.append(candidate)
        
        if valid_candidates:
            # Take the longest reasonable candidate
            title = max(valid_candidates, key=len)
            log(f"Extracted title: '{title}'")
            return title
        
        return "Untitled Document"
    
    def _detect_headings_strict(self, text_spans):
        """Detect headings with much stricter criteria"""
        potential_headings = []
        
        # Get font size statistics
        font_sizes = [span['size'] for span in text_spans]
        avg_font_size = sum(font_sizes) / len(font_sizes)
        
        # Only consider text that's significantly larger or has strong formatting
        size_threshold = avg_font_size + 2  # Stricter threshold
        
        for span in text_spans:
            text = span['text'].strip()
            
            # Skip very short or very long text
            if len(text) < 5 or len(text) > 150:
                continue
                
            # Skip if text is mostly blacklisted words
            text_words = text.lower().split()
            if len(text_words) > 0 and sum(1 for word in text_words if word in self.blacklist_words) > len(text_words) * 0.6:
                continue
            
            heading_score = 0
            
            # Strong patterns get high scores
            for pattern in self.strong_patterns:
                if re.match(pattern, text, re.IGNORECASE):
                    heading_score += 5
                    break
            
            # Weak patterns need additional signals
            for pattern in self.weak_patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    heading_score += 2
                    break
            
            # Font size scoring (stricter)
            if span['size'] > size_threshold:
                heading_score += 3
            elif span['size'] > avg_font_size + 1:
                heading_score += 1
            
            # Bold text
            if span['flags'] & 16:
                heading_score += 2
            
            # Strong keyword matching
            text_lower = text.lower()
            if any(keyword in text_lower for keyword in self.strong_keywords):
                heading_score += 2
            
            # Position and formatting
            bbox = span['bbox']
            if bbox[0] < 100:  # Left aligned
                heading_score += 1
            
            # Text characteristics
            if text.endswith(':'):
                heading_score += 1
            
            # Title case or proper capitalization
            if text.istitle() or (text[0].isupper() and len(text.split()) > 1):
                heading_score += 1
            
            # Much higher threshold - only very confident headings
            if heading_score >= 6:  # Raised from 3 to 6
                potential_headings.append({
                    'text': text,
                    'page': span['page'],
                    'size': span['size'],
                    'score': heading_score,
                    'bbox': span['bbox'],
                    'font': span['font']
                })
        
        # Sort by page then by y-coordinate (reading order)
        potential_headings.sort(key=lambda h: (h['page'], -h['bbox'][1]))
        
        # Remove duplicates and very similar headings
        filtered_headings = self._remove_duplicate_headings(potential_headings)
        
        log(f"Found {len(filtered_headings)} high-confidence headings")
        return filtered_headings
    
    def _remove_duplicate_headings(self, headings):
        """Remove duplicate or very similar headings"""
        if not headings:
            return []
        
        filtered = []
        seen_texts = set()
        
        for heading in headings:
            text = heading['text'].strip().lower()
            
            # Skip if we've seen very similar text
            is_duplicate = False
            for seen in seen_texts:
                if (text in seen or seen in text) and abs(len(text) - len(seen)) < 10:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                filtered.append(heading)
                seen_texts.add(text)
        
        return filtered
    
    def _classify_heading_levels_improved(self, headings):
        """Improved heading level classification"""
        if not headings:
            return []
        
        # Get unique font sizes and sort them (largest first)
        font_sizes = sorted(set(h['size'] for h in headings), reverse=True)
        
        # Create size-to-level mapping (more conservative)
        level_map = {}
        for i, size in enumerate(font_sizes):
            if i == 0 and len(font_sizes) > 1:
                level_map[size] = 'H1'
            elif i == 1 or (i == 0 and len(font_sizes) == 1):
                level_map[size] = 'H1'  # If only one size, make it H1
            elif i == 2:
                level_map[size] = 'H2'
            else:
                level_map[size] = 'H3'
        
        # Classify each heading with pattern-based overrides
        classified = []
        for heading in headings:
            size = heading['size']
            level = level_map.get(size, 'H3')
            text = heading['text']
            
            # Strong pattern-based level assignment
            if re.match(r'^\d+\.?\s+', text):  # "1. Introduction"
                level = 'H1'
            elif re.match(r'^\d+\.\d+\.?\s+', text):  # "1.1 Overview"
                level = 'H2'
            elif re.match(r'^\d+\.\d+\.\d+\.?\s+', text):  # "1.1.1 Details"
                level = 'H3'
            elif re.match(r'^Round\s+\d+[A-Z]?:', text):  # "Round 1A:"
                level = 'H1'
            
            classified.append({
                'level': level,
                'text': heading['text'],
                'page': heading['page']
            })
        
        return classified