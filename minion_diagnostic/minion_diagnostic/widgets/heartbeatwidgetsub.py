'''
Heart Beat Widgit for Sub: The battery widget connected to the heartbeat to make sure they are on and connected to the boat
[Boolean; Is it connected? Yes(Green True) or No(Red False)]
'''

import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout
)
from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import QPainter, QColor, QFont, QPainterPath


class SubmarineStatusIcon(QWidget):
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

        # --- Hull ---
        painter.drawRoundedRect(
            int(w * 0.18),
            int(h * 0.50),
            int(w * 0.64),
            int(h * 0.20),
            int(h * 0.10),
            int(h * 0.10)
        )

        # --- Conning tower ---
        painter.drawRoundedRect(
            int(w * 0.42),
            int(h * 0.36),
            int(w * 0.16),
            int(h * 0.14),
            6,
            6
        )

        # --- Periscope pole ---
        pole_x = int(w * 0.50)
        painter.drawRect(
            pole_x - 2,
            int(h * 0.24),
            4,
            int(h * 0.12)
        )

        # --- Telescope (offset, upside-down L) ---
        elbow_y = int(h * 0.21)

        # Horizontal scope (to the right)
        painter.drawRect(
            pole_x,
            elbow_y,
            int(w * -0.10),
            int(h * 0.035),
        )


        # --- Rear shaft ---
        shaft_y = int(h * 0.60)
        painter.drawRect(
            int(w * 0.82),
            shaft_y - 2,
            int(w * 0.08),
            4
        )

        # --- Propellers (two blades) ---
        prop_center_x = int(w * 0.90)
        prop_center_y = shaft_y

        blade_length = int(w * 0.04)
        blade_width = 3

        # Vertical blade
        painter.drawRect(
            prop_center_x - blade_width // 2,
            prop_center_y - blade_length,
            blade_width,
            blade_length * 2
        )

        # Horizontal blade
        painter.drawRect(
            prop_center_x - blade_length,
            prop_center_y - blade_width // 2,
            blade_length * 2,
            blade_width
        )

        # --- Portholes ---
        hole = int(w * 0.045)
        for i in range(3):
            painter.drawEllipse(
                int(w * (0.40 + i * 0.09)),
                int(h * 0.57),
                hole,
                hole
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

        title = QLabel("Sub")
        title.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.status_circle = SubmarineStatusIcon(True)
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
