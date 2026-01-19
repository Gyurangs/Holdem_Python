import random

class EasyAI:
    def decide(self, player, to_call, big_blind):
        # hole_cards는 Card 객체 리스트
        ranks = [card.rank for card in player.hole_cards]

        # 페어 여부
        if ranks[0] == ranks[1]:
            # 강한 패
            if to_call == 0:
                return ("check", 0)
            elif to_call <= big_blind:
                return ("call", to_call)
            else:
                return ("fold", 0)

        # 약한 패
        if to_call == 0:
            return ("check", 0)
        if to_call <= big_blind:
            return ("call", to_call)

        return ("fold", 0)
