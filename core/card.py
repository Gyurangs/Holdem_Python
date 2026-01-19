class Card:
    def __init__(self, rank, suit):
        self.rank = rank    # 2~14
        self.suit = suit    # 'S', 'H', 'D', 'C'

    def __repr__(self):
        rank_map = {11: 'J', 12: 'Q', 13: 'K', 14: 'A'}
        r = rank_map.get(self.rank, str(self.rank))
        return f"{r}{self.suit}"
