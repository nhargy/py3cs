"""
class: system sensitivity
author: Nadav Hargittai
"""

from run_objects.sys3CS import sys3CS
from auxil.auxil import logprint
from run_objects.sys3CS import default_rule
import os
import time
import h5py as h5
import numpy as np
import json
import glob

# Default system_state_filepath
path_to_system_state = 'C:/rep_py3cs/py3cs/config/system/states'
path_to_system_components = 'C:/rep_py3cs/py3cs/config/system/components'
path_to_scan_protocols  = 'C:/rep_py3cs/py3cs/config/protocols'
path_to_solis_folder           = 'D:/solis_dump'
default_protocol = 'default.json'
default_state = 'state_AA.json'

# group keys
gp_keys = ["spectra", "system", "log"]

class senso:
    
    def __init__(self, min_wl, max_wl, step, path_to_hdf5, path_to_protocol, path_to_rule=default_rule, system_state_filepath = f'{path_to_system_state}/{default_state}', sys_obj=None):
        
        self.min_wl           = min_wl
        self.max_wl           = max_wl
        self.step             = step
        self.path_to_protocol = path_to_protocol
        self.path_to_rule     = path_to_rule
        self.path_to_hdf5     = path_to_hdf5
        self.system_state_filepath = system_state_filepath
        self.sys_obj          = sys_obj
            
            
            
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
        
        
        
    def go(self):

        if self.sys_obj == None:
            sys = sys3CS(rule_filepath = self.path_to_rule, log_target = self.path_to_hdf5)
        else:
            sys = self.sys_obj
            sys.log_target = self.path_to_hdf5
            sys.rule_filepath = self.rule_filepath        
       
        # open rules
        # extract rules from file
        with open(self.path_to_rule) as rules:
            data   = json.load(rules)
            devices  = data['devices']
            ranges   = data['ranges']
            states   = data['states']
            
        # open protocl
        # extract rules from file
        with open(self.path_to_protocol) as protocol:
            data   = json.load(protocol)
            ranges_p = data['ranges']
            times_p  = data['times']
            spec_offset = data['spec_offset']            
            sp_samples  = data['sp_samples']
            bg_samples  = data['bg_samples']
            
        num = len(states)
        print('NUUUUUMMMMM::::')
        print(num)
        
        path_to_dump = f'{path_to_solis_folder}/solis_temp.txt'
        
        # loop through states
        for i in range(0,num):
            print(i)
            # get first wavelength of state, and a representative wl
            first_wl = ranges[i+1]
            rep_wl = first_wl + 1
            
            # create group
            f = h5.File(self.path_to_hdf5, 'a')
            try:
                state_gp = f['spectra'].create_group(f'state_{i}')
            except:
                state_gp = f['spectra'][f'state_{i}']
            
            f.close()
            
            print(f"Applying rules to rep wl {rep_wl}")
            sys.apply_rules(rep_wl ,apply_exc =False)
        
            # the wavelengths for THIS state
            wl_arr   = np.arange(first_wl, self.max_wl, self.step)
            print(wl_arr)
            
            for wl in wl_arr:

                f = h5.File(self.path_to_hdf5, 'a')
                state_gp = f['spectra'][f'state_{i}']

                # create wl group
                try:
                    wl_gp = state_gp.create_group(str(wl))
                except:
                    wl_gp = state_gp[str(wl)]
                    
                f.close()

                sys.ctrl(mono_wl=int(wl), spec_wl = int(wl))
                
                # get times array
                for j in range(0, len(ranges_p) - 1):
                    if ranges_p[j] <= wl < ranges_p[j+1]:
                        t_arr = times_p[j]
                        
                for t in t_arr:
                    
                    logprint(f" * * * ", self.path_to_hdf5)
                    logprint(f"Taking spectra of {t}sec", self.path_to_hdf5)
                    
                    sys.ctrl(spec_exp = t)
                    
                    sp_data       = []
                    bg_data       = []
                    power_samples = []
                    
                # take bg data first
                
                logprint("Taking background data", self.path_to_hdf5)
                for k in range(0, bg_samples):
                    logprint(f' {k}.', self.path_to_hdf5)
                    sys.ctrl(spec_shutter=True)
                    sys.ctrl(spec_run=True)
                    sys.ctrl(spec_shutter=False)
                    np_data, solis_dict, power_sample = sys.ctrl(spec_save = path_to_dump)

                    time.sleep(0.25)
                    bg_data.append(np_data)
                    os.remove(path_to_dump)
                    time.sleep(0.5)
                
                # then take sp data
                logprint("Taking sample spectra", self.path_to_hdf5)
                for l in range(0,sp_samples):
                    logprint(f' {l}.', self.path_to_hdf5)
                    sys.ctrl(source_shutter_on=True, spec_shutter=True)
                    sys.ctrl(spec_run=True)
                    np_data, solis_dict, power_sample = sys.ctrl(spec_save = path_to_dump)
            
                    time.sleep(0.25)
                    sys.ctrl(source_shutter_on=False, spec_shutter=False)
                    
                    sp_data.append(np_data)
                    power_samples.append(power_sample)
                    os.remove(path_to_dump)
                    time.sleep(0.5)

                # now create the group, datasets and metadata
                
                # group
                f = h5.File(self.path_to_hdf5, 'a')
                t_gp = f['spectra'][f'state_{i}'][str(wl)].create_group(f"{float(t)}sec")
                
                # datasets
                t_gp.create_dataset("bg_data", data = bg_data)
                t_gp.create_dataset("sp_data", data = sp_data)
                t_gp.create_dataset("power_samples", data = np.array(power_samples))
                
                # metadata
                state_dict = sys.get_state()
                state_dict.update(solis_dict)
                
                t_gp.attrs.update(state_dict)
                
                f.close()
            
            
            
            
        
        return None