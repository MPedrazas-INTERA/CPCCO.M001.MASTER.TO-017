import os
import pandas as pd

"""
    If GWV stops labeling the GHB and/or RIV package by Stress Period,
    use this script to/add stress period labels
    Author: MPedrazas 
    Last updated: 08/24/2023 
"""

def label_ghb_package():
    wdir = os.path.join(os.path.dirname(cwd), 'model_packages', 'hist_2014_2023','ghb')
    SPcount = 0
    with open(os.path.join(wdir, 'gwv.ghb'), 'r') as input, open(os.path.join(wdir, '100hr3.ghb'), 'w') as output:
        lines = input.readlines()
        for idx, line in enumerate(lines):
            if (idx > 2) and ("         0" in line):#skip first three header lines
                SPcount +=1
                print(SPcount)
                output.write(f"{line.split()[0] :>10}{line.split()[1] :>10}                      Stress Period {SPcount}\n")
            else:
                output.write(line)

    print(f"Generated a copy of GHB Package with Stress Periods labeled")
    return None

def label_riv_package():
    wdir = os.path.join(os.path.dirname(cwd), 'model_packages', 'hist_2014_2023','riv')
    SPcount = 0
    with open(os.path.join(wdir, 'gwv.riv'), 'r') as input, open(os.path.join(wdir, '100hr3.riv'), 'w') as output:
        lines = input.readlines()
        for idx, line in enumerate(lines):
            if (idx > 2) and ("         0" in line):#skip first three header lines
                SPcount +=1
                print(SPcount)
                output.write(f"{line.split()[0] :>10}{line.split()[1] :>10}                      Stress Period {SPcount}\n")
            else:
                output.write(line)

    print(f"Generated a copy of RIV Package with Stress Periods labeled")
    return None

if __name__ == "__main__":

    # [1] Load input files ----------------------------------------------------
    cwd = os.getcwd()
    label_ghb_package()
    label_riv_package()

