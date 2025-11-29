"""Main flashcard application window (original app)."""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QMessageBox

from ..common.ui_widgets import CardDisplay, ControlButtons, TypeFilter
from ..common.data_manager import DataManager
from ..common.card_logic import CardLogic


MAX_CARDS = 10


class FlashcardApp(QWidget):
    """Main flashcard application."""

    def __init__(self, csv_file: str):
        super().__init__()
        self.csv_file = csv_file
        self.data_manager = DataManager(csv_file)
        self.card_logic = None
        self.card_count = 0
        self.current_mode = None
        self.filtered_words = []
        self.selected_types = []

        if not self.data_manager.load_csv():
            QMessageBox.critical(self, "Error", "Failed to load CSV file")
            return

        if self.data_manager.get_word_count() == 0:
            QMessageBox.warning(self, "No Data", "No words found in CSV file")
            return

        available_types = self.data_manager.get_types()
        if not available_types:
            QMessageBox.warning(self, "No Types", "No card types found in CSV file")
            return

        self.selected_types = available_types
        self.filtered_words = self.data_manager.filter_words_by_types(self.selected_types)

        self.card_logic = CardLogic(self.filtered_words)
        self.available_types = available_types
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Cantonese Flashcard - Enter to Check")
        self.resize(750, 600)

        self.type_filter = TypeFilter(
            self.available_types,
            on_filter_changed=self.on_filter_changed
        )
        self.card_display = CardDisplay(on_check_callback=self.check)
        self.buttons = ControlButtons(
            on_check_callback=self.check,
            on_next_callback=self.new_card
        )

        layout = QVBoxLayout()
        layout.addWidget(self.type_filter)
        layout.addWidget(self.card_display, 1)
        layout.addWidget(self.buttons)
        self.setLayout(layout)

        self.new_card()

    def on_filter_changed(self, selected_types):
        self.selected_types = selected_types

        if not selected_types:
            QMessageBox.warning(self, "No Selection", "Please select at least one card type")
            return

        self.filtered_words = self.data_manager.filter_words_by_types(selected_types)

        if not self.filtered_words:
            QMessageBox.warning(self, "No Cards", "No cards available for selected types")
            return

        self.card_logic = CardLogic(self.filtered_words)
        self.card_count = 0
        self.update_title()
        self.new_card()

    def new_card(self):
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
        self.setWindowTitle(f"Cantonese Flashcard - Card {self.card_count}/{MAX_CARDS}")

    def check(self):
        if not self.card_logic.current:
            return

        user_inputs = self.card_display.get_inputs()
        is_correct, message = self.card_logic.check_answer(self.current_mode, user_inputs)

        self.data_manager.save_csv()

        if is_correct:
            QMessageBox.information(self, "Correct!", message)
        else:
            QMessageBox.warning(self, "Try Again", message)

        if self.card_count < MAX_CARDS:
            self.new_card()
        else:
            self.ask_continue()

    def ask_continue(self):
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
