"""Investments view — portfolio holdings and asset allocation pie chart."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QSplitter, QMessageBox,
)
from PyQt6.QtCore import Qt

from ...repositories.account_repository import AccountRepository
from ...repositories.finance_repository import FinanceRepository
from ...services.investment_service import InvestmentService
from ...utils.currency import format_currency
from ..widgets.card import Card
from ..widgets.data_table import DataTable
from ..widgets.pie_chart import PieChartWidget
from ..dialogs.holding_dialog import HoldingDialog
from ...core.constants import AccountType


class InvestmentsView(QWidget):
    """View for investment portfolio tracking."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._account_repo = AccountRepository()
        self._finance_repo = FinanceRepository()
        self._investment_service = InvestmentService(self._finance_repo)
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 16, 16, 16)
        outer.setSpacing(12)

        # Header
        header = QHBoxLayout()
        header.addWidget(QLabel("<h2>Investments</h2>"))
        header.addStretch()
        self._add_btn = QPushButton("+ Add Holding")
        self._add_btn.clicked.connect(self._on_add)
        header.addWidget(self._add_btn)
        outer.addLayout(header)

        # Summary cards row
        summary_row = QHBoxLayout()

        self._value_card = Card("Portfolio Value")
        self._value_label = QLabel("$0.00")
        self._value_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        self._value_card.add_widget(self._value_label)
        summary_row.addWidget(self._value_card)

        self._gl_card = Card("Total Gain/Loss")
        self._gl_label = QLabel("$0.00")
        self._gl_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self._gl_card.add_widget(self._gl_label)
        summary_row.addWidget(self._gl_card)

        outer.addLayout(summary_row)

        # Splitter: table left, pie right
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Holdings table
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.addWidget(QLabel("<b>Holdings</b>"))

        self._holdings_table = DataTable(
            ["ID", "Account", "Ticker/Name", "Type", "Shares", "Cost Basis", "Current Value", "Gain/Loss", "G/L %"]
        )
        self._holdings_table.setColumnHidden(0, True)  # hide ID column
        self._holdings_table.doubleClicked.connect(self._on_edit)
        left_layout.addWidget(self._holdings_table)
        splitter.addWidget(left)

        # Pie chart
        right = QWidget()
        right.setMaximumWidth(320)
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.addWidget(QLabel("<b>Asset Allocation</b>"))
        self._pie_chart = PieChartWidget()
        right_layout.addWidget(self._pie_chart)
        right_layout.addStretch()
        splitter.addWidget(right)

        splitter.setSizes([600, 280])
        outer.addWidget(splitter, 1)

    def _load_data(self):
        # Portfolio summary
        summary = self._investment_service.get_portfolio_summary()
        self._value_label.setText(format_currency(summary.total_current_value))
        gl = summary.total_gain_loss
        gl_pct = summary.total_gain_loss_percent
        colour = "#4CAF50" if gl >= 0 else "#F44336"
        sign = "+" if gl >= 0 else ""
        self._gl_label.setText(f"{format_currency(gl)} ({sign}{gl_pct:.1f}%)")
        self._gl_label.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {colour};")

        # Holdings table
        self._holdings_table.clear_data()
        holdings = self._finance_repo.get_all_holdings()
        accounts = {a.id: a.name for a in self._account_repo.get_all()}

        for h in holdings:
            gl_sign = "+" if h.gain_loss >= 0 else ""
            self._holdings_table.add_row([
                h.id,
                accounts.get(h.account_id, "—"),
                h.ticker_or_name,
                h.asset_type,
                f"{h.shares:.4f}",
                format_currency(h.cost_basis),
                format_currency(h.current_value),
                f"{gl_sign}{format_currency(h.gain_loss)}",
                f"{gl_sign}{h.gain_loss_percent:.1f}%",
            ])

        # Pie chart
        allocation = self._investment_service.get_asset_allocation()
        chart_data = [(a.asset_type.capitalize(), a.total_value) for a in allocation]
        self._pie_chart.set_data(chart_data)

    def _get_investment_accounts(self) -> list:
        accounts = self._account_repo.get_all()
        return [(a.id, a.name) for a in accounts
                if a.account_type == AccountType.INVESTMENT]

    def _on_add(self):
        accounts = self._get_investment_accounts()
        if not accounts:
            QMessageBox.warning(
                self, "No Investment Accounts",
                "Please create an investment account first (Accounts → Add Account → Investment)."
            )
            return
        dialog = HoldingDialog(accounts, self)
        if dialog.exec():
            self._investment_service.add_holding(
                account_id=dialog.get_account_id(),
                ticker=dialog.get_ticker(),
                asset_type=dialog.get_asset_type(),
                shares=dialog.get_shares(),
                cost_basis=dialog.get_cost_basis(),
                current_price=dialog.get_current_price(),
            )
            self._load_data()

    def _on_edit(self):
        row = self._holdings_table.currentRow()
        if row < 0:
            return
        holding_id_item = self._holdings_table.item(row, 0)
        if not holding_id_item:
            return
        holding_id = int(holding_id_item.text())
        holding = self._finance_repo.get_holding(holding_id)
        if not holding:
            return
        accounts = self._get_investment_accounts()
        dialog = HoldingDialog(accounts, self, holding=holding)
        if dialog.exec():
            self._investment_service.update_price(holding_id, dialog.get_current_price())
            self._load_data()

    def refresh(self):
        self._load_data()
