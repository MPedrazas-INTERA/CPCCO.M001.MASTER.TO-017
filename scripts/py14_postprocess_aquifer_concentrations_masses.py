"""
Calculate average concentration of contaminant per model layer
To do: calculate total mass of contaminant per model layer/per aquifer using model dimensions + porosity

"""


import numpy as np
import os
import flopy.utils.binaryfile as bf
import pandas as pd
import matplotlib.pyplot as plt
import flopy

def get_layer_thickness():

    namfile = os.path.join(os.path.dirname(cwd), 'model_files', 'flow_2023_2125', '100hr3_2023to2125.nam')
    m = flopy.modflow.Modflow.load(namfile, load_only=['dis'])
    thickness = m.modelgrid.thick

    # sat_thickness = m.modelgrid.saturated_thick ##needs hds results

    return thickness, sat_thickness

def get_ave_concentration(ucnfile, area, case):

    ucnobj = bf.UcnFile(ucnfile, precision=precis)
    times = ucnobj.get_times()

    conc_df = pd.DataFrame()
    nlays = 9
    for lay in range(nlays):
        c_ave, c_ave_loc = [], []
        print(lay)
        for time in times:
            print(time)
            c_data = ucnobj.get_data(mflay=lay, totim=time) * conv
            if area == '100D':
                c_area = c_data[:ncols, :division]
            elif area == '100H':
                c_area = c_data[:ncols, division:]
            else:
                pass
            c_ave.append(c_area.mean())
        conc_df["Times"] = times
        conc_df["Years"] = round(conc_df["Times"] / 365.25, 2)
        conc_df[f"L{lay + 1}"] = c_ave

    #
    if not os.path.isdir(os.path.join(outputdir, case)):
        os.makedirs(os.path.join(outputdir, case))
    # conc_df.to_csv(os.path.join(outputdir, case, f"{area}_AveConcAq_{case}_v2.csv"), index=False)
    print(f"Generated CSV with Ave Aq Conc for layers specified for {case}")

    return None

if __name__ == "__main__":

    cwd = os.getcwd()
    outputdir = os.path.join(cwd, 'aquifer_concentrations_tests')

    nrows, ncols, nlays = 433, 875, 9
    division = 355  # column division between 100D and 100H
    precis = 'double'
    conv = 1.0e-03
    areas = ['100D', '100H']
    cases = ['nfa_to2125', 'sce2_to2125_rerun3']

    thickness, sat_thickness = get_layer_thickness()

    for case in cases:
        ucnfile = os.path.join(os.path.dirname(cwd), 'mruns', case, 'tran_2023to2125', 'MT3D001.UCN')
        ######Snapshot: Calculate Average Aq Concentration per Area in 100HR3:
        for area in areas:
            get_ave_concentration(ucnfile, area, case)


    ## to do: use model layer thickness and cell dimensions + porosity to calculate cell
    ## volume. Then volume*concentration to calculate total contaminant mass in each layer
