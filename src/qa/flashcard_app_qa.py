"""Simple QA flashcard app window using the QA data manager and logic."""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QMessageBox, QLabel

from ..common.ui_widgets import InputField, ControlButtons
from .data_manager_qa import DataManagerQA
from .card_logic_qa import CardLogicQA


MAX_CARDS = 10


class FlashcardQAApp(QWidget):
    def __init__(self, csv_file: str):
        super().__init__()
        self.csv_file = csv_file
        self.data_manager = DataManagerQA(csv_file)
        self.card_logic = None
        self.card_count = 0

        if not self.data_manager.load_csv():
            QMessageBox.critical(self, "Error", "Failed to load QA CSV file")
            return

        if self.data_manager.get_count() == 0:
            QMessageBox.warning(self, "No Data", "No QA cards found in CSV file")
            return

        self.cards = self.data_manager.get_cards()
        self.card_logic = CardLogicQA(self.cards)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Cantonese QA Flashcards")
        self.resize(700, 300)

        layout = QVBoxLayout()

        self.question_label = QLabel("")
        self.question_label.setWordWrap(True)

        self.answer_input = InputField()
        self.answer_input.returnPressed.connect(self.check)

        self.buttons = ControlButtons(on_check_callback=self.check, on_next_callback=self.new_card)

        layout.addWidget(self.question_label)
        layout.addWidget(self.answer_input)
        layout.addWidget(self.buttons)

        self.setLayout(layout)

        self.new_card()

    def new_card(self):
        if self.card_count >= MAX_CARDS:
            self.ask_continue()
            return

        res = self.card_logic.get_random_card()
        if not res or 'card' not in res:
            QMessageBox.critical(self, "Error", "Failed to get card")
            return

        card = res['card']
        q_text = card.get('q_text') or card.get('q_jyut') or ''
        self.question_label.setText(f"Q: {q_text}")
        self.answer_input.enable()
        self.card_count += 1

    def check(self):
        user = self.answer_input.text().strip()
        correct, msg = self.card_logic.check_answer(user)
        self.data_manager.save_csv()

        if correct:
            QMessageBox.information(self, "Correct", msg)
        else:
            QMessageBox.warning(self, "Incorrect", msg)

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
            self.new_card()
        else:
            self.close()
