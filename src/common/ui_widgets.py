"""UI components for the flashcard application (shared)."""

from PyQt5.QtWidgets import QLineEdit, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QCheckBox, QGroupBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, pyqtSignal


class InputField(QLineEdit):
    """Custom QLineEdit for flashcard input."""

    def __init__(self, font: QFont = None, height: int = 50, parent=None):
        super().__init__(parent)
        if font:
            self.setFont(font)
        self.setAlignment(Qt.AlignCenter)
        self.setFixedHeight(height)

    def disable(self, value: str):
        self.setText(value)
        self.setEnabled(False)
        self.setStyleSheet("background-color: #e0e0e0; color: black;")

    def enable(self):
        self.clear()
        self.setEnabled(True)
        self.setStyleSheet("")


class CardDisplay(QWidget):
    """Widget for displaying flashcard input fields."""

    def __init__(self, on_check_callback=None, parent=None):
        super().__init__(parent)
        self.on_check = on_check_callback
        self.init_ui()

    def init_ui(self):
        font_char = QFont("Noto Sans CJK HK", 24)
        font_jyut = QFont("DejaVu Sans", 18)
        font_eng = QFont("DejaVu Sans", 18)

        lbl_char = QLabel("Chinese Character:")
        lbl_jyut = QLabel("Jyutping:")
        lbl_eng = QLabel("English:")

        self.char_input = InputField(font_char, 60)
        if self.on_check:
            self.char_input.returnPressed.connect(self.on_check)

        self.jyut_input = InputField(font_jyut, 50)
        if self.on_check:
            self.jyut_input.returnPressed.connect(self.on_check)

        self.eng_input = InputField(font_eng, 50)
        if self.on_check:
            self.eng_input.returnPressed.connect(self.on_check)

        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(40, 30, 40, 30)

        for label, edit in [
            (lbl_char, self.char_input),
            (lbl_jyut, self.jyut_input),
            (lbl_eng, self.eng_input)
        ]:
            hbox = QHBoxLayout()
            hbox.addWidget(label)
            hbox.addWidget(edit, 1)
            layout.addLayout(hbox)

        self.setLayout(layout)

    def get_inputs(self) -> dict:
        return {
            'char': self.char_input.text().strip(),
            'jyut': self.jyut_input.text().strip(),
            'eng': self.eng_input.text().strip()
        }

    def reset_inputs(self):
        for field in [self.char_input, self.jyut_input, self.eng_input]:
            field.enable()

    def set_quiz_mode(self, mode: str, card: dict):
        self.reset_inputs()

        if mode == 'char':
            self.char_input.disable(card['char'])
            self.jyut_input.setFocus()
        elif mode == 'jyut':
            self.jyut_input.disable(card['jyut'])
            self.char_input.setFocus()
        else:  # eng
            self.eng_input.disable(card['eng'].title())
            self.char_input.setFocus()

        for field in [self.char_input, self.jyut_input, self.eng_input]:
            if field.isEnabled():
                field.setFocus()
                break


class TypeFilter(QGroupBox):
    """Widget for filtering flashcards by type."""

    filter_changed = pyqtSignal(list)

    def __init__(self, types: list, on_filter_changed=None, parent=None):
        super().__init__("Card Types", parent)
        self.types = types
        self.checkboxes = {}
        self.on_filter_changed = on_filter_changed
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        for card_type in self.types:
            checkbox = QCheckBox(card_type)
            checkbox.setChecked(True)
            checkbox.stateChanged.connect(self.on_checkbox_changed)
            self.checkboxes[card_type] = checkbox
            layout.addWidget(checkbox)

        layout.addStretch()
        self.setLayout(layout)

    def on_checkbox_changed(self):
        selected = self.get_selected_types()
        if self.on_filter_changed:
            self.on_filter_changed(selected)
        self.filter_changed.emit(selected)

    def get_selected_types(self) -> list:
        return [card_type for card_type, checkbox in self.checkboxes.items() if checkbox.isChecked()]


class ControlButtons(QWidget):
    """Widget for control buttons."""

    def __init__(self, on_check_callback=None, on_next_callback=None, parent=None):
        super().__init__(parent)
        self.init_ui(on_check_callback, on_next_callback)

    def init_ui(self, on_check, on_next):
        self.btn_check = QPushButton("Check Answer")
        self.btn_check.setStyleSheet(
            "background-color: #4CAF50; color: white; font-size: 14pt; padding: 10px;"
        )
        if on_check:
            self.btn_check.clicked.connect(on_check)

        self.btn_next = QPushButton("Next Card")
        self.btn_next.setStyleSheet("font-size: 12pt; padding: 8px;")
        if on_next:
            self.btn_next.clicked.connect(on_next)

        layout = QHBoxLayout()
        layout.addStretch()
        layout.addWidget(self.btn_check)
        layout.addWidget(self.btn_next)
        layout.addStretch()
        layout.setContentsMargins(0, 20, 0, 0)

        self.setLayout(layout)
