import random

class HardAI:
    def decide(self, player, to_call, big_blind):
        ranks = sorted([c[0] for c in player.hand], reverse=True)
        high, low = ranks

        # 프리플랍 강도
        if high == low:
            strength = 4
        elif high >= 13 and low >= 11:
            strength = 3
        elif high >= 11:
            strength = 2
        else:
            strength = 1

        # 공격적 블러핑
        if random.random() < 0.3:
            return ("raise", big_blind * random.choice([3, 4]))

        if strength >= 3:
            return ("raise", max(big_blind * 3, to_call))

        if strength == 2:
            if to_call <= big_blind * 2:
                return ("call", to_call)
            return ("fold", 0)

        if to_call == 0:
            return ("check", 0)

        return ("fold", 0)
