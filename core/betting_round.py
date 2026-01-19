class BettingRound:
    def __init__(self, players, start_index, big_blind):
        self.players = players
        self.current_bet = 0
        self.min_raise = big_blind
        self.start_index = start_index
        self.turn_index = start_index
        self.last_raiser = None

        # ✅ 이번 라운드에서 행동했는지 추적
        self.acted = {p: False for p in players}

    def next_player(self):
        self.turn_index = (self.turn_index + 1) % len(self.players)

    def mark_acted(self, player):
        self.acted[player] = True

    def reset_acted_except(self, raiser):
        # 레이즈 나오면 다시 모두 행동해야 함
        for p in self.players:
            if p.folded:
                continue
            self.acted[p] = (p == raiser)

    def all_acted_or_all_in(self):
        active_players = [p for p in self.players if not p.folded and not p.all_in]

        if len(active_players) <= 1:
            return True

        # 1) 모두 베팅 금액을 맞췄는지
        for p in active_players:
            if p.current_bet != self.current_bet:
                return False

        # 2) 모두 최소 1번 행동했는지
        for p in active_players:
            if not self.acted.get(p, False):
                return False

        return True
