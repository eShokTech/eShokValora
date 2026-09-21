from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, pyqtProperty
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QGraphicsDropShadowEffect,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
)

from app.ui.theme import (
    ACCENT,
    ACCENT_DARK,
    ACCENT_SOFT,
    BORDER,
    MUTED,
    SURFACE,
    SURFACE_SOFT,
    TEXT,
    SUCCESS,
    WARNING,
    BLACK,
)


class MatteGlassFrame(QFrame):
    def __init__(self, parent=None, accent=False):
        super().__init__(parent)
        self.setObjectName("MatteGlassAccent" if accent else "MatteGlass")
        border = ACCENT_DARK if accent else BORDER
        self.setStyleSheet(
            f"QFrame#{self.objectName()} {{"
            f"background:rgba(255,255,255,238);"
            f"border:1px solid {border};"
            f"border-radius:20px;"
            f"}}"
        )
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(22)
        shadow.setOffset(0, 5)
        shadow.setColor(QColor(16, 23, 19, 24))
        self.setGraphicsEffect(shadow)


class MatteCard(MatteGlassFrame):
    pass


class SectionTitle(QLabel):
    def __init__(self, title, subtitle="", parent=None):
        super().__init__(title, parent)
        self.setStyleSheet(f"color:{TEXT}; font-size:18px; font-weight:650; border:0;")
        if subtitle:
            self.setToolTip(subtitle)


class FieldLabel(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(f"color:{MUTED}; font-size:11px; font-weight:600; border:0;")


class MatteInput(QLineEdit):
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setMinimumHeight(42)
        self.setStyleSheet(
            f"QLineEdit {{background:{SURFACE}; color:{TEXT}; border:1px solid {BORDER}; "
            f"border-radius:12px; padding:0 13px; font-size:13px;}} "
            f"QLineEdit:focus {{background:{SURFACE}; border:1px solid {ACCENT_DARK};}}"
        )


class MatteSelector(QComboBox):
    def __init__(self, items=(), parent=None):
        super().__init__(parent)
        self.setMinimumHeight(42)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.addItems(list(items))
        self.setStyleSheet(
            f"QComboBox {{background:{SURFACE}; color:{TEXT}; border:1px solid {BORDER}; "
            f"border-radius:12px; padding:0 13px; font-size:13px;}} "
            f"QComboBox:hover {{border:1px solid {ACCENT};}} "
            f"QComboBox:focus {{border:1px solid {ACCENT_DARK};}} "
            f"QComboBox::drop-down {{width:30px; border:0;}} "
            f"QComboBox QAbstractItemView {{background:{SURFACE}; color:{TEXT}; "
            f"border:1px solid {BORDER}; selection-background-color:{ACCENT_SOFT}; "
            f"selection-color:{ACCENT_DARK}; padding:5px; outline:0;}}"
        )


class AnimatedButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self._lift = 0
        self._animation = QPropertyAnimation(self, b"lift", self)
        self._animation.setDuration(140)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def get_lift(self):
        return self._lift

    def set_lift(self, value):
        self._lift = value
        self.setContentsMargins(0, max(0, int(2 - value)), 0, max(0, int(2 + value)))

    lift = pyqtProperty(int, get_lift, set_lift)

    def enterEvent(self, event):
        self._animation.stop()
        self._animation.setStartValue(self._lift)
        self._animation.setEndValue(2)
        self._animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._animation.stop()
        self._animation.setStartValue(self._lift)
        self._animation.setEndValue(0)
        self._animation.start()
        super().leaveEvent(event)


class NavButton(AnimatedButton):
    def __init__(self, text, active=False, parent=None):
        super().__init__(text, parent)
        active_style = (
            f"background:{SURFACE}; color:{ACCENT_DARK}; border:1px solid {ACCENT};"
            if active
            else f"background:transparent; color:{MUTED}; border:1px solid transparent;"
        )
        self.setMinimumHeight(38)
        self.setStyleSheet(
            f"QPushButton {{{active_style} border-radius:10px; padding:0 14px; "
            f"font-size:12px; font-weight:600;}} "
            f"QPushButton:hover {{background:{SURFACE}; color:{ACCENT_DARK}; border:1px solid {BORDER};}}"
        )


class PrimaryButton(AnimatedButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(46)
        self.setStyleSheet(
            f"QPushButton {{background:{BLACK}; color:white; border:0; border-radius:13px; "
            f"padding:0 20px; font-size:13px; font-weight:650;}} "
            f"QPushButton:hover {{background:{ACCENT_DARK};}} "
            f"QPushButton:pressed {{background:#0A4D36;}}"
        )


class StatusPill(QLabel):
    def __init__(self, text, tone="neutral", parent=None):
        super().__init__(text, parent)
        colors = {
            "success": (SUCCESS, SURFACE),
            "warning": (WARNING, SURFACE),
            "neutral": (MUTED, SURFACE),
        }
        fg, bg = colors.get(tone, colors["neutral"])
        border = ACCENT if tone == "success" else BORDER
        self.setStyleSheet(
            f"QLabel {{color:{fg}; background:{bg}; border:1px solid {border}; "
            f"border-radius:9px; padding:5px 9px; font-size:10px; font-weight:650;}}"
        )
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)


class MoneyValue(QLabel):
    def __init__(self, value, parent=None):
        super().__init__(value, parent)
        self.setStyleSheet(f"color:{BLACK}; font-size:34px; font-weight:700; border:0;")
