"""Main window for GPT Window application."""

from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget

from gpt_window.config.logging_config import get_logger
from gpt_window.ui.control_panel import ControlPanel
from gpt_window.ui.transparent_window import TransparentWindow

logger = get_logger(__name__)


class MainWindow(QMainWindow):
    """
    Main application window containing the control panel.

    This window manages the lifecycle of the transparent window and control panel.
    """

    def __init__(self) -> None:
        """Initialize the main window."""
        super().__init__()
        self._init_ui()
        logger.info("Main window initialized")

    def _init_ui(self) -> None:
        """Initialize the user interface."""
        self.setWindowTitle("GPT Vision Interface")
        self.setGeometry(100, 100, 600, 400)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create and show transparent window
        self.transparent_window = TransparentWindow()
        self.transparent_window.show()
        logger.info("Transparent window created and shown")

        # Create control panel
        self.control_panel = ControlPanel(self.transparent_window)
        layout.addWidget(self.control_panel)
        logger.info("Control panel created")

    def closeEvent(self, event) -> None:  # type: ignore
        """
        Handle window close event.

        Args:
            event: QCloseEvent.
        """
        logger.info("Main window closing")
        self.transparent_window.close()
        event.accept()
