"""Goals view — savings targets, debt payoff, retirement."""

from datetime import date
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QProgressBar, QScrollArea, QFrame,
    QMessageBox, QInputDialog,
)
from PyQt6.QtCore import Qt

from ...services.goal_service import GoalService
from ...utils.currency import format_currency
from ..widgets.card import Card
from ..dialogs.goal_dialog import GoalDialog


_TYPE_LABELS = {
    "savings": "Savings",
    "debt_payoff": "Debt Payoff",
    "retirement": "Retirement",
}


class GoalsView(QWidget):
    """View for managing financial goals."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._goal_service = GoalService()
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

        header = QHBoxLayout()
        header.addWidget(QLabel("<h2>Goals</h2>"))
        header.addStretch()

        self._add_btn = QPushButton("+ Add Goal")
        self._add_btn.clicked.connect(self._on_add)
        header.addWidget(self._add_btn)

        main.addLayout(header)

        goals_card = Card("Active Goals")
        self._goals_container = QVBoxLayout()
        self._goals_container.setSpacing(10)
        goals_card._content_layout.addLayout(self._goals_container)
        main.addWidget(goals_card)

        main.addStretch()

    def _load_data(self):
        while self._goals_container.count():
            item = self._goals_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        goals = self._goal_service.get_active_goals()
        if not goals:
            self._goals_container.addWidget(
                QLabel("No active goals. Click '+ Add Goal' to create one.")
            )
            return

        for goal in goals:
            self._goals_container.addWidget(self._make_goal_card(goal))

    def _make_goal_card(self, goal) -> QWidget:
        card = QWidget()
        card.setStyleSheet("background: white; border: 1px solid #ddd; border-radius: 6px;")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)

        # Title row
        title_row = QHBoxLayout()
        type_label = QLabel(f"<small>{_TYPE_LABELS.get(goal.goal_type, goal.goal_type)}</small>")
        type_label.setStyleSheet("color: #888;")
        title_row.addWidget(type_label)
        title_row.addStretch()

        # Action buttons
        add_btn = QPushButton("+ Progress")
        add_btn.setMaximumWidth(90)
        add_btn.clicked.connect(lambda _, g=goal: self._on_add_progress(g))
        title_row.addWidget(add_btn)

        complete_btn = QPushButton("Complete")
        complete_btn.setMaximumWidth(80)
        complete_btn.clicked.connect(lambda _, g=goal: self._on_complete(g))
        title_row.addWidget(complete_btn)

        layout.addLayout(title_row)

        name_label = QLabel(f"<b>{goal.name}</b>")
        name_label.setStyleSheet("font-size: 14px;")
        layout.addWidget(name_label)

        # Progress bar
        bar = QProgressBar()
        bar.setMinimum(0)
        bar.setMaximum(100)
        pct = min(int(goal.percent_complete), 100)
        bar.setValue(pct)
        bar.setStyleSheet("""
            QProgressBar { border: 1px solid #ccc; border-radius: 4px; text-align: center; height: 22px; }
            QProgressBar::chunk { background-color: #2196F3; }
        """)
        bar.setFormat(
            f"{pct}%  ({format_currency(goal.current_amount)} / {format_currency(goal.target_amount)})"
        )
        layout.addWidget(bar)

        # Projection line
        if goal.deadline:
            days_left = (goal.deadline - date.today()).days
            projection = self._goal_service.get_projections(goal, goal.current_amount / max(1, 30))
            if projection.estimated_completion_date:
                proj_text = f"Est. completion: {projection.estimated_completion_date}  |  Deadline: {goal.deadline}  |  Days left: {days_left}"
            else:
                proj_text = f"Deadline: {goal.deadline}  |  Days left: {days_left}"
            proj_label = QLabel(proj_text)
            proj_label.setStyleSheet("color: #666; font-size: 12px;")
            layout.addWidget(proj_label)

        if goal.strategy:
            strat_label = QLabel(f"Strategy: {goal.strategy.capitalize()}")
            strat_label.setStyleSheet("color: #888; font-size: 11px;")
            layout.addWidget(strat_label)

        return card

    def _on_add(self):
        dialog = GoalDialog(self)
        if not dialog.exec():
            return

        goal_type = dialog.get_goal_type()
        name = dialog.get_name()
        target = dialog.get_target_amount()
        deadline = dialog.get_deadline()

        if goal_type == "savings":
            self._goal_service.create_savings_goal(name, target, deadline)
        elif goal_type == "debt_payoff":
            self._goal_service.create_debt_payoff_goal(name, target, dialog.get_strategy(), deadline)
        else:
            self._goal_service.create_retirement_goal(name, target, deadline)

        self._load_data()

    def _on_add_progress(self, goal):
        amount, ok = QInputDialog.getDouble(
            self, "Add Progress",
            f"Amount to add toward '{goal.name}':",
            min=0.01, max=999999.99, decimals=2
        )
        if ok and amount > 0:
            self._goal_service.add_progress(goal.id, amount)
            self._load_data()

    def _on_complete(self, goal):
        reply = QMessageBox.question(
            self, "Complete Goal",
            f"Mark '{goal.name}' as complete?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._goal_service.complete_goal(goal.id)
            self._load_data()

    def refresh(self):
        self._load_data()
