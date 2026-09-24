import sys
from PySide6.QtCore import Qt
from PySide6.QtGui import QDoubleValidator, QIntValidator
from PySide6.QtWidgets import QApplication, QCompleter, QDialog, QDialogButtonBox, QFrame, QGridLayout, QHBoxLayout, QLabel, QLineEdit, QMainWindow, QMessageBox, QScrollArea, QStackedWidget, QVBoxLayout, QWidget
from app.core.catalog import DeviceCatalog, DeviceModel, DeviceVariant
from app.core.engine import ValuationRequest, value_device
from app.core.identification import identity_from_variant
from app.core.market import MarketType
from app.core.models import Condition, MarketObservation, PriceSource
from app.data.catalog_seed import seed_catalog
from app.data.database import Database
from app.ui.theme import BG, BORDER, MUTED, SURFACE, TEXT, ACCENT, ACCENT_SOFT, ACCENT_DARK, apply_theme
from app.ui.widgets import MatteCard, MatteInput, MatteSelector, MatteCheckBox, MoneyValue, NavButton, PrimaryButton, SectionTitle, FieldLabel, StatusPill

def money(value: float) -> str:
    return "$" + f"{value:,.0f} MXN"

class ObservationDialog(QDialog):
    def __init__(self, parent, device_key: str, default_condition: Condition):
        super().__init__(parent)
        self.setWindowTitle("Agregar observación de mercado")
        self.setMinimumWidth(440)
        self.device_key = device_key
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(12)
        layout.addWidget(SectionTitle("Observación de mercado", "Alimenta la inteligencia de Valora con datos reales."))
        layout.addWidget(FieldLabel("Precio observado"))
        self.price = MatteInput("$5,000")
        self.price.setValidator(QDoubleValidator(0, 999999, 2, self))
        layout.addWidget(self.price)
        row = QHBoxLayout()
        self.condition = MatteSelector(["Funciona", "Detalles menores", "Dañado", "Para piezas", "Reacondicionado"])
        self.market_type = MatteSelector(["Segundo uso", "Venta rápida", "Reacondicionado", "Nuevo"])
        for label, widget in (("Condición", self.condition), ("Mercado", self.market_type)):
            col = QVBoxLayout()
            col.addWidget(FieldLabel(label))
            col.addWidget(widget)
            row.addLayout(col)
        condition_map = {Condition.WORKING: 0, Condition.MINOR_DETAILS: 1, Condition.DAMAGED: 2, Condition.FOR_PARTS: 3, Condition.REFURBISHED: 4}
        self.condition.setCurrentIndex(condition_map[default_condition])
        layout.addLayout(row)
        layout.addWidget(FieldLabel("Fuente"))
        self.source = MatteSelector(["Marketplace", "Local", "Operación propia", "Otra"])
        layout.addWidget(self.source)
        row2 = QHBoxLayout()
        city_col = QVBoxLayout()
        city_col.addWidget(FieldLabel("Ciudad"))
        self.city = MatteInput("Opcional")
        city_col.addWidget(self.city)
        conf_col = QVBoxLayout()
        conf_col.addWidget(FieldLabel("Confianza (0-100)"))
        self.confidence = MatteInput("100")
        self.confidence.setText("100")
        self.confidence.setValidator(QIntValidator(0, 100, self))
        conf_col.addWidget(self.confidence)
        row2.addLayout(city_col)
        row2.addLayout(conf_col)
        layout.addLayout(row2)
        self.sold = MatteCheckBox("Venta confirmada")
        layout.addWidget(self.sold)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def observation(self) -> MarketObservation:
        conditions = [Condition.WORKING, Condition.MINOR_DETAILS, Condition.DAMAGED, Condition.FOR_PARTS, Condition.REFURBISHED]
        markets = [MarketType.SECOND_LIFE.value, MarketType.QUICK_SALE.value, MarketType.REFURBISHED_SALE.value, MarketType.NEW.value]
        sources = [PriceSource.MARKETPLACE, PriceSource.LOCAL, PriceSource.USER_OPERATION, PriceSource.OTHER]
        price = float(self.price.text().replace(",", "").replace("$", "") or 0)
        from datetime import date
        return MarketObservation(self.device_key, conditions[self.condition.currentIndex()], price, date.today(), sources[self.source.currentIndex()], city=self.city.text().strip(), sold=self.sold.isChecked(), confidence=max(0.0, min(1.0, int(self.confidence.text() or "100") / 100)), market_type=markets[self.market_type.currentIndex()])

class ValoraWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("eShok Valora")
        self.resize(1180, 820)
        self.setMinimumSize(980, 680)
        self.db = Database()
        self.db.initialize()
        if not self.db.list_device_models():
            seed_catalog(self.db)
        self.catalog = DeviceCatalog(tuple(self.db.list_device_models()))
        self.selected_model: DeviceModel | None = None
        self.selected_variant: DeviceVariant | None = None
        self.last_result = None
        self._build()

    def _build(self):
        root = QWidget()
        root.setStyleSheet(f"background:{BG};")
        self.setCentralWidget(root)
        outer = QVBoxLayout(root)
        outer.setContentsMargins(28, 22, 28, 26)
        outer.setSpacing(18)
        outer.addWidget(self._header())

        self.pages = QStackedWidget()
        self.pages.setFrameShape(QFrame.Shape.NoFrame)
        outer.addWidget(self.pages, 1)

        self.info_page = self._info_page()
        self.valuation_page = self._valuation_page()
        self.pages.addWidget(self.info_page)
        self.pages.addWidget(self.valuation_page)
        self.pages.setCurrentIndex(0)

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
        brand.setStyleSheet(
            f"color:{TEXT}; font-size:17px; font-weight:700; border:0;"
        )
        sub = QLabel("Compra inteligente")
        sub.setStyleSheet(f"color:{MUTED}; font-size:10px; border:0;")
        brand_box.addWidget(brand)
        brand_box.addWidget(sub)
        layout.addLayout(brand_box)
        layout.addStretch()

        self.back_button = NavButton("← Información")
        self.back_button.clicked.connect(lambda: self.pages.setCurrentIndex(0))
        self.back_button.hide()
        layout.addWidget(self.back_button)

        self.header_state = QLabel("1  Información  ·  2  Valoración")
        self.header_state.setStyleSheet(
            f"color:{MUTED}; font-size:10px; border:0;"
        )
        layout.addWidget(self.header_state)

        self.pages_current_hook = self.pages.currentChanged.connect(
            self._page_changed
        )
        return bar

    def _page_changed(self, index):
        valuation = index == 1
        self.back_button.setVisible(valuation)
        self.header_state.setText(
            "1  Información  ·  2  Valoración"
            if not valuation
            else "1  Información  ✓  ·  2  Valoración"
        )

    def _scroll_page(self, widget):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        scroll.setWidget(widget)
        return scroll

    def _info_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(14)

        title = QLabel("Información del equipo")
        title.setStyleSheet(
            f"color:{TEXT}; font-size:27px; font-weight:700; border:0;"
        )
        subtitle = QLabel(
            "Captura lo que sabes del equipo. Valora se encargará de validar "
            "la información y convertir lo que falta en riesgo económico."
        )
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet(
            f"color:{MUTED}; font-size:12px; border:0;"
        )
        layout.addWidget(title)
        layout.addWidget(subtitle)

        layout.addWidget(self._device_card())

        footer = QHBoxLayout()
        footer.addStretch()
        self.value_button = PrimaryButton("Valorar equipo  →")
        self.value_button.clicked.connect(self._value)
        footer.addWidget(self.value_button)
        layout.addLayout(footer)

        return self._scroll_page(page)

    def _valuation_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(14)

        title = QLabel("Valoración")
        title.setStyleSheet(
            f"color:{TEXT}; font-size:27px; font-weight:700; border:0;"
        )
        subtitle = QLabel(
            "Valora el mercado de segunda vida, los costos, el riesgo y tu "
            "margen para calcular cuánto puedes ofrecer."
        )
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet(
            f"color:{MUTED}; font-size:12px; border:0;"
        )
        layout.addWidget(title)
        layout.addWidget(subtitle)

        columns = QHBoxLayout()
        columns.setSpacing(18)
        columns.addWidget(self._valuation_inputs_card(), 1)
        columns.addWidget(self._result_card(), 1)
        layout.addLayout(columns)

        note = QLabel(
            "Valora no determina cuánto vale el equipo. Determina cuánto "
            "puedes pagar por él sin destruir tu margen."
        )
        note.setAlignment(Qt.AlignmentFlag.AlignCenter)
        note.setWordWrap(True)
        note.setStyleSheet(
            f"color:{MUTED}; font-size:11px; padding:8px; border:0;"
        )
        layout.addWidget(note)

        return self._scroll_page(page)

    def _device_card(self):
        card = MatteCard()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(10)
        layout.addWidget(SectionTitle("Equipo", "Identificación y datos que cambian el precio."))
        self.search = MatteInput("Buscar modelo, ejemplo: Galaxy S22 Ultra")
        self.search.returnPressed.connect(self._resolve_search)
        names = []
        for model in self.catalog.models:
            names.extend([model.name, model.brand + " " + model.name, *model.aliases])
            for variant in model.variants:
                names.extend([variant.model_number, *variant.aliases])
        completer = QCompleter(sorted(set(x for x in names if x)), self)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.search.setCompleter(completer)
        completer.activated.connect(self._resolve_search)
        layout.addWidget(self.search)
        self.identity_label = QLabel("Sin equipo identificado")
        self.identity_label.setStyleSheet(f"color:{MUTED}; font-size:11px; border:0;")
        layout.addWidget(self.identity_label)
        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(7)
        self.variant = MatteSelector(["No sé"])
        self.ram = MatteSelector(["No sé"])
        self.storage = MatteSelector(["No sé"])
        for col, (label, widget) in enumerate([("Variante", self.variant), ("RAM", self.ram), ("Almacenamiento", self.storage)]):
            grid.addWidget(FieldLabel(label), 0, col)
            grid.addWidget(widget, 1, col)
        self.variant.currentIndexChanged.connect(self._variant_changed)
        grid.addWidget(FieldLabel("Operador / red"), 2, 0)
        self.carrier = MatteInput("Ej. AT&T, Telcel, libre")
        grid.addWidget(self.carrier, 3, 0, 1, 3)
        layout.addLayout(grid)
        status = QHBoxLayout()
        self.model_status = StatusPill("○ Modelo desconocido", "neutral")
        self.imei_status = StatusPill("○ IMEI no verificado", "warning")
        status.addWidget(self.model_status)
        status.addWidget(self.imei_status)
        status.addStretch()
        layout.addLayout(status)
        imei_row = QHBoxLayout()
        imei_col = QVBoxLayout()
        imei_col.addWidget(FieldLabel("IMEI"))
        self.imei = MatteInput("Puede quedar vacío")
        self.imei.textChanged.connect(self._update_imei_status)
        imei_col.addWidget(self.imei)
        imei_row.addLayout(imei_col, 2)
        checks = QVBoxLayout()
        self.imei_verified = MatteCheckBox("IMEI verificado")
        self.imei_reported = MatteCheckBox("IMEI reportado")
        self.functional = MatteCheckBox("Prueba funcional completa")
        self.imei_verified.toggled.connect(self._update_imei_status)
        self.imei_reported.toggled.connect(self._update_imei_status)
        checks.addWidget(self.imei_verified)
        checks.addWidget(self.imei_reported)
        checks.addWidget(self.functional)
        imei_row.addLayout(checks, 1)
        layout.addLayout(imei_row)

        condition_row = QHBoxLayout()
        condition_col = QVBoxLayout()
        condition_col.addWidget(FieldLabel("Condición del equipo"))
        self.condition = MatteSelector(
            ["Funciona", "Detalles menores", "Dañado", "Para piezas", "Reacondicionado"]
        )
        condition_col.addWidget(self.condition)
        condition_row.addLayout(condition_col, 1)

        observe = NavButton("+ Mercado")
        observe.clicked.connect(self._add_observation)
        condition_row.addWidget(observe, 0, Qt.AlignmentFlag.AlignBottom)
        layout.addLayout(condition_row)

        return card

    def _result_card(self):
        card = MatteCard()
        card.setStyleSheet(f"QFrame {{ background:rgba(255,255,255,238); border:1px solid {ACCENT_SOFT}; border-radius:20px; }}")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(9)
        self.eyebrow = QLabel("ESPERANDO VALUACIÓN")
        self.eyebrow.setStyleSheet(f"color:{ACCENT_DARK}; font-size:10px; font-weight:700; border:0;")
        layout.addWidget(self.eyebrow)
        self.money_value = MoneyValue("$0 MXN")
        layout.addWidget(self.money_value)
        suggested = QHBoxLayout()
        suggested.addWidget(QLabel("Oferta sugerida"))
        suggested.addStretch()
        self.offer = QLabel("$0")
        self.offer.setStyleSheet(f"color:{ACCENT_DARK}; font-size:16px; font-weight:700; border:0;")
        suggested.addWidget(self.offer)
        layout.addLayout(suggested)
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"color:{BORDER};")
        layout.addWidget(line)
        self.breakdown = {}
        for key, label in [("market", "Mercado usado"), ("repair", "Reparación"), ("risk", "Reserva total de riesgo"), ("profit", "Utilidad deseada"), ("costs", "Otros costos")]:
            row = QHBoxLayout()
            left = QLabel(label)
            left.setStyleSheet(f"color:{MUTED}; font-size:11px; border:0;")
            right = QLabel("$0")
            right.setStyleSheet(f"color:{TEXT}; font-size:12px; font-weight:650; border:0;")
            row.addWidget(left)
            row.addStretch()
            row.addWidget(right)
            layout.addLayout(row)
            self.breakdown[key] = right
        self.market_info = QLabel("Sin observaciones de mercado para este equipo.")
        self.market_info.setWordWrap(True)
        self.market_info.setStyleSheet(f"color:{MUTED}; font-size:10px; border:0;")
        layout.addWidget(self.market_info)
        layout.addStretch()
        self.notes = QLabel("Valora un equipo para ver el análisis.")
        self.notes.setWordWrap(True)
        self.notes.setStyleSheet(f"color:{MUTED}; font-size:10px; border:0;")
        layout.addWidget(self.notes)
        return card

    def _valuation_inputs_card(self):
        card = MatteCard()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(10)
        layout.addWidget(
            SectionTitle(
                "Cálculo",
                "Parámetros que Valora usa para convertir el análisis en una oferta."
            )
        )

        form = QGridLayout()
        form.setHorizontalSpacing(10)
        form.setVerticalSpacing(7)

        self.market_type = MatteSelector(
            ["Segundo uso", "Venta rápida", "Reacondicionado", "Nuevo"]
        )
        self.repair = self._money_input("1700")
        self.selling = self._money_input("0")
        self.other = self._money_input("0")
        self.desired_profit = self._money_input("1000")
        self.margin = self._percent_input()
        self.buffer = self._money_input("300")
        self.faults = MatteInput()
        self.faults.setText("1")
        self.faults.setValidator(QIntValidator(0, 99, self))
        self.unknown_faults = MatteCheckBox(
            "Hay fallas/datos funcionales desconocidos"
        )
        self.complexity = MatteSelector(["Baja", "Media", "Alta"])
        self.complexity.setCurrentIndex(1)

        fields = [
            ("Mercado", self.market_type),
            ("Reparación estimada", self.repair),
            ("Costo de venta", self.selling),
            ("Otros costos", self.other),
            ("Utilidad deseada", self.desired_profit),
            ("Margen deseado %", self.margin),
            ("Colchón de oferta", self.buffer),
            ("Fallas conocidas", self.faults),
            ("Complejidad", self.complexity),
        ]
        for i, (label, widget) in enumerate(fields):
            r, c = divmod(i, 2)
            form.addWidget(FieldLabel(label), r * 2, c)
            form.addWidget(widget, r * 2 + 1, c)

        form.addWidget(self.unknown_faults, 10, 0, 1, 2)
        layout.addLayout(form)
        return card

    @staticmethod
    def _money_input(value="0"):
        field = MatteInput()
        field.setText(value)
        field.setValidator(QDoubleValidator(0, 9999999, 2))
        return field

    @staticmethod
    def _percent_input():
        field = MatteInput("Opcional")
        field.setValidator(QDoubleValidator(0, 99.99, 2))
        return field

    def _resolve_search(self):
        candidates = self.catalog.search(self.search.text(), limit=1)
        if not candidates:
            self.selected_model = None
            self.identity_label.setText("No encontré ese modelo en el catálogo.")
            self.model_status.setText("○ Modelo desconocido")
            return
        self._select_model(candidates[0])

    def _select_model(self, model: DeviceModel):
        self.selected_model = model
        self.selected_variant = None
        self.identity_label.setText(f"{model.brand} · {model.name}" + (f" · {model.year}" if model.year else ""))
        self.model_status.setText("✓ Modelo confirmado")
        self._fill_selector(self.variant, ["No sé"] + [v.model_number or f"Variante {i+1}" for i, v in enumerate(model.variants)])
        self._fill_selector(self.ram, ["No sé"])
        self._fill_selector(self.storage, ["No sé"])
        self._variant_changed()
        self.search.setText(model.name)

    @staticmethod
    def _fill_selector(selector, items):
        selector.blockSignals(True)
        selector.clear()
        selector.addItems(items)
        selector.setCurrentIndex(0)
        selector.blockSignals(False)

    def _variant_changed(self):
        if not self.selected_model:
            return
        idx = self.variant.currentIndex() - 1
        self.selected_variant = self.selected_model.variants[idx] if 0 <= idx < len(self.selected_model.variants) else None
        ram = sorted(self.selected_variant.ram_options_gb) if self.selected_variant else []
        storage = sorted(self.selected_variant.storage_options_gb) if self.selected_variant else []
        self._fill_selector(self.ram, ["No sé"] + [f"{x} GB" for x in ram])
        self._fill_selector(self.storage, ["No sé"] + [f"{x} GB" for x in storage])

    def _update_imei_status(self):
        if self.imei_reported.isChecked():
            self.imei_status.setText("⚠ IMEI reportado")
        elif self.imei_verified.isChecked():
            self.imei_status.setText("✓ IMEI verificado")
        elif self.imei.text().strip():
            self.imei_status.setText("? IMEI capturado, no verificado")
        else:
            self.imei_status.setText("○ IMEI no verificado")

    def _identity(self):
        if not self.selected_model:
            return None
        return identity_from_variant(self.selected_model, self.selected_variant, ram_gb=self._selected_number(self.ram), storage_gb=self._selected_number(self.storage), imei=self.imei.text().strip() or None, imei_verified=self.imei_verified.isChecked(), imei_reported=self.imei_reported.isChecked(), carrier=self.carrier.text().strip() or None, functional_test_completed=self.functional.isChecked())

    @staticmethod
    def _selected_number(selector):
        text = selector.currentText().replace(" GB", "").strip()
        return None if text == "No sé" else int(text)

    def _device_key(self):
        if not self.selected_model:
            return ""
        key = f"{self.selected_model.brand.strip().lower()}|{self.selected_model.name.strip().lower()}"
        if self.selected_variant and self.selected_variant.model_number:
            key += f"|{self.selected_variant.model_number.lower()}"
        ram = self._selected_number(self.ram)
        storage = self._selected_number(self.storage)
        if ram is not None:
            key += f"|{ram}gb_ram"
        if storage is not None:
            key += f"|{storage}gb"
        return key

    def _observations(self):
        if not self.selected_model:
            return []
        exact = self.db.list_observations(self._device_key())
        return exact or self.db.list_observations_for_model(self.selected_model.brand, self.selected_model.name)

    def _value(self):
        if not self.selected_model:
            QMessageBox.warning(
                self,
                "Falta el equipo",
                "Usa el buscador para identificar el modelo."
            )
            return

        observations = self._observations()
        conditions = [
            Condition.WORKING,
            Condition.MINOR_DETAILS,
            Condition.DAMAGED,
            Condition.FOR_PARTS,
            Condition.REFURBISHED,
        ]
        markets = [
            MarketType.SECOND_LIFE,
            MarketType.QUICK_SALE,
            MarketType.REFURBISHED_SALE,
            MarketType.NEW,
        ]

        if not observations:
            self.eyebrow.setText("SIN DATOS DE MERCADO")
            self.money_value.setText("$0 MXN")
            self.offer.setText("$0")
            self.market_info.setText(
                "No hay observaciones guardadas. Agrega datos reales con «+ Mercado» "
                "para que Valora pueda calcular."
            )
            self.notes.setText(
                "Primero alimenta el mercado con una o más observaciones reales."
            )
            self.pages.setCurrentIndex(1)
            return

        try:
            result = value_device(
                ValuationRequest(
                    observations=tuple(observations),
                    condition=conditions[self.condition.currentIndex()],
                    market_type=markets[self.market_type.currentIndex()],
                    repair_cost=float(self.repair.text() or 0),
                    selling_cost=float(self.selling.text() or 0),
                    other_cost=float(self.other.text() or 0),
                    desired_profit=float(self.desired_profit.text() or 0),
                    desired_margin_percent=(
                        float(self.margin.text())
                        if self.margin.text().strip()
                        else None
                    ),
                    known_faults=int(self.faults.text() or 0),
                    unknown_faults=self.unknown_faults.isChecked(),
                    repair_complexity=[0.2, 0.6, 0.9][
                        self.complexity.currentIndex()
                    ],
                    recommendation_buffer=float(self.buffer.text() or 0),
                    identity=self._identity(),
                )
            )
        except ValueError as exc:
            self.eyebrow.setText("NO SE PUDO VALORAR")
            self.money_value.setText("$0 MXN")
            self.offer.setText("$0")
            self.market_info.setText(str(exc))
            self.pages.setCurrentIndex(1)
            return

        self.last_result = result
        self.eyebrow.setText("PUEDES PAGAR HASTA")
        self.money_value.setText(
            money(result.valuation.maximum_purchase_price)
        )
        self.offer.setText(money(result.valuation.recommended_offer))
        self.breakdown["market"].setText(money(result.market.price))
        self.breakdown["repair"].setText(
            "− " + money(float(self.repair.text() or 0))
        )
        self.breakdown["risk"].setText(
            "− " + money(result.risk.reserve + result.uncertainty.reserve)
        )
        self.breakdown["profit"].setText(
            "− " + money(result.valuation.expected_profit_at_max)
        )
        self.breakdown["costs"].setText(
            "− "
            + money(
                float(self.selling.text() or 0)
                + float(self.other.text() or 0)
            )
        )
        self.market_info.setText(
            f"{result.market.sample_count} observaciones · "
            f"rango {money(result.market.low)}–{money(result.market.high)} · "
            f"confianza {result.market.confidence * 100:.0f}%"
        )
        notes = (
            list(result.risk.reasons)
            + list(result.uncertainty.reasons)
            + list(result.valuation.notes)
        )
        self.notes.setText(
            " · ".join(notes)
            if notes
            else "Escenario viable con los datos disponibles."
        )
        self.pages.setCurrentIndex(1)

    def _add_observation(self):
        if not self.selected_model:
            QMessageBox.warning(self, "Falta el equipo", "Primero identifica el modelo con el buscador.")
            return
        conditions = [Condition.WORKING, Condition.MINOR_DETAILS, Condition.DAMAGED, Condition.FOR_PARTS, Condition.REFURBISHED]
        dialog = ObservationDialog(self, self._device_key(), conditions[self.condition.currentIndex()])
        if dialog.exec() == QDialog.DialogCode.Accepted:
            observation = dialog.observation()
            if observation.price <= 0:
                QMessageBox.warning(self, "Precio inválido", "Captura un precio mayor que cero.")
                return
            self.db.add_observation(observation)
            self._value()

def main():
    app = QApplication(sys.argv)
    apply_theme(app)
    window = ValoraWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
