'''
Heart Beat Widgit for Boat: The battery widget connected to the heartbeat to make sure they are on and connected to the boat
[Boolean; Is it connected? Yes(Green True) or No(Red False)]
'''

import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QFont, QPainterPath
from ..ros.boat_heartbeat_subscriber import BoatHeartbeatSubscriber


class BoatStatusIcon(QWidget):
    def __init__(self, connected=False, parent=None):
        super().__init__(parent)
        self.connected = connected
        self.setFixedSize(100, 100)

    def set_connected(self, state: bool):
        self.connected = state
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        status_color = QColor(0, 200, 0) if self.connected else QColor(200, 0, 0)
        painter.setBrush(status_color)
        painter.setPen(Qt.PenStyle.NoPen)

        w = self.width()
        h = self.height()

        # --- Hull ---
        hull = QPainterPath()
        hull.moveTo(w * 0.2, h * 0.62)
        hull.lineTo(w * 0.8, h * 0.62)
        hull.lineTo(w * 0.65, h * 0.78)
        hull.lineTo(w * 0.35, h * 0.78)
        hull.closeSubpath()
        painter.drawPath(hull)

        # --- Cabin ---
        painter.drawRoundedRect(
            int(w * 0.36),
            int(h * 0.45),
            int(w * 0.28),
            int(h * 0.15),
            4,
            4
        )

        # --- Mast ---
        mast_width = 3
        painter.drawRect(
            int(w * 0.5 - mast_width / 2),
            int(h * 0.25),
            mast_width,
            int(h * 0.20)
        )

        # --- Flag ---
        flag = QPainterPath()
        flag.moveTo(w * 0.5, h * 0.25)
        flag.lineTo(w * 0.68, h * 0.30)
        flag.lineTo(w * 0.5, h * 0.35)
        flag.closeSubpath()
        painter.drawPath(flag)


class BatteryWidget(QWidget):
    def __init__(self, percentage=0, parent=None):
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

        # Battery fill
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
    def __init__(self, ros_worker=None):
        super().__init__()
        self.setFixedSize(200, 200)
 
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.setObjectName("panel")
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                border: 2px solid #555555;
                border-radius: 12px;
                color: white;
            }
        """)
 
        title = QLabel("Boat")
        title.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("border: none; background: transparent;")
 
        self.status_icon = BoatStatusIcon(connected=False)
        self.battery     = BatteryWidget(0)
 
        self.mode_label  = QLabel("Mode: --")
        self.mode_label.setFont(QFont("Arial", 9))
        self.mode_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mode_label.setStyleSheet("color: white; border: none; background: transparent;")
 
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(6)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
 
        layout.addWidget(title,            alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_icon, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.battery,     alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.mode_label,  alignment=Qt.AlignmentFlag.AlignCenter)
 
        self.setLayout(layout)
 
        if ros_worker is not None:
            self._connect_subscriber(ros_worker)
 
    def _connect_subscriber(self, ros_worker):
 
        self.heartbeat_sub = BoatHeartbeatSubscriber(ros_worker.node)
        self.heartbeat_sub.signals.connection_status.connect(self.update_connection_status)
        self.heartbeat_sub.signals.battery_update.connect(self.update_battery)
        self.heartbeat_sub.signals.mode_update.connect(self.update_mode)
 
    def update_connection_status(self, connected: bool):
        self.status_icon.set_connected(connected)
 
    def update_battery(self, pct: float):
        self.battery.set_percentage(int(pct))
 
    def update_mode(self, mode: str):
        self.mode_label.setText(f"Mode: {mode}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = StatusWidget()
    widget.show()
    sys.exit(app.exec())
