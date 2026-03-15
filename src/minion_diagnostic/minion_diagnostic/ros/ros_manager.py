import threading
import rclpy
from rclpy.node import Node


class ROSManager(Node):

    def __init__(self):
        super().__init__("dashboard_node")


class ROSWorker:

    def __init__(self):

        rclpy.init()

        self.node = ROSManager()

        self.thread = threading.Thread(target=self.spin)
        self.thread.daemon = True
        self.thread.start()

    def spin(self):
        rclpy.spin(self.node)

    def shutdown(self):
        rclpy.shutdown()