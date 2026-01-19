from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QSpinBox
)
from PySide6.QtWidgets import QMessageBox
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

CARD_WIDTH = 90
CARD_HEIGHT = 130


def card_to_filename(card):
    rank_map = {
        11: "J",
        12: "Q",
        13: "K",
        14: "A"
    }
    rank = rank_map.get(card.rank, str(card.rank))
    suit = card.suit
    return f"{rank}{suit}.png"


class PokerWindow(QWidget):
    def __init__(self, human_action, go_home_callback=None):
        super().__init__()
        self.human_action = human_action
        self.go_home_callback = go_home_callback

        self.setWindowTitle("Texas Hold'em")
        self.setFixedSize(1000, 700)

        # 카드 라벨 저장
        self.player_card_labels = []
        self.ai_card_labels = []
        self.community_card_labels = []
        
        # 칩 레이블
        self.player_chips_label = QLabel("Player: 0", self)
        self.ai_chips_label = QLabel("AI: 0", self)
        
        # 🔹 베팅/팟 라벨
        self.current_bet_label = QLabel("To Call: 0", self)
        self.pot_label = QLabel("Pot: 0", self)
        
        # 스타일
        for lbl in (self.player_chips_label, self.ai_chips_label):
            lbl.setStyleSheet("color:white; font-size:18px;")
        for lbl in (self.current_bet_label, self.pot_label):
            lbl.setStyleSheet("color:white; font-size:16px;")

        self.fold_btn = QPushButton("FOLD")
        self.call_btn = QPushButton("CALL")
        self.raise_btn = QPushButton("RAISE")
        self.allin_btn = QPushButton("ALL-IN")
        self.raise_spin = QSpinBox()
        self.raise_spin.setRange(10, 2000)
        self.raise_spin.setSingleStep(10)

        for b in (self.fold_btn, self.call_btn, self.raise_btn, self.allin_btn):
            b.setFixedSize(120,40)

        self.init_ui()
        self.connect_buttons()
    # ======================
    # UI 초기화
    # ======================
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        
        main_layout.addStretch()
        self.table = QLabel("Texas Hold'em")
        self.table.setAlignment(Qt.AlignCenter)
        self.table.setStyleSheet(
            "background-color:#0b6623;color:white;"
            "font-size:24px;padding:30px;border-radius:20px;"
        )
        main_layout.addWidget(self.table)
        main_layout.addStretch()

        # 칩 표시 영역
        chips_layout = QHBoxLayout()
        chips_layout.addWidget(self.player_chips_label)
        chips_layout.addStretch()
        chips_layout.addWidget(self.ai_chips_label)
        main_layout.addLayout(chips_layout)

        bet_layout = QHBoxLayout()
        bet_layout.addWidget(self.current_bet_label)
        bet_layout.addStretch()
        bet_layout.addWidget(self.pot_label)
        main_layout.addLayout(bet_layout)

        # 버튼 영역
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.fold_btn)
        btn_layout.addWidget(self.call_btn)
        btn_layout.addWidget(self.raise_spin)
        btn_layout.addWidget(self.raise_btn)
        btn_layout.addWidget(self.allin_btn)
        main_layout.addLayout(btn_layout)

        main_layout.addStretch()  # 하단 여백

    def connect_buttons(self):
            self.fold_btn.clicked.connect(lambda: self.human_action.set("fold"))
            self.call_btn.clicked.connect(lambda: self.human_action.set("call"))
            self.raise_btn.clicked.connect(
                lambda: self.human_action.set("raise", self.raise_spin.value())
            )
            self.allin_btn.clicked.connect(self.all_in)

    def all_in(self):
        amount = self.get_player_chips()
        self.human_action.set("raise", amount)

    # ======================
    # 칩 업데이트 함수
    # ======================
    def update_chips(self, player_chips, ai_chips):
        self.player_chips_label.setText(f"Player: {player_chips}")
        self.ai_chips_label.setText(f"AI: {ai_chips}")

    def update_bets(self, to_call, pot):
        self.current_bet_label.setText(f"To Call: {to_call}")
        self.pot_label.setText(f"Pot: {pot}")
        max_raise = max(to_call, self.get_player_chips())
        self.raise_spin.setMaximum(max_raise)

    def get_player_chips(self):
        text = self.player_chips_label.text()
        return int(text.split(":")[1].strip())
    
    # ======================
    # 카드 렌더링
    # ======================
    def clear_labels(self, labels):
        for lbl in labels:
            lbl.deleteLater()
        labels.clear()

    def show_player_cards(self, cards):
        self.clear_labels(self.player_card_labels)
        x, y = 430, 520

        for i, card in enumerate(cards):
            lbl = QLabel(self)
            lbl.setFixedSize(CARD_WIDTH, CARD_HEIGHT)

            pix = QPixmap(f"assets/cards/{card_to_filename(card)}")
            lbl.setPixmap(pix.scaled(
                CARD_WIDTH,
                CARD_HEIGHT,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            ))
            lbl.move(x + i * 100, y)
            lbl.show()
            self.player_card_labels.append(lbl)

    def show_ai_cards(self, cards, reveal=False):
        self.clear_labels(self.ai_card_labels)
        x, y = 430, 60

        for i, card in enumerate(cards):
            lbl = QLabel(self)
            lbl.setFixedSize(CARD_WIDTH, CARD_HEIGHT)

            if reveal:
                pix = QPixmap(f"assets/cards/{card_to_filename(card)}")
            else:
                pix = QPixmap("assets/cards/BACK.png")
            lbl.setPixmap(pix.scaled(
                CARD_WIDTH, 
                CARD_HEIGHT, 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            ))
            lbl.move(x + i * 100, y)
            lbl.show()
            self.ai_card_labels.append(lbl)

    def show_community_cards(self, cards):
        self.clear_labels(self.community_card_labels)
        y = 310
        start_x = 500 - (len(cards) * CARD_WIDTH)//2  # 중앙 정렬

        for i, card in enumerate(cards):
            lbl = QLabel(self)
            lbl.setFixedSize(CARD_WIDTH, CARD_HEIGHT)
            pix = QPixmap(f"assets/cards/{card_to_filename(card)}")
            lbl.setPixmap(pix.scaled(
                CARD_WIDTH, CARD_HEIGHT, Qt.KeepAspectRatio, Qt.SmoothTransformation
            ))
            lbl.move(start_x + i*CARD_WIDTH, y)
            lbl.show()
            self.community_card_labels.append(lbl)

    def show_game_over(self, winner_name):
        # 버튼 비활성화
        self.fold_btn.setDisabled(True)
        self.call_btn.setDisabled(True)
        self.raise_btn.setDisabled(True)
        self.allin_btn.setDisabled(True)
        self.raise_spin.setDisabled(True)

        msg = QMessageBox(self)
        msg.setWindowTitle("Game Over")
        msg.setText(f"{winner_name} wins! Game Over!")
        msg.setStandardButtons(QMessageBox.Ok)
        ret = msg.exec()
        if ret == QMessageBox.Ok and self.go_home_callback:
            self.go_home_callback()
