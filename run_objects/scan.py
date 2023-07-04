"""
class   : scan
author  : Nadav Hargittai
"""

from run_objects.sys3CS import default_rule
from auxil.auxil import logprint
import os
import numpy as np
import h5py as h5
import time


# Default system_state_filepath
path_to_system_state = 'C:/rep_py3cs/py3cs/config/system/states'
default_state = 'state_AA.json'

# group keys
gp_keys = ["spectra", "system", "log"]

class scan:
    
    def __init__(self, path_to_hdf5, rule_filepath = default_rule, system_state_filepath = default_state):
        
        # now this class can have a method that takes the system state by
        # reading the state json file, and creating a group for each device
        # it can also check for a npy file in the folder of the component,
        # and create a named dataset for it within the group, alongside the id
        
        self.path_to_hdf5          = path_to_hdf5
        self.rule_filepath         = rule_filepath
        self.system_state_filepath = system_state_filepath
        
        return None
    
    
    def construct_hdf5(self):
        
        if os.path.exists(self.path_to_hdf5):
            print(f"{self.path_to_hdf5} already exists")
        else:
            f = h5.File(self.path_to_hdf5)
            
            print("Creating file ...")
            time.sleep(2)     # wait for file to properly created
            print("Created.")
            
            for key in gp_keys:
                try:
                    f.create_group(key)
                except:
                    pass
            
            # create log dataset
            
            dt = np.dtype([('date_time', 'S20'), ('string', 'S100')])
            
            f["log"].create_dataset("sys_log", shape=(1, 1), maxshape=(None, 2), dtype=dt)
            
            time.sleep(0.5)
            
            # close hdf5 file
            f.close()
            
            logprint(f"Constructed hdf5 file {self.path_to_hdf5} with groups: {gp_keys}.", self.path_to_hdf5)
            
    