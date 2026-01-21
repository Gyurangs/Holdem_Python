# players/ai_hard.py
import random

class HardAI:
    def decide(self, player, to_call, big_blind):
        # 방어코드: 카드 2장 없으면 체크/콜
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

        # 아주 러프한 프리플랍 강도 점수
        strength = 0
        if pair:
            strength += 4
            if high >= 11:
                strength += 2  # JJ+ 보너스
        if high >= 13:  # A,K
            strength += 2
        if high >= 11 and low >= 10:  # QJ, JT 등
            strength += 1
        if suited:
            strength += 1
        if connector:
            strength += 1

        # 블러핑 확률(콜 금액이 0일 때만 조금 공격)
        if to_call == 0 and random.random() < 0.15:
            return ("raise", big_blind * 2)

        # to_call이 너무 크면 방어적으로
        if to_call > big_blind * 4 and strength < 4:
            return ("fold", 0)

        # 강한 핸드: 공격
        if strength >= 6:
            if to_call == 0:
                return ("raise", big_blind * 3)
            return ("raise", to_call + big_blind * 2)  # 콜 + 추가

        # 중간: 콜 위주, 가끔 레이즈
        if strength >= 4:
            if to_call == 0:
                return ("raise", big_blind * 2) if random.random() < 0.35 else ("check", 0)
            return ("call", to_call)

        # 약한 핸드
        if to_call == 0:
            return ("check", 0)
        if to_call <= big_blind:
            return ("call", to_call)

        return ("fold", 0)
