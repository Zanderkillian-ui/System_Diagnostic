'''
Nodes Widgit: Control Node, Path Planner Node, YOLO Node, GBCACHE, Mapper, ROIS(Fusion)
For Each Node -> Label, Widget Type, Status Color [Binary; Is it delivering data? Yes or No]
'''

import sys
from PyQt6.QtCore import Qt, pyqtSignal, QObject
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QHBoxLayout,
    QVBoxLayout, QFrame, QGridLayout
)

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
        color = self.status_map.get(code, "gray")
        self.label.setStyleSheet(f"""
            border-radius: 4px;
            border: 1px solid black;
            background-color: {color};
            font-weight: bold;
        """)


class NodeStatusBridge(QObject):
    status_update = pyqtSignal(str, int)


# Main Node Widget; all nodes in a 5x1 grid
class NodePanel(QWidget):
    def __init__(self):
        super().__init__()

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

        # Demo Statuses
        self.nodes["Controls"].set_status_from_code(1)
        self.nodes["Path Planner"].set_status_from_code(0)
        self.nodes["Path Demo"].set_status_from_code(0)
        self.nodes["GBCACHE"].set_status_from_code(1)
        self.nodes["World Mapper"].set_status_from_code(0)
        self.nodes["ROI (Fusion)"].set_status_from_code(1)
        self.nodes["Dock Detection"].set_status_from_code(1)
        self.nodes["Task Manager"].set_status_from_code(0)
        self.nodes["PIDD 3DOF"].set_status_from_code(0)


    def update_node_from_signal(self, node_name, status_code):
        if node_name in self.nodes:
            self.nodes[node_name].set_status_from_code(status_code)

# Change the status of a node by doing self.node["YOLO Node"].set_status_from_code(#(0-1))
# 1 is green working
# 0 is red not working

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = NodePanel()
    window.setWindowTitle("Boat Nodes")
    window.resize(150, 200)
    window.show()

    sys.exit(app.exec())
