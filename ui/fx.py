          
from __future__ import annotations

from PySide6.QtCore import QObject, QEvent
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGraphicsDropShadowEffect

class GlowFilter(QObject):
    """
    ???/?? ? glow? ??, ???? ??.
    Qt?? effect ??? ? ??? ? ? ?? ?? ?? ????.
    """
    def __init__(self, color: QColor | None = None, radius: int = 18, offset: int = 0):
        super().__init__()
        self.color = color or QColor(90, 140, 255, 190)
        self.radius = int(radius)
        self.offset = int(offset)

    def _turn_on(self, w):
        if getattr(w, "_glow_on", False):
            return
        eff = QGraphicsDropShadowEffect(w)
        eff.setBlurRadius(self.radius)
        eff.setOffset(self.offset, self.offset)
        eff.setColor(self.color)
        w.setGraphicsEffect(eff)
        w._glow_on = True

    def _turn_off(self, w):
        if not getattr(w, "_glow_on", False):
            return

        w.setGraphicsEffect(None)
        w._glow_on = False

    def eventFilter(self, obj, event):
        t = event.type()

        if t in (QEvent.FocusIn, QEvent.Enter):
            self._turn_on(obj)

        elif t in (QEvent.FocusOut, QEvent.Leave):
            keep = False
            try:
                keep = obj.hasFocus() or obj.underMouse()
            except Exception:
                keep = False
            if not keep:
                self._turn_off(obj)

        return False
