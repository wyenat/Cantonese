"""Main flashcard application window."""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QMessageBox

from .data_manager import DataManager
from .card_logic import CardLogic
from .ui_widgets import CardDisplay, ControlButtons


MAX_CARDS = 10


class FlashcardApp(QWidget):
    """Main flashcard application."""

    def __init__(self, csv_file: str):
        """
        Initialize FlashcardApp.
        
        Args:
            csv_file: Path to the CSV file
        """
        super().__init__()
        self.csv_file = csv_file
        self.data_manager = DataManager(csv_file)
        self.card_logic = None
        self.card_count = 0
        self.current_mode = None

        # Load data
        if not self.data_manager.load_csv():
            QMessageBox.critical(self, "Error", "Failed to load CSV file")
            return

        if self.data_manager.get_word_count() == 0:
            QMessageBox.warning(self, "No Data", "No words found in CSV file")
            return

        self.card_logic = CardLogic(self.data_manager.get_words())
        self.init_ui()

    def init_ui(self):
        """Initialize UI."""
        self.setWindowTitle("Cantonese Flashcard - Enter to Check")
        self.resize(750, 520)

        # Create widgets
        self.card_display = CardDisplay(on_check_callback=self.check)
        self.buttons = ControlButtons(
            on_check_callback=self.check,
            on_next_callback=self.new_card
        )

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.card_display, 1)
        layout.addWidget(self.buttons)
        self.setLayout(layout)

        # Start first card
        self.new_card()

    def new_card(self):
        """Load a new flashcard."""
        if self.card_count >= MAX_CARDS:
            self.ask_continue()
            return

        card_info = self.card_logic.get_random_card()
        if not card_info:
            QMessageBox.critical(self, "Error", "Failed to get card")
            return

        self.current_mode = card_info['mode']
        self.card_display.set_quiz_mode(self.current_mode, card_info['card'])

        self.card_count += 1
        self.update_title()

    def update_title(self):
        """Update window title with card count."""
        self.setWindowTitle(f"Cantonese Flashcard - Card {self.card_count}/{MAX_CARDS}")

    def check(self):
        """Check user's answer."""
        if not self.card_logic.current:
            return

        user_inputs = self.card_display.get_inputs()
        is_correct, message = self.card_logic.check_answer(self.current_mode, user_inputs)

        self.data_manager.save_csv()

        if is_correct:
            QMessageBox.information(self, "Correct!", message)
        else:
            QMessageBox.warning(self, "Try Again", message)

        # Go to next card
        if self.card_count < MAX_CARDS:
            self.new_card()
        else:
            self.ask_continue()

    def ask_continue(self):
        """Ask user if they want to continue with another 10 cards."""
        reply = QMessageBox.question(
            self, "Session Complete",
            f"You've done {MAX_CARDS} cards!\n\nContinue with another {MAX_CARDS}?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes
        )
        if reply == QMessageBox.Yes:
            self.card_count = 0
            self.update_title()
            self.new_card()
        else:
            self.close()
