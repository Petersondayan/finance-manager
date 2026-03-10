"""Finance repository - consolidates budgets, goals, investments, and insights."""

from typing import List, Optional
from datetime import date, datetime
import json

from ..database.connection import DatabaseManager, get_db_manager
from ..models.budget import Budget, BudgetStatus
from ..models.category import Category
from ..models.goal import Goal
from ..models.investment import InvestmentHolding, PortfolioSummary, AssetAllocation
from ..models.ai_insight import AIInsight
from ..models.net_worth_snapshot import NetWorthSnapshot
from ..core.logging import get_logger

logger = get_logger()


class FinanceRepository:
    """Repository for financial data: budgets, goals, investments, insights."""
    
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self._db = db_manager or get_db_manager()
    
    # ========== Budgets ==========
    
    def create_budget(self, budget: Budget) -> Budget:
        """Create new budget."""
        query = """
            INSERT INTO budgets (category_id, monthly_limit, period, alert_threshold, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        now = datetime.now()
        params = (budget.category_id, budget.monthly_limit, budget.period, 
                 budget.alert_threshold, now, now)
        
        cursor = self._db.execute(query, params)
        self._db.commit()
        
        budget.id = cursor.lastrowid
        budget.created_at = now
        budget.updated_at = now
        return budget
    
    def get_budget(self, category_id: int, period: str) -> Optional[Budget]:
        """Get budget for category and period."""
        query = "SELECT * FROM budgets WHERE category_id = ? AND period = ?"
        row = self._db.fetch_one(query, (category_id, period))
        return self._row_to_budget(row) if row else None
    
    def get_budgets_for_period(self, period: str) -> List[Budget]:
        """Get all budgets for a period."""
        query = "SELECT * FROM budgets WHERE period = ?"
        rows = self._db.fetch_all(query, (period,))
        return [self._row_to_budget(row) for row in rows]
    
    def get_budget_status(self, period: str) -> List[BudgetStatus]:
        """Get budget status with current spending."""
        query = """
            SELECT b.*, c.name as category_name, 
                   COALESCE(SUM(ABS(t.amount)), 0) as spent
            FROM budgets b
            JOIN categories c ON b.category_id = c.id
            LEFT JOIN transactions t ON t.category_id = b.category_id 
                AND strftime('%Y-%m', t.date) = b.period
            WHERE b.period = ?
            GROUP BY b.id
            ORDER BY spent DESC
        """
        rows = self._db.fetch_all(query, (period,))
        
        statuses = []
        for row in rows:
            budget = self._row_to_budget(row)
            status = BudgetStatus(
                budget=budget,
                category_name=row['category_name'],
                spent=row['spent']
            )
            statuses.append(status)
        return statuses
    
    def update_budget(self, budget: Budget) -> Budget:
        """Update budget."""
        query = """
            UPDATE budgets 
            SET monthly_limit = ?, alert_threshold = ?, updated_at = ?
            WHERE id = ?
        """
        now = datetime.now()
        self._db.execute(query, (budget.monthly_limit, budget.alert_threshold, now, budget.id))
        self._db.commit()
        budget.updated_at = now
        return budget
    
    def get_budget_by_id(self, budget_id: int) -> Optional[Budget]:
        """Get a budget by its primary key."""
        query = "SELECT * FROM budgets WHERE id = ?"
        row = self._db.fetch_one(query, (budget_id,))
        return self._row_to_budget(row) if row else None

    def update_budget_limit(self, budget_id: int, new_limit: float) -> Optional[Budget]:
        """Update monthly_limit for an existing budget."""
        query = "UPDATE budgets SET monthly_limit = ?, updated_at = ? WHERE id = ?"
        now = datetime.now()
        self._db.execute(query, (new_limit, now, budget_id))
        self._db.commit()
        return self.get_budget_by_id(budget_id)

    def delete_budget(self, budget_id: int) -> bool:
        """Delete budget."""
        query = "DELETE FROM budgets WHERE id = ?"
        cursor = self._db.execute(query, (budget_id,))
        self._db.commit()
        return cursor.rowcount > 0

    def get_categories(self):
        """Get all categories."""
        query = "SELECT id, name, type, color_hex, icon, is_system, parent_category_id, created_at FROM categories ORDER BY name"
        rows = self._db.fetch_all(query)
        return [
            Category(
                id=row['id'],
                name=row['name'],
                type=row['type'],
                color_hex=row['color_hex'],
                icon=row['icon'],
                is_system=bool(row['is_system']),
                parent_category_id=row['parent_category_id'],
                created_at=row['created_at'],
            )
            for row in rows
        ]
    
    # ========== Goals ==========
    
    def create_goal(self, goal: Goal) -> Goal:
        """Create new goal."""
        query = """
            INSERT INTO goals (name, goal_type, target_amount, current_amount, deadline,
                             linked_account_id, strategy, notes, is_active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        now = datetime.now()
        params = (goal.name, goal.goal_type, goal.target_amount, goal.current_amount,
                 goal.deadline.isoformat() if goal.deadline else None,
                 goal.linked_account_id, goal.strategy, goal.notes, goal.is_active, now, now)
        
        cursor = self._db.execute(query, params)
        self._db.commit()
        
        goal.id = cursor.lastrowid
        goal.created_at = now
        goal.updated_at = now
        return goal
    
    def get_goal(self, goal_id: int) -> Optional[Goal]:
        """Get goal by ID."""
        query = "SELECT * FROM goals WHERE id = ?"
        row = self._db.fetch_one(query, (goal_id,))
        return self._row_to_goal(row) if row else None
    
    def get_active_goals(self, goal_type: Optional[str] = None) -> List[Goal]:
        """Get active goals, optionally filtered by type."""
        if goal_type:
            query = "SELECT * FROM goals WHERE is_active = 1 AND goal_type = ? ORDER BY deadline"
            rows = self._db.fetch_all(query, (goal_type,))
        else:
            query = "SELECT * FROM goals WHERE is_active = 1 ORDER BY deadline"
            rows = self._db.fetch_all(query)
        return [self._row_to_goal(row) for row in rows]
    
    def update_goal(self, goal: Goal) -> Goal:
        """Update goal."""
        query = """
            UPDATE goals 
            SET name = ?, target_amount = ?, current_amount = ?, deadline = ?,
                strategy = ?, notes = ?, is_active = ?, updated_at = ?
            WHERE id = ?
        """
        now = datetime.now()
        params = (goal.name, goal.target_amount, goal.current_amount,
                 goal.deadline.isoformat() if goal.deadline else None,
                 goal.strategy, goal.notes, goal.is_active, now, goal.id)
        
        self._db.execute(query, params)
        self._db.commit()
        goal.updated_at = now
        return goal
    
    def update_goal_progress(self, goal_id: int, amount: float) -> bool:
        """Update goal progress amount."""
        query = "UPDATE goals SET current_amount = ?, updated_at = ? WHERE id = ?"
        cursor = self._db.execute(query, (amount, datetime.now(), goal_id))
        self._db.commit()
        return cursor.rowcount > 0
    
    def delete_goal(self, goal_id: int) -> bool:
        """Delete goal."""
        query = "DELETE FROM goals WHERE id = ?"
        cursor = self._db.execute(query, (goal_id,))
        self._db.commit()
        return cursor.rowcount > 0
    
    # ========== Investments ==========
    
    def create_holding(self, holding: InvestmentHolding) -> InvestmentHolding:
        """Create new investment holding."""
        query = """
            INSERT INTO investments (account_id, ticker_or_name, asset_type, shares, cost_basis,
                                   current_value, last_price, as_of_date, notes, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        now = datetime.now()
        params = (holding.account_id, holding.ticker_or_name, holding.asset_type,
                 holding.shares, holding.cost_basis, holding.current_value,
                 holding.last_price, holding.as_of_date.isoformat() if holding.as_of_date else None,
                 holding.notes, now, now)
        
        cursor = self._db.execute(query, params)
        self._db.commit()
        
        holding.id = cursor.lastrowid
        holding.created_at = now
        holding.updated_at = now
        return holding
    
    def get_holding(self, holding_id: int) -> Optional[InvestmentHolding]:
        """Get holding by ID."""
        query = "SELECT * FROM investments WHERE id = ?"
        row = self._db.fetch_one(query, (holding_id,))
        return self._row_to_investment(row) if row else None
    
    def get_holdings_by_account(self, account_id: int) -> List[InvestmentHolding]:
        """Get holdings for an account."""
        query = "SELECT * FROM investments WHERE account_id = ? ORDER BY ticker_or_name"
        rows = self._db.fetch_all(query, (account_id,))
        return [self._row_to_investment(row) for row in rows]
    
    def get_all_holdings(self) -> List[InvestmentHolding]:
        """Get all holdings."""
        query = """
            SELECT i.*, a.name as account_name 
            FROM investments i
            JOIN accounts a ON i.account_id = a.id
            ORDER BY i.ticker_or_name
        """
        rows = self._db.fetch_all(query)
        return [self._row_to_investment(row) for row in rows]
    
    def update_holding(self, holding: InvestmentHolding) -> InvestmentHolding:
        """Update holding."""
        query = """
            UPDATE investments 
            SET shares = ?, cost_basis = ?, current_value = ?, last_price = ?,
                as_of_date = ?, notes = ?, updated_at = ?
            WHERE id = ?
        """
        now = datetime.now()
        params = (holding.shares, holding.cost_basis, holding.current_value,
                 holding.last_price, holding.as_of_date.isoformat() if holding.as_of_date else None,
                 holding.notes, now, holding.id)
        
        self._db.execute(query, params)
        self._db.commit()
        holding.updated_at = now
        return holding
    
    def update_holding_price(self, holding_id: int, price: float, as_of: date) -> bool:
        """Update holding price."""
        query = """
            UPDATE investments 
            SET last_price = ?, current_value = last_price * shares, as_of_date = ?, updated_at = ?
            WHERE id = ?
        """
        cursor = self._db.execute(query, (price, as_of.isoformat(), datetime.now(), holding_id))
        self._db.commit()
        return cursor.rowcount > 0
    
    def delete_holding(self, holding_id: int) -> bool:
        """Delete holding."""
        query = "DELETE FROM investments WHERE id = ?"
        cursor = self._db.execute(query, (holding_id,))
        self._db.commit()
        return cursor.rowcount > 0
    
    def get_portfolio_summary(self) -> PortfolioSummary:
        """Get portfolio summary."""
        query = """
            SELECT SUM(cost_basis) as total_cost, SUM(COALESCE(current_value, cost_basis)) as total_value
            FROM investments
        """
        row = self._db.fetch_one(query)
        
        cost = row[0] or 0
        value = row[1] or 0
        
        return PortfolioSummary(
            total_cost_basis=cost,
            total_current_value=value,
            total_gain_loss=value - cost
        )
    
    def get_asset_allocation(self) -> List[AssetAllocation]:
        """Get asset allocation breakdown."""
        query = """
            SELECT asset_type, SUM(COALESCE(current_value, cost_basis)) as value, COUNT(*) as count
            FROM investments
            GROUP BY asset_type
        """
        rows = self._db.fetch_all(query)
        
        # Calculate total
        total = sum(row[1] for row in rows)
        
        allocations = []
        for row in rows:
            allocations.append(AssetAllocation(
                asset_type=row[0],
                total_value=row[1],
                percentage=(row[1] / total * 100) if total > 0 else 0,
                holdings_count=row[2]
            ))
        return allocations
    
    # ========== AI Insights ==========
    
    def create_insight(self, insight: AIInsight) -> AIInsight:
        """Create new AI insight."""
        query = """
            INSERT INTO ai_insights (period, insight_type, summary_text, data_json, model_used, generated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        now = datetime.now()
        params = (insight.period, insight.insight_type, insight.summary_text,
                 insight.data_json, insight.model_used, now)
        
        cursor = self._db.execute(query, params)
        self._db.commit()
        
        insight.id = cursor.lastrowid
        insight.generated_at = now
        return insight
    
    def get_insights(self, period: str, insight_type: Optional[str] = None) -> List[AIInsight]:
        """Get insights for period."""
        if insight_type:
            query = """
                SELECT * FROM ai_insights 
                WHERE period = ? AND insight_type = ?
                ORDER BY generated_at DESC
            """
            rows = self._db.fetch_all(query, (period, insight_type))
        else:
            query = "SELECT * FROM ai_insights WHERE period = ? ORDER BY generated_at DESC"
            rows = self._db.fetch_all(query, (period,))
        return [self._row_to_insight(row) for row in rows]
    
    def get_latest_insight(self, insight_type: str) -> Optional[AIInsight]:
        """Get latest insight of specific type."""
        query = """
            SELECT * FROM ai_insights 
            WHERE insight_type = ?
            ORDER BY generated_at DESC
            LIMIT 1
        """
        row = self._db.fetch_one(query, (insight_type,))
        return self._row_to_insight(row) if row else None
    
    # ========== Net Worth Snapshots ==========
    
    def create_snapshot(self, snapshot: NetWorthSnapshot) -> NetWorthSnapshot:
        """Create net worth snapshot."""
        query = """
            INSERT INTO net_worth_snapshots (snapshot_date, total_assets, total_liabilities, net_worth, breakdown_json)
            VALUES (?, ?, ?, ?, ?)
        """
        params = (snapshot.snapshot_date.isoformat(), snapshot.total_assets,
                 snapshot.total_liabilities, snapshot.net_worth, snapshot.breakdown_json)
        
        cursor = self._db.execute(query, params)
        self._db.commit()
        
        snapshot.id = cursor.lastrowid
        return snapshot
    
    def get_snapshot(self, snapshot_date: date) -> Optional[NetWorthSnapshot]:
        """Get snapshot for date."""
        query = "SELECT * FROM net_worth_snapshots WHERE snapshot_date = ?"
        row = self._db.fetch_one(query, (snapshot_date.isoformat(),))
        return self._row_to_snapshot(row) if row else None
    
    def get_snapshots(self, start_date: date, end_date: date) -> List[NetWorthSnapshot]:
        """Get snapshots in date range."""
        query = """
            SELECT * FROM net_worth_snapshots 
            WHERE snapshot_date >= ? AND snapshot_date <= ?
            ORDER BY snapshot_date
        """
        rows = self._db.fetch_all(query, (start_date.isoformat(), end_date.isoformat()))
        return [self._row_to_snapshot(row) for row in rows]
    
    def get_latest_snapshot(self) -> Optional[NetWorthSnapshot]:
        """Get most recent snapshot."""
        query = "SELECT * FROM net_worth_snapshots ORDER BY snapshot_date DESC LIMIT 1"
        row = self._db.fetch_one(query)
        return self._row_to_snapshot(row) if row else None
    
    # ========== Helper Methods ==========
    
    def _row_to_budget(self, row) -> Budget:
        return Budget(
            id=row['id'],
            category_id=row['category_id'],
            monthly_limit=row['monthly_limit'],
            period=row['period'],
            alert_threshold=row['alert_threshold'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
    
    def _row_to_goal(self, row) -> Goal:
        return Goal(
            id=row['id'],
            name=row['name'],
            goal_type=row['goal_type'],
            target_amount=row['target_amount'],
            current_amount=row['current_amount'],
            deadline=date.fromisoformat(row['deadline']) if row['deadline'] else None,
            linked_account_id=row['linked_account_id'],
            strategy=row['strategy'],
            notes=row['notes'],
            is_active=bool(row['is_active']),
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
    
    def _row_to_investment(self, row) -> InvestmentHolding:
        return InvestmentHolding(
            id=row['id'],
            account_id=row['account_id'],
            ticker_or_name=row['ticker_or_name'],
            asset_type=row['asset_type'],
            shares=row['shares'],
            cost_basis=row['cost_basis'],
            current_value=row['current_value'],
            last_price=row['last_price'],
            as_of_date=date.fromisoformat(row['as_of_date']) if row['as_of_date'] else None,
            notes=row['notes'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
    
    def _row_to_insight(self, row) -> AIInsight:
        return AIInsight(
            id=row['id'],
            period=row['period'],
            insight_type=row['insight_type'],
            summary_text=row['summary_text'],
            data_json=row['data_json'],
            model_used=row['model_used'],
            generated_at=row['generated_at']
        )
    
    def _row_to_snapshot(self, row) -> NetWorthSnapshot:
        return NetWorthSnapshot(
            id=row['id'],
            snapshot_date=date.fromisoformat(row['snapshot_date']),
            total_assets=row['total_assets'],
            total_liabilities=row['total_liabilities'],
            net_worth=row['net_worth'],
            breakdown_json=row['breakdown_json'],
            created_at=row['created_at']
        )
