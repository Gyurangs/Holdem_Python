                  
from PySide6.QtCore import QObject, QEvent
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QWidget, QGraphicsDropShadowEffect,
    QAbstractButton, QAbstractSpinBox, QComboBox, QLineEdit
)

class FocusGlowFilter(QObject):
    """
    ???? ???? glow? ????, ??? ????.
    """
    def __init__(self, color=None, blur=18):
        super().__init__()
        self.color = color or QColor(107, 114, 128, 180)                  
        self.blur = blur

    def eventFilter(self, obj, event):

        target = isinstance(obj, (QAbstractButton, QAbstractSpinBox, QComboBox, QLineEdit))
        if not target:
            return super().eventFilter(obj, event)

        if obj.property("skip_focus_glow") is True:
            return super().eventFilter(obj, event)

        if event.type() == QEvent.FocusIn:
            eff = QGraphicsDropShadowEffect(obj)
            eff.setBlurRadius(self.blur)
            eff.setOffset(0, 0)           
            eff.setColor(self.color)
            obj.setGraphicsEffect(eff)

        elif event.type() == QEvent.FocusOut:

            obj.setGraphicsEffect(None)

        return super().eventFilter(obj, event)

def install_focus_glow(root: QWidget, glow_filter: FocusGlowFilter):
    """
    root ?? ??? glow ??? ????.
    """
    from PySide6.QtWidgets import QWidget                

    for w in root.findChildren(QWidget):
        if isinstance(w, (QAbstractButton, QAbstractSpinBox, QComboBox, QLineEdit)):
            # 클릭에도 포커스가 잡히도록 설정
            w.setFocusPolicy(w.focusPolicy() or 0x2)                             
            w.installEventFilter(glow_filter)
