"""
Enterprise Financial Report Generator
Advanced version handling:
- Streaming large files (Low Memory)
- Encoding detection
- Duplicate removal
- Formal logging
- Dataclasses & Separation of concerns
"""

import sys
import json
import csv
import argparse
import logging
from typing import Iterator, Optional, Set
from dataclasses import dataclass

# --- CONFIGURATION & LOGGING ---
logging.basicConfig(
    filename='report_errors.log',
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
console_handler = logging.StreamHandler(sys.stderr)
console_handler.setFormatter(logging.Formatter('⚠️  %(message)s'))
logging.getLogger().addHandler(console_handler)

# --- DATA STRUCTURES ---
@dataclass(frozen=True)  # frozen=True makes it hashable for deduping
class FinancialRecord:
    revenue: float
    profit: float

    @property
    def margin(self) -> Optional[float]:
        """Calculates margin safely. Returns None if invalid."""
        if self.revenue == 0:
            return None
        return self.profit / self.revenue

# --- CORE LOGIC ---
def detect_encoding(filepath: str) -> str:
    """Simple heuristic to detect encoding (UTF-8 vs Latin-1)."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            f.read(1024)
        return 'utf-8'
    except UnicodeDecodeError:
        logging.info(f"UTF-8 failed for {filepath}, trying latin-1 (windows default)")
        return 'latin-1'

def validate_record(raw_revenue: any, raw_profit: any) -> Optional[FinancialRecord]:
    """Validates raw data and returns a safe FinancialRecord object."""
    try:
        rev = float(raw_revenue)
        prof = float(raw_profit)
        return FinancialRecord(revenue=rev, profit=prof)
    except (ValueError, TypeError):
        logging.warning(f"Skipping invalid data row: rev='{raw_revenue}', prof='{raw_profit}'")
        return None

def stream_csv(filepath: str) -> Iterator[FinancialRecord]:
    """Yields records one by one to save memory (Generator Pattern)."""
    encoding = detect_encoding(filepath)
    try:
        with open(filepath, 'r', encoding=encoding) as f:
            reader = csv.reader(f)
            header = next(reader, None) # Skip header
            
            for line_num, row in enumerate(reader, start=2):
                if len(row) < 2:
                    logging.warning(f"Line {line_num}: Insufficient columns")
                    continue
                
                record = validate_record(row[0], row[1])
                if record:
                    yield record
    except Exception as e:
        logging.error(f"Failed to read CSV {filepath}: {e}")
        sys.exit(1)

def stream_json(filepath: str, key_rev='revenue', key_prof='profit') -> Iterator[FinancialRecord]:
    """Yields records from JSON. Note: JSON parsing often requires full load."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            # For massive JSON files, we would use 'ijson' library. 
            # Using standard json load here for simplicity as standard implementation.
            data = json.load(f)
            
        items = data if isinstance(data, list) else []
        if not items:
            logging.warning("JSON file contained no list data.")

        # Check for Format Drift (Schema Validation)
        if items and isinstance(items[0], dict):
            if key_rev not in items[0] or key_prof not in items[0]:
                 logging.critical(f"Format Drift Detected! Keys '{key_rev}'/'{key_prof}' missing. Found: {list(items[0].keys())}")
                 # We don't exit here, we let the validation log errors for individual rows

        for index, item in enumerate(items):
            if isinstance(item, dict):
                record = validate_record(item.get(key_rev), item.get(key_prof))
            elif isinstance(item, list) and len(item) >= 2:
                record = validate_record(item[0], item[1])
            else:
                continue

            if record:
                yield record

    except json.JSONDecodeError:
        logging.error(f"Invalid JSON file: {filepath}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Unexpected error reading JSON: {e}")
        sys.exit(1)

def pipeline_dedupe(iterator: Iterator[FinancialRecord]) -> Iterator[FinancialRecord]:
    """Filter that remembers seen records and blocks duplicates."""
    seen: Set[FinancialRecord] = set()
    duplicates_count = 0
    
    for record in iterator:
        if record in seen:
            duplicates_count += 1
            continue
        seen.add(record)
        yield record
    
    if duplicates_count > 0:
        logging.info(f"Removed {duplicates_count} duplicate records.")

# --- PRESENTATION LAYER ---
def format_table(records: Iterator[FinancialRecord]):
    """Consumes the stream and prints the report."""
    
    header = f"{'REVENUE':>10} | {'PROFIT':>10} | {'MARGIN':>8}"
    print(header)
    print("-" * len(header))

    count = 0
    total_revenue = 0.0

    for rec in records:
        count += 1
        total_revenue += rec.revenue
        
        margin_str = f"{rec.margin:>8.2%}" if rec.margin is not None else f"{'N/A':>8}"
        
        # Color coding for negative profit (ANSI escape codes)
        profit_str = f"{rec.profit:+10,.2f}"
        if rec.profit < 0:
            profit_str = f"\033[91m{profit_str}\033[0m" # Red text

        print(f"{rec.revenue:>10,.2f} | {profit_str} | {margin_str}")

    print("-" * len(header))
    print(f"Total Rows: {count} | Total Rev: ${total_revenue:,.2f}")

# --- MAIN ---
def main():
    parser = argparse.ArgumentParser(description="Enterprise Financial Reporter")
    parser.add_argument('file', help="Input file (CSV/JSON)")
    parser.add_argument('--rev-key', default='revenue', help="JSON key for revenue (handles format drift)")
    parser.add_argument('--prof-key', default='profit', help="JSON key for profit")
    
    args = parser.parse_args()

    # 1. Select Source Stream
    if args.file.endswith('.csv'):
        stream = stream_csv(args.file)
    elif args.file.endswith('.json'):
        stream = stream_json(args.file, args.rev_key, args.prof_key)
    else:
        logging.error("Unsupported file extension. Use .csv or .json")
        sys.exit(1)

    # 2. Apply Filters (Pipeline Pattern)
    unique_stream = pipeline_dedupe(stream)

    # 3. Output
    print(f"Generating report for: {args.file}...\n")
    format_table(unique_stream)

if __name__ == "__main__":
    main()
