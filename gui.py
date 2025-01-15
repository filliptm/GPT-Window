import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QTextEdit, QFrame, QLabel, QLineEdit, QDesktopWidget)
from PyQt5.QtCore import Qt, QRect, QPoint, QSize
from PyQt5.QtGui import QPainter, QColor, QPen, QCursor  # Added QCursor here
from api_handler import APIHandler
from utils import capture_screenshot
from PIL import Image


class TransparentWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background:transparent;")
        self.resize(600, 500)

        self.dragging = False
        self.resizing = False
        self.resize_edge = None
        self.drag_start_pos = None
        self.window_start_pos = None
        self.window_start_size = None
        self.corner_size = 20

        self.top_bar_height = 30
        self.top_bar = QWidget(self)
        self.top_bar.setStyleSheet("background-color: rgba(255, 0, 0, 100);")
        self.top_bar.setGeometry(0, 0, self.width(), self.top_bar_height)

        self.min_width = self.corner_size * 2
        self.min_height = self.corner_size * 2 + self.top_bar_height

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
        painter.drawRect(self.rect())

        # Draw corner handles
        painter.setBrush(QColor(255, 0, 0, 100))
        painter.drawRect(0, 0, self.corner_size, self.corner_size)
        painter.drawRect(self.width() - self.corner_size, 0, self.corner_size, self.corner_size)
        painter.drawRect(0, self.height() - self.corner_size, self.corner_size, self.corner_size)
        painter.drawRect(self.width() - self.corner_size, self.height() - self.corner_size, self.corner_size,
                         self.corner_size)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_pos = event.globalPos()
            self.window_start_pos = self.pos()
            self.window_start_size = self.size()

            if self.top_bar.geometry().contains(event.pos()):
                self.dragging = True
                self.setCursor(QCursor(Qt.ClosedHandCursor))
            else:
                self.resize_edge = self.get_resize_edge(event.pos())
                if self.resize_edge:
                    self.resizing = True
                    self.setCursor(self.get_resize_cursor())
            event.accept()

    def mouseMoveEvent(self, event):
        if self.dragging:
            new_pos = self.window_start_pos + event.globalPos() - self.drag_start_pos
            self.move(new_pos)
        elif self.resizing:
            diff = event.globalPos() - self.drag_start_pos
            new_geometry = self.geometry()

            if 'left' in self.resize_edge:
                new_geometry.setLeft(min(self.window_start_pos.x() + diff.x(),
                                         self.window_start_pos.x() + self.window_start_size.width() - self.min_width))
            if 'top' in self.resize_edge:
                new_geometry.setTop(min(self.window_start_pos.y() + diff.y(),
                                        self.window_start_pos.y() + self.window_start_size.height() - self.min_height))
            if 'right' in self.resize_edge:
                new_geometry.setRight(max(self.window_start_pos.x() + self.window_start_size.width() + diff.x(),
                                          self.window_start_pos.x() + self.min_width))
            if 'bottom' in self.resize_edge:
                new_geometry.setBottom(max(self.window_start_pos.y() + self.window_start_size.height() + diff.y(),
                                           self.window_start_pos.y() + self.min_height))

            self.setGeometry(new_geometry)
            self.top_bar.setGeometry(0, 0, self.width(), self.top_bar_height)

        event.accept()

    def mouseReleaseEvent(self, event):
        self.dragging = False
        self.resizing = False
        self.resize_edge = None
        self.unsetCursor()
        event.accept()

    def get_resize_edge(self, pos):
        edge = ''
        if pos.x() <= self.corner_size:
            edge += 'left'
        elif pos.x() >= self.width() - self.corner_size:
            edge += 'right'
        if pos.y() <= self.corner_size:
            edge += 'top'
        elif pos.y() >= self.height() - self.corner_size:
            edge += 'bottom'
        return edge

    def get_resize_cursor(self):
        if self.resize_edge in ['top', 'bottom']:
            return Qt.SizeVerCursor
        elif self.resize_edge in ['left', 'right']:
            return Qt.SizeHorCursor
        elif self.resize_edge in ['topleft', 'bottomright']:
            return Qt.SizeFDiagCursor
        elif self.resize_edge in ['topright', 'bottomleft']:
            return Qt.SizeBDiagCursor
        return Qt.ArrowCursor

    def enterEvent(self, event):
        if not self.dragging and not self.resizing:
            self.setCursor(QCursor(Qt.SizeAllCursor))

    def leaveEvent(self, event):
        if not self.dragging and not self.resizing:
            self.unsetCursor()


class ControlPanel(QWidget):
    def __init__(self, transparent_window):
        super().__init__()
        self.transparent_window = transparent_window
        self.api_handler = APIHandler()
        self.api_handler.load_api_key()  # Try to load API key from environment variable
        self.initUI()

    def initUI(self):
        self.setWindowTitle('GPT Vision Controls')
        layout = QVBoxLayout()

        # API Key input
        api_key_layout = QHBoxLayout()
        api_key_label = QLabel("API Key:")
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setText(self.api_handler.api_key or "")
        api_key_layout.addWidget(api_key_label)
        api_key_layout.addWidget(self.api_key_input)
        layout.addLayout(api_key_layout)

        # Input text box
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Enter your query here...")
        self.input_text.setMaximumHeight(50)
        layout.addWidget(self.input_text)

        # Send button
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.onSendClicked)
        layout.addWidget(self.send_button)

        # Output text box
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        layout.addWidget(self.output_text)

        self.setLayout(layout)

    def onSendClicked(self):
        try:
            api_key = self.api_key_input.text()
            if not api_key:
                self.output_text.setPlainText("Please enter your API key.")
                return

            self.api_handler.set_api_key(api_key)

            global_pos = self.transparent_window.mapToGlobal(QPoint(0, 0))
            screenshot_rect = QRect(global_pos, self.transparent_window.size())

            screenshot = capture_screenshot(screenshot_rect)

            if screenshot is None:
                self.output_text.setPlainText("Failed to capture screenshot.")
                return

            query = self.input_text.toPlainText()

            self.output_text.setPlainText("Sending request...")
            QApplication.processEvents()  # Update the GUI

            response = self.api_handler.send_request(screenshot, query)
            self.output_text.setPlainText(response)
        except Exception as e:
            self.output_text.setPlainText(f"An error occurred: {str(e)}")
            print(f"Error in onSendClicked: {str(e)}")  # This will print to the console


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('GPT Vision Interface')
        self.setGeometry(100, 100, 600, 400)  # Reduced size for the control panel

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.transparent_window = TransparentWindow()
        self.transparent_window.show()

        self.control_panel = ControlPanel(self.transparent_window)
        layout.addWidget(self.control_panel)

    def closeEvent(self, event):
        self.transparent_window.close()
        event.accept()


def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()