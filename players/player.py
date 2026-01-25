class Player:
    __hash__ = object.__hash__

    def __init__(self, name, chips=2000,    ai=None):
        self.name = name
        self.chips = chips
        self.hole_cards = []
        self.ai = ai
        self.folded = False
        self.all_in = False
        self.current_bet = 0
        self.busted = False

    def reset_for_new_hand(self):
        if self.busted:
            self.hole_cards.clear()
            self.folded = True
            self.all_in = True
            self.current_bet = 0
            return
        self.hole_cards.clear()
        self.folded = False
        self.all_in = False
        self.current_bet = 0
