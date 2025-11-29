"""Simple QA flashcard app window using the QA data manager and logic."""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QMessageBox, QLabel, QHBoxLayout, QPushButton
from PyQt5.QtMultimedia import QSound
import re

# Chinese regex used by the TTS generator
CHINESE_RE = re.compile(r'[\u4E00-\u9FFF\u3400-\u4DBF\uF900-\uFAFF]+')
import threading
import shutil
import subprocess

from ..common.ui_widgets import InputField, ControlButtons
from .data_manager_qa import DataManagerQA
from .card_logic_qa import CardLogicQA
from pathlib import Path


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

    # UI contains six input boxes (created below). No separate prompt label.

        # Create input fields for the six possible keys in CSV order (if available)
        self.input_fields = {}
        order = getattr(self.data_manager, 'field_order', ['ChineseQ', 'JyutpingQ', 'EnglishQ', 'ChineseA', 'JyutpingA', 'EnglishA'])
        for key in order:
            lbl = QLabel(key + ':')
            fld = InputField()
            fld.returnPressed.connect(self.check)
            h = QHBoxLayout()
            h.addWidget(lbl)
            h.addWidget(fld, 1)
            # If this is a Chinese field, add a listen button
            if key in ('ChineseQ', 'ChineseA'):
                btn_listen = QPushButton('Listen')
                btn_listen.setFixedWidth(90)
                # play the EXPECTED answer for this key (from current card), not the field text
                btn_listen.clicked.connect(lambda _checked, k=key: self.play_key_audio(k))
                h.addWidget(btn_listen)
                fld._listen_button = btn_listen
            self.input_fields[key] = (lbl, fld, h)
            layout.addLayout(h)

        # Buttons
        self.buttons = ControlButtons(on_check_callback=self.check, on_next_callback=self.new_card)
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
        prompt_key = res.get('prompt_key')
        expected_keys = res.get('expected_keys', [])

        prompt_val = card.get(prompt_key) or ''
        self.current_prompt_key = prompt_key
        self.current_expected_keys = expected_keys
        self.current_prompt_val = prompt_val

        # configure inputs: always show all 6 fields; prefill & disable prompted field
        for key, (lbl, fld, h) in self.input_fields.items():
            lbl.show()
            if key == prompt_key:
                # pre-fill and grey out
                fld.disable(prompt_val or '')
                if hasattr(fld, '_listen_button'):
                    # prompt listen should play the expected prompt (use prompt_listen_button too)
                    fld._listen_button.show()
            else:
                # reset/enable other fields for answers
                fld.enable()
                # ensure input is empty
                fld.clear()
                if hasattr(fld, '_listen_button'):
                    fld._listen_button.show()

        self.card_count += 1

    def check(self):
        # gather user answers for expected keys
        # use stored expected keys from last new_card
        current = self.card_logic.current
        if not current:
            return
        expected_keys = getattr(self, 'current_expected_keys', [])
        user_answers = {}
        for k in expected_keys:
            user_answers[k] = self.input_fields[k][1].text().strip()

        correct, msg = self.card_logic.check_answer(user_answers, expected_keys)
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

    def safe_name(self, text: str) -> str:
        # prefer extracting pure Chinese characters (generator uses Chinese-only matches)
        if not text:
            return ''
        m = CHINESE_RE.findall(text)
        if m:
            base = ''.join(m)
        else:
            base = ''.join(ch if ch.isalnum() else '_' for ch in text)
        return base

    def get_audio_path_for_text(self, text: str) -> Path:
        safe = self.safe_name(text)
        return Path('resources') / 'audio' / f"{safe}.wav"

    def generate_audio_and_play(self, text: str):
        """Ensure audio exists for text: generate via ekho in background if missing and play when ready."""
        if not text:
            QMessageBox.warning(self, "No Audio", "Empty text")
            return

        out_path = self.get_audio_path_for_text(text)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        if out_path.exists():
            try:
                QSound.play(str(out_path))
            except Exception as e:
                QMessageBox.warning(self, "Playback Error", str(e))
            return

        # Need to generate. Check ekho availability
        if not shutil.which('ekho'):
            QMessageBox.warning(self, "Missing ekho", "ekho command not found on PATH; cannot synthesize audio")
            return

        def worker():
            cmd = ['ekho', '-v', 'Cantonese', '-o', str(out_path), text]
            try:
                subprocess.run(cmd, check=True)
                # play the generated file
                try:
                    QSound.play(str(out_path))
                except Exception:
                    pass
            except Exception as e:
                print('ekho generation failed:', e)

        # Inform user and start background generation
        QMessageBox.information(self, "Generating audio", f"Generating audio for: {text}")
        t = threading.Thread(target=worker, daemon=True)
        t.start()

    def play_field_audio(self, field: InputField):
        # Deprecated: field playback is not used. Keep for compatibility.
        text = field.text().strip()
        if not text:
            QMessageBox.warning(self, "No Text", "No text to play")
            return
        p = self.get_audio_path_for_text(text)
        if not p.exists():
            QMessageBox.warning(self, "No Audio", f"Audio not found: {p}")
            return
        try:
            QSound.play(str(p))
        except Exception as e:
            QMessageBox.warning(self, "Playback Error", str(e))

    def play_key_audio(self, key: str):
        """Play the expected answer text for `key` from the current card."""
        card = getattr(self.card_logic, 'current', None)
        if not card:
            QMessageBox.warning(self, "No Card", "No card loaded")
            return
        text = (card.get(key) or '').strip()
        if not text:
            QMessageBox.warning(self, "No Audio", f"No expected text for {key}")
            return
        # Generate on-demand and play (will run ekho in background if missing)
        self.generate_audio_and_play(text)

    def play_prompt_audio(self):
        txt = getattr(self, 'current_prompt_val', '')
        if not txt:
            QMessageBox.warning(self, "No Audio", "No prompt audio available")
            return
        self.generate_audio_and_play(txt)
