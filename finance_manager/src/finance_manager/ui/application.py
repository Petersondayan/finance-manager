"""QApplication setup."""

import sys
import traceback
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon

from ..core.config import get_config
from ..core.logging import get_logger

# Enable high DPI scaling BEFORE creating QApplication
QApplication.setHighDpiScaleFactorRoundingPolicy(
    Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
)

logger = get_logger()


class Application(QApplication):
    """Application with custom setup."""
    
    def __init__(self, argv=None):
        argv = argv or sys.argv
        super().__init__(argv)
        
        self._setup_application()
    
    def _setup_application(self):
        """Setup application properties."""
        config = get_config()
        
        # Application metadata
        self.setApplicationName("Finance Manager")
        self.setApplicationVersion("1.0.0")
        self.setOrganizationName("FinanceManager")
        
        # App icon — resolve correctly in both dev and frozen (PyInstaller) environments
        base = Path(sys._MEIPASS) if hasattr(sys, "_MEIPASS") else Path(__file__).parent.parent
        icon_path = base / "assets" / "app_icon.ico"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        # Global font
        font = QFont("Segoe UI", 10)
        self.setFont(font)
        
        # Load and apply stylesheet
        self._apply_stylesheet()
        
        logger.info("Application initialized")
        self._install_exception_hooks()

    def _install_exception_hooks(self):
        """Install global exception handlers."""
        def _excepthook(exc_type, exc_value, exc_tb):
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_tb)
                return
            msg = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
            logger.error(f"Unhandled exception:\n{msg}")
            QMessageBox.critical(
                None,
                "Unexpected Error",
                f"An unexpected error occurred:\n\n{exc_value}\n\n"
                "The application will continue running. Check logs for details.",
            )

        sys.excepthook = _excepthook

    def notify(self, receiver, event):
        """Override to catch exceptions thrown during Qt event dispatch."""
        try:
            return super().notify(receiver, event)
        except Exception as e:
            msg = traceback.format_exc()
            logger.error(f"Unhandled Qt exception:\n{msg}")
            QMessageBox.critical(
                None,
                "Unexpected Error",
                f"An unexpected error occurred:\n\n{e}\n\n"
                "The application will continue running.",
            )
            return False
    
    def _apply_stylesheet(self):
        """Apply application stylesheet."""
        stylesheet = """
        QMainWindow {
            background-color: #f5f5f5;
        }
        
        QPushButton {
            background-color: #2196F3;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }
        
        QPushButton:hover {
            background-color: #1976D2;
        }
        
        QPushButton:pressed {
            background-color: #0D47A1;
        }
        
        QPushButton:disabled {
            background-color: #BDBDBD;
        }
        
        QTableWidget {
            background-color: white;
            alternate-background-color: #f5f5f5;
            border: 1px solid #ddd;
        }
        
        QTableWidget::item:selected {
            background-color: #2196F3;
            color: white;
        }
        
        QHeaderView::section {
            background-color: #E0E0E0;
            padding: 8px;
            border: none;
            font-weight: bold;
        }
        
        QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
            padding: 6px;
            border: 1px solid #ccc;
            border-radius: 4px;
            background-color: white;
        }
        
        QLineEdit:focus, QComboBox:focus {
            border: 2px solid #2196F3;
        }
        
        QGroupBox {
            font-weight: bold;
            border: 1px solid #ccc;
            border-radius: 4px;
            margin-top: 12px;
            padding-top: 12px;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }
        
        QLabel {
            color: #333;
        }
        
        QStatusBar {
            background-color: #E0E0E0;
        }
        
        QProgressBar {
            border: 1px solid #ccc;
            border-radius: 4px;
            text-align: center;
        }
        
        QProgressBar::chunk {
            background-color: #4CAF50;
            border-radius: 4px;
        }
        """
        
        self.setStyleSheet(stylesheet)
