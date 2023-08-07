"""
class   : power
author  : Nadav Hargittai
"""

from run_objects.sys3CS import sys3CS
from auxil.auxil import logprint
import numpy as np
import json

class power:
    
    def __init__(self, path_to_config, path_to_save, path_to_rule, sys = None):
        
        self.sys            = sys
        self.path_to_config = path_to_config
        self.path_to_save   = path_to_save
        self.path_to_rule   = path_to_rule
        
        # get parameters from power config json file
        f = open(path_to_config)
        data = f.read()
        f_dict = json.loads(data)
        
        self.min_wl         = f_dict["min_wl"]
        self.max_wl         = f_dict["max_wl"]
        self.step           = f_dict["step"]
        self.samples        = f_dict["samples"]
        
        f.close()
        
        # get parameters from rules json file
        f = open(path_to_rule)
        data = f.read()
        f_dict = json.loads(data) 
        
        self.devices  = f_dict['devices']
        self.ranges   = f_dict['ranges']
        self.states   = f_dict['states']
    
        f.close()
        
        if sys == None:
            self.sys = sys3CS()
            
    
    def go(self):
        
        output = []
        gr_arr = [0,1]
        wl_arr = np.arange(self.min_wl, self.max_wl + 1, self.step)
        
        self.sys.ctrl(source_shutter_on=True)
        
        for gr in gr_arr:
            arr = [[],[]]
            self.sys.ctrl(mono_gr=gr)
            for wl in wl_arr:
                
                self.sys.ctrl(mono_wl = int(wl))
                
                # apply rule only to spf
                for i in range(len(self.ranges)-1):
                    if self.ranges[i] <= wl < self.ranges[i+1]:
                        device    = self.devices[0]
                        value     = self.states[i][0]
                        arguments = {device:value}
                        try:
                            self.sys.ctrl(**arguments)
                        except:
                            logprint(f'Did not apply rules from {self.path_to_rule} to {device} for required value {value}')
                
                # get power
                a,b,c = self.sys.get_power(pm_a = True, pm_b = True, wl_agree = True, samples = self.samples)
                
                arr[0].append(a); arr[1].append(b)
                
            output.append(arr)
            
        self.sys.ctrl(source_shutter_on=False)
            
        np.save(self.path_to_save, output)
            
            
        