# players/ai_normal.py
import random

class NormalAI:
    def decide(self, player, to_call, big_blind):
        if len(player.hole_cards) < 2:
            return ("check", 0) if to_call == 0 else ("call", to_call)

        r1 = player.hole_cards[0].rank
        r2 = player.hole_cards[1].rank
        high, low = max(r1, r2), min(r1, r2)

        pair = (r1 == r2)
        strength = 0
        if pair:
            strength = 3
        elif high >= 13 and low >= 10:
            strength = 2
        elif high >= 11:
            strength = 1

        # 블러핑
        if to_call == 0 and random.random() < 0.10:
            return ("raise", big_blind * 2)

        if strength >= 2:
            if to_call == 0:
                return ("raise", big_blind * 2)
            return ("call", to_call)

        if strength == 1:
            if to_call <= big_blind:
                return ("call", to_call)
            return ("fold", 0)

        if to_call == 0:
            return ("check", 0)
        return ("fold", 0)
