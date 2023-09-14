# analysis scan object

import h5py as h5
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import requests
import io

class scan:

    def __init__(self, path, senso = False, url=False):

        self.path = path

        # open hdf5 file and gather more self parameters

        if url == False:
            f       = h5.File(path, 'r')

        elif url == True:
            response = requests.get(path)
            response.raise_for_status()  # Check if the request was successful

            f = h5.File(io.BytesIO(response.content), 'r')

        spectra = f['spectra'] 


        self.wl_list = list(spectra.keys())
        
        tup_arr   = [] # tuple array for df
        em_wl_arr = []
        count_arr = []

        meta_tup_arr = [] # tuple array for metadata
        flipperA_arr = []
        spf_arr      = []
        lpf_arr      = []
        lpf2_arr     = []
        mono_gr_arr  = []
        spec_gr_arr  = []
        gain_arr     = []
        bin_arr      = []
        temp_arr     = []
        pw_arr       = []
        date_arr     = []
                
        for wl in self.wl_list:
            wl_gp = spectra[f'{wl}']
            ori     = list(wl_gp.keys())

            for o in ori:
                ori_gp = wl_gp[f'{o}']
                times = list(ori_gp.keys())

                for t in times:
                    t_gp = ori_gp[f'{t}']

                    ### -- get metadata -- ###

                    flipperA = t_gp.attrs['flipperA']
                    spf      = t_gp.attrs['spf']
                    lpf      = t_gp.attrs['lpf']
                    lpf2     = t_gp.attrs['lpf2']
                    mono_gr  = t_gp.attrs['mono_gr']
                    spec_gr  = t_gp.attrs['spec_gr']
                    gain     = t_gp.attrs['Pre-Amplifier Gain']
                    bins     = t_gp.attrs['Horizontal binning']
                    temp     = t_gp.attrs['Temperature (C)']
                    date     = t_gp.attrs['Date and Time']

                    spf = f['system']['filter_wheel_A'].attrs[str(spf)]
                    lpf = f['system']['filter_wheel_B'].attrs[str(lpf)]
                    lpf2 = f['system']['filter_wheel_C'].attrs[str(lpf2)]

                    meta_tup_arr.append((wl,o,t))
                    flipperA_arr.append(flipperA)
                    spf_arr.append(spf)
                    lpf_arr.append(lpf)
                    lpf2_arr.append(lpf2)
                    mono_gr_arr.append(mono_gr)
                    spec_gr_arr.append(spec_gr)
                    gain_arr.append(gain)
                    bin_arr.append(bins)
                    temp_arr.append(temp)
                    date_arr.append(date)
                    

                    ### -- --------------- ###

                    sp = t_gp['sp_data']
                    bg = t_gp['bg_data']
                    pw = np.array(t_gp['power_samples'])

                    temp_pw_arr = []
                    for p in pw:
                        temp_pw_arr.append("{:.3e}".format(p))
                    
                    pw_arr.append(np.array(temp_pw_arr))
                    
                    sp_samples = len(sp)
                    bg_samples  = len(bg)

                    for i in range(bg_samples):
                        ind     = f'bg_{i}'
                        em_wl   = bg[i]['em_wl']; count = bg[i]['count']
                        

                        for n in range(len(em_wl)):
                            tup_arr.append((wl, o, t, ind))
                            em_wl_arr.append(em_wl[n])
                            count_arr.append(count[n])

                    for j in range(sp_samples):
                        ind     = f'sp_{j}'
                        em_wl   = sp[j]['em_wl']; count = sp[j]['count']

                        for n in range(len(em_wl)):
                            tup_arr.append((wl, o, t, ind))
                            em_wl_arr.append(em_wl[n])
                            count_arr.append(count[n])
        f.close()                            

        if senso == True:
            index = pd.MultiIndex.from_tuples(tup_arr, names=["state", "wavelength", "t_exp", "kind"])
        else:
            index = pd.MultiIndex.from_tuples(tup_arr, names=["wavelength", "orientation", "t_exp", "kind"])
            meta_index = pd.MultiIndex.from_tuples(meta_tup_arr, names=["wavelength", "orientation", "t_exp"])

        data = {'em_wl': em_wl_arr,
                'count': count_arr}

        meta = {'flipperA' : flipperA_arr ,
                'spf'      : spf_arr,
                'lpf'      : lpf_arr,
                'lpf2'     : lpf2_arr,
                'mono_gr'  : mono_gr_arr,
                'spec_gr'  : spec_gr_arr, 
                'gain'     : gain_arr,
                'bin'      : bin_arr,
                'temp'     : temp_arr,
                'pw'       : pw_arr,
                'date'     : date_arr               
                }
          
        # Creates pandas DataFrame.
        df = pd.DataFrame(data, index=index, columns=['em_wl', 'count'])
        meta_df = pd.DataFrame(meta, index=meta_index, columns=['flipperA', 'spf', 'lpf', 'lpf2', 'mono_gr', 'spec_gr', 'gain', 'bin','spec_temp','pw', 'date'])

        # attribute the dataframe to self.df
        setattr(self,'df', df)
        setattr(self,'meta_df', meta_df)
        
