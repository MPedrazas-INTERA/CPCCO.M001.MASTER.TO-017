import pandas as pd
import os 

'''
updated by mpedrazas 08/23/2023
- author: hpham@intera.com, 02/14/2023, 100-HR-3 modeling
- Read in riv text file of interest (exported from 03_RiverCells.xlsx as RiverCSV/*.csv)
- Search and replace conductance values
- Export to riv text file to be imported into GWV

'''
import os
import pandas as pd

if __name__ == "__main__":
    cwd = os.getcwd()
    dic_val = {10000:16000,3100:4000, 1000:900, 310:500, 500:450, 6000:450}
    ### Workflow to extend model from Dec 2022 to July 2023: ###----------------------------
    ifile_path = os.path.join(cwd, 'RiverCSV', 'River_sp97to204_2014_2022_for_GWV.csv')
    df_2014_2022 = pd.read_csv(ifile_path) #this df already has CORRECT Ks
    df_2014_2022["SP"] = df_2014_2022["SP"] - 96  #correcting SPs to it starts with SP 1, not SP 97

    ifile_path2 = os.path.join(cwd, 'RiverCSV', '03_River_new2023.csv') #until July 2023
    df_2023 = pd.read_csv(ifile_path2) #1,032,083 rows
    df_2023.dropna(inplace=True) #979,374
    df_2023 = df_2023.loc[(df_2023.SP >= 109) & (df_2023.SP <= 115)] #only need SP 109 to 115.
    print(f"Correct SPs: {df_2023.SP.unique()}\n")
    df_2023.Cond = df_2023.Cond.astype(int)
    df_2023['Cond'] = df_2023['Cond'].replace(dic_val)  # correcting Ks for 2023 dataset
    print(f"Correct Ks: {df_2023.Cond.unique()}\n")

    ###Concatenate from SP 1 in Jan 2014 to July 2023 (SP 115):
    keep_cols = df_2014_2022.columns
    df_final = pd.concat([df_2014_2022, df_2023[keep_cols]], axis=0)
    ofile_path = os.path.join(cwd, 'RiverCSV','04_River_2014_2023_correctK.csv')
    df_final.to_csv(ofile_path, index=False)

#-------------------------IGNORE------------------------------------------------------------------
    ### History Log: Hai had to update conductance for 2014 to 2022 before:
    # Replace K for the 2014-2020 data
    # ifile = os.path.join(cwd,'04_BCs_sspa_exported_021423.txt')
    # ofile = os.path.join(cwd,'04_BCs_riv_sspa_exported_021423_corrected_K.csv')
    #
    # df = pd.read_csv(ifile)
    # old_cond = df['K'].unique() # current values in the GWV file by sspa
    # df['K'] = df['K'].replace(dic_val) #replaced old K values
    #
    # ### rename columns
    # old_cols = ['r', 'c', 'l', 'K', 'start', 'head','reach',  'bottom']
    # df=df[old_cols]
    # new_cols = ['row','col','lay','Cond','SP','Stage','Reach','RiverBottom']
    # dict_cols = dict(zip(old_cols, new_cols))
    # df=df.rename(columns=dict_cols)
    # df1420 = df.copy()
    #
    # # Generate 2021-2022 data (24 stress periods, from 181 to 204)
    # list_files = ['River181_191_new2020.csv','River192_203_new2020.csv','River204_new2020.csv']
    # dfout = pd.DataFrame()
    # for ifile in list_files:
    #     ifile_path = os.path.join(cwd,'RiverCSV',ifile)
    #     df=pd.read_csv(ifile_path)
    #     dfout=pd.concat([dfout, df], axis=0)
    # # ofile
    # dfout['Cond'] = dfout['Cond'].replace(dic_val)
    # ofile_path = os.path.join(cwd, 'RiverCSV','River181_204_new2022_for_GWV.csv')
    # dfout.to_csv(ofile_path, index=False)
