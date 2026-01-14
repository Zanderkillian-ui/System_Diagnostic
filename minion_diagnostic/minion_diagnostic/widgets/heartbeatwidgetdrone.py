'''
Heart Beat Widgit for Drone: The battery widget connected to the heartbeat to make sure they are on and connected to the boat
[Boolean; Is it connected? Yes(Green True) or No(Red False)]
'''

import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout
)
from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import QPainter, QColor, QFont, QPainterPath


class DroneStatusIcon(QWidget):
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

        w = self.width()
        h = self.height()
        cx = w // 2
        cy = h // 2

        # --- Body ---
        body_size = int(w * 0.20)
        painter.drawRoundedRect(
            cx - body_size // 2,
            cy - body_size // 2,
            body_size,
            body_size,
            6,
            6
        )

        # --- Arms ---
        arm_length = int(w * 0.30)
        arm_width = int(w * 0.05)

        # Horizontal arm
        painter.drawRect(
            cx - arm_length // 2,
            cy - arm_width // 2,
            arm_length,
            arm_width
        )

        # Vertical arm
        painter.drawRect(
            cx - arm_width // 2,
            cy - arm_length // 2,
            arm_width,
            arm_length
        )

        # --- Rotors ---
        rotor_radius = int(w * 0.10)
        offsets = [
            (-arm_length // 2, -arm_length // 2),
            ( arm_length // 2, -arm_length // 2),
            (-arm_length // 2,  arm_length // 2),
            ( arm_length // 2,  arm_length // 2),
        ]

        for ox, oy in offsets:
            painter.drawEllipse(
                QPointF(cx + ox, cy + oy),
                rotor_radius,
                rotor_radius
            )

        # --- Rotor hubs ---
        hub_radius = int(w * 0.025)
        painter.setBrush(QColor(30, 30, 30))
        for ox, oy in offsets:
            painter.drawEllipse(
                QPointF(cx + ox, cy + oy),
                hub_radius,
                hub_radius
            )


class BatteryWidget(QWidget):
    def __init__(self, percentage=75, parent=None):
        super().__init__(parent)
        self.percentage = percentage
        self.setFixedSize(180, 45)

    def set_percentage(self, value):
        self.percentage = max(0, min(100, value))
        self.update()

    def battery_color(self):
        if self.percentage <= 20:
            return QColor(200, 0, 0)      # Red
        elif self.percentage <= 50:
            return QColor(220, 180, 0)    # Yellow
        else:
            return QColor(0, 200, 0)      # Green

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # --- Battery body ---
        body_width = 90
        body_height = 26
        terminal_width = 6
        padding = 4

        x = 10
        y = (self.height() - body_height) // 2

        # Outline
        painter.setPen(QColor(180, 180, 180))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(x, y, body_width, body_height, 4, 4)

        # Terminal (nub)
        terminal_x = x + body_width
        terminal_y = y + body_height // 4
        painter.drawRect(
            terminal_x,
            terminal_y,
            terminal_width,
            body_height // 2
        )

        # --- Battery fill ---
        fill_margin = 3
        fill_width = int((body_width - fill_margin * 2) * (self.percentage / 100))
        fill_height = body_height - fill_margin * 2

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.battery_color())
        painter.drawRoundedRect(
            x + fill_margin,
            y + fill_margin,
            fill_width,
            fill_height,
            2,
            2
        )

        # --- Percentage text ---
        painter.setPen(Qt.GlobalColor.white)
        painter.setFont(QFont("Arial", 11))
        painter.drawText(
            x + body_width + terminal_width + 10,
            0,
            self.width(),
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

        title = QLabel("Drone")
        title.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.status_circle = DroneStatusIcon(True)
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
