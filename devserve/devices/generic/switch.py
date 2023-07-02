from ..device import Device
import serial


class Switch(Device):

    public = ['on', 'port']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._port = kwargs.get('com', 'COM1')
        self._baud = kwargs.get('baud', 115200)
        self.conn = None

    def connect(self):
        try:
            self.conn = serial.Serial(self._port, baudrate=self._baud, timeout=1)
        except:
            return f'Could not connect to port {self._port}.'

    @property
    def connected(self):
        if self.conn is not None:
            return self.conn.is_open
        return False

    def disconnect(self):
        if self.connected:
            self.conn.close()

    @property
    def on(self):
        resp = self.conn.query("?")
        if resp in [True, 1, 'True', "true", "1"]:
            return True
        if resp in [False, 0, "off", "False", "false", "0"]:
            return False

    @on.setter
    def on(self, value):
        if value in [True, 1, 'True', "true", "1"]:
            self.conn.command("on")
        if value in [False, 0, "off", "False", "false", "0"]:
            self.conn.command("off")

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, value):
        self._port = value
        if self.connected:
            self.disconnect()
        try:
            self.connect()
        except:
            pass
