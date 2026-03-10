"""Reports view — monthly/annual financial reports with PDF and Excel export."""

import calendar
from datetime import date
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTabWidget, QComboBox, QFileDialog,
    QMessageBox,
)

from ...services.report_service import ReportService
from ...services.export_service import ExportService
from ...utils.currency import format_currency
from ..widgets.card import Card
from ..widgets.data_table import DataTable


_MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]


class ReportsView(QWidget):
    """View for generating and exporting financial reports."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._report_service = ReportService()
        self._export_service = ExportService()
        self._current_monthly = None
        self._current_annual = None
        self._setup_ui()
        self._load_monthly()

    def _setup_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 16, 16, 16)
        outer.setSpacing(12)

        # Header
        header = QHBoxLayout()
        header.addWidget(QLabel("<h2>Reports</h2>"))
        header.addStretch()
        self._export_pdf_btn = QPushButton("Export PDF")
        self._export_pdf_btn.clicked.connect(self._on_export_pdf)
        self._export_xlsx_btn = QPushButton("Export Excel")
        self._export_xlsx_btn.clicked.connect(self._on_export_xlsx)
        header.addWidget(self._export_pdf_btn)
        header.addWidget(self._export_xlsx_btn)
        outer.addLayout(header)

        # Tabs: Monthly / Annual
        self._tabs = QTabWidget()
        self._tabs.currentChanged.connect(self._on_tab_changed)

        # --- Monthly tab ---
        monthly_widget = QWidget()
        monthly_layout = QVBoxLayout(monthly_widget)
        monthly_layout.setContentsMargins(8, 8, 8, 8)
        monthly_layout.setSpacing(10)

        today = date.today()

        period_row = QHBoxLayout()
        self._month_combo = QComboBox()
        for i, name in enumerate(_MONTH_NAMES, 1):
            self._month_combo.addItem(name, i)
        self._month_combo.setCurrentIndex(today.month - 1)

        self._year_combo = QComboBox()
        for yr in range(today.year, today.year - 5, -1):
            self._year_combo.addItem(str(yr), yr)

        refresh_btn = QPushButton("Generate")
        refresh_btn.clicked.connect(self._load_monthly)

        period_row.addWidget(QLabel("Period:"))
        period_row.addWidget(self._month_combo)
        period_row.addWidget(self._year_combo)
        period_row.addWidget(refresh_btn)
        period_row.addStretch()
        monthly_layout.addLayout(period_row)

        # Summary cards
        sum_row = QHBoxLayout()
        self._m_income_card = Card("Income")
        self._m_income_label = QLabel("$0.00")
        self._m_income_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #4CAF50;")
        self._m_income_card.add_widget(self._m_income_label)
        sum_row.addWidget(self._m_income_card)

        self._m_expense_card = Card("Expenses")
        self._m_expense_label = QLabel("$0.00")
        self._m_expense_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #F44336;")
        self._m_expense_card.add_widget(self._m_expense_label)
        sum_row.addWidget(self._m_expense_card)

        self._m_net_card = Card("Net Change")
        self._m_net_label = QLabel("$0.00")
        self._m_net_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self._m_net_card.add_widget(self._m_net_label)
        sum_row.addWidget(self._m_net_card)

        monthly_layout.addLayout(sum_row)

        monthly_layout.addWidget(QLabel("<b>Spending by Category</b>"))
        self._m_category_table = DataTable(["Category", "Amount"])
        monthly_layout.addWidget(self._m_category_table)

        self._tabs.addTab(monthly_widget, "Monthly")

        # --- Annual tab ---
        annual_widget = QWidget()
        annual_layout = QVBoxLayout(annual_widget)
        annual_layout.setContentsMargins(8, 8, 8, 8)
        annual_layout.setSpacing(10)

        year_row = QHBoxLayout()
        self._annual_year_combo = QComboBox()
        for yr in range(today.year, today.year - 5, -1):
            self._annual_year_combo.addItem(str(yr), yr)
        refresh_annual_btn = QPushButton("Generate")
        refresh_annual_btn.clicked.connect(self._load_annual)
        year_row.addWidget(QLabel("Year:"))
        year_row.addWidget(self._annual_year_combo)
        year_row.addWidget(refresh_annual_btn)
        year_row.addStretch()
        annual_layout.addLayout(year_row)

        ann_sum_row = QHBoxLayout()
        self._a_income_card = Card("Total Income")
        self._a_income_label = QLabel("$0.00")
        self._a_income_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #4CAF50;")
        self._a_income_card.add_widget(self._a_income_label)
        ann_sum_row.addWidget(self._a_income_card)

        self._a_expense_card = Card("Total Expenses")
        self._a_expense_label = QLabel("$0.00")
        self._a_expense_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #F44336;")
        self._a_expense_card.add_widget(self._a_expense_label)
        ann_sum_row.addWidget(self._a_expense_card)

        self._a_savings_card = Card("Savings Rate")
        self._a_savings_label = QLabel("0.0%")
        self._a_savings_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2196F3;")
        self._a_savings_card.add_widget(self._a_savings_label)
        ann_sum_row.addWidget(self._a_savings_card)

        annual_layout.addLayout(ann_sum_row)

        annual_layout.addWidget(QLabel("<b>Monthly Breakdown</b>"))
        self._a_monthly_table = DataTable(["Month", "Income", "Expenses", "Net"])
        annual_layout.addWidget(self._a_monthly_table)

        self._tabs.addTab(annual_widget, "Annual")

        outer.addWidget(self._tabs, 1)

    def _load_monthly(self):
        month = self._month_combo.currentData()
        year = self._year_combo.currentData()
        report = self._report_service.generate_monthly_report(year, month)
        self._current_monthly = report

        self._m_income_label.setText(format_currency(report.income))
        self._m_expense_label.setText(format_currency(report.expenses))
        net = report.net_change
        colour = "#4CAF50" if net >= 0 else "#F44336"
        self._m_net_label.setText(format_currency(net))
        self._m_net_label.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {colour};")

        self._m_category_table.clear_data()
        for cat in report.top_categories:
            self._m_category_table.add_row([cat["name"], format_currency(cat["amount"])])

    def _load_annual(self):
        year = self._annual_year_combo.currentData()
        report = self._report_service.generate_annual_report(year)
        self._current_annual = report

        self._a_income_label.setText(format_currency(report.total_income))
        self._a_expense_label.setText(format_currency(report.total_expenses))
        self._a_savings_label.setText(f"{report.savings_rate:.1f}%")

        self._a_monthly_table.clear_data()
        for row in report.monthly_breakdown:
            self._a_monthly_table.add_row([
                calendar.month_abbr[row["month"]],
                format_currency(row["income"]),
                format_currency(row["expenses"]),
                format_currency(row["net"]),
            ])

    def _on_tab_changed(self, index: int):
        if index == 1 and self._current_annual is None:
            self._load_annual()

    def _on_export_pdf(self):
        self._do_export("pdf")

    def _on_export_xlsx(self):
        self._do_export("xlsx")

    def _do_export(self, fmt: str):
        tab = self._tabs.currentIndex()
        is_monthly = tab == 0
        filter_str = "PDF Files (*.pdf)" if fmt == "pdf" else "Excel Files (*.xlsx)"
        default_name = (
            f"report_{self._month_combo.currentData():02d}_{self._year_combo.currentData()}"
            if is_monthly
            else f"annual_{self._annual_year_combo.currentData()}"
        )
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Report", f"{default_name}.{fmt}", filter_str
        )
        if not path:
            return
        try:
            if is_monthly:
                if self._current_monthly is None:
                    self._load_monthly()
                if fmt == "pdf":
                    self._export_service.export_monthly_pdf(self._current_monthly, path)
                else:
                    self._export_service.export_monthly_xlsx(self._current_monthly, path)
            else:
                if self._current_annual is None:
                    self._load_annual()
                if fmt == "pdf":
                    self._export_service.export_annual_pdf(self._current_annual, path)
                else:
                    self._export_service.export_annual_xlsx(self._current_annual, path)
            QMessageBox.information(self, "Export Complete", f"Report saved to:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", str(e))

    def refresh(self):
        self._current_monthly = None
        self._current_annual = None
        self._load_monthly()
