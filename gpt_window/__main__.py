"""Main entry point for GPT Window application."""

import sys

from PyQt5.QtWidgets import QApplication

from gpt_window.config.logging_config import setup_logging
from gpt_window.config.settings import Settings
from gpt_window.ui.main_window import MainWindow


def main() -> None:
    """
    Main entry point for the GPT Window application.

    This function:
    1. Loads settings from environment
    2. Sets up logging
    3. Creates the Qt application
    4. Shows the main window
    5. Starts the event loop
    """
    # Load settings
    settings = Settings.from_env()

    # Setup logging
    logger = setup_logging(log_level=settings.log_level, log_file=settings.log_file)
    logger.info("=" * 60)
    logger.info("GPT Window application starting")
    logger.info("=" * 60)

    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("GPT Window")
    app.setOrganizationName("GPT Window")

    # Create and show main window
    main_window = MainWindow()
    main_window.show()

    logger.info("Application started successfully")

    # Start event loop
    exit_code = app.exec_()

    logger.info(f"Application exiting with code {exit_code}")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
