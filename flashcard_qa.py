#!/usr/bin/env python3
"""
QA style Cantonese flashcard app runner
"""
import sys
import os
from PyQt5.QtWidgets import QApplication

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.qa.flashcard_app_qa import FlashcardQAApp


def main():
    csv_file = 'resources/qa/cantonese-QA.csv' if len(sys.argv) < 2 else sys.argv[1]

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = FlashcardQAApp(csv_file)
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
