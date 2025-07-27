# src/round1a/heading_extractor.py
"""
Heading extraction and classification
"""

import re
import sys
import os
import time
from collections import Counter
from statistics import mean, median

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
        start_time = time.time()
        log("Starting heading extraction...")
        
        # Flatten all text spans
        all_spans = [span for page_data in all_pages_data for span in page_data]
        
        # Filter out empty or very short text, and merge fragments
        text_spans = self._preprocess_spans(all_spans)
        
        log(f"Analyzing {len(text_spans)} processed text spans for headings")
        
        # Extract title
        title = self._extract_title_improved(text_spans)
        
        # Detect headings with optimized criteria
        headings = self._detect_headings_strict(text_spans)
        
        # Classify heading levels
        classified_headings = self._classify_heading_levels_improved(headings)
        
        elapsed_time = time.time() - start_time
        log(f"Found {len(classified_headings)} headings in {elapsed_time:.2f} seconds")
        
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
        """Extract document title from text spans"""
        if not text_spans:
            return "Untitled Document"
        
        # Get spans from first page only (titles are almost always on first page)
        first_page_spans = [span for span in text_spans if span['page'] == 1]
        
        if not first_page_spans:
            # Fall back to first two pages if first page has no text
            first_page_spans = [span for span in text_spans if span['page'] <= 2]
            
        if not first_page_spans:
            return "Untitled Document"
        
        # Find the largest font size in first page
        font_sizes = [span['size'] for span in first_page_spans]
        max_size = max(font_sizes)
        
        # Get spans with largest font size and those close to it (within 2 points)
        title_spans = [
            span for span in first_page_spans 
            if span['size'] >= max_size - 2 and len(span['text'].strip()) > 3
        ]
        
        # Also consider bold text in top quarter of first page
        page_height = max(span['bbox'][3] for span in first_page_spans) if first_page_spans else 800
        top_quarter = page_height * 0.25
        
        bold_top_spans = [
            span for span in first_page_spans 
            if span['flags'] & 16 and span['bbox'][1] <= top_quarter and len(span['text'].strip()) > 5
        ]
        
        # Combine both sets of potential title spans and remove duplicates
        combined_spans = title_spans + bold_top_spans
        # Remove duplicates by comparing text content
        seen_texts = set()
        title_spans = []
        for span in combined_spans:
            if span['text'] not in seen_texts:
                seen_texts.add(span['text'])
                title_spans.append(span)
        
        if not title_spans:
            return "Untitled Document"
        
        # Try to merge fragments that might be parts of the same title
        title_candidates = []
        current_candidate = ""
        
        # Sort by y-coordinate (top to bottom)
        title_spans.sort(key=lambda s: -s['bbox'][1])
        
        # Group spans that are close together vertically
        y_threshold = 5  # Maximum vertical distance to consider spans part of same line
        prev_y = None
        
        for span in title_spans:
            text = span['text'].strip()
            current_y = span['bbox'][1]
            
            # Check if this span is on same line or a continuation
            if prev_y is not None and abs(current_y - prev_y) <= y_threshold:
                # Same line or very close - append to current candidate
                current_candidate += " " + text
            elif (current_candidate and 
                  (text[0].islower() or len(text) < 10) and 
                  len(current_candidate + " " + text) < 150):
                # Looks like a continuation
                current_candidate += " " + text
            else:
                # New title candidate
                if current_candidate:
                    title_candidates.append(current_candidate)
                current_candidate = text
            
            prev_y = current_y
        
        if current_candidate:
            title_candidates.append(current_candidate)
        
        # Filter candidates
        valid_candidates = []
        for candidate in title_candidates:
            candidate = clean_text(candidate)
            # Must be reasonable length and not just fragments
            if 10 <= len(candidate) <= 200 and not candidate.lower().startswith(('welcome', 'contents', 'table of')):
                valid_candidates.append(candidate)
        
        if valid_candidates:
            # Prioritize candidates from top of page
            top_candidates = sorted(valid_candidates, key=len, reverse=True)[:3]
            
            # Take the longest reasonable candidate
            title = max(top_candidates, key=len) if len(top_candidates) > 0 else valid_candidates[0]
            log(f"Extracted title: '{title}'")
            return title
        
        return "Untitled Document"
    
    def _detect_headings_strict(self, text_spans):
        """Detect headings with optimized criteria for better performance and accuracy"""
        potential_headings = []
        
        # Get font size statistics more efficiently
        font_sizes = [span['size'] for span in text_spans]
        avg_font_size = mean(font_sizes) if font_sizes else 12  # Default if empty
        median_font_size = median(font_sizes) if font_sizes else 12  # More robust to outliers
        
        # Calculate thresholds based on statistics
        size_threshold = max(avg_font_size + 1.5, median_font_size * 1.2)  # Adaptive threshold
        
        # Precompile regex patterns for better performance
        strong_patterns_compiled = [re.compile(pattern, re.IGNORECASE) for pattern in self.strong_patterns]
        weak_patterns_compiled = [re.compile(pattern, re.IGNORECASE) for pattern in self.weak_patterns]
        
        # Create a set of strong keywords for faster lookup
        strong_keywords_set = set(self.strong_keywords)
        blacklist_words_set = set(self.blacklist_words)
        
        # Process each span
        for span in text_spans:
            text = span['text'].strip()
            
            # Skip very short or very long text
            if len(text) < 5 or len(text) > 150:
                continue
                
            # Skip if text is mostly blacklisted words (optimized)
            text_words = text.lower().split()
            if not text_words:
                continue
                
            blacklist_count = sum(1 for word in text_words if word in blacklist_words_set)
            if blacklist_count > len(text_words) * 0.5:  # Slightly more lenient
                continue
            
            heading_score = 0
            text_lower = text.lower()
            
            # Strong patterns get high scores (using precompiled patterns)
            for pattern in strong_patterns_compiled:
                if pattern.match(text):
                    heading_score += 5
                    break
            
            # Weak patterns need additional signals (using precompiled patterns)
            for pattern in weak_patterns_compiled:
                if pattern.search(text):
                    heading_score += 2
                    break
            
            # Font size scoring (adaptive)
            if span['size'] > size_threshold + 1:
                heading_score += 3
            elif span['size'] > size_threshold:
                heading_score += 2
            elif span['size'] > avg_font_size:
                heading_score += 1
            
            # Bold text
            if span['flags'] & 16:  # Bold flag
                heading_score += 2
            
            # Strong keyword matching (optimized with set)
            if any(keyword in text_lower for keyword in strong_keywords_set):
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
            
            # Threshold for confident headings
            if heading_score >= 4:
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
        """Classify headings into H1, H2, H3 levels with improved pattern recognition and clustering"""
        if not headings:
            return []
        
        # Precompile regex patterns for better performance
        numbered_heading_pattern = re.compile(r'^\d+\.?\s+\w+')
        chapter_pattern = re.compile(r'^Chapter\s+\d+', re.IGNORECASE)
        round_pattern = re.compile(r'^Round\s+\d+[A-Z]?:')
        section_pattern = re.compile(r'^Section\s+\d+', re.IGNORECASE)
        appendix_pattern = re.compile(r'^Appendix\s+[A-Z]', re.IGNORECASE)
        roman_pattern = re.compile(r'^[IVX]+\.\s+\w+')
        decimal_pattern = re.compile(r'^\d+\.\d+\.?\s+')
        sub_decimal_pattern = re.compile(r'^\d+\.\d+\.\d+\.?\s+')
        
        # Sort headings by font size (largest to smallest)
        headings_by_size = sorted(headings, key=lambda h: h['size'], reverse=True)
        
        # Get unique font sizes and their frequencies
        sizes = [h['size'] for h in headings]
        size_counts = {}
        for size in sizes:
            size_counts[size] = size_counts.get(size, 0) + 1
        
        # Find clusters of font sizes using a more sophisticated approach
        unique_sizes = sorted(set(sizes), reverse=True)
        
        # If we have very few headings, use a simpler approach
        if len(headings) <= 5:
            size_to_level = {}
            if len(unique_sizes) >= 3:
                size_to_level[unique_sizes[0]] = "H1"
                size_to_level[unique_sizes[1]] = "H2"
                size_to_level[unique_sizes[2]] = "H3"
                for size in unique_sizes[3:]:
                    size_to_level[size] = "H3"
            elif len(unique_sizes) == 2:
                size_to_level[unique_sizes[0]] = "H1"
                size_to_level[unique_sizes[1]] = "H2"
            elif len(unique_sizes) == 1:
                size_to_level[unique_sizes[0]] = "H1"
        else:
            # Use clustering to identify natural groups of font sizes
            # First, check if there are clear divisions between sizes
            size_to_level = {}
            
            # If we have many unique sizes, try to cluster them
            if len(unique_sizes) > 3:
                # Calculate size differences
                diffs = [unique_sizes[i] - unique_sizes[i+1] for i in range(len(unique_sizes)-1)]
                
                # Find significant gaps (larger than average difference)
                avg_diff = sum(diffs) / len(diffs) if diffs else 0
                significant_gaps = [i for i, diff in enumerate(diffs) if diff > avg_diff * 1.5]
                
                # Use gaps to define clusters
                if significant_gaps:
                    # H1 is everything above first significant gap
                    h1_threshold = unique_sizes[significant_gaps[0] + 1]
                    
                    # If we have a second significant gap, use it for H2/H3 boundary
                    if len(significant_gaps) > 1:
                        h2_threshold = unique_sizes[significant_gaps[1] + 1]
                    else:
                        # Otherwise split remaining sizes evenly
                        remaining = unique_sizes[significant_gaps[0]+1:]
                        mid = len(remaining) // 2
                        h2_threshold = remaining[mid] if mid < len(remaining) else unique_sizes[-1]
                    
                    # Assign levels based on thresholds
                    for size in unique_sizes:
                        if size > h1_threshold:
                            size_to_level[size] = "H1"
                        elif size > h2_threshold:
                            size_to_level[size] = "H2"
                        else:
                            size_to_level[size] = "H3"
                else:
                    # No significant gaps, fall back to simple division
                    third = len(unique_sizes) // 3
                    for i, size in enumerate(unique_sizes):
                        if i < third:
                            size_to_level[size] = "H1"
                        elif i < third * 2:
                            size_to_level[size] = "H2"
                        else:
                            size_to_level[size] = "H3"
            else:
                # Simple case with 3 or fewer unique sizes
                if len(unique_sizes) == 3:
                    size_to_level[unique_sizes[0]] = "H1"
                    size_to_level[unique_sizes[1]] = "H2"
                    size_to_level[unique_sizes[2]] = "H3"
                elif len(unique_sizes) == 2:
                    size_to_level[unique_sizes[0]] = "H1"
                    size_to_level[unique_sizes[1]] = "H2"
                elif len(unique_sizes) == 1:
                    size_to_level[unique_sizes[0]] = "H1"
        
        # Check for pattern-based structure in the document
        has_chapters = any(chapter_pattern.match(h['text']) for h in headings)
        has_sections = any(section_pattern.match(h['text']) for h in headings)
        has_numbered = any(numbered_heading_pattern.match(h['text']) for h in headings)
        
        # Apply pattern-based overrides
        classified = []
        for heading in headings:
            size = heading['size']
            level = size_to_level.get(size, "H3")
            text = heading['text']
            is_bold = heading.get('flags', 0) & 16 > 0
            
            # Pattern-based overrides
            if numbered_heading_pattern.match(text):
                # Check if it's a top-level numbered heading (1. Introduction)
                if text.startswith("1.") and (level == "H2" or is_bold):
                    level = "H1"
                elif level == "H3" and not has_chapters:  # Don't demote H1 or H2
                    level = "H2"
            
            # Chapter headings are almost always H1
            elif chapter_pattern.match(text):
                level = "H1"
            
            # Round X: style headings are typically H1
            elif round_pattern.match(text):
                level = "H1"
            
            # Section headings are typically H2 unless they're the main structure
            elif section_pattern.match(text):
                if text.startswith("Section 1") and not has_chapters:
                    level = "H1"
                else:
                    level = "H2"
            
            # Appendices are typically H2 unless they're the main structure
            elif appendix_pattern.match(text):
                if not (has_chapters or has_sections):
                    level = "H1"
                else:
                    level = "H2"
            
            # Roman numeral headings
            elif roman_pattern.match(text):
                if text.startswith("I.") and level != "H1" and not has_numbered:
                    level = "H2"
            
            # Decimal notation (1.1, 1.2, etc.)
            elif decimal_pattern.match(text):
                level = "H2"
            
            # Sub-decimal notation (1.1.1, 1.1.2, etc.)
            elif sub_decimal_pattern.match(text):
                level = "H3"
            
            # Contents or Table of Contents
            elif text.lower() in ["contents", "table of contents", "index"]:
                level = "H1"
            
            # If this is the only heading with this font size and it's large, it's likely H1
            elif size_counts.get(size, 0) == 1 and size == unique_sizes[0]:
                level = "H1"
            
            classified.append({
                'level': level,
                'text': text,
                'page': heading['page']
            })
        
        # Post-processing: ensure logical hierarchy
        # If we have no H1 headings but have H2, promote the first H2 to H1
        h1_count = sum(1 for h in classified if h['level'] == 'H1')
        if h1_count == 0 and any(h['level'] == 'H2' for h in classified):
            # Find the first H2 heading
            for heading in classified:
                if heading['level'] == 'H2':
                    heading['level'] = 'H1'
                    break
        
        return classified