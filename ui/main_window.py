from PySide6.QtWidgets import QMainWindow, QStackedWidget
from ui.poker_window import PokerWindow
from ui.home_screen import HomeScreen



class MainWindow(QMainWindow):
    def __init__(self, game, human_action):
        super().__init__()

        self.game = game
        self.human_action = human_action

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # 화면들
        self.home_screen = HomeScreen(self.start_game)
        self.poker_screen = PokerWindow(human_action)

        self.stack.addWidget(self.home_screen)
        self.stack.addWidget(self.poker_screen)

        self.stack.setCurrentWidget(self.home_screen)

    def update_cards(self, players, community_cards, reveal_ai=False):
        human = players[0]
        ai = players[1]

        self.poker_screen.show_player_cards(human.hole_cards)
        self.poker_screen.show_ai_cards(ai.hole_cards, reveal=reveal_ai)
        self.poker_screen.show_community_cards(community_cards)
        

    def start_game(self):
        print("🎮 GAME START")
        self.stack.setCurrentWidget(self.poker_screen)
            # 초기 칩/베팅 UI 업데이트
        self.poker_screen.update_chips(player_chips=2000, ai_chips=2000)
        self.poker_screen.update_bets(to_call=0, pot=0)

        self.game.start()   # 게임 루프 시작

    def update_bet_ui(self):
        if self.gui:
            # 현재 베팅 금액 = max(current_bet) - player.current_bet
            max_current = max(p.current_bet for p in self.players)
            to_call = max_current - self.players[0].current_bet
            self.gui.poker_screen.current_bet_label.setText(f"To Call: {to_call}")

            # 팟 총액
            self.gui.poker_screen.pot_label.setText(f"Pot: {self.pot.total_chips()}")
