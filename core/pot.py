class Pot:
    def __init__(self):
        self.bets = {}  # player -> total bet

    def add_bet(self, player, amount):
        if player not in self.bets:
            self.bets[player] = 0
        self.bets[player] += amount

    def reset(self):
        self.bets.clear()

    def build_pots(self):
        """
        return: list of (amount, eligible_players)
        """
        pots = []
        remaining = self.bets.copy()

        while remaining:
            min_bet = min(remaining.values())
            eligible = list(remaining.keys())

            pot_amount = min_bet * len(eligible)
            pots.append((pot_amount, eligible))

            # 차감
            for p in eligible:
                remaining[p] -= min_bet
                if remaining[p] == 0:
                    del remaining[p]

        return pots
