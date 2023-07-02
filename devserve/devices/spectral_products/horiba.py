import serial
import struct
import usb.core
import time
from ..device import Device

# Values for Horiba
LANG_ID_US_ENGLISH = 0x489

# Identifiers of the product in USB spec
JOBIN_YVON_ID_VENDOR = 0xC9B
MICRO_HR_ID_PRODUCT = 0x100
IHR320_ID_PRODUCT = 0x101

# Parameters for ctrl_transfer
BM_REQUEST_TYPE = 0xB3
B_REQUEST_OUT = 0x40
B_REQUEST_IN = 0xC0

# wIndex values for USB commands
INITIALIZE = 0
SET_WAVELENGTH = 4
READ_WAVELENGTH = 2
SET_TURRET = 17
READ_TURRET = 16
SET_MIRROR = 41
READ_MIRROR = 40
SET_SLITWIDTH = 33
READ_SLITWIDTH = 32
IS_BUSY = 5

class horiba(Device):

    public = ['gr','wl','sl']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conn = None
        self._gr = None
        self._wl = None
        self._sl = None

    ### grating functionality ###
    def gr_query(self):
        qu = self.conn.ctrl_transfer(B_REQUEST_IN, BM_REQUEST_TYPE, wIndex=READ_TURRET, data_or_wLength=4)
        return struct.unpack("<i", qu)[0]

    @property
    def gr(self):
        self._gr = self.gr_query()
        return self._gr

    @gr.setter
    def gr(self,value):
        self.conn.ctrl_transfer(B_REQUEST_OUT,BM_REQUEST_TYPE,wIndex=SET_TURRET,data_or_wLength=struct.pack("<i",value))
        time.sleep(7.5)

    ### wavelength functionality ###
    def wl_query(self):
        qu = self.conn.ctrl_transfer(B_REQUEST_IN, BM_REQUEST_TYPE, wIndex=READ_WAVELENGTH, data_or_wLength=4)
        return struct.unpack("<f",qu)[0]

    @property
    def wl(self):
        self._wl = self.wl_query()
        return self._wl

    @wl.setter
    def wl(self,value):
        self.conn.ctrl_transfer(B_REQUEST_OUT, BM_REQUEST_TYPE, wIndex=SET_WAVELENGTH, data_or_wLength=struct.pack("<f",value))
        time.sleep(2.5)




    ###################
    ### connections ###
    ###################
    def connect(self):
        
        try:
            self.conn = usb.core.find(idVendor=JOBIN_YVON_ID_VENDOR, idProduct=MICRO_HR_ID_PRODUCT, backend=None)
            self.conn.ctrl_transfer(B_REQUEST_IN, BM_REQUEST_TYPE, wIndex=INITIALIZE, data_or_wLength=4)
            dev_langids = (LANG_ID_US_ENGLISH,)
        except:
            print("shit")
            pass

    @property
    def connected(self):
        if self.conn is None:
            return False
        else:
            return True

    def disconnect(self):
        if self.connected:
            self.conn.close()