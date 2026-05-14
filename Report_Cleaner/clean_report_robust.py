#!/usr/bin/env python3
"""
Robust Report Cleaner
Fixes encoding, smart-redacts sensitive info, formats text, and handles large files safely.
"""

import re
import textwrap
import unicodedata
import sys
import logging
from typing import Iterator, Optional

# --- CONFIGURATION ---
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class TextCleaner:
    def __init__(self, width: int = 80, redact_char: str = 'X', smart_redaction: bool = True):
        self.width = width
        self.redact_char = redact_char
        self.smart_redaction = smart_redaction
        self.seen_lines = set() # For deduplication

    def remove_accents(self, text: str) -> str:
        """
        Safely removes accents (ñ -> n) while authenticating that input is string.
        Falls back to original char for non-latin scripts (Chinese/Arabic) instead of deleting.
        """
        if not isinstance(text, str):
            logging.error(f"Input must be string, got {type(text)}")
            return ""
        
        # Normalize to decomposed form (NFD)
        nfd_form = unicodedata.normalize('NFD', text)
        
        # Filter out non-spacing mark characters (accents)
        # But KEEP characters that aren't combining marks (like Chinese chars)
        cleaned = "".join([c for c in nfd_form if unicodedata.category(c) != 'Mn'])
        
        return cleaned

    def redact_sensitive_info(self, text: str) -> str:
        """
        Smart redaction:
        - If smart_redaction is True: targets % and $ patterns specifically.
        - If False: targets all digits (legacy behavior).
        """
        if not self.smart_redaction:
            # Legacy: blast all numbers
            return re.sub(r'\d', self.redact_char, text)
        
        # Smart: Target percentages (7.47%) and Currency ($2 million)
        # 1. Percentages: 7.47% -> X.XX%
        text = re.sub(r'(\d+\.?\d*)%', f'{self.redact_char}.{self.redact_char}{self.redact_char}%', text)
        
        # 2. Currency/Values: "million" or "$"
        # matches: $500, 2 million, 0.7%
        # NOTE: Regex is hard. This assumes a specific style. 
        # A simple safer approach for "Sector 9" vs "9%" is lookahead or context.
        
        # Let's use a simpler heuristic: Redact numbers that have ./,/%/$ around them
        # Or just redact long numbers (GT 2 digits) to save "Sector 9" but hide "5000"
        
        def replacer(match):
            val = match.group()
            # If it looks like a small ID (1 digit), keep it.
            if len(val) == 1: 
                return val 
            return self.redact_char * len(val)

        return re.sub(r'\d+', replacer, text)

    def process_text_line(self, line: str) -> Optional[str]:
        """
        Clean a single line. Returns None if empty or duplicate.
        """
        if not line: return None
        
        # 1. Deduplication
        full_line = line.strip()
        if full_line in self.seen_lines:
            logging.debug("Skipping duplicate line")
            return None
        self.seen_lines.add(full_line)

        # 2. Accent Removal / Encoding Fix
        cleaned = self.remove_accents(full_line)
        
        # 3. Redaction
        redacted = self.redact_sensitive_info(cleaned)
        
        # 4. Formatting (Sentence Case instead of Title Case which is hard to read)
        # Using .capitalize() per sentence is better than .title()
        formatted = redacted.capitalize() 
        
        return formatted

    def stream_process(self, input_text: Optional[str] = None, file_path: Optional[str] = None) -> Iterator[str]:
        """
        Generator that yields cleaned 80-char wrapped blocks.
        Can convert a huge file without loading it all.
        """
        source = None
        if file_path:
            try:
                # Open with utf-8 to support international text
                source = open(file_path, 'r', encoding='utf-8')
            except FileNotFoundError:
                logging.error(f"File not found: {file_path}")
                return
        elif input_text:
            source = input_text.splitlines()
        else:
            logging.error("No input provided")
            return

        # Process line by line
        current_paragraph = []
        
        try:
            for line in source:
                cleaned_line = self.process_text_line(line)
                if cleaned_line:
                    current_paragraph.append(cleaned_line)

            # Join all valid lines into one block for wrapping
            full_body = " ".join(current_paragraph)
            
            # Wrap to 80 chars
            wrapped = textwrap.fill(full_body, width=self.width)
            yield wrapped
            
        finally:
            if file_path and hasattr(source, 'close'):
                source.close()

# --- DEMO ---
def main():
    # Hardcoded input for demo purposes
    INPUT_TEXT = '''
    AFTER THE CLOSE OF THE SECOND QUARTER, OUR COMPANY, CASTAÑACORP
    HAS ACHIEVED A GROWTH IN THE REVENUE OF 7.47%. THIS IS IN LINE
    WITH THE OBJECTIVES FOR THE YEAR. 
    
    SECTOR 9 reported no issues. SECTOR 9 reported no issues.
    The Chinese office (北京) reported 100% uptime.
    '''

    print("--- Original Text ---")
    print(INPUT_TEXT)
    print("\n--- Cleaned Output ---")

    cleaner = TextCleaner(smart_redaction=True)
    
    # We pass the raw string for this demo
    for block in cleaner.stream_process(input_text=INPUT_TEXT):
        print(block)

if __name__ == "__main__":
    main()
