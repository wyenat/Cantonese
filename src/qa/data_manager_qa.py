"""Data manager for QA-style CSV (question -> answer)."""

import csv
import os
from typing import List, Dict, Any


class DataManagerQA:
    """Loads QA CSV with six possible fields per row.

    The CSV may have slightly different header names. This loader attempts
    to map fields containing keywords to the canonical keys:
    ChineseQ, JyutpingQ, EnglishQ, ChineseA, JyutpingA, EnglishA
    """

    CANONICAL_KEYS = [
        'ChineseQ', 'JyutpingQ', 'EnglishQ',
        'ChineseA', 'JyutpingA', 'EnglishA'
    ]

    def __init__(self, csv_file: str):
        self.csv_file = csv_file
        self.cards: List[Dict[str, Any]] = []

    def _find_field(self, fieldnames, keyword):
        """Find a field name in fieldnames that contains the keyword (case-insensitive).
        Returns None if not found.
        """
        if not fieldnames:
            return None
        key_l = keyword.lower()
        for f in fieldnames:
            if f and key_l in f.lower():
                return f
        return None

    def load_csv(self) -> bool:
        if not os.path.exists(self.csv_file):
            print(f"CSV file {self.csv_file} not found")
            return False

        try:
            with open(self.csv_file, encoding='utf-8') as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames or []

                # Map canonical keys to actual CSV columns (if present)
                mapping = {}
                for k in self.CANONICAL_KEYS:
                    found = self._find_field(fieldnames, k)
                    mapping[k] = found
                # Determine field order based on CSV header order where possible
                field_order = []
                for f in fieldnames:
                    # try to map this header to a canonical key
                    for k in self.CANONICAL_KEYS:
                        if mapping.get(k) and mapping[k] == f and k not in field_order:
                            field_order.append(k)
                # append any missing canonical keys at the end in default order
                for k in self.CANONICAL_KEYS:
                    if k not in field_order:
                        field_order.append(k)
                self.field_order = field_order

                for row in reader:
                    # Build card with canonical keys
                    card = {'_row': row}
                    for k in self.CANONICAL_KEYS:
                        col = mapping.get(k)
                        card[k] = (row.get(col) or '').strip() if col else ''

                    # Counters
                    try:
                        questioned_val = int(row.get('Questioned') or 0)
                    except Exception:
                        questioned_val = 0
                    try:
                        correct_val = int(row.get('Correct') or 0)
                    except Exception:
                        correct_val = 0

                    card['questioned'] = questioned_val
                    card['correct'] = correct_val

                    # Skip rows without any question content
                    if not any(card[k] for k in ['ChineseQ', 'JyutpingQ', 'EnglishQ']):
                        continue

                    self.cards.append(card)
            return True
        except Exception as e:
            print(f"Error loading QA CSV: {e}")
            return False

    def save_csv(self):
        try:
            with open(self.csv_file, encoding='utf-8') as f:
                reader = csv.DictReader(f)
                headers = reader.fieldnames or []

            with open(self.csv_file, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=headers, extrasaction='ignore', restval='')
                writer.writeheader()
                for c in self.cards:
                    row = c.get('_row', {}) or {}
                    row['Questioned'] = str(c.get('questioned', 0))
                    row['Correct'] = str(c.get('correct', 0))
                    writer.writerow(row)
        except Exception as e:
            print(f"Error saving QA CSV: {e}")

    def get_cards(self) -> List[Dict[str, Any]]:
        return self.cards

    def get_count(self) -> int:
        return len(self.cards)
