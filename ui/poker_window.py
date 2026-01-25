                    
from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QSpinBox,
    QFrame, QMessageBox, QSizePolicy,
    QGraphicsOpacityEffect, QGridLayout
)
from PySide6.QtGui import QPixmap, QKeySequence, QColor, QShortcut
from PySide6.QtCore import Qt, QTimer, QPoint, QPropertyAnimation, QDateTime, QRect, QSize

from ui.fx import GlowFilter

BASE_CARD_W = 82
BASE_CARD_H = 118


def card_to_filename(card) -> str:
    rank_map = {11: "J", 12: "Q", 13: "K", 14: "A"}
    rank = rank_map.get(card.rank, str(card.rank))
    return f"{rank}{card.suit}.png"


class SeatWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.folded = False
        self._highlighted = False

        self.card_w = 64
        self.card_h = 92

        self._bubble_shown_at = 0
        self._bubble_min_hold_ms = 1400

        self._qss_normal = """
            QWidget {
                background: rgba(0,0,0,85);
                border: 1px solid rgba(255,255,255,60);
                border-radius: 16px;
            }
        """
        self._qss_folded = """
            QWidget {
                background: rgba(0,0,0,55);
                border: 1px solid rgba(255,255,255,35);
                border-radius: 16px;
            }
        """
        self._qss_highlight_border = """
            QWidget { border: 2px solid rgba(255,215,0,180); }
        """

                
        self.avatar = QLabel(self)
        self.avatar.setFixedSize(50, 50)
        self.avatar.setAlignment(Qt.AlignCenter)

        self.name_label = QLabel("Player", self)
        self.name_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.name_label.setStyleSheet("font-size: 13px; font-weight: 900; color: white;")

        self.chips_label = QLabel("Chips: 0", self)
        self.chips_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.chips_label.setStyleSheet("font-size: 11px; color: rgba(255,255,255,190);")

        top_info = QVBoxLayout()
        top_info.setSpacing(2)
        top_info.setContentsMargins(0, 0, 0, 0)
        top_info.addWidget(self.name_label)
        top_info.addWidget(self.chips_label)

        top_row = QHBoxLayout()
        top_row.setSpacing(10)
        top_row.setContentsMargins(10, 10, 10, 0)
        top_row.addWidget(self.avatar)
        top_row.addLayout(top_info)
        top_row.addStretch()
        self.info_row_widget = QWidget(self)
        self.info_row_widget.setLayout(top_row)

               
        self.card1 = QLabel(self)
        self.card2 = QLabel(self)
        for c in (self.card1, self.card2):
            c.setAlignment(Qt.AlignCenter)

        self._op1 = QGraphicsOpacityEffect(self.card1)
        self._op2 = QGraphicsOpacityEffect(self.card2)
        self.card1.setGraphicsEffect(self._op1)
        self.card2.setGraphicsEffect(self._op2)

        cards_row = QHBoxLayout()
        cards_row.setSpacing(8)
        cards_row.setContentsMargins(10, 6, 10, 8)
        cards_row.addWidget(self.card1)
        cards_row.addWidget(self.card2)
        self.cards_row_widget = QWidget(self)
        self.cards_row_widget.setLayout(cards_row)

        self.action_label = QLabel("—", self)
        self.action_label.setAlignment(Qt.AlignCenter)
        self.action_label.setStyleSheet("font-size: 12px; font-weight: 900; color: rgba(255,255,255,210);")
        self.action_label.setContentsMargins(0, 0, 0, 10)

        self._side_info = False
        self._grid = QGridLayout(self)
        self._grid.setContentsMargins(0, 0, 0, 0)
        self._grid.setSpacing(0)
        self._apply_layout()

        self._apply_style()
        self.set_card_size(self.card_w, self.card_h)
        self.set_cards(None, None, back=True)
        self._set_card_dimmed(False)

                                                                   
        self.bubble = QLabel(self.parent())
        self.bubble.setWordWrap(True)
        self.bubble.setVisible(False)
        self.bubble.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.bubble.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.bubble.setStyleSheet("""
            QLabel {
                background: rgba(0,0,0,175);
                color: white;
                border: 1px solid rgba(255,255,255,55);
                border-radius: 12px;
                padding: 8px 10px;
                font-size: 12px;
                font-weight: 900;
            }
        """)

                                                                     
        self._bubble_op = QGraphicsOpacityEffect(self.bubble)
        self.bubble.setGraphicsEffect(self._bubble_op)
        self._bubble_anim = QPropertyAnimation(self._bubble_op, b"opacity", self)
        self._bubble_anim.setDuration(220)

        self._bubble_anim_mode = None                 
        self._bubble_anim.finished.connect(self._on_bubble_anim_finished)

        self._bubble_timer = QTimer(self)
        self._bubble_timer.setSingleShot(True)
        self._bubble_timer.timeout.connect(self._hide_bubble)

        self.destroyed.connect(lambda *_: self.bubble.deleteLater())
    
    def _on_bubble_anim_finished(self):
        if self._bubble_anim_mode == "out":
            self.bubble.setVisible(False)
        self._bubble_anim_mode = None
    
    def _apply_style(self):
        base = self._qss_folded if self.folded else self._qss_normal
        self.setStyleSheet(base + (self._qss_highlight_border if self._highlighted else ""))

    def _apply_layout(self):
        while self._grid.count():
            item = self._grid.takeAt(0)
            if item.widget():
                item.widget().setParent(self)

        if self._side_info:
            self._grid.addWidget(self.cards_row_widget, 0, 0, 1, 1)
            self._grid.addWidget(self.info_row_widget, 0, 1, 1, 1)
            self._grid.addWidget(self.action_label, 1, 0, 1, 2, alignment=Qt.AlignCenter)
            self._grid.setColumnStretch(0, 2)
            self._grid.setColumnStretch(1, 1)
        else:
            self._grid.addWidget(self.info_row_widget, 0, 0, 1, 2)
            self._grid.addWidget(self.cards_row_widget, 1, 0, 1, 2)
            self._grid.addWidget(self.action_label, 2, 0, 1, 2, alignment=Qt.AlignCenter)
            self._grid.setColumnStretch(0, 1)
            self._grid.setColumnStretch(1, 1)

    def set_side_info(self, side: bool):
        side = bool(side)
        if self._side_info == side:
            return
        self._side_info = side
        self._apply_layout()

    def preferred_size(self) -> QSize:
        if self._side_info:
            w = self.card_w * 2 + 72 + 150
            h = max(self.card_h + 40, 120)
            return QSize(w, h)
        return QSize(self.card_w * 2 + 72, self.card_h + 118)

    def _set_card_dimmed(self, dim: bool):
        self._op1.setOpacity(0.28 if dim else 1.0)
        self._op2.setOpacity(0.28 if dim else 1.0)

    def set_card_size(self, w: int, h: int):
        self.card_w, self.card_h = w, h
        self.card1.setFixedSize(w, h)
        self.card2.setFixedSize(w, h)

    def set_avatar_by_name(self, name: str):
        key = name.lower()
        fname = "assets/avatars/human.png" if key == "human" else f"assets/avatars/{key}.png"
        pix = QPixmap(fname)
        if pix.isNull():
            self.avatar.setStyleSheet("""
                QLabel {
                    background: rgba(255,255,255,28);
                    border: 1px solid rgba(255,255,255,55);
                    border-radius: 25px;
                    color: white;
                    font-size: 22px;
                }
            """)
            self.avatar.setPixmap(QPixmap())
            self.avatar.setText("🙂" if key == "human" else "🤖")
            return
        self.avatar.setStyleSheet("background: transparent; border: none;")
        self.avatar.setText("")
        self.avatar.setPixmap(pix.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def set_info(self, name: str, chips: int, action_text: str = "—", folded: bool = False):
        self.name_label.setText(name)
        self.chips_label.setText(f"Chips: {chips}")
        self.set_avatar_by_name(name)

        self.folded = bool(folded)
        if self.folded:
            self.action_label.setText("FOLD")
            self.set_cards(None, None, back=True)
            self._set_card_dimmed(True)
        else:
            self.action_label.setText(action_text or "—")
            self._set_card_dimmed(False)

        self._apply_style()

    def set_action_text(self, text: str):
        self.action_label.setText("FOLD" if self.folded else (text or "—"))

    def set_highlight(self, on: bool):
        self._highlighted = bool(on)
        self._apply_style()

    def say(self, text: str, ms: int = 2200):
        if not text:
            return

        now = int(QDateTime.currentMSecsSinceEpoch())
        if self.bubble.isVisible():
            elapsed = now - int(self._bubble_shown_at or now)
            if elapsed < self._bubble_min_hold_ms:
                ms = max(ms, self._bubble_min_hold_ms)

        self._bubble_shown_at = now

        self._bubble_timer.stop()
        try:
            self._bubble_anim.stop()
        except Exception:
            pass

        self.bubble.setText(text)
        self.bubble.adjustSize()
        self._position_bubble()
        self.bubble.setVisible(True)
        self.bubble.raise_()

        self._bubble_anim_mode = "in"
        self._bubble_op.setOpacity(0.0)
        self._bubble_anim.setStartValue(0.0)
        self._bubble_anim.setEndValue(1.0)
        self._bubble_anim.start()

        self._bubble_timer.start(int(ms))

    def _hide_bubble(self):
        if not self.bubble.isVisible():
            return

        self._bubble_timer.stop()
        try:
            self._bubble_anim.stop()
        except Exception:
            pass

        start_op = float(self._bubble_op.opacity())
        if start_op <= 0.02:
            self.bubble.setVisible(False)
            self._bubble_anim_mode = None
            return

        self._bubble_anim_mode = "out"
        self._bubble_anim.setStartValue(start_op)
        self._bubble_anim.setEndValue(0.0)
        self._bubble_anim.start()

    def _position_bubble(self):
        parent = self.parent()
        if parent is None:
            return
        top_left = self.mapToParent(QPoint(0, 0))
        bx = top_left.x() + 60
        by = top_left.y() - self.bubble.height() - 8

        margin = 10
        bx = max(margin, min(bx, parent.width() - self.bubble.width() - margin))
        by = max(margin, min(by, parent.height() - self.bubble.height() - margin))
        self.bubble.move(bx, by)

    def moveEvent(self, event):
        super().moveEvent(event)
        if self.bubble.isVisible():
            self._position_bubble()

    def set_cards(self, filename_a: str | None, filename_b: str | None, back: bool):
        if back:
            self._set_pix(self.card1, None, back=True)
            self._set_pix(self.card2, None, back=True)
        else:
            self._set_pix(self.card1, filename_a, back=False)
            self._set_pix(self.card2, filename_b, back=False)

    def _set_pix(self, lbl: QLabel, filename: str | None, back: bool):
        pix = QPixmap("assets/cards/BACK.png") if back else QPixmap(f"assets/cards/{filename}") if filename else QPixmap()
        if pix.isNull():
            pix = QPixmap("assets/cards/BACK.png")
        if pix.isNull():
            lbl.setPixmap(QPixmap())
            lbl.setText("")
            return
        lbl.setPixmap(pix.scaled(self.card_w, self.card_h, Qt.KeepAspectRatio, Qt.SmoothTransformation))


class PokerWindow(QWidget):
    def __init__(self, human_action, go_home_callback=None):
        super().__init__()
        self.human_action = human_action
        self.go_home_callback = go_home_callback

        self.setMinimumSize(1000, 700)

        self.num_players = 2
        self.card_w = BASE_CARD_W
        self.card_h = BASE_CARD_H

        self.seats: list[SeatWidget] = []
        self.community_labels: list[QLabel] = []
        self.community_visible_count = 0
        self.name_to_seat_index: dict[str, int] = {}
        self.seat_actions: dict[str, str] = {}

        self._current_player_name = None
        self._glow = GlowFilter(color=QColor(90, 140, 255, 190), radius=18)

        self._build_ui()
        self.connect_buttons()
        self._install_shortcuts()
        self._install_glow()

        self.configure_table(2)
        self.reset_ui_for_new_game()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.table_frame = QFrame()
        self.table_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table_frame.setStyleSheet("QFrame { background-color: #0b6623; }")
        root.addWidget(self.table_frame, stretch=1)

        self.table_surface = QWidget(self.table_frame)
        self.table_surface.setGeometry(0, 0, self.table_frame.width(), self.table_frame.height())

                             
        self.community_labels = []
        for _ in range(5):
            lbl = QLabel(self.table_surface)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setVisible(False)
            self.community_labels.append(lbl)

                         
        self.hud = QFrame(self.table_surface)
        self.hud.setStyleSheet("""
            QFrame {
                background: rgba(0,0,0,135);
                border: 1px solid rgba(255,255,255,45);
                border-radius: 14px;
            }
            QLabel { color: white; font-weight: 900; }
            QLabel.small { color: rgba(255,255,255,190); font-weight: 700; font-size: 12px; }
        """)
        hud_layout = QVBoxLayout(self.hud)
        hud_layout.setContentsMargins(12, 10, 12, 10)
        hud_layout.setSpacing(6)

        self.hud_status = QLabel("Ready")
        self.hud_status.setProperty("class", "small")
        self.hud_pot = QLabel("Pot: 0")
        self.hud_tocall = QLabel("To Call: 0")
        self.hud_blinds = QLabel("Blinds: 10/20")
        self.hud_blinds.setProperty("class", "small")

        hud_layout.addWidget(self.hud_status)
        hud_layout.addWidget(self.hud_pot)
        hud_layout.addWidget(self.hud_tocall)
        hud_layout.addWidget(self.hud_blinds)

                                      
        self.action_panel = QFrame(self.table_surface)
        self.action_panel.setStyleSheet("""
            QFrame {
                background: rgba(0,0,0,155);
                border: 1px solid rgba(255,255,255,45);
                border-radius: 16px;
            }
            QPushButton {
                background-color: rgba(255,255,255,18);
                border: 1px solid rgba(255,255,255,45);
                padding: 10px 14px;
                border-radius: 12px;
                font-weight: 900;
                color: white;
                min-width: 100px;
                min-height: 44px;
            }
            QPushButton:hover { background-color: rgba(255,255,255,26); }
            QPushButton:pressed { background-color: rgba(255,255,255,14); }
            QPushButton:disabled {
                background-color: rgba(255,255,255,10);
                color: rgba(255,255,255,90);
                border-color: rgba(255,255,255,25);
            }
            QSpinBox {
                background-color: rgba(0,0,0,120);
                border: 1px solid rgba(255,255,255,45);
                border-radius: 12px;
                padding: 8px 10px;
                color: white;
                min-width: 100px;
                min-height: 44px;
                font-weight: 900;
            }
            QSpinBox:hover { border-color: rgba(255,255,255,65); }
            QSpinBox:focus { border: 2px solid rgba(90,140,255,180); }
        """)
        action_layout = QHBoxLayout(self.action_panel)
        action_layout.setContentsMargins(12, 10, 12, 10)
        action_layout.setSpacing(10)

        self.fold_btn = QPushButton("FOLD")
        self.call_btn = QPushButton("CALL")
        self.raise_spin = QSpinBox()
        self.raise_spin.setRange(10, 2000)
        self.raise_spin.setSingleStep(10)
        self.raise_btn = QPushButton("RAISE")
        self.allin_btn = QPushButton("ALL-IN")

        action_layout.addWidget(self.fold_btn)
        action_layout.addWidget(self.call_btn)
        action_layout.addWidget(self.raise_spin)
        action_layout.addWidget(self.raise_btn)
        action_layout.addWidget(self.allin_btn)

    def _install_glow(self):
                           
        for w in (self.fold_btn, self.call_btn, self.raise_spin, self.raise_btn, self.allin_btn):
            w.installEventFilter(self._glow)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.table_surface.setGeometry(0, 0, self.table_frame.width(), self.table_frame.height())
        self._layout_overlay()
        self._layout_all()

    def _layout_overlay(self):
        w = self.table_surface.width()
        h = self.table_surface.height()

        self.hud.adjustSize()
        self.hud.move(w - self.hud.width() - 16, 16)

        panel_w = min(720, w - 40)
        self.action_panel.setFixedWidth(panel_w)
        self.action_panel.adjustSize()
        self.action_panel.move(w // 2 - self.action_panel.width() // 2, h - self.action_panel.height() - 14)

    def configure_table(self, num_players: int):
        self.num_players = max(2, min(5, int(num_players)))

        scale = max(0.70, 1.0 - 0.10 * (self.num_players - 2))
        if self.num_players == 5:
            scale += 0.03
        self.card_w = int(BASE_CARD_W * scale)
        self.card_h = int(BASE_CARD_H * scale)

        for s in self.seats:
            s.setParent(None)
            s.deleteLater()
        self.seats.clear()

        for i in range(self.num_players):
            seat = SeatWidget(self.table_surface)
            seat.set_card_size(self.card_w, self.card_h)
            seat.set_side_info(i == 0)
            seat.setFixedSize(seat.preferred_size())
            seat.show()
            self.seats.append(seat)

        for lbl in self.community_labels:
            lbl.setFixedSize(self.card_w, self.card_h)

        self._layout_overlay()
        self._layout_all()

        if self._current_player_name:
            self.highlight_current_seat(self._current_player_name)

    def _layout_all(self):
        self._layout_seats()
        self._layout_community_slots(self.community_visible_count)

    def _layout_seats(self):
        if not self.seats:
            return

        w = self.table_surface.width()
        h = self.table_surface.height()

        anchors = [(0.50, 0.74), (0.30, 0.14), (0.70, 0.14), (0.12, 0.52), (0.88, 0.52)]
        anchors = [anchors[0]] + anchors[1:][: self.num_players - 1]

        margin = 12
        for i, (seat, (ax, ay)) in enumerate(zip(self.seats, anchors)):
            x = int(w * ax - seat.width() / 2)
            if i == 0 and self.action_panel.isVisible():
                panel_h = self.action_panel.height()
                y = h - panel_h - seat.height() - 18
            else:
                y = int(h * ay - seat.height() / 2)
            x = max(margin, min(x, w - seat.width() - margin))
            y = max(margin, min(y, h - seat.height() - margin))
            seat.move(x, y)

    def _layout_community_slots(self, visible_count: int):
        w = self.table_surface.width()
        h = self.table_surface.height()

        cnt = max(0, min(5, visible_count))
        if cnt == 0:
            for lbl in self.community_labels:
                lbl.setVisible(False)
            return

        gap = max(10, int(self.card_w * 0.14))
        total_w = self.card_w * cnt + gap * (cnt - 1)
        start_x = int(w / 2 - total_w / 2)
        y = int(h * 0.42 - self.card_h / 2)

        for i, lbl in enumerate(self.community_labels):
            if i < cnt:
                final_x = start_x + i * (self.card_w + gap)
                final_rect = QRect(final_x, y, self.card_w, self.card_h)
                if not lbl.isVisible():
                    lbl.setVisible(True)
                    lbl.setGeometry(final_rect.adjusted(self.card_w // 4, self.card_h // 4, -self.card_w // 4, -self.card_h // 4))
                    self._animate_community_card(lbl, final_rect)
                else:
                    lbl.move(final_x, y)
            else:
                lbl.setVisible(False)

    def connect_buttons(self):
        self.fold_btn.clicked.connect(lambda: self.human_action.set("fold"))
        self.call_btn.clicked.connect(lambda: self.human_action.set("call"))
        self.raise_btn.clicked.connect(lambda: self.human_action.set("raise", self.raise_spin.value()))
        self.allin_btn.clicked.connect(self.all_in)

    def _install_shortcuts(self):
        QShortcut(QKeySequence("F"), self, activated=lambda: self.fold_btn.click())
        QShortcut(QKeySequence("C"), self, activated=lambda: self.call_btn.click())
        QShortcut(QKeySequence("R"), self, activated=lambda: self.raise_btn.click())
        QShortcut(QKeySequence("A"), self, activated=lambda: self.allin_btn.click())

    def highlight_current_seat(self, player_name: str):
        for s in self.seats:
            s.set_highlight(False)
        idx = self.name_to_seat_index.get(player_name)
        if idx is not None:
            self.seats[idx].set_highlight(True)
            self._current_player_name = player_name

    def set_actions_enabled(self, enabled: bool):
        self.fold_btn.setEnabled(enabled)
        self.call_btn.setEnabled(enabled)
        self.raise_btn.setEnabled(enabled)
        self.allin_btn.setEnabled(enabled)
        self.raise_spin.setEnabled(enabled)

    def all_in(self):
        amount = self.get_player_chips()
        self.human_action.set("raise", amount)

    def set_status_text(self, text: str):
        self.hud_status.setText(text)

    def reset_ui_for_new_game(self, players=None):
        self.set_actions_enabled(True)
        self.seat_actions.clear()
        self.set_status_text("Ready")
        self._current_player_name = None

        self.community_visible_count = 0
        for lbl in self.community_labels:
            lbl.setVisible(False)

        for i, seat in enumerate(self.seats):
            name = "Human" if i == 0 else f"AI{i}"
            seat.set_info(name, 1000, "—", folded=False)
            seat.set_cards(None, None, back=True)
            seat.set_highlight(False)

        self.hud_pot.setText("Pot: 0")
        self.hud_tocall.setText("To Call: 0")

    def update_chips(self, player_chips: int, ai_chips: int):
        pass

    def update_bets(self, to_call: int, pot: int, sb: int | None = None, bb: int | None = None):
        self.hud_tocall.setText(f"To Call: {to_call}")
        self.hud_pot.setText(f"Pot: {pot}")
        if sb is not None and bb is not None:
            self.hud_blinds.setText(f"Blinds: {sb}/{bb}")

        player_chips = self.get_player_chips()
        base = int(bb) if bb is not None else 10
        min_raise = max(base, to_call)
        self.raise_spin.setMinimum(min_raise)
        self.raise_spin.setMaximum(max(min_raise, player_chips))

    def update_cards(self, players, community_cards, reveal_ai=False):
        if len(players) != self.num_players:
            self.configure_table(len(players))

        self.name_to_seat_index = {p.name: i for i, p in enumerate(players)}

        for i, p in enumerate(players):
            seat = self.seats[i]
            default_action = "ALL-IN" if getattr(p, "all_in", False) else "—"
            action_text = self.seat_actions.get(p.name, default_action)

            seat.set_info(
                name=p.name,
                chips=p.chips,
                action_text=action_text,
                folded=getattr(p, "folded", False)
            )

            if getattr(p, "folded", False):
                continue

            a = b = None
            if len(getattr(p, "hole_cards", [])) >= 2:
                a = card_to_filename(p.hole_cards[0])
                b = card_to_filename(p.hole_cards[1])

            if i == 0:
                seat.set_cards(a, b, back=False)
            else:
                seat.set_cards(a, b, back=not bool(reveal_ai))

        self.community_visible_count = min(5, len(community_cards))
        for i in range(self.community_visible_count):
            self._set_face(self.community_labels[i], card_to_filename(community_cards[i]))
        self._layout_community_slots(self.community_visible_count)

        if self._current_player_name:
            self.highlight_current_seat(self._current_player_name)

    def append_action_log(self, text: str):
        self._apply_action_to_seat(text)

    def _apply_action_to_seat(self, log_text: str):
        if not log_text:
            return

        parts = log_text.strip().split()
        if not parts:
            return

        name = parts[0].rstrip(":")
        rest = " ".join(parts[1:]).strip()

        idx = self.name_to_seat_index.get(name)
        if idx is None:
            return

        show = rest
        show = show.replace("CALLS", "CALL").replace("CHECKS", "CHECK").replace("FOLDS", "FOLD")
        show = show.replace("RAISES TO", "RAISE").replace("RAISES", "RAISE")
        show = show.replace("POSTS SB", "SB").replace("POSTS BB", "BB")

        self.seat_actions[name] = show
        seat = self.seats[idx]
        seat.set_action_text(show)
        seat.say(show)

    def get_player_chips(self) -> int:
        if self.seats:
            txt = self.seats[0].chips_label.text()
            try:
                return int(txt.split(":")[1].strip())
            except Exception:
                return 0
        return 0

    def show_game_over(self, winner_name: str):
        self.set_actions_enabled(False)
        msg = QMessageBox(self)
        msg.setWindowTitle("Game Over")
        msg.setText(f"{winner_name} wins!\nReturn to Home?")
        msg.setStandardButtons(QMessageBox.Ok)
        ret = msg.exec()
        if ret == QMessageBox.Ok and self.go_home_callback:
            self.go_home_callback()

    def _set_face(self, lbl: QLabel, filename: str):
        pix = QPixmap(f"assets/cards/{filename}")
        if pix.isNull():
            pix = QPixmap("assets/cards/BACK.png")
        if pix.isNull():
            lbl.setPixmap(QPixmap())
            lbl.setText("")
            return
        lbl.setPixmap(pix.scaled(self.card_w, self.card_h, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def _animate_community_card(self, lbl: QLabel, final_rect: QRect):
        try:
            eff = lbl.graphicsEffect()
            if not isinstance(eff, QGraphicsOpacityEffect):
                eff = QGraphicsOpacityEffect(lbl)
                lbl.setGraphicsEffect(eff)
            eff.setOpacity(0.0)

            anim_op = QPropertyAnimation(eff, b"opacity", self)
            anim_op.setDuration(260)
            anim_op.setStartValue(0.0)
            anim_op.setEndValue(1.0)

            start_rect = final_rect.adjusted(self.card_w // 4, self.card_h // 4, -self.card_w // 4, -self.card_h // 4)
            anim_geo = QPropertyAnimation(lbl, b"geometry", self)
            anim_geo.setDuration(260)
            anim_geo.setStartValue(start_rect)
            anim_geo.setEndValue(final_rect)

            anim_op.start()
            anim_geo.start()
        except Exception:
            lbl.setGeometry(final_rect)
            eff = lbl.graphicsEffect()
            if isinstance(eff, QGraphicsOpacityEffect):
                eff.setOpacity(1.0)
