"""Main application window."""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QStackedWidget, QStatusBar, QLabel, 
    QFrame, QSplitter, QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction

from ..core.config import get_config
from ..core.logging import get_logger
from ..database.connection import get_db_manager
from ..database.migrations import run_migrations
from .views.accounts_view import AccountsView
from .views.transactions_view import TransactionsView
from .views.dashboard_view import DashboardView
from .views.budgets_view import BudgetsView
from .views.goals_view import GoalsView
from .views.investments_view import InvestmentsView
from .views.reports_view import ReportsView

logger = get_logger()


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        
        self._config = get_config()
        self._setup_window()
        self._create_menu_bar()
        self._create_central_widget()
        self._create_status_bar()
        
        # Initialize database
        self._init_database()
    
    def _setup_window(self):
        """Setup window properties."""
        self.setWindowTitle("Personal Finance Manager")
        self.setMinimumSize(1000, 700)
        self.resize(
            self._config.window.width,
            self._config.window.height
        )
    
    def _create_menu_bar(self):
        """Create menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        import_action = QAction("&Import Statement...", self)
        import_action.setShortcut("Ctrl+I")
        import_action.triggered.connect(self._on_import)
        file_menu.addAction(import_action)
        
        export_action = QAction("&Export Report...", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self._on_export)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        
        prefs_action = QAction("&Preferences...", self)
        prefs_action.triggered.connect(self._on_preferences)
        edit_menu.addAction(prefs_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)
    
    def _create_central_widget(self):
        """Create central widget with sidebar and content."""
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Sidebar
        self._sidebar = self._create_sidebar()
        layout.addWidget(self._sidebar)
        
        # Content area
        self._content = QStackedWidget()
        layout.addWidget(self._content, 1)
        
        # Add placeholder views
        self._create_placeholder_views()
    
    def _create_sidebar(self) -> QWidget:
        """Create navigation sidebar."""
        sidebar = QFrame()
        sidebar.setFrameStyle(QFrame.Shape.StyledPanel)
        sidebar.setMaximumWidth(200)
        sidebar.setMinimumWidth(180)
        
        layout = QVBoxLayout(sidebar)
        layout.setSpacing(8)
        layout.setContentsMargins(8, 16, 8, 16)
        
        # Navigation buttons
        nav_buttons = [
            ("Dashboard", self._show_dashboard),
            ("Accounts", self._show_accounts),
            ("Transactions", self._show_transactions),
            ("Budgets", self._show_budgets),
            ("Goals", self._show_goals),
            ("Investments", self._show_investments),
            ("Reports", self._show_reports),
        ]
        
        for text, callback in nav_buttons:
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.clicked.connect(callback)
            layout.addWidget(btn)
        
        layout.addStretch()
        
        # Settings button at bottom
        settings_btn = QPushButton("Settings")
        settings_btn.clicked.connect(self._on_preferences)
        layout.addWidget(settings_btn)
        
        return sidebar
    
    def _create_placeholder_views(self):
        """Create views."""
        # Dashboard
        self._dashboard_view = DashboardView()
        self._content.addWidget(self._dashboard_view)
        
        # Accounts
        self._accounts_view = AccountsView()
        self._content.addWidget(self._accounts_view)
        
        # Transactions
        self._transactions_view = TransactionsView()
        self._content.addWidget(self._transactions_view)
        
        # Budgets
        self._budgets_view = BudgetsView()
        self._content.addWidget(self._budgets_view)
        
        # Goals
        self._goals_view = GoalsView()
        self._content.addWidget(self._goals_view)
        
        # Investments
        self._investments_view = InvestmentsView()
        self._content.addWidget(self._investments_view)
        
        # Reports
        self._reports_view = ReportsView()
        self._content.addWidget(self._reports_view)
    
    def _create_status_bar(self):
        """Create status bar."""
        self._statusbar = QStatusBar()
        self.setStatusBar(self._statusbar)
        
        self._statusbar.showMessage("Ready")
        
        # Add permanent widgets
        self._db_label = QLabel("DB: Not connected")
        self._statusbar.addPermanentWidget(self._db_label)
    
    def _init_database(self):
        """Initialize database connection."""
        try:
            db_manager = get_db_manager()
            db_manager.initialize()
            run_migrations()
            
            self._db_label.setText(f"DB: {db_manager.db_path.name}")
            logger.info("Database initialized")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            QMessageBox.critical(self, "Error", f"Failed to initialize database: {e}")
    
    # Navigation handlers
    def _show_dashboard(self):
        self._content.setCurrentIndex(0)
        self._dashboard_view.refresh()
        self._statusbar.showMessage("Dashboard")
    
    def _show_accounts(self):
        self._content.setCurrentIndex(1)
        self._statusbar.showMessage("Accounts")
    
    def _show_transactions(self):
        self._content.setCurrentIndex(2)
        self._statusbar.showMessage("Transactions")
    
    def _show_budgets(self):
        self._content.setCurrentIndex(3)
        self._budgets_view.refresh()
        self._statusbar.showMessage("Budgets")
    
    def _show_goals(self):
        self._content.setCurrentIndex(4)
        self._goals_view.refresh()
        self._statusbar.showMessage("Goals")
    
    def _show_investments(self):
        self._content.setCurrentIndex(5)
        self._investments_view.refresh()
        self._statusbar.showMessage("Investments")
    
    def _show_reports(self):
        self._content.setCurrentIndex(6)
        self._reports_view.refresh()
        self._statusbar.showMessage("Reports")
    
    # Menu handlers
    def _on_import(self):
        """Handle import statement."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Statement",
            "",
            "Statement Files (*.pdf *.csv *.xlsx *.docx);;All Files (*)"
        )
        if file_path:
            self._statusbar.showMessage(f"Importing: {file_path}")
    
    def _on_export(self):
        """Handle export report — navigate to Reports and trigger PDF export."""
        self._show_reports()
        self._reports_view._on_export_pdf()
    
    def _on_preferences(self):
        """Handle preferences."""
        self._statusbar.showMessage("Preferences not yet implemented")
    
    def _on_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About Finance Manager",
            "<h2>Personal Finance Manager</h2>"
            "<p>Version 1.0.0</p>"
            "<p>A desktop application for personal finance management with AI-powered insights.</p>"
        )
    
    def closeEvent(self, event):
        """Handle window close."""
        # Save window size
        self._config.window.width = self.width()
        self._config.window.height = self.height()
        from ..core.config import get_config_manager
        get_config_manager().save()
        
        event.accept()
