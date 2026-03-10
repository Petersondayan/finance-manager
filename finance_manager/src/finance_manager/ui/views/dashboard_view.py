"""Dashboard view — home screen with net worth, MTD spending, budget bars, recent transactions."""

from datetime import date
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QFrame, QProgressBar, QSizePolicy,
)
from PyQt6.QtCore import Qt

from ...repositories.account_repository import AccountRepository
from ...repositories.transaction_repository import TransactionRepository
from ...services.budget_service import BudgetService
from ...utils.currency import format_currency
from ..widgets.card import Card
from ..widgets.amount_label import AmountLabel


class DashboardView(QWidget):
    """Dashboard showing financial overview."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._account_repo = AccountRepository()
        self._transaction_repo = TransactionRepository()
        self._budget_service = BudgetService()
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        """Build the UI layout."""
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

        # Title
        title = QLabel("<h2>Dashboard</h2>")
        main.addWidget(title)

        # --- Top summary row ---
        summary_row = QHBoxLayout()
        summary_row.setSpacing(12)

        self._net_worth_card = Card("Net Worth")
        self._net_worth_label = AmountLabel(0)
        self._net_worth_label.setStyleSheet("font-size: 22px; font-weight: bold;")
        self._net_worth_card.add_widget(self._net_worth_label)
        summary_row.addWidget(self._net_worth_card)

        self._income_card = Card("Income (MTD)")
        self._income_label = AmountLabel(0)
        self._income_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self._income_card.add_widget(self._income_label)
        summary_row.addWidget(self._income_card)

        self._expenses_card = Card("Expenses (MTD)")
        self._expenses_label = AmountLabel(0)
        self._expenses_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self._expenses_card.add_widget(self._expenses_label)
        summary_row.addWidget(self._expenses_card)

        main.addLayout(summary_row)

        # --- Budget status bars ---
        budget_card = Card("Budget Status — This Month")
        self._budget_container = QVBoxLayout()
        self._budget_container.setSpacing(8)
        budget_card._content_layout.addLayout(self._budget_container)
        main.addWidget(budget_card)

        # --- Recent transactions ---
        recent_card = Card("Recent Transactions")
        self._recent_table = _RecentTransactionsWidget()
        recent_card.add_widget(self._recent_table)
        main.addWidget(recent_card)

        main.addStretch()

    def _load_data(self):
        """Populate all dashboard widgets from services."""
        today = date.today()

        # Net worth
        summary = self._account_repo.get_summary()
        self._net_worth_label.set_amount(summary.net_worth)

        # MTD income / expenses
        income, expenses = self._transaction_repo.get_monthly_totals(today.year, today.month)
        self._income_label.set_amount(income)
        self._expenses_label.set_amount(-abs(expenses))

        # Budget bars — clear then rebuild
        while self._budget_container.count():
            item = self._budget_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        budgets = self._budget_service.get_current_budgets()
        if not budgets:
            self._budget_container.addWidget(QLabel("No budgets set for this month."))
        else:
            for status in budgets:
                row = _BudgetBarRow(status)
                self._budget_container.addWidget(row)

        # Recent transactions (last 10)
        start = today.replace(day=1)
        txns = self._transaction_repo.get_by_date_range(start, today)
        txns_sorted = sorted(txns, key=lambda t: t.date, reverse=True)[:10]
        self._recent_table.set_transactions(txns_sorted)

    def refresh(self):
        """Public refresh — called when navigating to this view."""
        self._load_data()


class _BudgetBarRow(QWidget):
    """Single budget row with label and colour-coded progress bar."""

    STATUS_COLOURS = {
        "on_track": "#4CAF50",
        "warning": "#FF9800",
        "exceeded": "#F44336",
    }

    def __init__(self, status, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        name_label = QLabel(status.category_name)
        name_label.setMinimumWidth(140)
        layout.addWidget(name_label)

        bar = QProgressBar()
        bar.setMinimum(0)
        bar.setMaximum(100)
        pct = min(int(status.percent_used), 100)
        bar.setValue(pct)
        colour = self.STATUS_COLOURS.get(status.status, "#4CAF50")
        bar.setStyleSheet(f"""
            QProgressBar {{ border: 1px solid #ccc; border-radius: 4px; text-align: center; }}
            QProgressBar::chunk {{ background-color: {colour}; border-radius: 3px; }}
        """)
        bar.setFormat(f"{pct}%")
        bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout.addWidget(bar, 1)

        limit_label = QLabel(
            f"{format_currency(status.spent)} / {format_currency(status.budget.monthly_limit)}"
        )
        limit_label.setMinimumWidth(160)
        limit_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(limit_label)


class _RecentTransactionsWidget(QWidget):
    """Compact recent-transactions list."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(4)

    def set_transactions(self, transactions):
        while self._layout.count():
            item = self._layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not transactions:
            self._layout.addWidget(QLabel("No transactions this month."))
            return

        for txn in transactions:
            row = QWidget()
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(8)

            date_label = QLabel(str(txn.date))
            date_label.setMinimumWidth(90)
            date_label.setStyleSheet("color: #666; font-size: 12px;")
            row_layout.addWidget(date_label)

            desc_label = QLabel(txn.description or "")
            desc_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            row_layout.addWidget(desc_label, 1)

            amount_label = AmountLabel(txn.amount)
            amount_label.setMinimumWidth(90)
            amount_label.setAlignment(Qt.AlignmentFlag.AlignRight)
            row_layout.addWidget(amount_label)

            self._layout.addWidget(row)
