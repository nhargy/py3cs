from serial.rs485 import RS485
import time
from ..device import Device
# from .. import device_directory


class EQ77(Device):

    public = ['power', 'port']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._port = kwargs.get('com', "COM1")
        self.conn = None

    def query(self, q):
        if q not in ['U', 'D', 'Q']:
            return ''
        self.conn.write(q.encode())
        res = self.conn.read(2048)
        return float(res.decode().strip().split(' = ')[-1].replace('%',''))

    @property
    def power(self):
        return self.query('Q')

    @power.setter
    def power(self, pwr):
        pwr = int(pwr)
        if pwr>100 or pwr<15:
            return
        p = self.power
        while True:
            if p==pwr:
                break
            elif p>pwr:
                p = self.query('D')
            elif p<pwr:
                p = self.query('U')
            time.sleep(0.2)

    def connect(self):
        try:
            self.conn = RS485(self._port, baudrate=9600, timeout=1)
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


if __name__ == '__main__':
    with EQ77('COM8') as en:
        print(en.power)