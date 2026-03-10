"""Simple pie chart widget using QPainter — no external chart library needed."""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QPen, QFont
from PyQt6.QtCore import Qt, QRectF


_PALETTE = [
    "#2196F3", "#4CAF50", "#FF9800", "#E91E63",
    "#9C27B0", "#00BCD4", "#FF5722", "#607D8B",
    "#795548", "#3F51B5",
]


class PieChartWidget(QWidget):
    """Lightweight pie chart rendered with QPainter."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._slices: list[tuple[str, float]] = []  # (label, value)
        self.setMinimumSize(280, 220)

    def set_data(self, slices: list[tuple[str, float]]):
        """Set chart data. slices = [(label, value), ...]"""
        self._slices = [(lbl, max(0.0, val)) for lbl, val in slices]
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        legend_width = 140
        chart_size = min(w - legend_width - 20, h - 20)
        if chart_size < 40:
            return

        cx = chart_size // 2 + 10
        cy = h // 2
        r = chart_size // 2 - 4

        total = sum(v for _, v in self._slices)
        if total <= 0:
            painter.drawText(QRectF(0, 0, w, h), Qt.AlignmentFlag.AlignCenter, "No data")
            return

        # Draw pie slices
        start_angle = 90 * 16  # Qt angles: 1/16 degree, start from 12 o'clock
        rect = QRectF(cx - r, cy - r, r * 2, r * 2)

        for i, (label, value) in enumerate(self._slices):
            span = int(round(value / total * 360 * 16))
            colour = QColor(_PALETTE[i % len(_PALETTE)])
            painter.setBrush(colour)
            painter.setPen(QPen(Qt.GlobalColor.white, 1))
            painter.drawPie(rect, start_angle, span)
            start_angle += span

        # Legend
        font = QFont()
        font.setPointSize(9)
        painter.setFont(font)
        painter.setPen(Qt.GlobalColor.black)

        lx = cx + r + 16
        ly = cy - len(self._slices) * 11
        for i, (label, value) in enumerate(self._slices):
            colour = QColor(_PALETTE[i % len(_PALETTE)])
            painter.setBrush(colour)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(lx, ly + i * 22, 12, 12)
            painter.setPen(Qt.GlobalColor.black)
            pct = value / total * 100
            painter.drawText(lx + 18, ly + i * 22 + 11, f"{label} ({pct:.1f}%)")
