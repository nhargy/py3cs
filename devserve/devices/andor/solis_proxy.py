import serial
import struct
import time
from ..device import Device
import ast

class SolisProxy(Device):
    """
    Connects to a proxy script running in
    Andor solis, written with Andor BASIC.
    """
    _valid_baud = [4800, 9600, 14400, 19200, 38400, 57600, 115200]

    public = [    'pixel_wl',    'npixel_h',       'npixel_v', # Hardware properties
                      'port',        'baud',                   # Connection properties
                   'grating',     'shutter',                   # Device configuration
                  'exposure',  'slit_width',                   # .
                'wavelength',      'min_wl',         'max_wl', # .
                 'save_path', 'carea_wlmin',    'carea_wlmax', # Data management
                   'running',       'saved', 'corrected_area', # Operations
              'clear_screen']                                  # .

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._port = kwargs.get('com', "COM1")
        self._baud = kwargs.get('baud', 38400)
        self._path = kwargs.get('save_path', f"andor_file_{time.time()}")
        self._saved = False
        self._running = False
        self.conn = None

        self._pixel_wl =    0.523955
        self._npixel_h = 1600
        self._npixel_v =  400

        self._carea_range = [-1, -1] # Must be mutable!

    @property
    def pixel_wl(self):
        return self._pixel_wl

    @property
    def npixel_h(self):
        return self._npixel_h

    @property
    def npixel_v(self):
        return self._npixel_v

    @property
    def min_wl(self):
        return self.wavelength - self.pixel_wl * self.npixel_h // 2

    @property
    def max_wl(self):
        return self.wavelength + self.pixel_wl * self.npixel_h // 2

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

    @property
    def baud(self):
        return self._baud

    @baud.setter
    def baud(self, value):
        if value not in self._valid_baud:
            raise ValueError(f"Invalid baud rate: {value}. Valud must be one of {self._valid_baud}")

        self._baud = value
        self.connect()

    def query(self, q):
        self.conn.write(f'{q}\r'.encode())
        resp = self.conn.read(150)
        resp = resp.strip().decode()
        return resp

    def command(self, cmd, *args):
        self.conn.write(f'{cmd}\r'.encode())
        time.sleep(0.01)
        self.conn.read(150)
        for arg in args:
            self.conn.write(f'{arg}\r'.encode())
            self.conn.read(150)

    @property
    def save_path(self):
        return self._path

    @save_path.setter
    def save_path(self, path):
        if not isinstance(path, str):
            raise ValueError(f"`path` must be a str, got {type(path)}")

        self._path  =  path
        self._saved = False

    @property
    def clear_screen(self):
        self.command("ClearScreen")
        return 'clear'

    @clear_screen.setter
    def clear_screen(self, value):
        if value not in [1, True, 'True', 'clear']:
            raise ValueError(f"Unrecognized value {value}")

        self.command("ClearScreen")

    @property
    def saved(self):
        return self._saved

    @saved.setter
    def saved(self, value):
        if   value in [1,  True,  'True',  'true']:
            self.command("Save", self._path)
            self._saved = True
        elif value in [0, False, 'False', 'false']:
            self._saved = False
        else:
            raise ValueError(f"Unrecognized save value {value}")

    @property
    def shutter(self):
        return self.query("GetShutter")

    @shutter.setter
    def shutter(self, value):
        if value in [1, True, 'Open', 'open']:
            self.command("SetShutter", "open")
        elif value in [0, False, 'Closed', 'closed']:
            self.command("SetShutter", 'close')
        elif value in ["auto", "Auto"]:
            self.command("SetShutter", 'auto')
        else:
            raise ValueError(f"Unrecognized shutter value {value}")

    @property
    def running(self):
        return False

    @running.setter
    def running(self, running):
        if running not in [1, True, 'True']:
            raise ValueError(f"Unrecognized running status {running}")

        self.command('Run')
        while True:
            try:
                if self.conn.read(150) == b"Done\r\n":
                    break
            except:
                pass

            time.sleep(0.2)

        self._saved = False

    @property
    def grating(self):
        out = ""
        while not out.strip():
            out = self.query("GetGrating")
        return out

    @grating.setter
    def grating(self, value):
        if value not in [1, 2]:
            raise ValueError(f"Invalid grating number: {value}")

        self.command("SetGrating", value)
        while True:
            if self.grating == f"{value}":
                break
            else:
                time.sleep(4)

    @property
    def wavelength(self):
        response = self.query("GetWavelength").split("\r")[0]
        return float(response) if response else 0

    @wavelength.setter
    def wavelength(self, value):
        if not 2000 >= value >= 200:
            raise ValueError(f"Invalid wavelength {value}. Must be between 200 and 2000 nm")

        self.command("SetWavelength", value)

    @property
    def exposure(self):
        return self.query("GetExposureTime")

    @exposure.setter
    def exposure(self, value):
        self.command("SetExposureTime", value)

    @property
    def slit_width(self):
        return self.query("GetSlit")

    @slit_width.setter
    def slit_width(self, value):
        if not 2500 >= value >= 10:
            raise ValueError(f"Invalid slit width {value}. Must be between 10 and 2500 µm")

        self.command("SetSlit", value)

    def _pixel_number(self, wl):
        return 1 + int(round((wl - self.min_wl) / self.pixel_wl))

    @property
    def carea_wlmin(self):
        return self._carea_range[0]

    @property
    def carea_wlmax(self):
        return self._carea_range[1]

    @carea_wlmin.setter
    def carea_wlmin(self, value):
        self._carea_range[0] = self._pixel_number(value)

    @carea_wlmax.setter
    def carea_wlmax(self, value):
        self._carea_range[1] = self._pixel_number(value)

    @property
    def corrected_area(self):
        pmin, pmax = self._carea_range
        response = self.query(f"CArea\r{pmin}\r{pmax}")
        return float(response)

    def connect(self):
        self.disconnect()
        try:
            self.conn = serial.Serial(self._port, baudrate=self._baud, timeout=0.2)
        except:
            pass

    @property
    def connected(self):
        if self.conn:
            return self.conn.is_open
        return False

    def disconnect(self):
        if self.connected:
            self.conn.close()
