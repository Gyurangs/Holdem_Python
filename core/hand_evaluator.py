from itertools import combinations
from collections import Counter

HAND_RANKS = {
    "HIGH_CARD": 1,
    "ONE_PAIR": 2,
    "TWO_PAIR": 3,
    "THREE_KIND": 4,
    "STRAIGHT": 5,
    "FLUSH": 6,
    "FULL_HOUSE": 7,
    "FOUR_KIND": 8,
    "STRAIGHT_FLUSH": 9
}


def evaluate_7cards(cards):
    """
    cards: list of 7 Card objects
    return: best hand score tuple
    """
    best = None
    for combo in combinations(cards, 5):
        score = evaluate_5cards(combo)
        if best is None or score > best:
            best = score
    return best


def evaluate_5cards(cards):
    ranks = sorted([c.rank for c in cards], reverse=True)
    suits = [c.suit for c in cards]

    rank_counter = Counter(ranks)
    suit_counter = Counter(suits)

    is_flush = max(suit_counter.values()) == 5
    is_straight, straight_high = check_straight(ranks)

    # 🔥 스트레이트 플러시
    if is_flush and is_straight:
        return (HAND_RANKS["STRAIGHT_FLUSH"], straight_high)

    # 🔥 포카드
    if 4 in rank_counter.values():
        four = get_key_by_value(rank_counter, 4)
        kicker = max(r for r in ranks if r != four)
        return (HAND_RANKS["FOUR_KIND"], four, kicker)

    # 🔥 풀하우스
    if sorted(rank_counter.values()) == [2, 3]:
        three = get_key_by_value(rank_counter, 3)
        pair = get_key_by_value(rank_counter, 2)
        return (HAND_RANKS["FULL_HOUSE"], three, pair)

    # 🔥 플러시
    if is_flush:
        return (HAND_RANKS["FLUSH"], *ranks)

    # 🔥 스트레이트
    if is_straight:
        return (HAND_RANKS["STRAIGHT"], straight_high)

    # 🔥 트리플
    if 3 in rank_counter.values():
        three = get_key_by_value(rank_counter, 3)
        kickers = sorted([r for r in ranks if r != three], reverse=True)
        return (HAND_RANKS["THREE_KIND"], three, *kickers)

    # 🔥 투페어
    pairs = [r for r, c in rank_counter.items() if c == 2]
    if len(pairs) == 2:
        high, low = sorted(pairs, reverse=True)
        kicker = max(r for r in ranks if r not in pairs)
        return (HAND_RANKS["TWO_PAIR"], high, low, kicker)

    # 🔥 원페어
    if 2 in rank_counter.values():
        pair = get_key_by_value(rank_counter, 2)
        kickers = sorted([r for r in ranks if r != pair], reverse=True)
        return (HAND_RANKS["ONE_PAIR"], pair, *kickers)

    # 🔥 하이카드
    return (HAND_RANKS["HIGH_CARD"], *ranks)


def check_straight(ranks):
    unique = sorted(set(ranks), reverse=True)

    # A-5 스트레이트 처리
    if unique == [14, 5, 4, 3, 2]:
        return True, 5

    for i in range(len(unique) - 4):
        if unique[i] - unique[i + 4] == 4:
            return True, unique[i]

    return False, None


def get_key_by_value(counter, value):
    for k, v in counter.items():
        if v == value:
            return k
