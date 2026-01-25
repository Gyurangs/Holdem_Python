class BettingRound:
    def __init__(self, players, start_index, big_blind):
        self.players = players
        self.current_bet = 0
        self.min_raise = big_blind
        self.start_index = start_index
        self.turn_index = start_index
        self.last_raiser = None

        # 이번 라운드에서 행동 완료 여부
        self.acted = {p: False for p in players}

    def next_player(self):
        self.turn_index = (self.turn_index + 1) % len(self.players)

    def mark_acted(self, player):
        self.acted[player] = True

    def reset_acted_except(self, raiser):
        # 레이즈가 나오면 raiser만 acted 유지
        for p in self.players:
            if p.folded or p.all_in:
                self.acted[p] = True
            else:
                self.acted[p] = (p == raiser)

    def all_acted_or_all_in(self):
        # 폴드 제외 플레이어가 모두 행동 완료했는지 확인
        non_folded = [p for p in self.players if not p.folded]
        if len(non_folded) <= 1:
            return True
        for p in non_folded:
            if p.all_in:
                continue
            if p.current_bet != self.current_bet:
                return False
            if not self.acted.get(p, False):
                return False

        return True

