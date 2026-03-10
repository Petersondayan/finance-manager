"""Budget service."""

from typing import List, Optional
from datetime import date

from ..repositories.finance_repository import FinanceRepository
from ..models.budget import Budget, BudgetStatus
from ..core.logging import get_logger

logger = get_logger()


class BudgetService:
    """Service for budget business logic."""
    
    def __init__(self, finance_repo: Optional[FinanceRepository] = None):
        self._finance_repo = finance_repo or FinanceRepository()
    
    def create_budget(self, category_id: int, monthly_limit: float, 
                     period: Optional[str] = None, alert_threshold: float = 0.8) -> Budget:
        """Create new budget for category."""
        # Default to current month if no period specified
        if period is None:
            today = date.today()
            period = f"{today.year:04d}-{today.month:02d}"
        
        # Check if budget already exists
        existing = self._finance_repo.get_budget(category_id, period)
        if existing:
            raise ValueError(f"Budget already exists for category {category_id} in {period}")
        
        budget = Budget(
            category_id=category_id,
            monthly_limit=monthly_limit,
            period=period,
            alert_threshold=alert_threshold
        )
        
        created = self._finance_repo.create_budget(budget)
        logger.info(f"Created budget: ${monthly_limit:.2f} for period {period}")
        return created
    
    def get_current_budgets(self) -> List[BudgetStatus]:
        """Get all budgets for current month with status."""
        today = date.today()
        period = f"{today.year:04d}-{today.month:02d}"
        return self._finance_repo.get_budget_status(period)
    
    def get_budget_status(self, period: str) -> List[BudgetStatus]:
        """Get budget status for specific period."""
        return self._finance_repo.get_budget_status(period)
    
    def check_alerts(self) -> List[dict]:
        """Check for budgets approaching or exceeding limits."""
        budgets = self.get_current_budgets()
        alerts = []
        
        for status in budgets:
            if status.is_exceeded:
                alerts.append({
                    "budget_id": status.budget.id,
                    "category": status.category_name,
                    "status": "exceeded",
                    "message": f"Budget exceeded: {status.category_name} (${status.spent:.2f} / ${status.budget.monthly_limit:.2f})"
                })
            elif status.is_warning:
                alerts.append({
                    "budget_id": status.budget.id,
                    "category": status.category_name,
                    "status": "warning",
                    "message": f"Budget warning: {status.category_name} at {status.percent_used:.0f}%"
                })
        
        return alerts
    
    def update_budget_amount(self, budget_id: int, new_limit: float) -> Optional[Budget]:
        """Update budget limit in-place."""
        budget = self._finance_repo.get_budget_by_id(budget_id)
        if budget is None:
            return None
        return self._finance_repo.update_budget_limit(budget_id, new_limit)
    
    def copy_budgets_to_period(self, from_period: str, to_period: str) -> int:
        """Copy all budgets from one period to another."""
        budgets = self._finance_repo.get_budgets_for_period(from_period)
        copied = 0
        
        for budget in budgets:
            try:
                self.create_budget(
                    category_id=budget.category_id,
                    monthly_limit=budget.monthly_limit,
                    period=to_period,
                    alert_threshold=budget.alert_threshold
                )
                copied += 1
            except ValueError:
                # Budget already exists
                pass
        
        logger.info(f"Copied {copied} budgets from {from_period} to {to_period}")
        return copied
    
    def get_spending_trend(self, category_id: int, months: int = 6) -> List[dict]:
        """Get spending trend for category over months."""
        # This would need a custom query in the repository
        return []
