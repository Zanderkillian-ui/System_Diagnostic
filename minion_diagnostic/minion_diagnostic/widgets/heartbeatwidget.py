'''
Heart Beat Widgit: The battery widget connected to the heartbeat to make sure they are on and connected to the boat
[Binary; Is it connected? Yes(Green True) or No(Red False)]
'''

import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QFont


class StatusCircle(QWidget):
    def __init__(self, connected=True, parent=None):
        super().__init__(parent)
        self.connected = connected
        self.setFixedSize(100, 100)

    def set_connected(self, state: bool):
        self.connected = state
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        color = QColor(0, 200, 0) if self.connected else QColor(200, 0, 0)
        painter.setBrush(color)
        painter.setPen(Qt.PenStyle.NoPen)

        diameter = 60
        x = (self.width() - diameter) // 2
        y = (self.height() - diameter) // 2
        painter.drawEllipse(x, y, diameter, diameter)


class BatteryWidget(QWidget):
    def __init__(self, percentage=75, parent=None):
        super().__init__(parent)
        self.percentage = percentage
        self.setFixedSize(180, 45)

    def set_percentage(self, value):
        self.percentage = max(0, min(100, value))
        self.update()

    def battery_color(self):
        if self.percentage <= 10:
            return QColor(200, 0, 0)      # Red
        elif self.percentage <= 50:
            return QColor(220, 180, 0)    # Yellow
        else:
            return QColor(0, 200, 0)      # Green

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        bars = 4
        bar_width = 15
        bar_height = 27
        spacing = 5

        filled_bars = round((self.percentage / 100) * bars)
        percentage_width = 55
        total_width = bars * bar_width + (bars - 1) * spacing + percentage_width

        x = (self.width() - total_width) // 2
        y = (self.height() - bar_height) // 2

        color = self.battery_color()

        for i in range(bars):
            painter.setBrush(color if i < filled_bars else QColor(90, 90, 90))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(x, y, bar_width, bar_height)
            x += bar_width + spacing

        painter.setPen(Qt.GlobalColor.white)
        painter.setFont(QFont("Arial", 11))
        painter.drawText(
            x + 6,
            0,
            percentage_width,
            self.height(),
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            f"{self.percentage}%"
        )


class StatusWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(200, 200)
        self.setStyleSheet("background-color: #1e1e1e; color: white;")

# Change the values here

        title = QLabel("Boat")
        title.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.status_circle = StatusCircle(True)
        self.battery_widget = BatteryWidget(75)

        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_circle, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.battery_widget, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = StatusWidget()
    widget.show()
    sys.exit(app.exec())
