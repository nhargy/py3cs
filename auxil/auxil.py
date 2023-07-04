"""
auxillary functions
author: Nadav Hargittai
"""

import h5py
from datetime import datetime
import numpy as np


# global variable solis keys
solis_keys = [
    'Date and Time',
    'Software Version',
    'Temperature (C)',
    'Model',
    'Data Type',
    'Acquisition Mode',
    'Trigger Mode',
    'Exposure Time (secs)',
    'Readout Mode',
    'Horizontal binning',
    'Extended Dynamic Range',
    'Horizontally flipped',
    'Vertical Shift Speed (usecs)',
    'Pixel Readout Rate (MHz)',
    'Baseline Clamp',
    'Clock Amplitude',
    'Output Amplifier',
    'Serial Number',
    'Pre-Amplifier Gain',
    'Spurious Noise Filter Mode',
    'Photon counted',
    'Data Averaging Filter Mode',
    'SR193i',
    'Serial Number',
    'Wavelength (nm)',
    'Grating Groove Density (l/mm)',
    'Grating Blaze',
    'Input Side Slit Width (um)'
    ]

def logprint(string, target, toprint=True, gp = 'log', ds = 'sys_log'):
    
    """ _logprint()_ both prints a string onto the console
        and tries to save it in a timestamped array to the
        log dataset of the hdf5 file.
        
    Input:
        string   (required) : {type=str}  ; {desc: the string to be printed and saved}
        target   (required) : {type=str}  ; {desc: path to hdf5 file, can also be None}
        toprint  (optional) : {type=bool} ; {desc: to print or not to print to console}  ; {default: True}
        gp       (optional) : {type=str}  ; {desc: the name of the hdf5 group to access} ; {default: 'log'}
        ds       (optional) : {type=str}  ; {desc: the name of the group dataset}        : {default: 'sys_log'}

    Returns:
        None
    """
    
    # generate timestamp from datetime.now object
    now      = datetime.now()
    day      = str(now.day).zfill(2)
    month    = str(now.month).zfill(2)
    hour     = str(now.hour).zfill(2)
    minute   = str(now.minute).zfill(2)
    second   = str(now.second).zfill(2)
    date_time = f'{day}/{month}/{now.year}  {hour}:{minute}:{second}'



    # try to write log entry into sys_log dataset
    if target != None:
        try:
            # get sys_log object
            f      = h5py.File(target, 'a')  # open hdf5 file in 'append' mode
            log_ds =  f[gp][ds]    # open 'sys_log' dataset

            # create the log array
            dt = np.dtype([('date_time', 'S20'), ('string', 'S100')])
            log_data = np.array([(date_time, string)], dtype=dt)
            
            # resize and append log data to sys_log dataset
            log_ds.resize((log_ds.shape[0] + 1), axis=0)
            log_ds[-1:] = log_data
            
            # close hdf5 file
            f.close()
            
            if toprint:
                print(date_time + ' [+]', string)
            
        except Exception as e:
            # close hdf5 file if managed to open in try
            try:
                f.close()
            except:
                pass
            if toprint:
                print(date_time + ' [-]', string)
            print("FAILED TO LOG. Could not write data into sys_log dataset.")
            print(e)
        else:
            pass
    else:
        if toprint:
            print(date_time + ' [ ]', string)
        
    return None


def read_solis_txt(filepath):
    
    # start line number of data
    startline = 31
    
    # open the solis file
    solis       = open(filepath, 'r')
    solis_lines = solis.readlines()
    
    # construct metadata tuple and dtype
    solis_dict = {}
    count       = 0
    for key in solis_keys:
        
        try:
            val         = solis_lines[count].split(f'{key}:')[1].strip()
            solis_dict[key] = val
        except:
            solis_dict[key] = 'NA'
        
        count+=1
    
    
    # construct data np array
    dt_data  = np.dtype([('em_wl', 'f'), ('count', 'i')])
    
    arr_data = []
    for line in range(startline, len(solis_lines)):
        row = solis_lines[line].split('\t')
        tup = (float(row[0]), int(row[1]))
        arr_data.append(tup)
    np_data = np.array(arr_data, dtype=dt_data)
    
    return np_data, solis_dict