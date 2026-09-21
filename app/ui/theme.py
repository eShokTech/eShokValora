from PySide6.QtGui import QColor, QFont, QPalette
from PySide6.QtWidgets import QApplication

BG = "#EEF8F3"
SURFACE = "#FFFFFF"
SURFACE_SOFT = "#E2F1EA"
TEXT = "#17231D"
MUTED = "#617168"
BORDER = "#C6DED2"
ACCENT = "#35B982"
ACCENT_DARK = "#177A55"
ACCENT_SOFT = "#D9F2E6"
BLACK = "#101713"
SUCCESS = "#23845C"
WARNING = "#9A6A21"
DANGER = "#B64B4B"

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
