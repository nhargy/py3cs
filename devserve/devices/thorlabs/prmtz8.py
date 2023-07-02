from ..device import Device
import ast

class PRMTZ8(Device):
    public = ['position', 'port', 'zero', 'step', 'reverse']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._port = ast.literal_eval(kwargs.get('com', 27503140))
        self._motor = None
        self._zero = kwargs.get('zero', None)
        self._reverse = kwargs.get('reverse', True)
        self._step = kwargs.get('step', 30)
        self._make_pos_mapper()
        
    def _make_pos_mapper(self):
        self._pos_mapper = {x:(-y if self._reverse else y) for x,y in zip(list(range(7,12))+list(range(7)), range(-5,7))}

    @property
    def reverse(self):
        return self._reverse

    @reverse.setter
    def reverse(self, value):
        if value in [True, False]:
            self._reverse = value
        self._make_pos_mapper()
        
        
    @property
    def step(self):
        return self._step

    @step.setter
    def step(self, value):
        self._step = value
    
    @property
    def zero(self):
        return self._zero

    @zero.setter
    def zero(self, value):
        self._zero = value

    @property
    def position(self):
        if self._motor is None:
            return
        deg = self._motor.position
        pos = (deg-self._zero)/self._step
        if self._reverse:
            pos = -pos
        # print(f'At abs pos: {deg} degrees')
        pos = int(round(pos))
        if pos>=0:
            return pos
        else:
            return pos+12

    @position.setter
    def position(self, pos):
        if self._motor is None or pos not in range(12):
            return
        pos = self._pos_mapper[pos]
        now = self._pos_mapper[self.position]
        # print(f'now at {now} moving to {pos}')
        deg = (pos-now)*self._step
        # print(f'moving {deg} degrees')
        self._motor.move_by(deg, blocking=True)


    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, value):
        self._port = value
        self.connect()

    def connect(self):
        if self.connected:
            return
        try:
            import thorlabs_apt as apt
            self._motor = apt.Motor(self._port)
            if self._zero is None:
                self._zero = self._motor.position
         
        except:
            pass

    def disconnect(self):
        try:
            import thorlabs_apt as apt
            self._motor = None
            apt.core._cleanup()
        except:
            pass
            
    @property
    def connected(self):
        if self._motor is None:
            return False
        return True
