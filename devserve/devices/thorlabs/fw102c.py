# fw102c.py
#
# Thorlabs FW102C - Six-Position Motorized Filter Wheel - Python interface

# Gilles Simond <gilles.simond@unige.ch>	

# who       when        what
# --------  ----------  -------------------------------------------------
# gsimond   20140922    modified from Adrien.Deline version
# jmosbacher 20181020   modified to fit my needs
from ..device import Device
# from .. import device_directory
import io,re,sys

import serial


class FW102C(Device):
    public = [ 'speed', 'sensors', 'port', 'cached_status', 'filter', 'position',]
    regerr = re.compile("Command error.*")
    """
       Class to control the ThorLabs FW102C filter wheel
       
          fwl = FW102C(port='COM5')
          fwl.help()
          fwl.position = 5
          fwl.position
          fwl.disconnect()
          
       The following table describes all of the available commands and queries:
        *idn?     Get ID: Returns the model number and firmware version
        pos=n     Moves the wheel to filter position n
        pos?      Get current Position
        pcount=n  Set Position Count: Sets the wheel type where n is 6 or 12
        pcount?   Get Position Count: Returns the wheel type
        trig=0    Sets the external trigger to the input mode
        trig=1    Sets the external trigger to the output mode
        trig?     Get current Trigger Mode
        speed=0   Sets the move profile to slow speed
        speed=1   Sets the move profile to high speed
        speed?    Returns the move profile mode
        sensors=0 Sensors turn off when wheel is idle to eliminate stray light
        sensors=1 Sensors remain active
        sensors?  Get current Sensor Mode
        baud=0    Sets the baud rate to 9600
        baud=1    Sets the baud rate to 115200
        baud?     Returns the baud rate where 0 = 9600 and 1 = 115200
        save      This will save all the settings as default on power up
        
    """
    
    
    devInfo  = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._port = kwargs.get('com', "COM1")
        self._fw = None
        self._status = {}
        self._filter_map = kwargs.get('filter_map', {})

    def help(self):
        print( self.__doc__)

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
    def connected(self):
        if self._fw is not None:
            return self._fw.is_open
        return False

    def connect(self):
        try:
            self._fw = serial.Serial(port=self.port, baudrate=115200,
                                  bytesize=8, parity='N', stopbits=1,
                                  timeout=1, xonxoff=0, rtscts=0)
            self._sio = io.TextIOWrapper(io.BufferedRWPair(self._fw, self._fw, 1),
                                         newline=None, encoding='ascii')
            self._sio.write(u'*idn?\r')
            self.devInfo = self._sio.readlines(2048)[1][:-1]

            for attr in self.public:
                if attr == 'cached_status':
                    continue
                self._status[attr] = getattr(self, attr)

        except  serial.SerialException as ex:
            print( 'Port {0} is unavailable: {1}'.format(self.port, ex))
            return

        except  OSError as ex:
            print( 'Port {0} is unavailable: {1}'.format(self.port, ex))
            return
    
    @property
    def cached_status(self):
        return self._status
    
    def disconnect(self):
        if not self.connected:
            print( "Disconnect error: Device not open")
            return "ERROR"
        #end if
        
        self._fw.close()
        return "OK"
    # end def disconnect

    def query(self, cmdstr):
        """
           Send query, get and return answer
        """
        if not self.connected:
            print( "Query error: Device not open")
            return "DEVICE NOT OPEN"
        #end if
        
        ans = 'ERROR'
        self._sio.flush()
        res = self._sio.write(cmdstr+u'\r')
        if res:
            ans = self._sio.readlines(2048)[1][:-1]
        #print 'queryans=',repr(ans)
        return ans
    # end def query

    def command(self, cmdstr):
        """
           Send command, check for error, send query to check and return answer
           If no error, answer value should be equal to command argument value
        """
        if not self.connected:
            print( "Command error: Device not open")
            return "DEVICE NOT OPEN"
        #end if
        
        ans = 'ERROR'
        self._sio.flush()
        cmd = cmdstr.split('=')[0]
        res = self._sio.write(cmdstr+u'\r')
        ans = self._sio.readlines(2048)

        errors = [m.group(0) for l in ans for m in [self.regerr.search(l)] if m]
        #print 'res=',repr(res),'ans=',repr(ans),cmd
        if len(errors) > 0:
            return errors[0]
        ans = self.query(cmd+'?')
        #print 'ans=',repr(ans),cmd+'?'
        return ans
        
    # end def command
    @property
    def info(self):
        if not self.connected:
            print( "Get info error: Device not open")
            return "DEVICE NOT OPEN"
        #end if
        
        return self.devInfo

    @property
    def position(self):
        return self.query("pos?")

    @position.setter
    def position(self, value):
        self.command(f'pos={value}')
        self._status['position'] = value

    @property
    def filter(self):
        pos = self.position
        return self._filter_map.get(pos, None)

    @filter.setter
    def filter(self, value):
        for pos, filter in self._filter_map.items():
            if filter == value:
                self.positon = pos

    @property
    def sensors(self):
        return self.query("sensors?")

    @sensors.setter
    def sensors(self, value):
        if value in [0,1]:
            self.command(f'sensors={value}')
            self._status['sensors'] = value

    @property
    def speed(self):
        return self.query("speed?")

    @speed.setter
    def speed(self, value):
        if value in [0,1]:
            self.command(f'speed={value}')
            self._status['speed'] = value

# Class test, when called directly
if __name__ == "__main__":
    fwl = FW102C(port='COM9')
    if not fwl.connected:
        print( "FWL INIT FAILED")
        sys.exit(2)
    print( '**info',fwl.info)
    print( '**idn?',fwl.query('*idn?'))

    print( '**pos=5',fwl.command('pos=5'))
    print( '**pos?',fwl.query('pos?'))
    print( '**pos=7',fwl.command('pos=7'))
    print( '**pos?',fwl.query('pos?'))
    print( '**pos=3',fwl.command('pos=3'))
    print( '**pos?',fwl.query('pos?'))
    print( '**pos=6',fwl.command('pos=6'))
    print( '**pos?',fwl.query('pos?'))
    print( '**qwzs=3',fwl.command('qwz=3'))
    print( '**pos?',fwl.query('pos?'))
    print(fwl.disconnect())

# oOo
# device_directory['FW102C'] = FW102C
