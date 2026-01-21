# ui/main_window.py
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

        self.home_screen = HomeScreen(self.start_game)
        self.poker_screen = PokerWindow(human_action, go_home_callback=self.go_home)

        self.stack.addWidget(self.home_screen)
        self.stack.addWidget(self.poker_screen)
        self.stack.setCurrentWidget(self.home_screen)

    def go_home(self):
        self.game.stop()
        self.stack.setCurrentWidget(self.home_screen)

    def update_cards(self, players, community_cards, reveal_ai=False):
        self.poker_screen.update_cards(players, community_cards, reveal_ai=reveal_ai)

    def show_action(self, text: str):
        self.poker_screen.append_action_log(text)

    # ✅ HomeScreen이 넘기는 포맷과 100% 동일
    def start_game(self, ai_count: int, difficulty: str, start_chips: int, bb: int):
        print("🎮 GAME START", ai_count, difficulty, start_chips, "BB", bb)

        # ✅ 게임 설정(= SB는 내부에서 BB/2로 자동)
        self.game.configure(ai_count=ai_count, difficulty=difficulty, start_chips=start_chips, bb=bb)

        # ✅ UI 초기화/좌석 재구성
        self.poker_screen.configure_table(len(self.game.players))
        self.poker_screen.reset_ui_for_new_game(self.game.players)
        self.update_cards(self.game.players, self.game.community_cards, reveal_ai=False)
        self.poker_screen.update_bets(to_call=0, pot=0, sb=self.game.small_blind, bb=self.game.big_blind)
        self.poker_screen.set_status_text("Ready")

        self.stack.setCurrentWidget(self.poker_screen)
        self.game.start()
