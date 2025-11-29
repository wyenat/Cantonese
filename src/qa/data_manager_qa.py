"""Data manager for QA-style CSV (question -> answer)."""

import csv
import os
from typing import List, Dict, Any


class DataManagerQA:
    """Loads simple QA CSV with question and answer columns."""

    def __init__(self, csv_file: str):
        self.csv_file = csv_file
        self.cards: List[Dict[str, Any]] = []

    def load_csv(self) -> bool:
        if not os.path.exists(self.csv_file):
            print(f"CSV file {self.csv_file} not found")
            return False

        try:
            with open(self.csv_file, encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    q = (row.get('ChineseQ') or '').strip()
                    jq = (row.get('JyutpingQ，EnglishQ') or '').strip()
                    a = (row.get('ChineseA') or '').strip()
                    ja = (row.get('JyutpingA，EnglishA') or '').strip()

                    try:
                        questioned_val = int(row.get('Questioned') or 0)
                    except Exception:
                        questioned_val = 0
                    try:
                        correct_val = int(row.get('Correct') or 0)
                    except Exception:
                        correct_val = 0

                    if not q and not jq:
                        continue

                    self.cards.append({
                        'q_text': q,
                        'q_jyut': jq,
                        'a_text': a,
                        'a_jyut': ja,
                        'questioned': questioned_val,
                        'correct': correct_val,
                        '_row': row,
                    })
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
