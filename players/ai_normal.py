import random

class NormalAI:
    def decide(self, player, to_call, big_blind):
        ranks = sorted([c[0] for c in player.hand], reverse=True)
        high, low = ranks

        strength = 0

        if high == low:
            strength = 3  # 페어
        elif high >= 13 and low >= 10:
            strength = 2  # AK, AQ, KQ
        elif high >= 11:
            strength = 1

        # 블러핑
        if random.random() < 0.12:
            return ("raise", big_blind * 2)

        if strength >= 2:
            if to_call == 0:
                return ("raise", big_blind * 2)
            return ("call", to_call)

        if strength == 1:
            if to_call <= big_blind:
                return ("call", to_call)
            return ("fold", 0)

        return ("fold", 0)
