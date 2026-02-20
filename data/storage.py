"""
CSV storage and file operations for EduManage SIS.
"""

import csv
import os
from config import FILES, FIELDS


def init_files():
    """Initialize CSV files with headers if they don't exist."""
    for key, filename in FILES.items():
        if not os.path.exists(filename):
            with open(filename, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=FIELDS[key])
                writer.writeheader()


def load_csv(key):
    """Load data from CSV file."""
    if not os.path.exists(FILES[key]):
        init_files()
    with open(FILES[key], 'r', newline='') as f:
        return list(csv.DictReader(f))


def save_csv(key, data):
    """Save data to CSV file."""
    with open(FILES[key], 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS[key])
        writer.writeheader()
        try:
            writer.writerows(data)
        except Exception:
            # Fail-safe: write rows that are dict-like only
            safe_rows = []
            for r in data:
                if isinstance(r, dict):
                    safe_rows.append(r)
            writer.writerows(safe_rows)


def create_backups():
    """Create backup of all CSV files (placeholder for future implementation)."""
    pass
