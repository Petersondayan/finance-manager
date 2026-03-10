"""Budgets view — manage monthly spending limits per category."""

from datetime import date
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QProgressBar, QMessageBox, QScrollArea, QFrame,
)
from PyQt6.QtCore import Qt

from ...repositories.finance_repository import FinanceRepository
from ...services.budget_service import BudgetService
from ...utils.currency import format_currency
from ..widgets.card import Card
from ..dialogs.budget_dialog import BudgetDialog


class BudgetsView(QWidget):
    """View for managing monthly budgets."""

    STATUS_COLOURS = {
        "on_track": "#4CAF50",
        "warning": "#FF9800",
        "exceeded": "#F44336",
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self._finance_repo = FinanceRepository()
        self._budget_service = BudgetService(self._finance_repo)
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        scroll.setWidget(container)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        main = QVBoxLayout(container)
        main.setContentsMargins(16, 16, 16, 16)
        main.setSpacing(16)

        # Header
        today = date.today()
        self._period = f"{today.year:04d}-{today.month:02d}"

        header = QHBoxLayout()
        header.addWidget(QLabel(f"<h2>Budgets — {self._period}</h2>"))
        header.addStretch()

        self._add_btn = QPushButton("+ Add Budget")
        self._add_btn.clicked.connect(self._on_add)
        header.addWidget(self._add_btn)

        main.addLayout(header)

        # Alerts card
        self._alerts_card = Card("Alerts")
        self._alerts_card.setVisible(False)
        main.addWidget(self._alerts_card)

        # Budgets container
        self._budgets_card = Card("Monthly Limits")
        self._table = QVBoxLayout()
        self._table.setSpacing(6)
        self._budgets_card._content_layout.addLayout(self._table)
        main.addWidget(self._budgets_card)

        main.addStretch()

    def _load_data(self):
        """Load budget statuses and rebuild rows."""
        # Clear
        while self._table.count():
            item = self._table.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        statuses = self._budget_service.get_current_budgets()

        if not statuses:
            self._table.addWidget(QLabel("No budgets for this month. Click '+ Add Budget' to start."))
        else:
            for status in statuses:
                self._table.addWidget(self._make_row(status))

        # Alerts
        while self._alerts_card._content_layout.count():
            item = self._alerts_card._content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        alerts = self._budget_service.check_alerts()
        if alerts:
            self._alerts_card.setVisible(True)
            for alert in alerts:
                colour = "#F44336" if alert["status"] == "exceeded" else "#FF9800"
                lbl = QLabel(alert["message"])
                lbl.setStyleSheet(f"color: {colour};")
                self._alerts_card._content_layout.addWidget(lbl)
        else:
            self._alerts_card.setVisible(False)

    def _make_row(self, status) -> QWidget:
        row = QWidget()
        row.setStyleSheet("background: white; border: 1px solid #eee; border-radius: 4px;")
        layout = QHBoxLayout(row)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)

        name = QLabel(f"<b>{status.category_name}</b>")
        name.setMinimumWidth(150)
        layout.addWidget(name)

        bar = QProgressBar()
        bar.setMinimum(0)
        bar.setMaximum(100)
        pct = min(int(status.percent_used), 100)
        bar.setValue(pct)
        colour = self.STATUS_COLOURS.get(status.status, "#4CAF50")
        bar.setStyleSheet(f"""
            QProgressBar {{ border: 1px solid #ccc; border-radius: 4px; text-align: center; height: 20px; }}
            QProgressBar::chunk {{ background-color: {colour}; }}
        """)
        bar.setFormat(f"{pct}%  ({format_currency(status.spent)} / {format_currency(status.budget.monthly_limit)})")
        layout.addWidget(bar, 1)

        edit_btn = QPushButton("Edit")
        edit_btn.setMaximumWidth(55)
        edit_btn.clicked.connect(lambda _, s=status: self._on_edit(s))
        layout.addWidget(edit_btn)

        return row

    def _get_categories(self) -> list:
        cats = self._finance_repo.get_categories()
        return [(c.id, c.name) for c in cats]

    def _on_add(self):
        cats = self._get_categories()
        dialog = BudgetDialog(cats, self)
        if dialog.exec():
            try:
                self._budget_service.create_budget(
                    category_id=dialog.get_category_id(),
                    monthly_limit=dialog.get_limit(),
                    period=self._period,
                )
                self._load_data()
            except ValueError as e:
                QMessageBox.warning(self, "Error", str(e))

    def _on_edit(self, status):
        cats = self._get_categories()
        dialog = BudgetDialog(cats, self, budget=status.budget, category_name=status.category_name)
        if dialog.exec():
            self._budget_service.update_budget_amount(status.budget.id, dialog.get_limit())
            self._load_data()

    def refresh(self):
        self._load_data()
