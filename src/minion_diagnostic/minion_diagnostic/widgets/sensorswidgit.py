'''
Sensor Widgit: Camera [w/ Rate], LiDAR [w/ Rate], GPS [w/ Rate]
For Each Node -> Label & Status Color [Binary; Is it delivering data? Yes or No]
'''

import sys
from PyQt6.QtCore import Qt, pyqtSignal, QObject
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QHBoxLayout,
    QVBoxLayout, QFrame, QGridLayout
)
from ..ros.camera_subscriber import CameraRateSubscriber
from ..ros.lidar_subscriber import LidarRateSubscriber
from ..ros.gps_subscriber import GpsRateSubscriber


class NodeStatusWidget(QWidget):
    # Node Widget
    def __init__(self, node_name: str):
        super().__init__()

        self.label = QLabel(node_name)

        # Small Padding + Bold Text
        self.label.setContentsMargins(5, 3, 5, 3)
        self.label.setStyleSheet("""
            border-radius: 4px;
            border: 1px solid white;
            background-color: grey;
            font-weight: bold;
        """)

        # Small Margins
        layout = QHBoxLayout()
        layout.setContentsMargins(2, 2, 2, 2)
        layout.addWidget(self.label)
        self.setLayout(layout)

        # Background Color Options: Green(Yes,1) or Red(No,0)
        self.status_map = {
            1: "green",
            0: "red",
        }

    def set_status_from_code(self, code: int):
        # Apply Background Color Using Status Code
        color = self.status_map.get(code, "grey")
        self.label.setStyleSheet(f"""
            border-radius: 4px;
            border: 1px solid white;
            background-color: {color};
            font-weight: bold;
        """)


class NodeStatusBridge(QObject):
    status_update = pyqtSignal(str, int)


# Main Node Widget; all nodes in a grid 3x1
class NodePanel(QWidget):
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

        self.node_names = [
            "Camera",
            "LiDAR",
            "GPS"
        ]

        self.nodes = {name: NodeStatusWidget(name) for name in self.node_names}

        # 3x1 Grid Layout
        layout = QGridLayout()
        layout.setSpacing(8)

        rows = 3
        cols = 1
        index = 0

        for r in range(rows):
            for c in range(cols):
                name = self.node_names[index]
                layout.addWidget(self.nodes[name], r, c)
                index += 1

        self.setLayout(layout)

        # Signal Bridge
        self.bridge = NodeStatusBridge()
        self.bridge.status_update.connect(self.update_node_from_signal)

        # Connect ROS subscribers if a ros_worker was provided
        if ros_worker is not None:
            self._connect_subscribers(ros_worker)

    def _connect_subscribers(self, ros_worker):

        self.camera_sub = CameraRateSubscriber(ros_worker.node)
        self.camera_sub.signals.rate_update.connect(self.update_camera_rate)

        self.lidar_sub = LidarRateSubscriber(ros_worker.node)
        self.lidar_sub.signals.rate_update.connect(self.update_lidar_rate)

        self.gps_sub = GpsRateSubscriber(ros_worker.node)
        self.gps_sub.signals.rate_update.connect(self.update_gps_rate)

    def update_camera_rate(self, hz):

        label = self.nodes["Camera"].label
        label.setText(f"Camera: {hz:.1f} Hz")

        if hz >= 5:
            self.nodes["Camera"].set_status_from_code(1)
        else:
            self.nodes["Camera"].set_status_from_code(0)

    def update_lidar_rate(self, hz):

        label = self.nodes["LiDAR"].label
        label.setText(f"LiDAR: {hz:.1f} Hz")

        if hz >= 5:
            self.nodes["LiDAR"].set_status_from_code(1)
        else:
            self.nodes["LiDAR"].set_status_from_code(0)

    def update_gps_rate(self, hz):

        label = self.nodes["GPS"].label
        label.setText(f"GPS: {hz:.1f} Hz")

        if hz >= 1:
            self.nodes["GPS"].set_status_from_code(1)
        else:
            self.nodes["GPS"].set_status_from_code(0)

    def update_node_from_signal(self, node_name, status_code):
        if node_name in self.nodes:
            self.nodes[node_name].set_status_from_code(status_code)

# Change the status of a node by doing self.node["LiDAR"].set_status_from_code(#(0-1))
# 1 is green working
# 0 is red not working

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = NodePanel()
    window.setWindowTitle("Boat Sensors")
    window.show()

    sys.exit(app.exec())