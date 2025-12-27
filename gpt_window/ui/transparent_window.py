"""Transparent overlay window for screenshot region selection."""

from typing import Optional

from PyQt5.QtCore import QPoint, QRect, QSize, Qt
from PyQt5.QtGui import QColor, QCursor, QPainter, QPen
from PyQt5.QtWidgets import QWidget

from gpt_window.config.constants import CORNER_SIZE, MIN_WINDOW_HEIGHT, MIN_WINDOW_WIDTH, TOP_BAR_HEIGHT


class TransparentWindow(QWidget):
    """
    Transparent, draggable, and resizable window for selecting screen regions.

    This window appears as a transparent overlay with a red border that the user
    can move and resize to select the area they want to capture.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        Initialize the transparent window.

        Args:
            parent: Optional parent widget.
        """
        super().__init__(parent)
        self._setup_window()
        self._setup_interaction_state()
        self._setup_ui_elements()

    def _setup_window(self) -> None:
        """Configure window properties."""
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background:transparent;")
        self.resize(600, 500)

    def _setup_interaction_state(self) -> None:
        """Initialize interaction state variables."""
        self.dragging = False
        self.resizing = False
        self.resize_edge: Optional[str] = None
        self.drag_start_pos: Optional[QPoint] = None
        self.window_start_pos: Optional[QPoint] = None
        self.window_start_size: Optional[QSize] = None

    def _setup_ui_elements(self) -> None:
        """Set up UI elements like the top bar."""
        self.corner_size = CORNER_SIZE
        self.top_bar_height = TOP_BAR_HEIGHT

        # Top bar for dragging
        self.top_bar = QWidget(self)
        self.top_bar.setStyleSheet("background-color: rgba(255, 0, 0, 100);")
        self.top_bar.setGeometry(0, 0, self.width(), self.top_bar_height)

        # Minimum window size
        self.min_width = MIN_WINDOW_WIDTH
        self.min_height = MIN_WINDOW_HEIGHT

    def paintEvent(self, event) -> None:  # type: ignore
        """
        Paint the window border and corner handles.

        Args:
            event: QPaintEvent (not used but required by Qt).
        """
        painter = QPainter(self)
        painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
        painter.drawRect(self.rect())

        # Draw corner handles for resizing
        painter.setBrush(QColor(255, 0, 0, 100))
        painter.drawRect(0, 0, self.corner_size, self.corner_size)
        painter.drawRect(self.width() - self.corner_size, 0, self.corner_size, self.corner_size)
        painter.drawRect(0, self.height() - self.corner_size, self.corner_size, self.corner_size)
        painter.drawRect(
            self.width() - self.corner_size,
            self.height() - self.corner_size,
            self.corner_size,
            self.corner_size,
        )

    def mousePressEvent(self, event) -> None:  # type: ignore
        """
        Handle mouse press events for dragging and resizing.

        Args:
            event: QMouseEvent.
        """
        if event.button() == Qt.LeftButton:
            self.drag_start_pos = event.globalPos()
            self.window_start_pos = self.pos()
            self.window_start_size = self.size()

            if self.top_bar.geometry().contains(event.pos()):
                self.dragging = True
                self.setCursor(QCursor(Qt.ClosedHandCursor))
            else:
                self.resize_edge = self._get_resize_edge(event.pos())
                if self.resize_edge:
                    self.resizing = True
                    self.setCursor(self._get_resize_cursor())
            event.accept()

    def mouseMoveEvent(self, event) -> None:  # type: ignore
        """
        Handle mouse move events for dragging and resizing.

        Args:
            event: QMouseEvent.
        """
        if self.dragging and self.drag_start_pos and self.window_start_pos:
            new_pos = self.window_start_pos + event.globalPos() - self.drag_start_pos
            self.move(new_pos)
        elif self.resizing and self.resize_edge and self.drag_start_pos and self.window_start_pos and self.window_start_size:
            diff = event.globalPos() - self.drag_start_pos
            new_geometry = self.geometry()

            if "left" in self.resize_edge:
                new_geometry.setLeft(
                    min(
                        self.window_start_pos.x() + diff.x(),
                        self.window_start_pos.x() + self.window_start_size.width() - self.min_width,
                    )
                )
            if "top" in self.resize_edge:
                new_geometry.setTop(
                    min(
                        self.window_start_pos.y() + diff.y(),
                        self.window_start_pos.y()
                        + self.window_start_size.height()
                        - self.min_height,
                    )
                )
            if "right" in self.resize_edge:
                new_geometry.setRight(
                    max(
                        self.window_start_pos.x() + self.window_start_size.width() + diff.x(),
                        self.window_start_pos.x() + self.min_width,
                    )
                )
            if "bottom" in self.resize_edge:
                new_geometry.setBottom(
                    max(
                        self.window_start_pos.y() + self.window_start_size.height() + diff.y(),
                        self.window_start_pos.y() + self.min_height,
                    )
                )

            self.setGeometry(new_geometry)
            self.top_bar.setGeometry(0, 0, self.width(), self.top_bar_height)

        event.accept()

    def mouseReleaseEvent(self, event) -> None:  # type: ignore
        """
        Handle mouse release events.

        Args:
            event: QMouseEvent.
        """
        self.dragging = False
        self.resizing = False
        self.resize_edge = None
        self.unsetCursor()
        event.accept()

    def _get_resize_edge(self, pos: QPoint) -> str:
        """
        Determine which edge/corner is being clicked for resizing.

        Args:
            pos: Mouse position.

        Returns:
            String indicating the edge(s) ("left", "right", "top", "bottom", or combinations).
        """
        edge = ""
        if pos.x() <= self.corner_size:
            edge += "left"
        elif pos.x() >= self.width() - self.corner_size:
            edge += "right"
        if pos.y() <= self.corner_size:
            edge += "top"
        elif pos.y() >= self.height() - self.corner_size:
            edge += "bottom"
        return edge

    def _get_resize_cursor(self) -> Qt.CursorShape:
        """
        Get the appropriate cursor for the current resize edge.

        Returns:
            Qt cursor shape for the resize direction.
        """
        if self.resize_edge in ["top", "bottom"]:
            return Qt.SizeVerCursor
        elif self.resize_edge in ["left", "right"]:
            return Qt.SizeHorCursor
        elif self.resize_edge in ["topleft", "bottomright"]:
            return Qt.SizeFDiagCursor
        elif self.resize_edge in ["topright", "bottomleft"]:
            return Qt.SizeBDiagCursor
        return Qt.ArrowCursor

    def enterEvent(self, event) -> None:  # type: ignore
        """
        Handle mouse enter events.

        Args:
            event: QEvent.
        """
        if not self.dragging and not self.resizing:
            self.setCursor(QCursor(Qt.SizeAllCursor))

    def leaveEvent(self, event) -> None:  # type: ignore
        """
        Handle mouse leave events.

        Args:
            event: QEvent.
        """
        if not self.dragging and not self.resizing:
            self.unsetCursor()
