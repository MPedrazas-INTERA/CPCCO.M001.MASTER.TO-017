import pandas as pd
import os
from datetime import datetime
import pyodbc # Read MS Access files

'''
-- Read in MS Access file from CPCCo and qryMANHEIS.txt to generate CSVs with CORRECT WATER LEVELS for CY 2022.
-- Outputs:
"C:\100HR3-Rebound\data\water_levels\WaterLevel_CY2022\awln_wl_cy2022.csv"
"C:\100HR3-Rebound\data\water_levels\WaterLevel_CY2022\manual_wl_cy2022.csv"
'''

def read_msaccess(db_path):
    db_driver = '{Microsoft Access Driver (*.mdb, *.accdb)}'
    
    conn_str = (rf'DRIVER={db_driver};' rf'DBQ={db_path};')

    conn = pyodbc.connect(conn_str)

    df = pd.read_sql(sql="select * from AWLN_CY22", con=conn)
    print(df.head())
    conn.close()

    # Save to csv file 
    col = ["NAME","EVENT","TYPE","VAL_FINAL","MAP_USE"]
    df = df[col]
    df.to_csv(f'{wdir}/ALWN_ValidatedData_CY22.csv', index=False)
    return df

def format_awnl_df(df):
    # rename columns
    df=df.rename(columns={'VAL_FINAL':'VAL'})
    
    # Choose ONLY the data within 2022
    flag = ((df['EVENT'] >= datetime(2022, 1, 1)) & (df['EVENT'] < datetime(2023, 1, 1)))
    df = df[flag]

    #Make sure you only use data without red flag, MAP_USE == "NOT_VALID"
    df = df.loc[df.MAP_USE != "NOT_VALID"]

    # Only keep subset, dropping MAP_USE
    df = df[["NAME","EVENT","TYPE","VAL"]]

    # Save data:
    df.to_csv(f'{wdir}/awln_wl_cy2022.csv', index=False)
    print(df.head())
    print(f'\nSaved {wdir}/awln_wl_cy2022.csv')
    return df

def read_heis_man_txt_file(ifile_heis_man):
    df = pd.read_csv(ifile_heis_man, delimiter='|')
    # df=df.rename(columns={'VAL':'SSPAVAL'})
    df['EVENT'] = pd.to_datetime(df['EVENT'])
    flag = (df['EVENT'] >= datetime(2022, 1, 1)) & (df['EVENT'] < datetime(2023, 1, 1))
    df=df[flag]

    # Save data: 
    #df['TYPE'] = 'MAN'

    #Makign sure cols are in the correct order:
    df = df.loc[:,["NAME", "EVENT", "TYPE","VAL"]]

    df.to_csv(f'{wdir}/manual_wl_cy2022.csv', index=False)
    print(df.head())
    print(f'Saved {wdir}/manual_wl_cy2022.csv')
    return df

if __name__ == "__main__":
    cwd = os.getcwd()
    wdir = os.path.join(os.path.dirname(cwd), "data", "water_levels", "WaterLevel_CY2022")

    # =========================================================================
    # Read AWLN data in MS Acess format =======================================
    # [01] Manually unzip LWN_ValidatedData_CY22.7z to get ALWN_ValidatedData_CY22.accdb

    # [02] process ms access file and convert to csv file ---------------------
    opt_process_awln_data = True
    if opt_process_awln_data:
        db_path = os.path.join(wdir, 'ALWN_ValidatedData_CY22.accdb')
        df = read_msaccess(db_path)
        df_awln = format_awnl_df(df)
    # -------------------------------------------------------------------------
    # [03] Read in HEIS MAN water level measuremnts ---------------------------
    opt_process_heis_man_data = True
    if opt_process_heis_man_data:
        ifile_heis_man = os.path.join(wdir, 'qryManHEIS.txt')
        df_man = read_heis_man_txt_file(ifile_heis_man)
