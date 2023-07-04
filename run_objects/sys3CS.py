"""
class   : sys3CS
author  : Nadav Hargittai
"""

import numpy as np
from auxil.auxil import logprint
from auxil.auxil import read_solis_txt
from datetime import datetime
import os
import time
import json

# PATHS
path_to_rules = 'C:/rep_py3cs/py3cs/config/rules'; default_rule = f'{path_to_rules}/rule_AA.json'

# DEFAULT SLIT
mono_slit     = 1000

from devserve.clients import SystemClient

class sys3CS:
    
    def __init__(self, rule_filepath=default_rule, log_target=None):
        
        """system class initialises 3CS setup and
           controls system states
           
           rule_filepath: type 'str'    ; path to json folder holding rules
           log_target   : type  '<obj>' ; hdf5 object pointing to log dataset
        """
        
        """initialise system client object from devserve"""
        path_to_config = "D:X3CS/Server/dev_config.json"
        self.s = SystemClient.from_json_file("localhost", path_to_config) ; logprint(f'Initialised SystemClient object from {path_to_config}',log_target)
        
        self.rule_filepath    = rule_filepath
        self.log_target       = log_target
        
        """all device states"""
        
        # source
        try:
            logprint("Connecting to source_power ...",log_target)
            self.source_power              = self.s.source.power             ; logprint(f'Connected! Reading: {self.source_power}',log_target)
        except:
            self.source_power              = 'NA'                            ; logprint("Failed to connect to source_power",log_target)
            
        try:
            logprint("Connecting to source_shutter_control ...",log_target)
            self.s.source_shutter.control  = 'computer'  # immediately set  computer control
            self.source_shutter_control    = self.s.source_shutter.control  ; logprint(f'Connected! Reading: {self.source_shutter_control}',log_target)
        except:
            self.source_shutter_control    = 'NA'                           ; logprint("Failed to connect to source_shutter_control",log_target)
            
        try:
            logprint("Connecting to source_shutter_on ...",log_target)
            self.source_shutter_on         = self.s.source_shutter.on       ; logprint(f'Connected! Reading: {self.source_shutter_on}',log_target)
        except:
            self.source_shutter_on         = 'NA'                           ; logprint("Failed to connect to source_shutter_on",log_target)
            
        
        # filter wheels
        try:
            logprint("Connecting to spf ...",log_target)
            self.spf                       = self.s.spfw.position           ; logprint(f'Connected! Reading: {self.spf}',log_target)
        except:
            self.spf                       = 'NA'                           ; logprint("Failed to connect to spf",log_target)
            
        try:
            logprint("Connecting to lpf ...",log_target)
            self.lpf                       = self.s.lpfw.position           ; logprint(f'Connected! Reading: {self.spl}',log_target)
        except:
            self.lpf                       = 'NA'                           ; logprint("Failed to connect to lpf",log_target)
            
        try:
            logprint("Connecting to lpf2 ...",log_target)
            self.lpf2                      = self.s.lpfw2.position          ; logprint(f'Connected! Reading: {self.lpf2}',log_target)
        except:
            self.lpf2                      = 'NA'                           ; logprint("Failed to connect to lpf2",log_target)
            
        
        # flippers
        try:
            logprint("Connecting to flipperA ...",log_target)
            self.flipperA                  = self.s.flipper.position        ; logprint(f'Connected! Reading: {self.flipperA}',log_target)
        except:
            self.flipperA                  = 'NA'                           ; logprint("Failed to connect to flipperA",log_target)
            
        try:
            logprint("Connecting to flipperB ...",log_target)
            self.flipperB                  = self.s.flipperB.position       ; logprint(f'Connected! Reading: {self.flipperB}',log_target)
        except:
            self.flipperB                  = 'NA'                           ; logprint("Failed to connect to flipperB",log_target)
            
            
        # horiba microHR
        try:
            logprint("Connecting to mono ...",log_target)
            self.mono_wl                   = round(self.s.horiba.wl)
            self.mono_gr                   = self.s.horiba.gr               ; logprint(f'Connected! Reading: mono_wl={self.mono_wl}, mono_gr={self.mono_gr}',log_target)
        except:
            self.mono_wl = 'NA' ; self.mono_gr = 'NA'                       ; logprint("Failed to connect to mono",log_target)


        # spectrograph
        try:
            logprint("Connecting to spectrograph ...",log_target)
            self.spec_gr                   = self.s.spectro.grating
            self.spec_shutter              = self.s.spectro.shutter
            self.spec_wl                   = round(self.s.spectro.wavelength)
            self.spec_exp                  = self.s.spectro.exposure        ; logprint(f'Connected! Reading: spec_gr={self.spec_gr}, spec_shutter={self.spec_shutter}, spec_wl={self.spec_wl}, spec_exp={self.spec_exp}',log_target)
        except:
            self.spec_gr = 'NA' ; self.spec_shutter = 'NA' ; self.spec_wl = 'NA' ; self.spec_exp = 'NA' ; logprint("Failed to connect to spectrograph",log_target)
        
            
        # power metres
        try:
            logprint("Connecting to power metre a ...",log_target)
            self.pm_a_wl                   = round(self.s.power_meter_a.wavelength)
            self.pm_a_unit                 = self.s.power_meter_a.unit
            self.pm_a_count                = self.s.power_meter_a.count    ; logprint(f'Connected! Reading: pm_a_wl={self.pm_a_wl}, pm_a_unit={self.pm_a_unit}, pm_a_count={self.pm_a_count}',log_target)
        except:
            self.pm_a_wl = 'NA' ; self.pm_a_unit = 'NA' ; self.pm_a_count = 'NA' ; logprint("Failed to connect to power metre a",log_target)
            
        try:
            logprint("Connecting to power metre b ...",log_target)
            self.pm_b_wl                   = round(self.s.power_meter_b.wavelength)
            self.pm_b_unit                 = self.s.power_meter_b.unit
            self.pm_b_count                = self.s.power_meter_b.count    ; logprint(f'Connected! Reading: pm_b_wl={self.pm_b_wl}, pm_b_unit={self.pm_b_unit}, pm_b_count={self.pm_b_count}',log_target)
        except:
            self.pm_b_wl = 'NA' ; self.pm_b_unit = 'NA' ; self.pm_b_count = 'NA' ; logprint("Failed to connect to power metre b",log_target)
            
        try:
            logprint("Connecting to power metre t ...",log_target)
            self.pm_t_wl                   = round(self.s.power_meter_t.wavelength)
            self.pm_t_unit                 = self.s.power_meter_t.unit
            self.pm_t_count                = self.s.power_meter_t.count    ; logprint(f'Connected! Reading: pm_t_wl={self.pm_t_wl}, pm_t_unit={self.pm_t_unit}, pm_t_count={self.pm_t_count}',log_target)
        except:
            self.pm_t_wl = 'NA' ; self.pm_t_unit = 'NA' ; self.pm_t_count = 'NA' ; logprint("Failed to connect to power metre t",log_target)
            
        self.mono_slit                     = mono_slit                     ; logprint(f'Mono_slit manually set to {self.mono_slit}',log_target)
        
        
        
    def get_state(self, get_tuple = False):
        
        state_dict = {
                    "source_power"            : self.source_power,
                    "source_shutter_control"  : self.source_shutter_control,
                    "source_shutter_on"       : self.source_shutter_on,
                    "spf"                     : self.spf,
                    "lpf"                     : self.lpf,
                    "lpf2"                    : self.lpf2,
                    "flipperA"                : self.flipperA,
                    "flipperB"                : self.flipperB,
                    "mono_wl"                 : self.mono_wl,
                    "mono_gr"                 : self.mono_gr,
                    "mono_slit"               : self.mono_slit,
                    "spec_gr"                 : self.spec_gr,
                    "spec_shutter"            : self.spec_shutter,
                    "spec_wl"                 : self.spec_wl,
                    "spec_exp"                : self.spec_exp,
                    "pm_a_wl"                 : self.pm_a_wl,
                    "pm_a_unit"               : self.pm_a_unit,
                    "pm_a_count"              : self.pm_a_count,
                    "pm_b_wl"                 : self.pm_b_wl,
                    "pm_b_unit"               : self.pm_b_unit,
                    "pm_b_count"              : self.pm_b_count,
                    "pm_t_wl"                 : self.pm_t_wl,
                    "pm_t_unit"               : self.pm_t_unit,
                    "pm_t_count"              : self.pm_t_count
        }

        logprint(f"Retrieved system state: {state_dict}", self.log_target, toprint=False)

        return state_dict



    def ctrl(self,
             source_power           = None,
             source_shutter_control = None,
             source_shutter_on      = None,
             spf                    = None,
             lpf                    = None,
             lpf2                   = None,
             flipperA               = None,
             flipperB               = None,
             mono_wl                = None,
             mono_gr                = None,
             spec_gr                = None,
             spec_shutter           = None,
             spec_wl                = None,
             spec_exp               = None,
             spec_run               = None,
             spec_save              = None,
             pm_a_wl                = None,
             pm_a_unit              = None,
             pm_a_count             = None,
             pm_b_wl                = None,
             pm_b_unit              = None,
             pm_b_count             = None,
             pm_t_wl                = None,
             pm_t_unit              = None,
             pm_t_count             = None
             ):

        # source
        if source_power != None:
            if self.source_power == source_power:
                logprint(f'source_power already set to {source_power}', self.log_target)
            else:
                if (type(source_power) == float or type(source_power) == int) and (0 <= source_power <= 100):
                    logprint(f'Setting source_power to {source_power}', self.log_target)
                    try:
                        self.s.source.power = source_power   # issue command
                        self.source_power   = source_power   # update self state
                        logprint('Set.', self.log_target)
                    except:
                        logprint('Failed to issue command.', self.log_target)
                else:
                    logprint('INPUT ERROR: source_power can only take float or integer values between 0 and 100', self.log_target)

        if source_shutter_control != None:
            if self.source_shutter_control ==  source_shutter_control:
                logprint(f'source_shutter_control already set to {source_shutter_control}', self.log_target)
            else:
                if (source_shutter_control == 'computer') or (source_shutter_control == 'manual'):
                    logprint(f'Setting source_shutter_control to {source_shutter_control}', self.log_target)
                    try:
                        self.s.source_shutter.control = source_shutter_control   # issue command
                        self.source_shutter_control   = source_shutter_control   # update self state
                        logprint('Set.', self.log_target)
                    except:
                        logprint("Failed to issue command", self.log_target)
                else:
                    logprint("INPUT ERROR: source_shutter control takes only 'copmuter' or 'manual' as an argument", self.log_target)

        if source_shutter_on != None:
            if self.source_shutter_on ==  source_shutter_on:
                logprint(f'source_shutter_on already set to {source_shutter_on}', self.log_target)
            else:
                if type(source_shutter_on) == bool:
                    logprint(f'Setting source_shutter_on to {source_shutter_on}', self.log_target)
                    try:
                        self.s.source_shutter.on = source_shutter_on   # issue command
                        self.source_shutter_on   = source_shutter_on   # update self state
                        logprint('Set.', self.log_target)
                    except:
                        logprint("Failed to issue command", self.log_target)
                else:
                    logprint('INPUT ERROR: source_shutter_on must be a boolean', self.log_target)
                    
        
        # filters
        if spf != None:
            if self.spf == spf:
                logprint(f"spf already set to {spf}", self.log_target)
            else:
                if (type(spf) == int) and (1 <= spf <= 6):
                    logprint(f'Setting spf to {spf}', self.log_target)
                    try:
                        self.s.spfw.position = spf   # issue command
                        self.spf             = spf   # update self state
                        logprint("Set.", self.log_target)
                    except:
                        logprint("Failed to issue command", self.log_target)
                else:
                    logprint("INPUT ERROR: spf take only integer values between 1 and 6 (including both)", self.log_target)
                    
        if lpf != None:
            if self.lpf == lpf:
                logprint(f"lpf already set to {lpf}", self.log_target)
            else:
                if (type(lpf) == int) and (1 <= lpf <= 6):
                    logprint(f'Setting lpf to {lpf}', self.log_target)
                    try:
                        self.s.lpfw.position = lpf   # issue command
                        self.lpf             = lpf   # update self state
                        logprint("Set.", self.log_target)
                    except:
                        logprint("Failed to issue command", self.log_target)
                else:
                    logprint("INPUT ERROR: lpf take only integer values between 1 and 6 (including both)", self.log_target)
                    
        if lpf2 != None:
            if self.lpf2 == lpf2:
                logprint(f"lpf2 already set to {lpf2}", self.log_target)
            else:
                if (type(lpf2) == int) and (1 <= lpf2 <= 6):
                    logprint(f'Setting lpf2 to {lpf2}', self.log_target)
                    try:
                        self.s.lpfw2.position = lpf2   # issue command
                        self.lpf2             = lpf2   # update self state
                        logprint("Set.", self.log_target)
                    except:
                        logprint("Failed to issue command", self.log_target)
                else:
                    logprint("INPUT ERROR: lpf2 take only integer values between 1 and 6 (including both)", self.log_target)
                    
        
        # flippers
        if flipperA != None:
            if self.flipperA == flipperA:
                logprint(f"FlipperA already set to {flipperA}", self.log_target)
            else:
                if (flipperA == 'up') or (flipperA == 'down'):
                    logprint(f'Setting flipperA to {flipperA}', self.log_target)
                    try:
                        self.s.flipper.position  = flipperA   # issue command
                        self.flipperA            = flipperA   # update self state
                        logprint("Set.", self.log_target)
                    except:
                        logprint("Failed to issue command", self.log_target)
                else:
                    logprint("INPUT ERROR: flipperA only takes the arguments 'up' or 'down", self.log_target)
                    
        if flipperB != None:
            if self.flipperB == flipperB:
                logprint(f"FlipperB already set to {flipperB}", self.log_target)
            else:
                if (flipperB == 'up') or (flipperB == 'down'):
                    logprint(f'Setting flipperB to {flipperB}', self.log_target)
                    try:
                        self.s.flipperB.position  = flipperB   # issue command
                        self.flipperB            = flipperB   # update self state
                        logprint("Set.", self.log_target)
                    except:
                        logprint("Failed to issue command", self.log_target)
                else:
                    logprint("INPUT ERROR: flipperB only takes the arguments 'up' or 'down", self.log_target)
                    
                    
        # monochromator
        if mono_wl != None:
            if self.mono_wl == mono_wl:
                logprint(f"mono_wl already set to {mono_wl}", self.log_target)
            else:
                if (type(mono_wl) == int or type(mono_wl) == float) and (250 <= mono_wl <= 800):
                    logprint(f'Setting mono_wl to {mono_wl}', self.log_target)
                    try:
                        self.s.horiba.wl  = round(mono_wl)   # issue command
                        self.mono_wl      = round(mono_wl)   # update self state
                        logprint("Set", self.log_target)
                    except:
                        logprint("Failed to issue command", self.log_target)
                else:
                    logprint("INPUT ERROR: mono_wl must be integer or float between 250 and 800 (including both)", self.log_target)
                    
        if mono_gr != None:
            if self.mono_gr == mono_gr:
                logprint(f"mono_gr already set to {mono_gr}", self.log_target)
            else:
                if (type(mono_gr) == int) and (0 <= mono_gr <= 1):
                    logprint(f"Setting mono_gr to {mono_gr}", self.log_target)
                    try:
                        self.s.horiba.gr   = mono_gr   # issue command
                        self.mono_gr       = mono_gr   # update self state
                        logprint("Set", self.log_target)
                    except:
                        logprint("Failed to issue command", self.log_target)
                else:
                    logprint("INPUT ERROR: mono_gr must be integer between 0 and 1 (including both)", self.log_target)
                    
                    
        # spectrograph
        if spec_gr != None:
            if self.spec_gr == spec_gr:
                logprint(f"spec_gr already set to {spec_gr}", self.log_target)
            else:
                if (type(spec_gr) == int) and (1 <= spec_gr <= 2):
                    logprint(f"Setting spec_gr to {spec_gr}", self.log_target)
                    try:
                        self.s.spectro.grating = spec_gr   # issue command
                        self.spec_gr           = spec_gr   # update self state
                        logprint("Set", self.log_target)
                    except:
                        logprint("Failed to issue command", self.log_target)
                else:
                    logprint("INPUT ERROR: spec_gr must be integer between 1 and 2 (including both)", self.log_target)
                    
        if spec_exp != None:
            if self.spec_exp == spec_exp:
                logprint(f"spec_exp already set to {spec_exp}", self.log_target)
            else:
                if (type(spec_exp) == int) or (type(spec_exp) == float):
                    logprint(f"Setting spec_exp to {spec_exp}", self.log_target)
                    try:
                        self.s.spectro.exposure = spec_exp   # issue command
                        self.spec_exp           = spec_exp   # update self state
                        logprint("Set", self.log_target)
                    except:
                        logprint("Failed to issue command", self.log_target)
                else:
                    logprint("INPUT ERROR: spec_exp must be integer or float", self.log_target)
                    
        if spec_shutter != None:
            if self.spec_shutter == spec_shutter:
                logprint(f"spec_shutter already set to {spec_shutter}", self.log_target)
            else:
                if type(spec_shutter) == bool:
                    logprint(f"Setting spec_shutter to {spec_shutter}", self.log_target)
                    try:
                        self.s.spectro.shutter  = spec_shutter
                        self.spec_shutter       = spec_shutter
                        logprint("Set", self.log_target)
                    except:
                        logprint("Failed to issue command", self.log_target)
                else:
                    logprint("INPUT ERROR: spec_shutter must be a boolean", self.log_target)
                    
        if spec_wl != None:
            if self.spec_wl == spec_wl:
                logprint(f"spec_wl already set to {spec_wl}", self.log_target)
            else:
                if type(spec_wl) == int:
                    logprint(f"Setting spec_wl to {spec_wl}", self.log_target)
                    try:
                        self.s.spectro.wavelength = spec_wl   # issue command
                        self.spec_wl              = spec_wl   # update self state
                        logprint("Set", self.log_target)
                    except:
                        logprint("Failed to issue command", self.log_target)
                else:
                    logprint("INPUT ERROR: spec_wl must be an integer", self.log_target)             
        
        # spectrograph run
        if spec_run != None:
            if type(spec_run) == bool:
                logprint('Taking spectrum ...', self.log_target)
                try:
                    self.s.spectro.running = spec_run   # run spectrum command
                    logprint('Done.', self.log_target)
                except:
                    logprint("Failed to issue command", self.log_target)
            else:
                logprint("INPUT ERROR: spec_run must be a boolean", self.log_target)   
        
        # spectrogrpah save
        if spec_save != None:
            if type(spec_save) == str:
                logprint('Saving spectrum ...', self.log_target)
                try:
                    self.s.spectro.save_path = spec_save; time.sleep(0.25)
                    self.s.spectro.saved     = True     ; time.sleep(1)
                    logprint(f"Saved spectrum to {spec_save}", self.log_target)
                    
                    while os.path.exists(spec_save) == False:
                        logprint(f"Waiting for {spec_save} to be created")
                        
                    logprint(f"Solis file created.", self.log_target)
                    try:
                        tup_state, dt_state            = self.get_state(get_tuple=True)
                        solis_tuple, dt_solis, np_data = read_solis_txt(spec_save)
                        power_sample                   = self.get_power(pm_b=True)[1]
                        logprint("Extracted data and metadata", self.log_target)
                        return solis_tuple, tup_state, power_sample, np_data
                    except Exception as e:
                        logprint("FAILED to extract data and metadata", self.log_target)
                        logprint(e, self.log_target)
                        return None
                    
                except:
                    logprint("Failed to issue command", self.log_target)
            else:
                logprint("INPUT ERROR: spec_save must be a string", self.log_target)  
    
    
        # power metres
        if pm_a_wl != None:
            if self.pm_a_wl == pm_a_wl:
                logprint(f"pm_a_wl already set to {pm_a_wl}", self.log_target)
            else:
                if (type(pm_a_wl) == int) and (250 <= pm_a_wl <= 800):
                    logprint(f"Setting pm_a_wl to {pm_a_wl}", self.log_target)
                    try:
                        self.s.power_meter_a.wavelength = pm_a_wl   # issue command
                        self.pm_a_wl                    = pm_a_wl   # update self state
                        logprint("Set", self.log_target)
                    except:
                        logprint("Failed to issue command", self.log_target)
                else:
                    logprint("INPUT ERROR: pm_a_wl must be an integer", self.log_target)        

        if pm_b_wl != None:
            if self.pm_b_wl == pm_b_wl:
                logprint(f"pm_b_wl already set to {pm_b_wl}", self.log_target)
            else:
                if (type(pm_b_wl) == int) and (250 <= pm_b_wl <= 800):
                    logprint(f"Setting pm_b_wl to {pm_b_wl}", self.log_target)
                    try:
                        self.s.power_meter_b.wavelength = pm_b_wl   # issue command
                        self.pm_b_wl                    = pm_b_wl   # update self state
                        logprint("Set", self.log_target)
                    except:
                        logprint("Failed to issue command", self.log_target)
                else:
                    logprint("INPUT ERROR: pm_b_wl must be an integer", self.log_target) 
                    
        if pm_t_wl != None:
            if self.pm_t_wl == pm_t_wl:
                logprint(f"pm_t_wl already set to {pm_t_wl}", self.log_target)
            else:
                if (type(pm_t_wl) == int) and (250 <= pm_t_wl <= 800):
                    logprint(f"Setting pm_t_wl to {pm_t_wl}", self.log_target)
                    try:
                        self.s.power_meter_t.wavelength = pm_t_wl   # issue command
                        self.pm_t_wl                    = pm_t_wl   # update self state
                        logprint("Set", self.log_target)
                    except:
                        logprint("Failed to issue command", self.log_target)
                else:
                    logprint("INPUT ERROR: pm_t_wl must be an integer", self.log_target)



    def get_power(self, pm_a = False, pm_b = False, pm_t = False, wl_agree = True, samples = 3):
        
        logprint("Getting power", self.log_target)
        
        wl = self.mono_wl
        
        logprint(f"mono_wl is {wl}", self.log_target)
        
        if pm_a == True:
            if wl_agree == True:
                self.ctrl(pm_a_wl=wl)

            sum_a = 0
            try:
                logprint("Getting measurement for pm_a", self.log_target)
                for i in range(0, samples):
                    sample = self.s.power_meter_a.power
                    sum_a+= sample
                sample_a = sum_a/samples
                logprint(f"Done. Average measurement: {sample_a}", self.log_target)
            except:
                logprint("FAILED to get power for pm_a", self.log_target)
                sample_a = None
        else:
            sample_a = None
            
        if pm_b == True:
            if wl_agree == True:
                self.ctrl(pm_b_wl=wl)

            sum_b = 0
            try:
                logprint("Getting measurement for pm_b", self.log_target)
                for i in range(0, samples):
                    sample = self.s.power_meter_b.power
                    sum_b+= sample
                sample_b = sum_b/samples
                logprint(f"Done. Average measurement: {sample_b}", self.log_target)
            except:
                logprint("FAILED to get power for pm_b", self.log_target)
                sample_b = None
        else:
            sample_b = None
            
        if pm_t == True:
            if wl_agree == True:
                self.ctrl(pm_t_wl=wl)

            sum_t = 0
            try:
                logprint("Getting measurement for pm_t", self.log_target)
                for i in range(0, samples):
                    sample = self.s.power_meter_t.power
                    sum_t+= sample
                sample_t = sum_t/samples
                logprint(f"Done. Average measurement: {sample_t}", self.log_target)
            except:
                logprint("FAILED to get power for pm_t", self.log_target)
                sample_t = None
        else:
            sample_t = None
            
        return sample_a, sample_b, sample_t



    def apply_rules(self, exc_wl, rule_filepath = default_rule):
    
        logprint(f"Applying rules from {rule_filepath}", self.log_target)
        
        self.ctrl(mono_wl=exc_wl)
        
        # extract rules from file
        with open(rule_filepath) as rules:
            data   = json.load(rules)
            devices  = data['devices']
            ranges   = data['ranges']
            states   = data['states']
            
        # loop thorugh to apply correct states according to exc_wl
        for i in range(len(ranges)-1):
            if ranges[i] <= exc_wl < ranges[i+1]:
                for j in range(len(devices)):
                    device    = devices[j]
                    value     = states[i][j]
                    arguments = {device:value}
                    try:
                        self.ctrl(**arguments)
                    except:
                        logprint(f'Did not apply rules from {rule_filepath} to {device} for required value {value}',self.log_target)
            
        logprint(f'Rules applied.',self.log_target)
    
        return None