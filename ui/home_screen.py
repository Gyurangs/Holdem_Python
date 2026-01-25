# ui/home_screen.py
from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QSpinBox, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from ui.fx import GlowFilter


class HomeScreen(QWidget):
    def __init__(self, on_start_game):
        super().__init__()
        # on_start_game(ai_count:int, difficulty:str, start_chips:int, bb:int)
        self.on_start_game = on_start_game
        self._glow = GlowFilter(color=QColor(90, 140, 255, 190), radius=20)
        self.init_ui()

    def init_ui(self):
        # 화이트/그레이 모던 테마
        self.setStyleSheet("""
            QWidget { background: #f4f6f9; color: #111827; font-family: Arial; }

            QLabel#Title { font-size: 44px; font-weight: 900; letter-spacing: 0.2px; }
            QLabel#Sub { font-size: 14px; color: rgba(17,24,39,150); }

            QFrame#Card {
                background: #ffffff;
                border: 1px solid rgba(17,24,39,18);
                border-radius: 20px;
            }

            QLabel.h { font-size: 14px; color: rgba(17,24,39,160); font-weight: 800; }
            QLabel.v { font-size: 15px; font-weight: 900; color: #111827; }

            QComboBox, QSpinBox {
                background: #ffffff;
                border: 1px solid rgba(17,24,39,22);
                border-radius: 14px;
                padding: 10px 12px;
                color: #111827;
                min-height: 46px;
                font-size: 15px;
                font-weight: 800;
            }
            QComboBox:hover, QSpinBox:hover { border-color: rgba(17,24,39,35); }
            QComboBox:focus, QSpinBox:focus { border: 2px solid rgba(90,140,255,180); }

            QPushButton#Start {
                background: #111827;
                color: #ffffff;
                border: none;
                border-radius: 16px;
                padding: 14px 18px;
                font-size: 18px;
                font-weight: 900;
                min-height: 56px;
                min-width: 300px;
            }
            QPushButton#Start:hover { background: #1f2937; }
            QPushButton#Start:pressed { background: #0b1220; }

            QPushButton#Ghost {
                background: rgba(17,24,39,6);
                border: 1px solid rgba(17,24,39,12);
                border-radius: 14px;
                padding: 10px 14px;
                font-weight: 900;
                min-height: 46px;
            }
            QPushButton#Ghost:hover { background: rgba(17,24,39,10); }
            QPushButton#Ghost:pressed { background: rgba(17,24,39,16); }
        """)

        root = QVBoxLayout(self)
        root.setAlignment(Qt.AlignCenter)
        root.setSpacing(18)
        root.setContentsMargins(24, 24, 24, 24)

        title = QLabel("Texas Hold'em")
        title.setObjectName("Title")
        title.setAlignment(Qt.AlignCenter)

        sub = QLabel("Set players & blinds, then start.")
        sub.setObjectName("Sub")
        sub.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setObjectName("Card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(22, 20, 22, 18)
        card_layout.setSpacing(14)

        def add_row(label_text: str, widget):
            row = QHBoxLayout()
            row.setSpacing(14)
            lbl = QLabel(label_text)
            lbl.setProperty("class", "h")
            lbl.setFixedWidth(170)
            row.addWidget(lbl)
            row.addWidget(widget)
            row.addStretch()
            card_layout.addLayout(row)

        # AI 인원수
        self.ai_count_spin = QSpinBox()
        self.ai_count_spin.setRange(1, 4)
        self.ai_count_spin.setValue(1)
        self.ai_count_spin.setFixedWidth(240)
        add_row("AI Players", self.ai_count_spin)

        # 난이도 기본 Normal
        self.diff_combo = QComboBox()
        self.diff_combo.addItems(["Easy", "Normal", "Hard"])
        self.diff_combo.setCurrentText("Normal")
        self.diff_combo.setFixedWidth(240)
        add_row("Difficulty", self.diff_combo)

        # 시드머니 기본 1000
        self.start_chips_spin = QSpinBox()
        self.start_chips_spin.setRange(100, 20000)
        self.start_chips_spin.setSingleStep(100)
        self.start_chips_spin.setValue(1000)
        self.start_chips_spin.setFixedWidth(240)
        add_row("Start Chips", self.start_chips_spin)

        # BB만 설정, SB = BB/2 자동
        self.bb_spin = QSpinBox()
        self.bb_spin.setRange(2, 20000)
        self.bb_spin.setSingleStep(10)
        self.bb_spin.setValue(20)
        self.bb_spin.setFixedWidth(240)
        add_row("Big Blind (BB)", self.bb_spin)

        self.sb_value = QLabel("")
        self.sb_value.setProperty("class", "v")
        self.sb_value.setFixedWidth(240)
        add_row("Small Blind (Auto)", self.sb_value)

        self.bb_spin.valueChanged.connect(self._sync_sb_from_bb)
        self._sync_sb_from_bb()

        # 버튼 영역
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        start_btn = QPushButton("GAME START")
        start_btn.setObjectName("Start")
        start_btn.clicked.connect(self._on_click_start)

        btn_row.addStretch()
        btn_row.addWidget(start_btn)
        btn_row.addStretch()

        root.addWidget(title)
        root.addWidget(sub)
        root.addSpacing(8)
        root.addWidget(card)
        root.addSpacing(10)
        root.addLayout(btn_row)

        # glow 적용(Home)
        for w in (self.ai_count_spin, self.diff_combo, self.start_chips_spin, self.bb_spin, start_btn):
            w.installEventFilter(self._glow)

    def _sync_sb_from_bb(self):
        bb = int(self.bb_spin.value())
        if bb % 2 != 0:
            bb += 1
            self.bb_spin.setValue(bb)
        sb = max(1, bb // 2)
        self.sb_value.setText(str(sb))

    def _on_click_start(self):
        ai_count = int(self.ai_count_spin.value())
        difficulty = self.diff_combo.currentText()
        start_chips = int(self.start_chips_spin.value())
        bb = int(self.bb_spin.value())
        if bb % 2 != 0:
            bb += 1
        self.on_start_game(ai_count, difficulty, start_chips, bb)
