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

HAND_RANK_NAMES_EN = {
    HAND_RANKS["HIGH_CARD"]: "High Card",
    HAND_RANKS["ONE_PAIR"]: "One Pair",
    HAND_RANKS["TWO_PAIR"]: "Two Pair",
    HAND_RANKS["THREE_KIND"]: "Three of a Kind",
    HAND_RANKS["STRAIGHT"]: "Straight",
    HAND_RANKS["FLUSH"]: "Flush",
    HAND_RANKS["FULL_HOUSE"]: "Full House",
    HAND_RANKS["FOUR_KIND"]: "Four of a Kind",
    HAND_RANKS["STRAIGHT_FLUSH"]: "Straight Flush",
}


def hand_name(score):
    if not score:
        return "Unknown"
    return HAND_RANK_NAMES_EN.get(score[0], "Unknown")


def evaluate_7cards(cards):
    """
    cards: Card 7장 리스트
    return: 최고 족보 점수 튜플
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

    if is_flush and is_straight:
        return (HAND_RANKS["STRAIGHT_FLUSH"], straight_high)

    if 4 in rank_counter.values():
        four = get_key_by_value(rank_counter, 4)
        kicker = max(r for r in ranks if r != four)
        return (HAND_RANKS["FOUR_KIND"], four, kicker)

    if sorted(rank_counter.values()) == [2, 3]:
        three = get_key_by_value(rank_counter, 3)
        pair = get_key_by_value(rank_counter, 2)
        return (HAND_RANKS["FULL_HOUSE"], three, pair)

    if is_flush:
        return (HAND_RANKS["FLUSH"], *ranks)

    if is_straight:
        return (HAND_RANKS["STRAIGHT"], straight_high)

    if 3 in rank_counter.values():
        three = get_key_by_value(rank_counter, 3)
        kickers = sorted([r for r in ranks if r != three], reverse=True)
        return (HAND_RANKS["THREE_KIND"], three, *kickers)

    pairs = [r for r, c in rank_counter.items() if c == 2]
    if len(pairs) == 2:
        high, low = sorted(pairs, reverse=True)
        kicker = max(r for r in ranks if r not in pairs)
        return (HAND_RANKS["TWO_PAIR"], high, low, kicker)

    if 2 in rank_counter.values():
        pair = get_key_by_value(rank_counter, 2)
        kickers = sorted([r for r in ranks if r != pair], reverse=True)
        return (HAND_RANKS["ONE_PAIR"], pair, *kickers)

    return (HAND_RANKS["HIGH_CARD"], *ranks)


def check_straight(ranks):
    unique = sorted(set(ranks), reverse=True)

    # A-5 스트레이트(휠) 처리
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
