"""Logic for QA cards (question -> answer)."""

from typing import List, Dict, Any, Tuple
import random


class CardLogicQA:
    def __init__(self, cards: List[Dict[str, Any]]):
        self.cards = cards
        self.current = None
        self.current_idx = -1

    def get_random_card(self) -> Dict[str, Any]:
        if not self.cards:
            return None
        self.current_idx = random.randint(0, len(self.cards) - 1)
        self.current = self.cards[self.current_idx]
        self.current['questioned'] = self.current.get('questioned', 0) + 1
        if self.current.get('_row') is not None:
            self.current['_row']['Questioned'] = str(self.current['questioned'])
        return {'card': self.current}

    def check_answer(self, user_answer: str) -> Tuple[bool, str]:
        if not self.current:
            return False, "No card loaded"

        user = (user_answer or '').strip().lower()
        expected = (self.current.get('a_text') or '').strip().lower()
        correct = False
        msg = ""
        if expected:
            if user == expected or expected in user or user in expected:
                correct = True
                self.current['correct'] = self.current.get('correct', 0) + 1
                if self.current.get('_row') is not None:
                    self.current['_row']['Correct'] = str(self.current['correct'])
                msg = "Correct"
            else:
                msg = f"Expected: {self.current.get('a_text')}"
        else:
            msg = "No expected answer available"

        return correct, msg
