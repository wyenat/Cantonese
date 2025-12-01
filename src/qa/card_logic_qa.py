"""Logic for QA cards (question -> answer)."""

from typing import List, Dict, Any, Tuple
import random


class CardLogicQA:
    def __init__(self, cards: List[Dict[str, Any]], prompt_weights: Dict[str, float] = None):
        """cards: list of card dicts

        prompt_weights: optional mapping of prompt key -> weight (probability coefficient).
        If not provided, defaults to preferring ChineseQ (weight 1) and zero for others
        so the prompt will be ChineseQ unless it's empty.
        """
        self.cards = cards
        self.current = None
        self.current_idx = -1

        # default keys
        self.keys = ['ChineseQ', 'JyutpingQ', 'EnglishQ', 'ChineseA', 'JyutpingA', 'EnglishA']

        # initialize weights - default: ChineseQ preferred
        default = {k: (1.0 if k == 'ChineseQ' else 0.0) for k in self.keys}
        self.prompt_weights = default if prompt_weights is None else {**default, **prompt_weights}

    def set_prompt_weights(self, weights: Dict[str, float]):
        """Replace or update prompt weights. Accepts partial dict of key->weight."""
        for k, v in weights.items():
            if k in self.keys:
                try:
                    self.prompt_weights[k] = float(v)
                except Exception:
                    pass
    def get_random_card(self) -> Dict[str, Any]:
        """Select a random card and choose one of the six fields as the prompt.

        Returns a dict with 'card', 'prompt_key', and 'expected_keys'.
        """
        if not self.cards:
            return None

        # choose a random card (try up to N attempts to find one with content)
        attempts = 0
        while attempts < 10:
            self.current_idx = random.randint(0, len(self.cards) - 1)
            self.current = self.cards[self.current_idx]
            # available keys on this card
            keys = self.keys

            # build candidate prompt keys preserving configured weights and presence of content
            candidates = []
            weights = []
            for k in keys:
                if self.current.get(k):
                    w = float(self.prompt_weights.get(k, 0.0) or 0.0)
                    if w > 0:
                        candidates.append(k)
                        weights.append(w)

            # if no weighted candidates (all weights zero or missing), fall back to any key that has content
            if not candidates:
                candidates = [k for k in keys if self.current.get(k)]
                weights = [1.0] * len(candidates)

            if candidates:
                prompt_key = random.choices(candidates, weights=weights, k=1)[0]
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
