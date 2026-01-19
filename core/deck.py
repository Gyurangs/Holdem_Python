import random
from core.card import Card

class Deck:
    def __init__(self):
        self.cards = []
        self.reset()

    def reset(self):
        self.cards = [
            Card(rank, suit)
            for suit in ['S', 'H', 'D', 'C']
            for rank in range(2, 15)
        ]

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self):
        return self.cards.pop()

    def burn(self):
        self.cards.pop()
