from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QLineEdit, QPushButton, QSizePolicy

from app.ui.theme import ACCENT, ACCENT_DARK, ACCENT_SOFT, BORDER, MUTED, SURFACE, SURFACE_SOFT, TEXT, SUCCESS, WARNING, BLACK

class MatteCard(QFrame):
    def __init__(self, parent=None, accent=False):
        super().__init__(parent)
        self.setObjectName("MatteCardAccent" if accent else "MatteCard")
        border = ACCENT_DARK if accent else BORDER
        self.setStyleSheet(f"QFrame#{self.objectName()} {{background:{SURFACE}; border:1px solid {border}; border-radius:20px;}}")

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
        self.setStyleSheet(f"QLineEdit {{background:{SURFACE_SOFT}; color:{TEXT}; border:1px solid {BORDER}; border-radius:12px; padding:0 13px; font-size:13px;}} QLineEdit:focus {{background:{SURFACE}; border:1px solid {ACCENT_DARK};}}")

class NavButton(QPushButton):
    def __init__(self, text, active=False, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(38)
        self.setStyleSheet(f"QPushButton {{background:{ACCENT_SOFT if active else 'transparent'}; color:{ACCENT_DARK if active else MUTED}; border:0; border-radius:10px; padding:0 14px; font-size:12px; font-weight:600;}} QPushButton:hover {{background:{ACCENT_SOFT}; color:{ACCENT_DARK};}}")

class PrimaryButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(46)
        self.setStyleSheet(f"QPushButton {{background:{BLACK}; color:white; border:0; border-radius:13px; padding:0 20px; font-size:13px; font-weight:650;}} QPushButton:hover {{background:{ACCENT_DARK};}} QPushButton:pressed {{background:#0A4D36;}}")

class StatusPill(QLabel):
    def __init__(self, text, tone="neutral", parent=None):
        super().__init__(text, parent)
        colors = {"success": (SUCCESS, ACCENT_SOFT), "warning": (WARNING, "#F7EED8"), "neutral": (MUTED, SURFACE_SOFT)}
        fg, bg = colors.get(tone, colors["neutral"])
        self.setStyleSheet(f"QLabel {{color:{fg}; background:{bg}; border-radius:9px; padding:5px 9px; font-size:10px; font-weight:650;}}")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)

class MoneyValue(QLabel):
    def __init__(self, value, parent=None):
        super().__init__(value, parent)
        self.setStyleSheet(f"color:{BLACK}; font-size:34px; font-weight:700; border:0;")
