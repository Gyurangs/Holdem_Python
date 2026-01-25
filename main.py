import sys
from PySide6.QtWidgets import QApplication

from core.game import HoldemGame
from core.human_action import HumanAction
from ui.main_window import MainWindow


app = QApplication(sys.argv)

human_action = HumanAction()
game = HoldemGame(human_action)

window = MainWindow(game, human_action)
game.gui = window

window.show()



sys.exit(app.exec())
