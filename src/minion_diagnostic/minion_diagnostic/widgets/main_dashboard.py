import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QMainWindow, QPushButton, QLabel
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QPen

from .nodeswidgit import NodePanel
from .heartbeatwidgetboat import StatusWidget as BoatHeartPanel
from .heartbeatwidgetdrone import StatusWidget as DroneHeartPanel
from .heartbeatwidgetsub import StatusWidget as SubHeartPanel
from .sensorswidgit import NodePanel as SensorsPanel
from ..ros.ros_manager import ROSWorker

GRID_SIZE = 100


class Canvas(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: black;")

    def paintEvent(self, event):
        painter = QPainter(self)
        pen = QPen(QColor(40, 40, 40))
        pen.setWidth(1)
        painter.setPen(pen)

        for x in range(0, self.width(), GRID_SIZE):
            painter.drawLine(x, 0, x, self.height())

        for y in range(0, self.height(), GRID_SIZE):
            painter.drawLine(0, y, self.width(), y)


class DraggableWidget(QWidget):
    def __init__(self, widget: QWidget):
        super().__init__()

        self.inner = widget
        self.inner.setParent(self)
        self.inner.move(0, 0)

        self.resize(self.inner.size())

        self.drag_offset = None
        self.locked = False

    def mousePressEvent(self, event):
        if self.locked:
            return

        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_offset = event.globalPosition().toPoint() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.locked or not self.drag_offset:
            return

        if event.buttons() & Qt.MouseButton.LeftButton:
            parent = self.parentWidget()
            if not parent:
                return

            new_pos = event.globalPosition().toPoint() - self.drag_offset

            x = round(new_pos.x() / GRID_SIZE) * GRID_SIZE
            y = round(new_pos.y() / GRID_SIZE) * GRID_SIZE

            max_x = parent.width() - self.width()
            max_y = parent.height() - self.height()

            x = max(0, min(x, max_x))
            y = max(0, min(y, max_y))

            self.move(x, y)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.drag_offset = None
        event.accept()


class ModularDashboard(QMainWindow):
    def __init__(self, ros_worker):
        super().__init__()

        self.ros_worker = ros_worker

        self.setWindowTitle("Autonomous Boat Dashboard")
        self.setFixedSize(1000, 600)

        self.canvas = Canvas()
        self.setCentralWidget(self.canvas)

        self.add_widgets()
        self.create_lock_ui()

    def add_widgets(self):
        nodes_panel = NodePanel(ros_worker=self.ros_worker)
        boat_heart = BoatHeartPanel(ros_worker=self.ros_worker)
        drone_heart = DroneHeartPanel()
        sub_heart = SubHeartPanel()
        sensors_panel = SensorsPanel(ros_worker=self.ros_worker)

        self.widgets = [
            DraggableWidget(nodes_panel),
            DraggableWidget(boat_heart),
            DraggableWidget(drone_heart),
            DraggableWidget(sub_heart),
            DraggableWidget(sensors_panel),
        ]

        start_positions = [
            (0, 0),
            (800, 400),
            (600, 400),
            (400, 400),
            (0, 400),
        ]

        for widget, (x, y) in zip(self.widgets, start_positions):
            widget.setParent(self.canvas)
            widget.move(x, y)
            widget.show()

    def create_lock_ui(self):
        self.lock_label = QLabel("UNLOCKED", self.canvas)
        self.lock_label.setStyleSheet("color: white; font-weight: bold;")
        self.lock_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lock_button = QPushButton("", self.canvas)
        self.lock_button.setFixedSize(60, 60)
        self.lock_button.clicked.connect(self.toggle_lock)
        self.lock_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.lock_button.setFlat(True)

        self.locked_state = False

        self.update_button_style()
        self.update_lock_ui_position()

        self.lock_label.show()
        self.lock_button.show()

    def update_button_style(self):
        if self.locked_state:
            self.lock_button.setStyleSheet("""
                QPushButton {
                    border-radius: 30px;
                    background-color: #cc4444;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #ff6666;
                }
            """)
            self.lock_label.setText("LOCKED")
        else:
            self.lock_button.setStyleSheet("""
                QPushButton {
                    border-radius: 30px;
                    background-color: #44aa44;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #66cc66;
                }
            """)
            self.lock_label.setText("UNLOCKED")

    def update_lock_ui_position(self):
        grid_x = (self.canvas.width() // GRID_SIZE - 1) * GRID_SIZE

        btn_x = grid_x + (GRID_SIZE - self.lock_button.width()) // 2
        btn_y = GRID_SIZE // 2 - self.lock_button.height() // 2

        self.lock_button.move(btn_x, btn_y)

        self.lock_label.setFixedWidth(GRID_SIZE)
        self.lock_label.move(grid_x, 0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_lock_ui_position()

    def toggle_lock(self):
        self.locked_state = not self.locked_state
        self.update_button_style()

        for widget in self.widgets:
            widget.locked = self.locked_state

    def closeEvent(self, event):
        self.ros_worker.shutdown()
        event.accept()


if __name__ == "__main__":
    import rclpy
    rclpy.init()
    ros_worker = ROSWorker()
    app = QApplication(sys.argv)
    window = ModularDashboard(ros_worker=ros_worker)
    window.show()
    sys.exit(app.exec())