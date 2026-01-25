class Pot:
    def __init__(self):
        # player -> 누적 베팅
        self.bets = {}

    def add_bet(self, player, amount):
        if amount <= 0:
            return
        if player not in self.bets:
            self.bets[player] = 0
        self.bets[player] += amount

    def reset(self):
        self.bets.clear()

    @property
    def total(self):
        return sum(self.bets.values())

    def total_chips(self):
        return self.total

    def build_pots(self):
        """
        반환: (금액, 자격 있는 플레이어 목록) 튜플 리스트
        """
        pots = []
        remaining = self.bets.copy()

        while remaining:
            min_bet = min(remaining.values())
            eligible = list(remaining.keys())

            pot_amount = min_bet * len(eligible)
            pots.append((pot_amount, eligible))

            for p in eligible:
                remaining[p] -= min_bet
                if remaining[p] == 0:
                    del remaining[p]

        return pots
