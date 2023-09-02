# tools.py

from analysis import scan
import os
import scipy.constants as const
import numpy as np
import matplotlib.pyplot as plt


def get_file_dict(path):

    file_dict = {}  # dictionary to contain all run objects (df & meta_df)
    count    = 0
    for filename in os.listdir(path):
        file = scan.scan(f'{path}/{filename}')
        key  = filename.split('.')[0]
        file_dict[key] = file
        count+=1

    return file_dict


def normalise(y, wl, t, pw, gain):
    # total number of photons calc
    E     = (const.h * const.c) / (wl*1e-9)
    tot_E = pw * t
    N_ph  = tot_E / E;
    
    norm = gain*t*N_ph

    sp_norm  = np.divide(y,norm)

    return sp_norm


def gaussian(x,m,s,A):
    return A * np.exp(-(x-m)**2/(2*s**2))


def two_gauss(x,m1,m2,s1,s2,A1,A2):
    return gaussian(x,m1,s1,A1) + gaussian(x,m2,s2,A2)


def plot(scan, wl,t, ori='unk', plot=True, label=None, y_lim = None, color = 'darkblue'):
    
    df     = scan.df.loc[(f'{wl}', f'{ori}', f'{t}sec')]
    meta   = scan.meta_df.loc[(f'{wl}', f'{ori}', f'{t}sec')]
    pw     = float(meta['pw'][0])

    sp_x   = np.array(df.loc[('sp_0')]['em_wl']);  sp_y   = np.array(df.loc[('sp_0')]['count'])
    bg_x   = np.array(df.loc[('bg_0')]['em_wl']);  bg_y   = np.array(df.loc[('bg_0')]['count'])
    
    sp_sub = np.subtract(sp_y, bg_y)
    
    # gain
    gain = int(meta['gain'].split('x')[0])

    # t_exp
    t_exp = float(t)
    
    # total number of photons calc
    E = (const.h * const.c) / (int(wl)*1e-7) # energy of one photon of wavelength: wl
    tot_E = pw * t_exp
    N_ph  = tot_E / E;
    
    norm = t_exp * gain * pw * 1e6  #*N_ph

    sp_norm  = np.divide(sp_sub,norm)
    
    # -  - - - - - - - - - - - #
    
    # set limit

    if y_lim == None:
        
        sorted_indices = np.argsort(sp_norm)[::-1]
        top_twen_values = sp_norm[sorted_indices[:10]]
        
        mean = np.mean(top_twen_values)
        lim  = mean*1.4

    else:
        lim = y_lim

    
    if plot == True:
        plt.plot(sp_x, sp_norm, label = label, color=color)
        plt.grid("on")
        plt.xlabel('Emission Wavelength [nm]')
        plt.ylabel(r'photons $\cdot$ sec$^{-1}$  ${\mu W}^{-1}$')
        plt.ylim(0,lim)
        plt.legend()
    
    return sp_x, sp_norm


def get_diff(scan1, scan2, wl, t, ori, toplot = True, y_lim = [-0.2,2.5], color='darkblue', label=None):

    sp_x_1, sp_norm_1 = plot(scan1, wl, t, ori=ori, plot=False);  sp_x_2, sp_norm_2 =  plot(scan2, wl, t, ori=ori, plot=False)
    diff = np.subtract(sp_norm_2, sp_norm_1)
    plt.plot(sp_x_1, diff, color=color, label = label)
    plt.grid("on")
    plt.xlabel('Emission Wavelength [nm]')
    plt.ylabel(r'photons $\cdot$ sec$^{-1}$  ${\mu W}^{-1}$')
    plt.ylim(y_lim[0], y_lim[1])
    plt.legend()

    return sp_x_1, diff



# a function that takes path to study, species and returns dictionary of scan objects
# ordered as follows: the keys are the collections "coll1" : {"500" : sample, "501" : sample2} ...
# zno['coll1']['500'] gives the scan object
# define the dicts as global variables

def extract_species(path, species):

    path_to_species = f'{path}/{species}'

    species_dict = {}
    count        = 1

    coll_exists  = os.path.exists(f'{path_to_species}/'coll1')
    while coll_exists:

    

    return None