import sys

from PySide6.QtWidgets import QApplication, QLabel, QMainWindow
from PySide6.QtCore import Qt


class ValoraWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("eShok Valora")
        self.resize(1000, 650)

        title = QLabel("eShok VALORA")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.setCentralWidget(title)


def main():
    app = QApplication(sys.argv)

    window = ValoraWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()