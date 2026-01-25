import random

class EasyAI:
    def decide(self, player, to_call, big_blind):
                                 
        ranks = [card.rank for card in player.hole_cards]

               
        if ranks[0] == ranks[1]:
                  
            if to_call == 0:
                return ("check", 0)
            elif to_call <= big_blind:
                return ("call", to_call)
            else:
                return ("fold", 0)

              
        if to_call == 0:
            return ("check", 0)
        if to_call <= big_blind:
            return ("call", to_call)

        return ("fold", 0)
