"""Data manager for loading and saving flashcard data."""

import csv
import os
from typing import List, Dict, Any


REQUIRED_HEADERS = ['Word', 'Jyutping', 'English', 'Questioned', 'Correct', 'Type']


class DataManager:
    """Handles loading and saving CSV flashcard data."""

    def __init__(self, csv_file: str):
        """
        Initialize DataManager with CSV file path.
        
        Args:
            csv_file: Path to the CSV file
        """
        self.csv_file = csv_file
        self.words: List[Dict[str, Any]] = []

    def create_default_csv(self):
        """Create a default CSV file if it doesn't exist."""
        with open(self.csv_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(REQUIRED_HEADERS)
        print(f"Created {self.csv_file}.")

    def load_csv(self) -> bool:
        """
        Load CSV file and populate words list.
        
        Returns:
            True if successful, False otherwise
        """
        if not os.path.exists(self.csv_file):
            self.create_default_csv()
            return True

        try:
            with open(self.csv_file, encoding='utf-8') as f:
                reader = csv.DictReader(f)
                if reader.fieldnames != REQUIRED_HEADERS:
                    print(f"Warning: CSV headers should be: {', '.join(REQUIRED_HEADERS)}")
                
                for row_idx, row in enumerate(reader):
                    # Skip empty rows
                    word = row['Word'].strip() if row['Word'] else ''
                    if not word:
                        continue
                    
                    # Safely convert to integers, defaulting to 0 for empty/invalid values
                    try:
                        questioned_val = int(row['Questioned'].strip()) if row['Questioned'] and row['Questioned'].strip().isdigit() else 0
                    except (ValueError, AttributeError):
                        questioned_val = 0
                    
                    try:
                        correct_val = int(row['Correct'].strip()) if row['Correct'] and row['Correct'].strip().isdigit() else 0
                    except (ValueError, AttributeError):
                        correct_val = 0
                    
                    self.words.append({
                        'char': word,
                        'jyut': row['Jyutping'].strip() if row['Jyutping'] else '',
                        'eng': row['English'].strip().lower() if row['English'] else '',
                        'q': questioned_val,
                        'c': correct_val,
                        'type': (row.get('Type') or '').strip(),
                        '_row': row
                    })
            return True
        except Exception as e:
            print(f"Error loading CSV: {e}")
            import traceback
            traceback.print_exc()
            return False

    def save_csv(self):
        """Save current words list to CSV file."""
        try:
            with open(self.csv_file, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=REQUIRED_HEADERS, extrasaction='ignore', restval='')
                writer.writeheader()
                for w in self.words:
                    # Create a clean row with only required fields
                    row = {}
                    for field in REQUIRED_HEADERS:
                        # Get value from _row, handling None keys and missing fields
                        value = w['_row'].get(field, '') if w['_row'] else ''
                        row[field] = value if value is not None else ''
                    
                    # Update with current values from word dict
                    row['Word'] = w['char']
                    row['Jyutping'] = w['jyut']
                    row['English'] = w['eng'].upper()  # Store in original case
                    row['Questioned'] = str(w['q'])
                    row['Correct'] = str(w['c'])
                    row['Type'] = w['type']
                    
                    writer.writerow(row)
        except Exception as e:
            print(f"Error saving CSV: {e}")
            import traceback
            traceback.print_exc()

    def get_words(self) -> List[Dict[str, Any]]:
        """Get all loaded words."""
        return self.words

    def get_word_count(self) -> int:
        """Get total number of words."""
        return len(self.words)

    def get_word_by_index(self, index: int) -> Dict[str, Any]:
        """Get a word by index."""
        if 0 <= index < len(self.words):
            return self.words[index]
        return None

    def get_full_answer(self, word: Dict[str, Any], mode: str) -> str:
        """
        Get the full expected answer for a word in a given mode.
        
        Args:
            word: Word dictionary
            mode: Quiz mode ('char', 'jyut', or 'eng')
        
        Returns:
            Full expected answer string
        """
        if mode == 'char':
            return word['char']
        elif mode == 'jyut':
            return word['jyut']
        elif mode == 'eng':
            # Return English with all alternatives
            return word['eng'].upper()  # Display in original case
        return ""

    def get_types(self) -> List[str]:
        """
        Get all unique types from loaded words.
        
        Returns:
            Sorted list of unique types (excluding empty strings)
        """
        types_set = set()
        for word in self.words:
            word_type = word.get('type', '').strip()
            if word_type:  # Only include non-empty types
                types_set.add(word_type)
        return sorted(list(types_set))

    def filter_words_by_types(self, selected_types: List[str]) -> List[Dict[str, Any]]:
        """
        Filter words based on selected types.
        
        Args:
            selected_types: List of selected type strings
        
        Returns:
            Filtered list of words
        """
        if not selected_types:
            return []
        
        filtered = []
        for word in self.words:
            word_type = word.get('type', '').strip()
            if word_type in selected_types:
                filtered.append(word)
        return filtered
