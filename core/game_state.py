from enum import Enum

class GameState(Enum):
    NEW_HAND = 1
    POST_BLINDS = 2
    DEAL_HOLE_CARDS = 3
    BETTING_PREFLOP = 4
    DEAL_FLOP = 5
    BETTING_FLOP = 6
    DEAL_TURN = 7
    BETTING_TURN = 8
    DEAL_RIVER = 9
    BETTING_RIVER = 10
    SHOWDOWN = 11
    END_HAND = 12
