"""Control panel UI for GPT Window."""

from typing import Optional

from PyQt5.QtCore import QPoint, QRect
from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from gpt_window.config.logging_config import get_logger
from gpt_window.core.api.openai_handler import OpenAIHandler
from gpt_window.core.exceptions import APIKeyError, APIResponseError, ScreenshotError
from gpt_window.core.utils.screenshot import capture_screenshot
from gpt_window.ui.transparent_window import TransparentWindow

logger = get_logger(__name__)


class ControlPanel(QWidget):
    """
    Control panel for managing API key, queries, and screenshot analysis.

    This panel provides the user interface for:
    - Setting the OpenAI API key
    - Entering queries about the screenshot
    - Viewing API responses
    """

    def __init__(self, transparent_window: TransparentWindow) -> None:
        """
        Initialize the control panel.

        Args:
            transparent_window: The transparent window used for screenshot selection.
        """
        super().__init__()
        self.transparent_window = transparent_window
        self.api_handler = OpenAIHandler()
        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize the user interface components."""
        self.setWindowTitle("GPT Vision Controls")
        layout = QVBoxLayout()

        # API Key input section
        self._setup_api_key_section(layout)

        # Query input section
        self._setup_query_section(layout)

        # Send button
        self._setup_send_button(layout)

        # Output section
        self._setup_output_section(layout)

        self.setLayout(layout)

    def _setup_api_key_section(self, layout: QVBoxLayout) -> None:
        """
        Set up the API key input section.

        Args:
            layout: The parent layout to add widgets to.
        """
        api_key_layout = QHBoxLayout()
        api_key_label = QLabel("API Key:")
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setPlaceholderText("Enter your OpenAI API key (sk-...)")

        # Load existing API key if available (show placeholder instead of actual key)
        if self.api_handler.api_key:
            self.api_key_input.setPlaceholderText("API key loaded from environment")

        api_key_layout.addWidget(api_key_label)
        api_key_layout.addWidget(self.api_key_input)
        layout.addLayout(api_key_layout)

    def _setup_query_section(self, layout: QVBoxLayout) -> None:
        """
        Set up the query input section.

        Args:
            layout: The parent layout to add widgets to.
        """
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Enter your query here...")
        self.input_text.setMaximumHeight(50)
        layout.addWidget(self.input_text)

    def _setup_send_button(self, layout: QVBoxLayout) -> None:
        """
        Set up the send button.

        Args:
            layout: The parent layout to add widgets to.
        """
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self._on_send_clicked)
        layout.addWidget(self.send_button)

    def _setup_output_section(self, layout: QVBoxLayout) -> None:
        """
        Set up the output text area.

        Args:
            layout: The parent layout to add widgets to.
        """
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setPlaceholderText("API responses will appear here...")
        layout.addWidget(self.output_text)

    def _on_send_clicked(self) -> None:
        """Handle the send button click event."""
        try:
            # Get and validate API key
            api_key = self.api_key_input.text()
            if not api_key and not self.api_handler.api_key:
                self.output_text.setPlainText(
                    "Error: Please enter your API key or set the OPENAI_API_KEY environment variable."
                )
                logger.warning("Send clicked without API key")
                return

            # Set API key if provided
            if api_key:
                self.api_handler.set_api_key(api_key)
                # Clear the input field for security
                self.api_key_input.clear()
                self.api_key_input.setPlaceholderText("API key is set ✓")
                logger.info("API key updated from UI")

            # Get screenshot geometry
            global_pos = self.transparent_window.mapToGlobal(QPoint(0, 0))
            screenshot_rect = QRect(global_pos, self.transparent_window.size())

            # Capture screenshot
            logger.info("Capturing screenshot...")
            screenshot = capture_screenshot(screenshot_rect)

            if screenshot is None:
                self.output_text.setPlainText(
                    "Error: Failed to capture screenshot. Please try again."
                )
                logger.error("Screenshot capture returned None")
                return

            # Get query text
            query = self.input_text.toPlainText()
            if not query:
                self.output_text.setPlainText("Error: Please enter a query.")
                logger.warning("Send clicked without query text")
                return

            # Update UI to show processing
            self.output_text.setPlainText("Sending request to OpenAI...")
            self.send_button.setEnabled(False)
            QApplication.processEvents()  # Update the GUI

            # Send API request
            logger.info(f"Sending API request with query: {query[:50]}...")
            response = self.api_handler.send_request(screenshot, query)

            # Display response
            self.output_text.setPlainText(response)
            logger.info("API response received and displayed")

        except APIKeyError as e:
            error_msg = f"API Key Error: {e}"
            self.output_text.setPlainText(error_msg)
            logger.error(error_msg)

        except ScreenshotError as e:
            error_msg = f"Screenshot Error: {e}"
            self.output_text.setPlainText(error_msg)
            logger.error(error_msg)

        except APIResponseError as e:
            error_msg = f"API Error: {e}\n\nPlease check your API key and try again."
            self.output_text.setPlainText(error_msg)
            logger.error(error_msg)

        except Exception as e:
            error_msg = f"Unexpected Error: {e}\n\nPlease try again or check the logs."
            self.output_text.setPlainText(error_msg)
            logger.error(f"Unexpected error in send handler: {e}", exc_info=True)

        finally:
            # Re-enable send button
            self.send_button.setEnabled(True)
