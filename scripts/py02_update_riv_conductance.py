import pandas as pd
import os 

'''
hpham@intera.com, 02/14/2023, 100-HR-3 modeling
- Read in riv text file (exported from GWV)
- Search and replace conductance values
- Export to riv text file to be imported into GWV

'''


if __name__ == "__main__":

    wdir = f'C:/Users/hpham/Documents/100HR3/'
        
    dic_val = {10000:16000,3100:4000, 1000:900, 310:500, 500:450, 6000:450}

    # Replace K for the 2014-2020 data
    ifile = os.path.join(wdir,'model_packages','hist_2014_2021','riv','GWV','BCs_sspa_exported_021423.txt')
    ofile = os.path.join(wdir,'model_packages','hist_2014_2021','riv','GWV','BCs_riv_sspa_exported_021423_corrected_K.csv')

    df = pd.read_csv(ifile)
    old_cond = df['K'].unique() # current values in the GWV file by sspa
    
    df['K'] = df['K'].replace(dic_val)

    old_cols = ['r', 'c', 'l', 'K', 'start', 'head','reach',  'bottom']
    df=df[old_cols]
    new_cols =    ['row','col','lay','Cond','SP','Stage','Reach','RiverBottom']
    dict_cols = dict(zip(old_cols, new_cols))
    df=df.rename(columns=dict_cols)

    df.head()
    df.columns
    df1420 = df.copy()

    #df_check = df[df['K']==6000]
    #df_check.describe()

    # save to txt file
    #df.to_csv(ofile, index=False)

    # Generate 2021-2022 data (24 stress periods, from 181 to 204)

    list_files = ['River181_191_new2020.csv','River192_203_new2020.csv','River204_new2020.csv']
    dfout = pd.DataFrame()
    for ifile in list_files:
        ifile_path = os.path.join(wdir,'model_packages','hist_2014_2021','riv','RiverCSV',ifile)
        df=pd.read_csv(ifile_path)
        dfout=pd.concat([dfout, df], axis=0)
    # ofile
    dfout['Cond'] = dfout['Cond'].replace(dic_val)
    ofile_path = os.path.join(wdir,'model_packages','hist_2014_2021','riv','RiverCSV','River181_204_new2022_for_GWV.csv')
    dfout.to_csv(ofile_path, index=False)

    dfout.head()
    df[new_cols].head()

    # 
    dfout=dfout[new_cols]

    # Combine 2014-2020 and 2021-2022 dataframes
    df_final = pd.concat([df1420[new_cols], dfout], axis=0)
    ofile_path = os.path.join(wdir,'model_packages','hist_2014_2021','riv','RiverCSV','River_sp97to204_2014_2022_for_GWV.csv')
    df_final.to_csv(ofile_path, index=False)

    df_final.columns
    df_final.describe()

