                    
import random

class HardAI:
    def decide(self, player, to_call, big_blind):
                              
        if len(player.hole_cards) < 2:
            return ("check", 0) if to_call == 0 else ("call", to_call)

        c1, c2 = player.hole_cards
        r1, r2 = c1.rank, c2.rank
        s1, s2 = c1.suit, c2.suit

        high = max(r1, r2)
        low = min(r1, r2)
        pair = (r1 == r2)
        suited = (s1 == s2)
        connector = (abs(r1 - r2) == 1)

        # 간단한 프리플랍 강도 점수
        strength = 0
        if pair:
            strength += 4
            if high >= 11:
                strength += 2           
        if high >= 13:       
            strength += 2
        if high >= 11 and low >= 10:            
            strength += 1
        if suited:
            strength += 1
        if connector:
            strength += 1

        # 블러핑 레이즈 확률
        if to_call == 0 and random.random() < 0.15:
            return ("raise", big_blind * 2)

        # 과한 콜 금액은 방어적으로 폴드
        if to_call > big_blind * 4 and strength < 4:
            return ("fold", 0)

        # 강한 핸드: 공격적으로 레이즈
        if strength >= 6:
            if to_call == 0:
                return ("raise", big_blind * 3)
            return ("raise", to_call + big_blind * 2)          

                          
        if strength >= 4:
            if to_call == 0:
                return ("raise", big_blind * 2) if random.random() < 0.35 else ("check", 0)
            return ("call", to_call)

               
        if to_call == 0:
            return ("check", 0)
        if to_call <= big_blind:
            return ("call", to_call)

        return ("fold", 0)
