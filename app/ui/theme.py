from PySide6.QtGui import QColor, QFont, QPalette
from PySide6.QtWidgets import QApplication

BG = "#F5F5F7"
SURFACE = "#FFFFFF"
SURFACE_SOFT = "#F0F0F3"
TEXT = "#25252B"
MUTED = "#777781"
BORDER = "#E4E4E8"
ACCENT = "#7657D9"
ACCENT_SOFT = "#EEE9FF"
SUCCESS = "#2E9B67"
WARNING = "#B87922"
DANGER = "#C95656"

def apply_theme(app: QApplication) -> None:
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(BG))
    palette.setColor(QPalette.ColorRole.Base, QColor(SURFACE))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(SURFACE_SOFT))
    palette.setColor(QPalette.ColorRole.Text, QColor(TEXT))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(TEXT))
    palette.setColor(QPalette.ColorRole.Button, QColor(SURFACE))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(TEXT))
    palette.setColor(QPalette.ColorRole.PlaceholderText, QColor(MUTED))
    app.setPalette(palette)
    app.setFont(QFont("Segoe UI", 10))
