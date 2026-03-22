from PyQt6.QtCore import QObject, pyqtSignal, QTimer


class DiagnosticsSignals(QObject):
    node_status_update = pyqtSignal(str, int)
    # int status codes: 1 = alive, 0 = not found


class DiagnosticsSubscriber:

    # Maps ROS2 node names to display names used in the widget
    NODE_MAP = {
        "usv_controls_node":         "Controls",
        "path_planner_node":         "Path Planner",
        "path_planner_demo_node":    "Path Demo",
        "gbcache_node":              "GBCACHE",
        "world_mapper_node":         "World Mapper",
        "roi_color_classifier_node": "ROI (Fusion)",
        "dock_detection_node":       "Dock Detection",
        "task_manager_node":         "Task Manager",
        "pidd_3DOF_node":            "PIDD 3DOF",
    }

    def __init__(self, node):

        self.signals = DiagnosticsSignals()
        self.node = node

        # Poll active nodes every 2 seconds
        self.poll_timer = QTimer()
        self.poll_timer.setInterval(2000)
        self.poll_timer.timeout.connect(self._check_nodes)
        self.poll_timer.start()

    def _check_nodes(self):

        try:
            # Returns list of (name, namespace) tuples
            active_nodes = self.node.get_node_names_and_namespaces()
            active_names = {name for name, _ in active_nodes}

            for ros_name, display_name in self.NODE_MAP.items():
                if ros_name in active_names:
                    self.signals.node_status_update.emit(display_name, 1)
                else:
                    self.signals.node_status_update.emit(display_name, 0)

        except Exception as e:
            print(f"[diagnostics] Node discovery error: {e}")