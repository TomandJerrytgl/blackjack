"""Card shoe operations. Card IDs are unique across all decks."""

import random


class GeneralDeck:
    def __init__(self, deck_number=5):
        if type(deck_number) is not int or deck_number < 1:
            raise ValueError("deck_number must be a positive integer")
        self.deck_number = deck_number
        self.cards = []

    def create_deck(self):
        self.cards = list(range(1, self.deck_number * 52 + 1))
        return self.cards

    def shuffle(self):
        random.shuffle(self.cards)

    def draw_card(self):
        if not self.cards:
            raise ValueError("The shoe is empty")
        return self.cards.pop()

    @staticmethod
    def get_card_identity(card):
        if type(card) is not int or card < 1:
            raise ValueError("Invalid card ID")
        code = (card - 1) % 52
        return ("♠♥♦♣"[code // 13],
                ("A", "2", "3", "4", "5", "6", "7", "8", "9",
                 "10", "J", "Q", "K")[code % 13])

    @staticmethod
    def card_value(card):
        """Return 1 for Ace and 10 for all ten-point ranks."""
        return min((card - 1) % 13 + 1, 10)
