#!/usr/bin/env python3
"""Generate TTS WAV files for Chinese strings found in CSV resources.

This script scans the `resources/` directory for CSV files, extracts Chinese
character sequences from CSV cells, and calls the external `ekho` command to
produce a WAV file for each unique Chinese string per package (subfolder).

Usage:
    python scripts/generate_tts.py

Requirements:
    - `ekho` must be installed and available on PATH.
"""

import csv
import os
import re
import subprocess
from pathlib import Path
from typing import Dict, Set


RESOURCE_DIR = Path('resources')
CSV_EXT = '.csv'

# Match CJK Unified Ideographs (basic range). This will capture most Chinese chars.
# Match CJK Unified Ideographs (covers the common Chinese character ranges)
CHINESE_RE = re.compile(r'[\u4E00-\u9FFF\u3400-\u4DBF\uF900-\uFAFF]+')


def find_csv_files(root: Path):
    for p in root.rglob(f'*{CSV_EXT}'):
        yield p


def extract_chinese(text: str) -> Set[str]:
    """Return set of Chinese substrings found in text."""
    if not text:
        return set()
    matches = CHINESE_RE.findall(text)
    # Return unique matches
    return set(matches)


def make_audio(package: str, text: str, out_dir: Path):
    """Call ekho to generate an audio file for the given text.

    Output filename is the text with unsafe characters replaced by underscores.
    """
    safe_name = ''.join(ch if ch.isalnum() else '_' for ch in text)
    filename = f"{safe_name}.wav"
    out_path = out_dir / filename
    if out_path.exists():
        print(f"Skipping existing: {out_path}")
        return

    cmd = ['ekho', '-v', 'Cantonese', '-o', str(out_path), text]
    print('Running:', ' '.join(cmd))
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print('ekho failed for', text, '->', e)


def main():
    if not RESOURCE_DIR.exists():
        print('No resources/ directory found')
        return

    # Map package (resources/<package>) -> set of chinese strings
    package_map: Dict[str, Set[str]] = {}

    for csv_path in find_csv_files(RESOURCE_DIR):
        # Determine package name: resources/<package>/... or resources/<file>.csv -> package is ''
        rel = csv_path.relative_to(RESOURCE_DIR)
        parts = rel.parts
        if len(parts) >= 2:
            package = parts[0]
        else:
            package = ''

        package_map.setdefault(package, set())

        try:
            with csv_path.open(encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    for val in row.values():
                        # Extract chinese substrings
                        found = extract_chinese(val)
                        package_map[package].update(found)
        except Exception as e:
            print('Failed reading', csv_path, e)

    # Consolidate all unique texts across packages and generate into resources/audio/
    all_texts = set()
    for texts in package_map.values():
        all_texts.update(texts)

    out_dir = RESOURCE_DIR / 'audio'
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f'Total unique Chinese items: {len(all_texts)}')
    for text in sorted(all_texts):
        if not text.strip():
            continue
        # package argument unused for single audio directory; pass empty string
        make_audio('', text, out_dir)


if __name__ == '__main__':
    main()
