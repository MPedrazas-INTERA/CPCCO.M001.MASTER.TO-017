



import os
import pandas as pd


cwd = os.getcwd()
wdir = os.path.dirname(cwd)

well_masses = {}

scenarios = ['nfa_to2125_rr4', 'sce2a_to2125_rr1', 'sce3a_rr12_to2125']
for sc in scenarios:
    massdir = os.path.join(wdir, 'mruns', sc, 'tran_2023to2125', 'post_process', 'mass_recovery')
    well_masses[sc] = pd.read_csv(os.path.join(massdir, 'total_mass_recovered.csv'), index_col = 0)

df = pd.concat(well_masses, axis = 1)

df.to_csv(os.path.join(cwd, 'output', 'mass_recovery', 'well_mass_recovered_nfa_sce2rr3.csv'))