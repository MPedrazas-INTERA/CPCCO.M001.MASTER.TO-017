import os
import pandas as pd
import numpy as np

gpmtom3d = (24*60)/1*231*(25.4/1000/1)**3 #

sce = 'mnw2_sce10a_rr1'
cwd = os.path.dirname(os.getcwd())
pdir = os.path.join(cwd, 'model_packages', 'pred_2023_2125', sce)

rates = pd.read_csv(os.path.join(pdir, 'wellratedxhx_cy2023_2125.csv'), index_col = 0) #,skiprows = [1)

ext_dx = rates[rates.index.str.contains('E_DX')]
inj_dx = rates[rates.index.str.contains('I_DX')]
ext_hx =rates[rates.index.str.contains('E_HX')]
inj_hx = rates[rates.index.str.contains('I_HX')]

ext_hx_sum = pd.DataFrame((ext_hx.sum()/gpmtom3d).unique(), columns = ['E_HX'])
inj_hx_sum = pd.DataFrame((inj_hx.sum()/gpmtom3d).unique(), columns = ['I_HX'])
ext_dx_sum = pd.DataFrame((ext_dx.sum()/gpmtom3d).unique(), columns = ['E_DX'])
inj_dx_sum = pd.DataFrame((inj_dx.sum()/gpmtom3d).unique(), columns = ['I_DX'])

sum = pd.concat([inj_hx_sum, ext_hx_sum, inj_dx_sum, ext_dx_sum], axis=1)