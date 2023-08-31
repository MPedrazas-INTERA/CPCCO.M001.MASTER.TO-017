import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Qt5Agg')

# gpm2m3d = 5.451 # Convert from gpm to m3/d
gpmtom3d = (24*60)/1*231*(25.4/1000/1)**3 #

cwd = os.getcwd()
wdir = os.path.dirname(cwd)


original = pd.read_csv(os.path.join(wdir, '..', 'model_packages', 'hist_2014_2022', 'mnw2',
                                    'wellratedxhx_cy2014_2022.csv'), index_col = 0)

t = pd.date_range(start = '01/01/2014', end='12/31/2022', freq = 'M').strftime('%b-%y')

original.columns = t

original_gpm = original/gpmtom3d

corrections = pd.read_excel(os.path.join(wdir, 'pumping', 'CY2022_well_realignment_ECF_table',
                                       'ECF_table_4_1.xlsx'), skiprows = [0,2])
corrections.insert(0, 'ID', corrections['Well Name'].str.strip() + '_' + corrections['Operation'].str[0] + '_' + corrections['System'].str[:])
corrections.set_index('ID', inplace=True, drop=True)


orig_in_cor = original_gpm[original_gpm.index.isin(corrections.index)] ## originals present in correction table
cor_in_orig = corrections[corrections.index.isin(original_gpm.index)] ## corrections present in original

orig_notin_cor = original_gpm[~original_gpm.index.isin(corrections.index)] ## originals NOT present in correction table
cor_notin_orig = corrections[~corrections.index.isin(original_gpm.index)] ## corrections NOT present in original

list_added = ['199-H4-15A_E_HX', '199-H4-69_E_HX', '199-H4-63_E_HX']

df = original_gpm.loc[list_added]
