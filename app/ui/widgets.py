from PySide6.QtCore import QEasingCurve, Property, QPropertyAnimation, Qt, QRectF, QTimer
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen, QRegion
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QFrame,
    QGraphicsDropShadowEffect,
    QLabel,
    QLineEdit,
    QListView,
    QPushButton,
    QSizePolicy,
    QStyle,
    QStyleOptionComboBox,
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


class MatteSelector(QComboBox):
    def __init__(self, items=(), parent=None):
        super().__init__(parent)
        self.setMinimumHeight(42)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.addItems(list(items))

        self._hover = 0.0
        self._hover_animation = QPropertyAnimation(self, b"hoverProgress", self)
        self._hover_animation.setDuration(150)
        self._hover_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        view = QListView()
        view.setSpacing(2)
        view.setUniformItemSizes(False)
        view.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        view.setFrameShape(QFrame.Shape.NoFrame)
        view.setStyleSheet(
            f"QListView {{"
            f"background:rgba(255,255,255,250);"
            f"color:{TEXT};"
            f"border:1px solid {BORDER};"
            f"border-radius:14px;"
            f"padding:6px;"
            f"outline:0;"
            f"}}"
            f"QListView::item {{"
            f"min-height:34px;"
            f"padding:7px 10px;"
            f"border-radius:10px;"
            f"}}"
            f"QListView::item:hover {{"
            f"background:{ACCENT_SOFT}; color:{ACCENT_DARK};"
            f"}}"
            f"QListView::item:selected {{"
            f"background:{ACCENT_SOFT}; color:{ACCENT_DARK};"
            f"font-weight:650;"
            f"}}"
        )
        self.setView(view)

    def get_hover_progress(self):
        return self._hover

    def set_hover_progress(self, value):
        self._hover = max(0.0, min(1.0, float(value)))
        self.update()

    hoverProgress = Property(float, get_hover_progress, set_hover_progress)

    def enterEvent(self, event):
        self._hover_animation.stop()
        self._hover_animation.setStartValue(self._hover)
        self._hover_animation.setEndValue(1.0)
        self._hover_animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hover_animation.stop()
        self._hover_animation.setStartValue(self._hover)
        self._hover_animation.setEndValue(0.0)
        self._hover_animation.start()
        super().leaveEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = QRectF(self.rect()).adjusted(0.7, 0.7, -0.7, -0.7)
        radius = 20.0

        base = QColor(SURFACE)
        painter.setBrush(base)

        base_border = QColor(BORDER)
        hover_border = QColor(ACCENT)
        border = QColor(
            int(base_border.red() + (hover_border.red() - base_border.red()) * self._hover),
            int(base_border.green() + (hover_border.green() - base_border.green()) * self._hover),
            int(base_border.blue() + (hover_border.blue() - base_border.blue()) * self._hover),
        )
        if self.hasFocus():
            border = QColor(ACCENT_DARK)

        painter.setPen(QPen(border, 1.2))
        painter.drawRoundedRect(rect, radius, radius)

        text_rect = QRectF(15, 0, self.width() - 50, self.height())
        painter.setPen(QPen(QColor(TEXT), 1))
        text = self.currentText()
        painter.drawText(
            text_rect,
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            text,
        )

        # Clean chevron. No native square drop-down button.
        cx = self.width() - 23
        cy = self.height() / 2
        path = QPainterPath()
        path.moveTo(cx - 5, cy - 2)
        path.lineTo(cx, cy + 3)
        path.lineTo(cx + 5, cy - 2)
        painter.setPen(QPen(QColor(ACCENT_DARK), 1.7, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)

        painter.end()

    def _round_popup(self, popup):
        radius = 14
        rect = popup.rect()
        if rect.width() <= 0 or rect.height() <= 0:
            return
        path = QPainterPath()
        path.addRoundedRect(QRectF(rect), radius, radius)
        popup.setMask(QRegion(path.toFillPolygon().toPolygon()))

    def showPopup(self):
        super().showPopup()
        popup = self.view().window()
        popup.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        popup.setStyleSheet(
            "QFrame { background: transparent; border: 0; }"
        )
        QTimer.singleShot(0, lambda: self._animate_popup(popup))

    def _animate_popup(self, popup):
        end = popup.geometry()
        if end.width() <= 0 or end.height() <= 0:
            return

        self._round_popup(popup)

        start = end
        start.setHeight(min(8, end.height()))
        popup.setGeometry(start)
        self._round_popup(popup)

        animation = QPropertyAnimation(popup, b"geometry", popup)
        animation.setDuration(155)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.setStartValue(start)
        animation.setEndValue(end)

        def update_mask(value):
            rect = value
            popup.setGeometry(rect)
            self._round_popup(popup)

        animation.valueChanged.connect(update_mask)
        popup._valora_popup_animation = animation
        animation.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)


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
