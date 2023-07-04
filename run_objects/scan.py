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
import json
import glob

# Default system_state_filepath
path_to_system_state = 'C:/rep_py3cs/py3cs/config/system/states'
path_to_system_components = 'C:/rep_py3cs/py3cs/config/system/components'
default_state = 'state_AA.json'

# group keys
gp_keys = ["spectra", "system", "log"]

class scan:
    
    def __init__(self, path_to_hdf5, rule_filepath = default_rule, system_state_filepath = f'{path_to_system_state}/{default_state}'):
        
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
            f = h5.File(self.path_to_hdf5 , 'a')
        else:
            print("Creating file ...")
            time.sleep(2)     # wait for file to properly created
            print("Created.")
            f = h5.File(self.path_to_hdf5 , 'w')
        
        
        for key in gp_keys:
            try:
                f.create_group(key)
            except:
                print(f'{key} already exists')
        
        # create log dataset
        
        dt = np.dtype([('date_time', 'S20'), ('string', 'S100')])
        
        f["log"].create_dataset("sys_log", shape=(1, 1), maxshape=(None, 2), dtype=dt)
        
        time.sleep(0.5)
        
        # close hdf5 file
        f.close()
        
        time.sleep(0.25)
        
        logprint(f"Constructed hdf5 file {self.path_to_hdf5} with groups: {gp_keys}.", self.path_to_hdf5)
    
    
    
    def write_metadata(self, meta_dict):
        
        f = h5.File(self.path_to_hdf5, 'a')
        f.attrs.update(meta_dict)
        f.close()
    
    
    
    def write_system_config(self):
        
        logprint(f"Writing system information from {self.system_state_filepath}", self.path_to_hdf5)
        
        sys_json = open(self.system_state_filepath, 'r')
        sys_data  = sys_json.read()
        sys_arr   = json.loads(sys_data)['components']
        sys_json.close()
        
        for comp in sys_arr:
            try:
                logprint(f"Writing component information for {comp}", self.path_to_hdf5)
                
                f = h5.File(self.path_to_hdf5, 'a')
                
                try:
                    gp = f['system'].create_group(comp)
                    logprint(f"Created group {gp}", self.path_to_hdf5)
                except:
                    gp = f[comp]
                
                time.sleep(0.25)
                
                # look for its folder
                comp_folder = f'{path_to_system_components}/{comp}'
                
                # get id dict
                id_json = open(f'{comp_folder}/id.json')
                id_data = id_json.read()
                id_dict = json.loads(id_data)

                # add the id as metadata to group
                gp.attrs.update(id_dict)
                
                # Specify the folder path and file extension
                file_extension = '*.npy'

                # Use glob to find files matching the specified pattern
                file_list = glob.glob(f"{comp_folder}/{file_extension}")

                # Loop through the files
                for file_path in file_list:
                    # Process each file as needed
                    np_arr = np.load(file_path)
                    gp.create_dataset("data", data=np_arr)
                    
                f.close()
            except Exception as e:
                logprint(f"Could not access information for {comp}", self.path_to_hdf5)
                logprint(e, self.path_to_hdf5)
                
        logprint("Done", self.path_to_hdf5)
        try:
            f.close()
        except:
            pass