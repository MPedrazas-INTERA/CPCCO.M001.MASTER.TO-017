import os
import pandas as pd

"""
    Add Well Coordinates to Table 1 of DOE/RL-2021-23-ADD2, REV0

"""

if __name__ == "__main__":

    # [1] Load input files ----------------------------------------------------
    ifile_table = f'input/temp/DSouth_Wells.csv'
    ifile_coors = f'input/qryWellHWIS_07202023.txt'

    # read in input files
    df_table = pd.read_csv(ifile_table)
    df_coors = pd.read_csv(ifile_coors, delimiter='|')

    # Combine two table
    df_final = pd.merge(df_table, df_coors, how='left', on='NAME')

    # Save to file 
    df_final.to_csv(f'output/DSouth_Wells_Coords.csv', index=False)