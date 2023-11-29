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


def plot_it(scan, wl,t, power_ratio = 10 , ori='0' ,plot=True, label=None, y_lim = None, color = 'darkblue', it = '0'):
    
    df     = scan.df.loc[(f'{wl}', f'{ori}', f'{t}sec')]
    meta   = scan.meta_df.loc[(f'{wl}', f'{ori}', f'{t}sec')]
    pw     = float(meta['pw'][int(it)]) ###
    pw = pw*power_ratio

    sp_x   = np.array(df.loc[(f'sp_{it}')]['em_wl']);  sp_y   = np.array(df.loc[(f'sp_{it}')]['count']) ###
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
        plt.xlabel('Emission Wavelength [nm]', fontsize = 14)
        plt.ylabel(r'photons $\cdot$ sec$^{-1}$  ${\mu W}^{-1}$', fontsize = 14)
        plt.ylim(0,lim)
        plt.legend()
    
    return sp_x, sp_norm


def get_diff(scan1, scan2, wl, t, ori, power_ratio = 10, toplot = True, y_lim = [-0.2,2.5], color='darkblue', label=None):

    sp_x_1, sp_norm_1 = plot_it(scan1, wl, t, power_ratio=power_ratio, ori=ori, plot=False);  sp_x_2, sp_norm_2 =  plot_it(scan2, wl, t, power_ratio=power_ratio, ori=ori, plot=False)
    diff = np.subtract(sp_norm_2, sp_norm_1)

    if toplot == True:

        plt.plot(sp_x_1, diff, color=color, label = label)
        plt.grid("on")
        plt.xlabel('Emission Wavelength [nm]')
        plt.ylabel(r'photons $\cdot$ sec$^{-1}$  ${\mu W}^{-1}$')
        plt.ylim(y_lim[0], y_lim[1])
        plt.legend()

    return sp_x_1, diff


def extract_species(path, species, ext = None): # ext is simply if the species folder is further subdivided into more folders



    species_dict = {}
    count        = 1

    coll_exists  = os.path.exists(f'{path}/coll{count}')
    while coll_exists:
        if ext != None:
            path_to_species = f'{path}/coll{count}/{species}/{ext}'
        else:
            path_to_species = f'{path}/coll{count}/{species}'   # folder of species in this collection

        coll_dict = {}

        files = os.listdir(path_to_species)                 # list all saved files in directory 

        for file in files:
            key = file.split('.')[0]
            obj = scan.scan(f'{path_to_species}/{file}')

            coll_dict[key] = obj

        species_dict[f'coll{count}'] = coll_dict
        count+=1
        coll_exists  = os.path.exists(f'{path}/coll{count}')

    return species_dict


def muon_filter(input, thresh=1,bins = 100):

    array = input.copy()
    
    hist = np.histogram(array, bins)
    muon_values = []

    for i in range(len(hist[0])):
        if   0 < hist[0][i] <= thresh:
            muon_values.append([hist[1][i], hist[1][i+1]])

    print(f'Found {len(muon_values)} muons')


    muon_indices = []
    # run through muon intervals
    for tup in muon_values:
        a = tup[0]; b = tup[1]

        # now loop the array to find this element
        for i in range(len(array)):
            if a <= array[i] <= b : 
                muon_indices.append(i)
    
    # clean muons
    for i in muon_indices:
            array[i] = 0
        
    return array