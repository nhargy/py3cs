from ..device import Device

class FirmataBoard(Device):
    public = ['port']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.com = kwargs.get('com', 'COM1')
        self._board_type = kwargs.get('board', 'Arduino')

        self._dpins = [f'digital{x}' for x in range(14)]
        self._apins = [f'analog{x}' for x in range(6)]

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, value):
        self._port = value
        self.connect()

    def __getattr__(self, item):
        if item in self._dpins:
            n = int(item.replace('digital', ''))
            return self._board.digital[n].read()

        if item in self._apins:
            n = int(item.replace('analog', ''))
            return self._board.analog[n].read()

    def __setattr__(self, key, value):
        if key in self._dpins and value in [0, 1]:
            n = int(key.replace('digital', ''))
            self._board.digital[n].write(value)

        if key in self._apins and (0 <= value <= 5):
            n = int(key.replace('analog', ''))
            self._board.analog[n].write(value)

        else:
            super().__setattr__(key, value)

    def connect(self):
        try:
            import pyfirmata
            self._board = getattr(pyfirmata,self._board_type)(self._port)

        except:
            self.connected = False

    def disconnect(self):
        self._board.exit()


class FirmataDigitalPin(Device):
    public = ['port', 'board', 'pin', 'on', 'control', 'control_pin']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._port = kwargs.get('com', 'COM1')
        self._board_type = kwargs.get('board', 'Arduino')
        self._pin = kwargs.get('pin', 13)
        self._board = None

        self._control_pin = kwargs.get('control_pin', 12)
        self._control     = kwargs.get("control", "camera")

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, value):
        self._port = value
        self.connect()

    @property
    def board(self):
        return self._board_type

    @board.setter
    def board(self, value):
        if value in ["Arduino", "ArduinoDue", "ArduinoMega"]:
            self._board_type = value
            self.connect()

    @property
    def pin(self):
        return self._pin

    @pin.setter
    def pin(self, value):
        if value in range(14):
            self._pin = value

    @property
    def control_pin(self):
        return self._control_pin

    @control_pin.setter
    def control_pin(self, value):
        if value not in range(14):
            raise ValueError("Invalid pin value. Must be in range(14)")
        self._control_pin = value

    @property
    def on(self):
        return self._board.digital[self._pin].read() if self.control == "computer" else None

    @on.setter
    def on(self, value):
        if self.control == "camera":
            print("Warning! Attempted to set value while delegating device control. Action not performed.")
            return

        if value in ['on', 1, True]:
            self._board.digital[self._pin].write(1)
        elif value in ['off', 0, False]:
            self._board.digital[self._pin].write(0)

    @property
    def control(self):
        return self._control

    @control.setter
    def control(self, value):
        value = value.lower()
        if value not in "computer camera".split():
            raise ValueError("Invalid control option. Must be either 'computer' or 'camera'")

        self._control = value
        self._board.digital[self._control_pin].write(int(value == "camera"))

    @property
    def connected(self):
        if self._board is None:
            return False
        else:
            return True

    def connect(self):
        try:
            import pyfirmata
            self._board = getattr(pyfirmata,self._board_type)(self._port)
            self.connected = True

            self.control_pin = self._control_pin
            self.control     = self._control

        except:
            pass

    def disconnect(self):
        self._board.exit()
        self.connected = False
