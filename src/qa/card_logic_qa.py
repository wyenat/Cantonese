"""Logic for QA cards (question -> answer)."""

from typing import List, Dict, Any, Tuple
import random


class CardLogicQA:
    def __init__(self, cards: List[Dict[str, Any]]):
        self.cards = cards
        self.current = None
        self.current_idx = -1
    def get_random_card(self) -> Dict[str, Any]:
        """Select a random card and choose one of the six fields as the prompt.

        Returns a dict with 'card', 'prompt_key', and 'expected_keys'.
        """
        if not self.cards:
            return None

        # choose a random card and pick a prompt key that has content
        attempts = 0
        while attempts < 10:
            self.current_idx = random.randint(0, len(self.cards) - 1)
            self.current = self.cards[self.current_idx]
            keys = ['ChineseQ', 'JyutpingQ', 'EnglishQ', 'ChineseA', 'JyutpingA', 'EnglishA']
            prompt_key = random.choice(keys)
            if self.current.get(prompt_key):
                break
            attempts += 1

        if not self.current:
            return None

        # increment questioned counter
        self.current['questioned'] = self.current.get('questioned', 0) + 1
        if self.current.get('_row') is not None:
            self.current['_row']['Questioned'] = str(self.current['questioned'])

        # expected keys are the other five
        expected_keys = [k for k in keys if k != prompt_key]

        return {
            'card': self.current,
            'prompt_key': prompt_key,
            'expected_keys': expected_keys,
        }

    def check_answer(self, user_answers: Dict[str, str], expected_keys: List[str]) -> Tuple[bool, str]:
        """Check user's answers for the expected keys.

        user_answers: mapping from key -> user input string
        expected_keys: list of keys to check
        Returns (True, message) on full match, otherwise (False, message)
        """
        if not self.current:
            return False, "No card loaded"

        failures = []
        for key in expected_keys:
            expected = (self.current.get(key) or '').strip()
            user = (user_answers.get(key) or '').strip()

            # Normalize for comparison
            exp_low = expected.lower()
            user_low = user.lower()

            ok = False
            if not expected:
                # no expected value, skip checking
                ok = True
            else:
                # accept exact match or substring presence
                if user_low == exp_low or exp_low in user_low or user_low in exp_low:
                    ok = True

            if not ok:
                failures.append(f"{key}: expected '{expected}'")

        if not failures:
            # all correct
            self.current['correct'] = self.current.get('correct', 0) + 1
            if self.current.get('_row') is not None:
                self.current['_row']['Correct'] = str(self.current['correct'])
            return True, "All correct"

        return False, "; ".join(failures)
