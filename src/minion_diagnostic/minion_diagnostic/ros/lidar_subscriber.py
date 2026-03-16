import time
from sensor_msgs.msg import PointCloud2
from PyQt6.QtCore import QObject, pyqtSignal


class LidarSignals(QObject):
    rate_update = pyqtSignal(float)


class LidarRateSubscriber:

    def __init__(self, node):

        self.signals = LidarSignals()

        self.last_time = None
        self.msg_count = 0

        self.sub = node.create_subscription(
            PointCloud2,
            "/wamv/sensors/lidars/lidar_sensor/points",
            self.callback,
            10
        )

    def callback(self, msg):

        now = time.time()

        if self.last_time is None:
            self.last_time = now
            return

        self.msg_count += 1

        dt = now - self.last_time

        if dt >= 1.0:

            hz = self.msg_count / dt

            self.signals.rate_update.emit(hz)

            self.msg_count = 0
            self.last_time = now