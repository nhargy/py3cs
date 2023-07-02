import random


class Device:
    _common = ['connected', 'attributes']
    public = []

    def __init__(self, *args, **kwargs):
        pass

    def connect(self):
        raise NotImplementedError

    def disconnect(self):
        raise NotImplementedError

    @property
    def attributes(self):
        return self.public + self._common

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.disconnect()

class Debugger(Device):
    public = ['echo', 'echo2','random']
    connected = True
    _echo = 'echo'
    _echo2 = 'echo2'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def echo(self):
        return self._echo

    @echo.setter
    def echo(self, value):
        self._echo = value

    @property
    def echo2(self):
        return self._echo2

    @echo2.setter
    def echo2(self, value):
        self._echo2 = value

    @property
    def random(self):
        return random.random()

    def connect(self):
        pass

    def disconnect(self):
        pass


