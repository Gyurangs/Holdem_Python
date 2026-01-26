                   
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
                                                                              
        self.on_start_game = on_start_game
        self._glow = GlowFilter(color=QColor(90, 140, 255, 190), radius=20)
        self.init_ui()

    def init_ui(self):
                       
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f8f4ef, stop:0.45 #eef3f9, stop:1 #e9f7f0);
                color: #0f172a;
                font-family: "Montserrat", "Segoe UI";
            }

            QLabel#Title { font-size: 46px; font-weight: 900; letter-spacing: 0.4px; }
            QLabel#Sub { font-size: 14px; color: rgba(15,23,42,150); }

            QFrame#Card {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #ffffff, stop:1 #f6f8fb);
                border: 1px solid rgba(15,23,42,16);
                border-radius: 22px;
            }

            QLabel.h { font-size: 13px; color: rgba(15,23,42,150); font-weight: 800; }
            QLabel.v { font-size: 15px; font-weight: 900; color: #0f172a; }

            QComboBox, QSpinBox {
                background: #fdfdfb;
                border: 1px solid rgba(15,23,42,22);
                border-radius: 16px;
                padding: 12px 14px;
                color: #0f172a;
                min-height: 52px;
                font-size: 16px;
                font-weight: 800;
            }
            QComboBox:hover, QSpinBox:hover { border-color: rgba(15,23,42,40); }
            QComboBox:focus, QSpinBox:focus { border: 2px solid rgba(255,122,87,190); }

            QSpinBox::up-button, QSpinBox::down-button {
                width: 28px;
            }

            QPushButton#Start {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #ff8a3d, stop:1 #ff5d5d);
                color: #ffffff;
                border: none;
                border-radius: 18px;
                padding: 16px 22px;
                font-size: 19px;
                font-weight: 900;
                min-height: 64px;
                min-width: 320px;
            }
            QPushButton#Start:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #ff9a53, stop:1 #ff6d6d);
            }
            QPushButton#Start:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f37531, stop:1 #f35a5a);
            }

            QPushButton#Ghost {
                background: rgba(15,23,42,6);
                border: 1px solid rgba(15,23,42,12);
                border-radius: 14px;
                padding: 10px 14px;
                font-weight: 900;
                min-height: 46px;
            }
            QPushButton#Ghost:hover { background: rgba(15,23,42,10); }
            QPushButton#Ghost:pressed { background: rgba(15,23,42,16); }
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

                
        self.ai_count_spin = QSpinBox()
        self.ai_count_spin.setRange(1, 4)
        self.ai_count_spin.setValue(2)
        self.ai_count_spin.setFixedWidth(240)
        add_row("AI Players", self.ai_count_spin)

                       
        self.diff_combo = QComboBox()
        self.diff_combo.addItems(["Easy", "Normal", "Hard"])
        self.diff_combo.setCurrentText("Hard")
        self.diff_combo.setFixedWidth(240)
        add_row("Difficulty", self.diff_combo)

                      
        self.start_chips_spin = QSpinBox()
        self.start_chips_spin.setRange(100, 20000)
        self.start_chips_spin.setSingleStep(100)
        self.start_chips_spin.setValue(500)
        self.start_chips_spin.setFixedWidth(240)
        add_row("Start Chips", self.start_chips_spin)

                              
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
