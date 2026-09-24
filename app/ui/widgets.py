from PySide6.QtCore import QEvent, QEasingCurve, Property, QPropertyAnimation, Qt, QRect, QRectF, QSize, Signal
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen, QRegion
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QFrame,
    QGraphicsDropShadowEffect,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSizePolicy,
    QWidget,
)

from app.ui.theme import (
    ACCENT,
    ACCENT_DARK,
    ACCENT_SOFT,
    BORDER,
    MUTED,
    SURFACE,
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
            f"background:rgba(255,255,255,242);"
            f"border:1px solid {border};"
            f"border-radius:20px;"
            f"}}"
        )
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24)
        shadow.setOffset(0, 5)
        shadow.setColor(QColor(16, 23, 19, 22))
        self.setGraphicsEffect(shadow)


class MatteCard(MatteGlassFrame):
    pass


class SectionTitle(QLabel):
    def __init__(self, title, subtitle="", parent=None):
        super().__init__(title, parent)
        self.setStyleSheet(
            f"color:{TEXT}; font-size:18px; font-weight:650; border:0;"
        )
        if subtitle:
            self.setToolTip(subtitle)


class FieldLabel(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(
            f"color:{MUTED}; font-size:11px; font-weight:600; border:0;"
        )


class MatteInput(QLineEdit):
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setMinimumHeight(42)
        self.setStyleSheet(
            f"QLineEdit {{"
            f"background:{SURFACE}; color:{TEXT};"
            f"border:1px solid {BORDER}; border-radius:13px;"
            f"padding:0 13px; font-size:13px;"
            f"}}"
            f"QLineEdit:hover {{border:1px solid {ACCENT};}}"
            f"QLineEdit:focus {{border:1px solid {ACCENT_DARK};}}"
        )


class MatteComboList(QListWidget):
    """Lista del selector con superficie mate y esquinas realmente redondeadas."""

    def paintEvent(self, event):
        painter = QPainter(self.viewport())
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.viewport().rect().adjusted(0, 0, -1, -1)

        path = QPainterPath()
        path.addRoundedRect(rect, 14, 14)
        painter.fillPath(path, QColor(255, 255, 255, 242))
        painter.setPen(QColor(198, 222, 210, 235))
        painter.drawPath(path)

        inner = QPainterPath()
        inner.addRoundedRect(rect.adjusted(1, 1, -1, -1), 13, 13)
        painter.setPen(QColor(255, 255, 255, 120))
        painter.drawPath(inner)
        painter.end()

        super().paintEvent(event)

        overlay = QPainter(self.viewport())
        overlay.setRenderHint(QPainter.RenderHint.Antialiasing)
        edge = self.viewport().rect().adjusted(0, 0, -1, -1)
        edge_path = QPainterPath()
        edge_path.addRoundedRect(edge, 14, 14)
        overlay.setBrush(Qt.BrushStyle.NoBrush)
        overlay.setPen(QColor(198, 222, 210, 235))
        overlay.drawPath(edge_path)
        overlay.end()


class MatteComboSurface(QFrame):
    """Superficie independiente del popup."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Fixed,
        )

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect().adjusted(0, 0, -1, -1)

        path = QPainterPath()
        path.addRoundedRect(rect, 14, 14)
        painter.fillPath(path, QColor(255, 255, 255, 228))
        painter.setPen(QColor(198, 222, 210, 220))
        painter.drawPath(path)

        inner = QPainterPath()
        inner.addRoundedRect(rect.adjusted(1, 1, -1, -1), 13, 13)
        painter.setPen(QColor(255, 255, 255, 105))
        painter.drawPath(inner)
        painter.end()


class MatteSelector(QWidget):
    """
    Selector basado en el mismo mecanismo de GlassComboBox de eShokFix:
    popup independiente, máscara real de esquinas y animación por altura.
    """

    CLOSED_HEIGHT = 42
    ROW_HEIGHT = 44
    LIST_PADDING = 8
    DROPDOWN_MAX_HEIGHT = 330

    currentIndexChanged = Signal(int)
    currentTextChanged = Signal(str)
    activated = Signal(int)

    def __init__(self, items=(), parent=None):
        super().__init__(parent)
        self.setFixedHeight(self.CLOSED_HEIGHT)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self._items = []
        self._data = []
        self._current_index = -1
        self._placeholder_text = "Seleccionar..."
        self._expanded = False
        self._progress = 0.0
        self._hover_progress = 0.0
        self._opens_upward = False

        self._surface = MatteComboSurface()
        self._surface.setWindowFlags(
            Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint
        )
        self._surface.hide()

        self._list = MatteComboList()
        self._list.setWindowFlags(
            Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint
        )
        self._list.setFrameShape(QFrame.Shape.NoFrame)
        self._list.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self._list.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self._list.setSpacing(0)
        self._list.setUniformItemSizes(True)
        self._list.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground
        )
        self._list.setAttribute(
            Qt.WidgetAttribute.WA_OpaquePaintEvent,
            False,
        )
        self._list.setStyleSheet(
            f"""
            QListWidget {{
                background: transparent;
                border: none;
                border-radius: 14px;
                outline: none;
                padding: 0px;
                color: {TEXT};
                font-family: "Segoe UI";
                font-size: 13px;
            }}

            QListWidget::item {{
                background: transparent;
                border: none;
                padding: 0px 16px;
                margin: 0px;
                min-height: 44px;
            }}
            """
        )
        self._list.hide()
        self._list.installEventFilter(self)
        self._list.itemClicked.connect(self._on_item_clicked)

        self._animation = QPropertyAnimation(
            self,
            b"expandProgress",
            self,
        )
        self._animation.setDuration(210)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._hover_animation = QPropertyAnimation(
            self,
            b"hoverProgress",
            self,
        )
        self._hover_animation.setDuration(150)
        self._hover_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.addItems(list(items))

    def setPlaceholderText(self, text):
        self._placeholder_text = str(text)
        self.update()

    def placeholderText(self):
        return self._placeholder_text

    def addItem(self, text, userData=None):
        self._items.append(str(text))
        self._data.append(userData)
        self._rebuild_list()
        self.update()

    def addItems(self, items):
        for item in items:
            if isinstance(item, (tuple, list)) and len(item) >= 2:
                self.addItem(item[0], item[1])
            else:
                self.addItem(item)

    def clear(self):
        self._items.clear()
        self._data.clear()
        self._current_index = -1
        self._list.clear()
        self.update()

    def count(self):
        return len(self._items)

    def itemText(self, index):
        if 0 <= index < len(self._items):
            return self._items[index]
        return ""

    def itemData(self, index):
        if 0 <= index < len(self._data):
            return self._data[index]
        return None

    def currentIndex(self):
        return self._current_index

    def currentText(self):
        if 0 <= self._current_index < len(self._items):
            return self._items[self._current_index]
        return self._placeholder_text

    def setCurrentIndex(self, index):
        index = int(index)
        if index < -1 or index >= len(self._items):
            index = -1
        if index == self._current_index:
            return

        self._current_index = index
        self._rebuild_list()
        self.update()
        self.currentIndexChanged.emit(self._current_index)
        self.currentTextChanged.emit(self.currentText())

    def currentData(self):
        if 0 <= self._current_index < len(self._data):
            return self._data[self._current_index]
        return None

    def _rebuild_list(self):
        self._list.clear()
        for index, text in enumerate(self._items):
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, index)
            item.setSizeHint(QSize(self.width(), self.ROW_HEIGHT))
            self._list.addItem(item)

    def get_expand_progress(self):
        return self._progress

    def set_expand_progress(self, value):
        self._progress = max(0.0, min(1.0, float(value)))
        self._position_layers()
        self.update()

    expandProgress = Property(
        float,
        get_expand_progress,
        set_expand_progress,
    )

    def get_hover_progress(self):
        return self._hover_progress

    def set_hover_progress(self, value):
        self._hover_progress = max(
            0.0,
            min(1.0, float(value)),
        )
        self.update()

    hoverProgress = Property(
        float,
        get_hover_progress,
        set_hover_progress,
    )

    def toggleExpanded(self):
        self.setExpanded(not self._expanded)

    def setExpanded(self, expanded):
        expanded = bool(expanded)
        if expanded == self._expanded:
            return
        if self.window() is None:
            return

        if expanded:
            self._rebuild_list()

        self._expanded = expanded

        if expanded:
            self._position_layers()
            self.raise_()
            self._list.raise_()

        self._animation.stop()
        self._animation.setStartValue(self._progress)
        self._animation.setEndValue(1.0 if expanded else 0.0)
        self._animation.start()

        if not expanded:
            self._position_layers()

    @staticmethod
    def _apply_rounded_mask(widget, radius=14):
        width = widget.width()
        height = widget.height()
        if width <= 0 or height <= 0:
            return

        radius = max(1, min(radius, width // 2, height // 2))
        diameter = radius * 2

        region = QRegion(
            QRect(0, radius, width, height - diameter),
            QRegion.RegionType.Rectangle,
        )
        region = region.united(
            QRegion(
                QRect(radius, 0, width - diameter, height),
                QRegion.RegionType.Rectangle,
            )
        )
        region = region.united(
            QRegion(
                QRect(0, 0, diameter, diameter),
                QRegion.RegionType.Ellipse,
            )
        )
        region = region.united(
            QRegion(
                QRect(width - diameter, 0, diameter, diameter),
                QRegion.RegionType.Ellipse,
            )
        )
        region = region.united(
            QRegion(
                QRect(0, height - diameter, diameter, diameter),
                QRegion.RegionType.Ellipse,
            )
        )
        region = region.united(
            QRegion(
                QRect(
                    width - diameter,
                    height - diameter,
                    diameter,
                    diameter,
                ),
                QRegion.RegionType.Ellipse,
            )
        )
        widget.setMask(region)

    def _position_layers(self):
        if self.window() is None:
            return

        full_height = min(
            self._list.count() * self.ROW_HEIGHT,
            self.DROPDOWN_MAX_HEIGHT,
        )
        expanded_height = (
            self.CLOSED_HEIGHT
            + self.LIST_PADDING
            + full_height
            + self.LIST_PADDING
        )
        current_height = (
            self.CLOSED_HEIGHT
            + (expanded_height - self.CLOSED_HEIGHT)
            * self._progress
        )

        global_top = self.mapToGlobal(self.rect().topLeft())
        global_bottom = self.mapToGlobal(self.rect().bottomLeft())

        if self._progress <= 0.001:
            self._surface.hide()
            self._list.hide()
            return

        screen = QApplication.screenAt(global_top)
        if screen is None:
            screen = QApplication.primaryScreen()

        available = (
            screen.availableGeometry()
            if screen is not None
            else None
        )

        space_below = (
            available.bottom() - global_bottom.y()
            if available is not None
            else expanded_height + 1
        )
        space_above = (
            global_top.y() - available.top()
            if available is not None
            else 0
        )

        self._opens_upward = (
            space_below < expanded_height
            and space_above > space_below
        )

        list_height = max(
            1,
            int(full_height * self._progress),
        )

        if self._opens_upward:
            surface_top = int(
                global_top.y()
                - (current_height - self.CLOSED_HEIGHT)
            )
        else:
            surface_top = int(global_top.y())

        self._surface.setGeometry(
            int(global_top.x()),
            surface_top,
            self.width(),
            max(1, int(current_height)),
        )
        self._apply_rounded_mask(self._surface)

        if self._opens_upward:
            list_global_y = int(
                global_top.y()
                - self.LIST_PADDING
                - list_height
            )
        else:
            list_global_y = int(
                global_bottom.y()
                + self.LIST_PADDING
            )

        self._surface.show()
        self._surface.raise_()

        self._list.setGeometry(
            int(global_top.x()),
            list_global_y,
            self.width(),
            list_height,
        )
        self._apply_rounded_mask(self._list)
        self._list.show()
        self._list.raise_()

    def _on_item_clicked(self, item):
        index = item.data(Qt.ItemDataRole.UserRole)
        if index is None:
            return

        index = int(index)
        self.setCurrentIndex(index)
        self.activated.emit(index)
        self.setExpanded(False)
        self.setFocus()

    def mousePressEvent(self, event):
        if (
            event.button() == Qt.MouseButton.LeftButton
            and event.position().y() <= self.CLOSED_HEIGHT
        ):
            self.toggleExpanded()
            event.accept()
            return
        super().mousePressEvent(event)

    def keyPressEvent(self, event):
        if (
            event.key() == Qt.Key.Key_Escape
            and self._expanded
        ):
            self.setExpanded(False)
            event.accept()
            return
        super().keyPressEvent(event)

    def enterEvent(self, event):
        self._hover_animation.stop()
        self._hover_animation.setStartValue(self._hover_progress)
        self._hover_animation.setEndValue(1.0)
        self._hover_animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hover_animation.stop()
        self._hover_animation.setStartValue(self._hover_progress)
        self._hover_animation.setEndValue(0.0)
        self._hover_animation.start()
        super().leaveEvent(event)

    def eventFilter(self, watched, event):
        if (
            watched is self._list
            and event.type() == QEvent.Type.Hide
            and self._expanded
        ):
            self._expanded = False
            self._animation.stop()
            self._animation.setStartValue(self._progress)
            self._animation.setEndValue(0.0)
            self._animation.start()
        return super().eventFilter(watched, event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = QRectF(self.rect()).adjusted(0.7, 0.7, -0.7, -0.7)
        hover_alpha = int(
            205 + (250 - 205) * self._hover_progress
        )
        painter.setBrush(QColor(255, 255, 255, hover_alpha))

        base_border = QColor(BORDER)
        hover_border = QColor(ACCENT)
        border = QColor(
            int(
                base_border.red()
                + (hover_border.red() - base_border.red())
                * self._hover_progress
            ),
            int(
                base_border.green()
                + (hover_border.green() - base_border.green())
                * self._hover_progress
            ),
            int(
                base_border.blue()
                + (hover_border.blue() - base_border.blue())
                * self._hover_progress
            ),
        )
        if self.hasFocus() and self._hover_progress < 0.05:
            border = QColor(ACCENT_DARK)

        # El hover conserva el selector exactamente igual en reposo y
        # añade solamente la transición mint solicitada al pasar el mouse.
        border_width = 1.2 + (0.8 * self._hover_progress)
        painter.setPen(QPen(border, border_width))
        painter.drawRoundedRect(rect, 21.0, 21.0)

        if self._hover_progress > 0.01:
            highlight = QColor(ACCENT)
            highlight.setAlpha(int(28 * self._hover_progress))
            painter.setBrush(highlight)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(
                rect.adjusted(1.5, 1.5, -1.5, -1.5),
                19.5,
                19.5,
            )

        painter.setPen(QPen(QColor(TEXT), 1))
        painter.drawText(
            QRectF(15, 0, self.width() - 50, self.height()),
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            self.currentText(),
        )

        painter.save()
        painter.translate(self.width() - 20, self.height() / 2)
        painter.rotate(180 * self._progress)

        arrow = QPainterPath()
        arrow.moveTo(-5, -2)
        arrow.lineTo(0, 3)
        arrow.lineTo(5, -2)
        painter.setPen(
            QPen(
                QColor(ACCENT_DARK),
                1.7,
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
                Qt.PenJoinStyle.RoundJoin,
            )
        )
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(arrow)
        painter.restore()
        painter.end()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._expanded:
            self._rebuild_list()
            self._position_layers()

    def focusInEvent(self, event):
        self.update()
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        self.update()
        super().focusOutEvent(event)


class MatteCheckBox(QCheckBox):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(28)
        self.setStyleSheet(
            f"QCheckBox {{"
            f"color:{TEXT}; font-size:11px; spacing:9px; border:0;"
            f"}}"
            f"QCheckBox::indicator {{"
            f"width:18px; height:18px;"
            f"border:1.5px solid {BORDER};"
            f"border-radius:9px;"
            f"background:{SURFACE};"
            f"}}"
            f"QCheckBox::indicator:hover {{"
            f"border:1.5px solid {ACCENT};"
            f"}}"
            f"QCheckBox::indicator:checked {{"
            f"border:1.5px solid {ACCENT_DARK};"
            f"background:{ACCENT_DARK};"
            f"}}"
            f"QCheckBox::indicator:checked:hover {{"
            f"background:{ACCENT};"
            f"border:1.5px solid {ACCENT};"
            f"}}"
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
        self.setContentsMargins(
            0, max(0, int(2 - value)), 0, max(0, int(2 + value))
        )

    lift = Property(int, get_lift, set_lift)

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
            f"background:{ACCENT_SOFT}; color:{ACCENT_DARK}; border:1px solid {ACCENT};"
            if active
            else f"background:transparent; color:{MUTED}; border:1px solid transparent;"
        )
        self.setMinimumHeight(38)
        self.setStyleSheet(
            f"QPushButton {{{active_style} border-radius:19px; padding:0 14px; "
            f"font-size:12px; font-weight:600;}} "
            f"QPushButton:hover {{background:{SURFACE}; color:{ACCENT_DARK}; border:1px solid {BORDER};}} "
            f"QPushButton:pressed {{background:{ACCENT_SOFT};}}"
        )


class PrimaryButton(AnimatedButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(46)
        self.setStyleSheet(
            f"QPushButton {{background:{BLACK}; color:white; border:0; border-radius:23px; "
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
            f"border-radius:13px; padding:5px 10px; font-size:10px; font-weight:650;}}"
        )
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)


class MoneyValue(QLabel):
    def __init__(self, value, parent=None):
        super().__init__(value, parent)
        self.setStyleSheet(
            f"color:{BLACK}; font-size:34px; font-weight:700; border:0;"
        )
