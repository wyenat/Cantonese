"""Core logic for flashcard operations."""

import random
from typing import List, Dict, Any, Tuple


class CardLogic:
    """Handles flashcard game logic and answer checking."""

    def __init__(self, words: List[Dict[str, Any]]):
        """
        Initialize CardLogic with word list.
        
        Args:
            words: List of word dictionaries
        """
        self.words = words
        self.current = None
        self.current_idx = -1

    def get_random_card(self) -> Dict[str, Any]:
        """
        Select a random card and return it with a quiz mode.
        
        Returns:
            Dictionary with 'card', 'mode', and 'question' keys
        """
        if not self.words:
            return None

        self.current_idx = random.randint(0, len(self.words) - 1)
        self.current = self.words[self.current_idx]
        mode = random.choice(['char', 'jyut', 'eng'])

        # Increment Questioned counter
        self.current['q'] += 1
        self.current['_row']['Questioned'] = str(self.current['q'])

        return {
            'card': self.current,
            'mode': mode,
        }

    def check_answer(self, mode: str, user_inputs: Dict[str, str]) -> Tuple[bool, str]:
        """
        Check user's answer against expected values.
        
        Args:
            mode: Quiz mode ('char', 'jyut', or 'eng')
            user_inputs: Dictionary with 'char', 'jyut', 'eng' keys and user responses
        
        Returns:
            Tuple of (is_correct, message)
        """
        if not self.current:
            return False, "No card loaded"

        c = user_inputs.get('char', '').strip()
        j = user_inputs.get('jyut', '').strip().lower()
        e = user_inputs.get('eng', '').strip().lower()

        exp_c = self.current['char']
        exp_j = self.current['jyut'].lower()
        exp_e_list = [x.strip() for x in self.current['eng'].split('/')]

        correct = True
        msg = [""]

        for tested, answer, expected in [
            ("Chinese", c, exp_c) if mode != 'char' else (None, None, None),
            ("Jyutping", j, exp_j) if mode != 'jyut' else (None, None, None),
            ("English", e, exp_e_list) if mode != 'eng' else (None, None, None),
        ]:
            if answer is None:
                continue

            if answer not in expected:
                correct = False
                msg.append(f"{tested} : expected {expected if type(expected) is str else ' / '.join(expected)}")
                break
            else:
               msg.append(f"{tested} : Correct!")
    
        if correct:
            self.current['c'] += 1
            self.current['_row']['Correct'] = str(self.current['c'])


        return correct, "\n".join(msg)
