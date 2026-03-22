'''
Nodes Widgit: Controls, Path Planner, Path Demo, GBCACHE, World Mapper
                ROI(Fusion), Dock Detection, Task Manager, RIDD 3DOF
For Each Node -> Label & Status Color [Binary; Is it delivering data? Yes(1) or No(0)]
'''

import sys
from PyQt6.QtCore import Qt, pyqtSignal, QObject
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QHBoxLayout,
    QVBoxLayout, QFrame, QGridLayout
)
from ..ros.nodes_subscriber import DiagnosticsSubscriber

class NodeStatusWidget(QWidget):
    # Node Widget
    def __init__(self, node_name: str):
        super().__init__()

        self.label = QLabel(node_name)

        # Small Padding + Bold Text
        self.label.setContentsMargins(5, 3, 5, 3)
        self.label.setStyleSheet("""
            border-radius: 4px;
            border: 1px solid black;
            background-color: gray;
            font-weight: bold;
        """)

        # Set Margins (small)
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
        # Set Background Color Using Status Code
        color = self.status_map.get(code, "gray")
        self.label.setStyleSheet(f"""
            border-radius: 4px;
            border: 1px solid black;
            background-color: {color};
            font-weight: bold;
        """)


class NodeStatusBridge(QObject):
    status_update = pyqtSignal(str, int)


# Main Node Widget; all nodes in a 3x3 grid
class NodePanel(QWidget):
    def __init__(self, ros_worker=None):
        super().__init__()

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setFixedSize(400, 200)

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
            "Controls",
            "Path Planner",
            "Path Demo",
            "GBCACHE",
            "World Mapper",
            "ROI (Fusion)",
            "Dock Detection",
            "Task Manager",
            "PIDD 3DOF"
        ]

        self.nodes = {name: NodeStatusWidget(name) for name in self.node_names}

        # 3x3 Grid Layout
        layout = QGridLayout()
        layout.setSpacing(8)

        rows = 3
        cols = 3
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

        if ros_worker is not None:
            self._connect_subscriber(ros_worker)
            
    def _connect_subscriber(self, ros_worker):
 
        self.diagnostics_sub = DiagnosticsSubscriber(ros_worker.node)
        self.diagnostics_sub.signals.node_status_update.connect(self.update_node_from_signal)

    def update_node_from_signal(self, node_name: str, status_code: int):
        if node_name in self.nodes:
            self.nodes[node_name].set_status_from_code(status_code)

# Change the status of a node by doing self.node["Controls Node"].set_status_from_code(#(0-1))
# 1 is green working
# 0 is red not working

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = NodePanel()
    window.setWindowTitle("Boat Nodes")
    window.show()

    sys.exit(app.exec())
