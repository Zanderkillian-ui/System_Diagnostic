import time
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from minion_msgs.msg import VehicleData


class BoatHeartbeatSignals(QObject):
    connection_status = pyqtSignal(bool)
    battery_update    = pyqtSignal(float)   # voltage as percentage


class BoatHeartbeatSubscriber:

    TIMEOUT_SEC = 10.0
    MAX_VOLTAGE = 24.0  

    def __init__(self, node):

        self.signals = BoatHeartbeatSignals()

        self.last_msg_time = None
        self.connected = False

        self.sub = node.create_subscription(
            VehicleData,
            "/mini_minion/controls/vehicle_info",
            self.callback,
            10
        )

        self.timeout_timer = QTimer()
        self.timeout_timer.setInterval(1000)
        self.timeout_timer.timeout.connect(self._check_timeout)
        self.timeout_timer.start()

    def callback(self, msg):

        self.last_msg_time = time.time()

        if not self.connected:
            self.connected = True
            self.signals.connection_status.emit(True)

        pct = min(100.0, max(0.0, (msg.voltage / self.MAX_VOLTAGE) * 100.0))
        self.signals.battery_update.emit(pct)

    def _check_timeout(self):

        if self.last_msg_time is None:
            return

        elapsed = time.time() - self.last_msg_time

        if elapsed >= self.TIMEOUT_SEC and self.connected:
            self.connected = False
            self.signals.connection_status.emit(False)