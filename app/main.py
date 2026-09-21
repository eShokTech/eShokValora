import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QFrame, QHBoxLayout, QLabel, QMainWindow, QScrollArea, QVBoxLayout, QWidget

from app.data.database import Database
from app.ui.theme import BG, BORDER, MUTED, SURFACE, TEXT, ACCENT, ACCENT_SOFT, apply_theme
from app.ui.widgets import (
    MatteCard,
    MatteInput,
    MatteSelector,
    MoneyValue,
    NavButton,
    PrimaryButton,
    SectionTitle,
    FieldLabel,
    StatusPill,
)


class ValoraWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("eShok Valora")
        self.resize(1180, 760)
        self.setMinimumSize(960, 650)
        self._build()

    def _build(self):
        root = QWidget()
        root.setStyleSheet(f"background:{BG};")
        self.setCentralWidget(root)
        outer = QVBoxLayout(root)
        outer.setContentsMargins(28, 22, 28, 26)
        outer.setSpacing(20)
        outer.addWidget(self._header())
        outer.addWidget(self._content(), 1)

    def _header(self):
        bar = QFrame()
        bar.setStyleSheet(
            f"background:{SURFACE}; border:1px solid {BORDER}; border-radius:18px;"
        )
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(18, 10, 18, 10)

        brand_box = QVBoxLayout()
        brand_box.setSpacing(0)
        brand = QLabel("eShok Valora")
        brand.setStyleSheet(f"color:{TEXT}; font-size:17px; font-weight:700; border:0;")
        sub = QLabel("Compra inteligente")
        sub.setStyleSheet(f"color:{MUTED}; font-size:10px; border:0;")
        brand_box.addWidget(brand)
        brand_box.addWidget(sub)
        layout.addLayout(brand_box)

        layout.addSpacing(24)
        for text, active in [
            ("Inicio", True),
            ("Valorar", False),
            ("Historial", False),
            ("Catálogo", False),
        ]:
            layout.addWidget(NavButton(text, active))

        layout.addStretch()

        settings = NavButton("⚙")
        settings.setFixedWidth(42)
        layout.addWidget(settings)
        return bar

    def _content(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        page = QWidget()
        page.setStyleSheet("background:transparent;")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(18)

        intro = QVBoxLayout()
        intro.setSpacing(3)
        title = QLabel("¿Cuánto puedes pagar por este equipo?")
        title.setStyleSheet(f"color:{TEXT}; font-size:27px; font-weight:700; border:0;")
        subtitle = QLabel(
            "Valora el mercado usado, la reparación y el riesgo para proteger tu margen."
        )
        subtitle.setStyleSheet(f"color:{MUTED}; font-size:12px; border:0;")
        intro.addWidget(title)
        intro.addWidget(subtitle)
        layout.addLayout(intro)

        columns = QHBoxLayout()
        columns.setSpacing(18)
        columns.addWidget(self._device_card(), 1)
        columns.addWidget(self._result_card(), 1)
        layout.addLayout(columns)

        note = QLabel(
            "La valuación no dice cuánto vale el equipo. Dice cuánto puedes pagar sin destruir tu margen."
        )
        note.setAlignment(Qt.AlignmentFlag.AlignCenter)
        note.setStyleSheet(f"color:{MUTED}; font-size:11px; padding:10px; border:0;")
        layout.addWidget(note)

        scroll.setWidget(page)
        return scroll

    def _device_card(self):
        card = MatteCard()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(12)

        layout.addWidget(SectionTitle("Equipo", "Identificación del dispositivo"))

        # ÚNICO buscador de toda la interfaz.
        layout.addWidget(MatteInput("Buscar modelo, por ejemplo: Galaxy S22 Ultra"))

        for pair in [
            (("Modelo", "Galaxy S22 Ultra"), ("Variante", "SM-S908U")),
            (("RAM", "8 GB"), ("Almacenamiento", "256 GB")),
        ]:
            row = QHBoxLayout()
            row.setSpacing(10)
            for label, value in pair:
                col = QVBoxLayout()
                col.setSpacing(5)
                col.addWidget(FieldLabel(label))

                if label == "Variante":
                    field = MatteSelector(["SM-S908U", "SM-S908B"])
                    field.setCurrentText(value)
                elif label == "RAM":
                    field = MatteSelector(["8 GB", "12 GB"])
                    field.setCurrentText(value)
                elif label == "Almacenamiento":
                    field = MatteSelector(["128 GB", "256 GB", "512 GB"])
                    field.setCurrentText(value)
                else:
                    field = MatteInput()
                    field.setText(value)

                col.addWidget(field)
                row.addLayout(col)
            layout.addLayout(row)

        status = QHBoxLayout()
        status.setSpacing(7)
        status.addWidget(StatusPill("✓ Modelo confirmado", "success"))
        status.addWidget(StatusPill("? IMEI no verificado", "warning"))
        status.addStretch()
        layout.addLayout(status)

        layout.addWidget(FieldLabel("Condición actual"))
        condition = MatteInput("Ej. pantalla rota, equipo funcional")
        condition.setText("Pantalla rota")
        layout.addWidget(condition)

        layout.addWidget(PrimaryButton("Valorar equipo"))
        return card

    def _result_card(self):
        card = MatteCard()
        card.setStyleSheet(
            f"QFrame {{ background:rgba(255,255,255,238); border:1px solid {ACCENT_SOFT}; border-radius:20px; }}"
        )
        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(10)

        eyebrow = QLabel("PUEDES PAGAR HASTA")
        eyebrow.setStyleSheet(
            f"color:{ACCENT}; font-size:10px; font-weight:700; border:0;"
        )
        layout.addWidget(eyebrow)
        layout.addWidget(MoneyValue("$2,100 MXN"))

        suggested = QHBoxLayout()
        suggested.addWidget(QLabel("Oferta sugerida"))
        suggested.addStretch()
        offer = QLabel("$1,800")
        offer.setStyleSheet(
            f"color:{ACCENT}; font-size:16px; font-weight:700; border:0;"
        )
        suggested.addWidget(offer)
        layout.addLayout(suggested)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"color:{BORDER};")
        layout.addWidget(line)

        for label, value in [
            ("Mercado usado", "$5,100"),
            ("Reparación", "− $1,700"),
            ("Reserva de riesgo", "− $300"),
            ("Utilidad deseada", "− $1,000"),
        ]:
            row = QHBoxLayout()
            left = QLabel(label)
            left.setStyleSheet(f"color:{MUTED}; font-size:11px; border:0;")
            right = QLabel(value)
            right.setStyleSheet(
                f"color:{TEXT}; font-size:12px; font-weight:650; border:0;"
            )
            row.addWidget(left)
            row.addStretch()
            row.addWidget(right)
            layout.addLayout(row)

        layout.addStretch()
        confidence = QLabel(
            "8 observaciones recientes  ·  Marketplace  ·  confianza alta"
        )
        confidence.setStyleSheet(f"color:{MUTED}; font-size:10px; border:0;")
        layout.addWidget(confidence)
        return card


def main():
    Database().initialize()
    app = QApplication(sys.argv)
    apply_theme(app)
    window = ValoraWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
