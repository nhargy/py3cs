"""
class   : scan
author  : Nadav Hargittai
"""

from run_objects.sys3CS import default_rule
from run_objects.sys3CS import sys3CS
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
path_to_scan_protocols  = 'C:/rep_py3cs/py3cs/config/protocols'
path_to_solis_folder           = 'D:/solis_dump'
default_protocol = 'default.json'
default_state = 'state_AA.json'

# group keys
gp_keys = ["spectra", "system", "log"]

class scan:
    
    def __init__(self, path_to_hdf5, rule_filepath = default_rule, system_state_filepath = f'{path_to_system_state}/{default_state}', scan_protocol_filepath = f'{path_to_scan_protocols}/{default_protocol}'):
        
        # now this class can have a method that takes the system state by
        # reading the state json file, and creating a group for each device
        # it can also check for a npy file in the folder of the component,
        # and create a named dataset for it within the group, alongside the id
        
        self.path_to_hdf5           = path_to_hdf5
        self.rule_filepath          = rule_filepath
        self.system_state_filepath  = system_state_filepath
        self.scan_protocol_filepath = scan_protocol_filepath
        
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



    def go(self, max_wl, min_wl, step, orientation = 'unk'):
        
        logprint("Starting scan!", self.path_to_hdf5)
        
        path_to_protocol = self.scan_protocol_filepath
        
        # extract protocol from scan json file
        protocol_json = open(path_to_protocol, 'r')
        time.sleep(0.25)
        protocol_data = protocol_json.read()
        protocol_dict = json.loads(protocol_data)
        
        print(protocol_dict)
        
        path_to_dump = f'{path_to_solis_folder}/solis_temp.txt'
        
        ranges = protocol_dict['ranges']
        times  = protocol_dict['times']
        spec_offset = protocol_dict['spec_offset'] 
        sp_samples  = protocol_dict['sp_samples']
        bg_samples  = protocol_dict['bg_samples']
        logprint(f"Extracted ranges as: {ranges}", self.path_to_hdf5, toprint=False)
        logprint(f"Extracted times as: {times}", self.path_to_hdf5, toprint=False)
        
        # set the wavelengths of the scan
        wl_arr = np.arange(max_wl, min_wl - 1, -step)
        logprint(f"Wavelengths array set to: {wl_arr}", self.path_to_hdf5)
        
        # initiate sys3CS object
        sys = sys3CS(rule_filepath = self.rule_filepath, log_target = self.path_to_hdf5)
        
        # loop through wavelengths
        for wl in wl_arr:
            
            print()
            logprint(" - - - - - - - - - - ", self.path_to_hdf5)
            logprint(f"Starting scan for {wl} nm", self.path_to_hdf5)
            print()
            
            # set monochromator excitation wavelength
            sys.ctrl(mono_wl = int(wl), spec_wl = int(wl) + spec_offset)
            
            # create the wavelength group
            f     = h5.File(self.path_to_hdf5, 'a')
            try:
                wl_gp = f['spectra'].create_group(str(wl))
            except:
                wl_gp = f['spectra'][str(wl)]
                
                
            # create the orientation group
            try:
                or_gp = wl_gp.create_group(orientation)
            except:
                pass
                
            f.close()
            
            # find the time array of this wavelength
            for i in range(0, len(ranges) - 1):
                if ranges[i] <= wl < ranges[i+1]:
                    t_arr = times[i]
            
            # apply rules
            sys.apply_rules(wl)
            
            for t in t_arr:
                
                logprint(f"Taking spectra of {t}sec", self.path_to_hdf5)
                
                sys.ctrl(spec_exp = t)
                
                sp_data       = []
                bg_data       = []
                power_samples = []
                
                # take bg data first
                
                logprint("Taking background data", self.path_to_hdf5)
                for i in range(0, bg_samples):
                    logprint(f' {i}.', self.path_to_hdf5)
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
                for j in range(0,sp_samples):
                    logprint(f' {j}.', self.path_to_hdf5)
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
                t_gp = f['spectra'][str(wl)][orientation].create_group(f"{float(t)}sec")
                
                # datasets
                t_gp.create_dataset("bg_data", data = bg_data)
                t_gp.create_dataset("sp_data", data = sp_data)
                t_gp.create_dataset("power_samples", data = np.array(power_samples))
                
                # metadata
                state_dict = sys.get_state()
                state_dict.update(solis_dict)
                
                t_gp.attrs.update(state_dict)
                

        return None