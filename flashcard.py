#!/usr/bin/env python3
"""
Cantonese Flashcard Application
Main entry point
"""

import sys
import os
from PyQt5.QtWidgets import QApplication

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.flashcard_app import FlashcardApp


def main():
    """Main entry point."""
    csv_file = 'cantonese.csv' if len(sys.argv) < 2 else sys.argv[1]
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = FlashcardApp(csv_file)
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
