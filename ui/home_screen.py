from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt


class HomeScreen(QWidget):
    def __init__(self, on_start_game):
        super().__init__()
        self.on_start_game = on_start_game
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("Texas Hold'em")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 36px; font-weight: bold;")

        start_btn = QPushButton("GAME START")
        start_btn.setFixedSize(200, 60)
        start_btn.setStyleSheet("font-size: 20px;")
        start_btn.clicked.connect(self.on_start_game)

        layout.addWidget(title)
        layout.addSpacing(40)
        layout.addWidget(start_btn)

        self.setLayout(layout)
