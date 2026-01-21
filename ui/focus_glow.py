# ui/focus_glow.py
from PySide6.QtCore import QObject, QEvent
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QWidget, QGraphicsDropShadowEffect,
    QAbstractButton, QAbstractSpinBox, QComboBox, QLineEdit
)

class FocusGlowFilter(QObject):
    """
    포커스가 들어오면 glow(드랍섀도우)를 붙이고,
    포커스가 나가면 제거한다.
    """
    def __init__(self, color=None, blur=18):
        super().__init__()
        self.color = color or QColor(107, 114, 128, 180)  # 기본: 살짝 파란 glow
        self.blur = blur

    def eventFilter(self, obj, event):
        # 필요한 위젯만 적용(버튼/스핀/콤보/라인에딧)
        target = isinstance(obj, (QAbstractButton, QAbstractSpinBox, QComboBox, QLineEdit))
        if not target:
            return super().eventFilter(obj, event)

        # 특정 위젯은 예외 처리하고 싶으면:
        # obj.setProperty("skip_focus_glow", True)
        if obj.property("skip_focus_glow") is True:
            return super().eventFilter(obj, event)

        if event.type() == QEvent.FocusIn:
            eff = QGraphicsDropShadowEffect(obj)
            eff.setBlurRadius(self.blur)
            eff.setOffset(0, 0)  # glow 느낌
            eff.setColor(self.color)
            obj.setGraphicsEffect(eff)

        elif event.type() == QEvent.FocusOut:
            # 포커스 빠지면 glow 제거
            obj.setGraphicsEffect(None)

        return super().eventFilter(obj, event)


def install_focus_glow(root: QWidget, glow_filter: FocusGlowFilter):
    """
    root 이하의 입력/버튼 위젯들에 포커스 glow를 일괄 설치.
    """
    from PySide6.QtWidgets import QWidget  # local import

    for w in root.findChildren(QWidget):
        if isinstance(w, (QAbstractButton, QAbstractSpinBox, QComboBox, QLineEdit)):
            # 버튼도 포커스가 잡히게 (마우스 클릭에도 포커스 들어옴)
            w.setFocusPolicy(w.focusPolicy() or 0x2)  # Qt.StrongFocus 느낌 (간단 처리)
            w.installEventFilter(glow_filter)
