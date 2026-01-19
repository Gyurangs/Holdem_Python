from players.player import Player

class AIPlayer(Player):
    def __init__(self, name, difficulty):
        super().__init__(name)
        self.difficulty = difficulty
