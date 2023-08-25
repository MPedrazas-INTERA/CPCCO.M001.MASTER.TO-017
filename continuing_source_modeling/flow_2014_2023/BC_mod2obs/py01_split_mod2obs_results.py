"""

Takes mod2obs .dat output file for STOMP and separates into separate .dat outputs for each bore cell
BASED ON ORIGINAL  SCRIPT: S:\PSC\CHPRC.C003.HANOFF\Rel.126\predictive_model\scripts\06a_gen_fake_sim_hds_mod2obs_v2.py

@author: mpedrazas
edited by rweatherl for STOMP-specific workflow

"""

import pandas as pd
import os

### Add 1SP at beginning and 1SP at end of each STOMP cell to mod2obs .dat output file to fit STOMP layout
### 1st SP should (generally) be set to Jan 1 of beginning simulation year, and last SP will be one SP later than last
### SP of simulation year (i.e. 12/01/2022 --> add 01/01/2023)
def add_SP2mod2obs_ofile(inputDir):

    file = 'bore_sample_output.dat'
    cols = ['WellName', 'Date', 'Time', 'Groundwater level (m)']
    df = pd.read_csv(os.path.join(inputDir, file), delim_whitespace=True,
                     skipinitialspace=True, names=cols)
    df['Date'] = pd.to_datetime(df['Date'])

    df3 = pd.DataFrame()

    for well in df.WellName.unique():
        print(well)
        OneWellataTime = df.loc[df.WellName == well]
        dt = '2014-02-01'
        first_dt = '2014-01-01'
        dt2 = '07/01/2023'    
        last_dt = '08/01/2023'
        firstRow = OneWellataTime.loc[OneWellataTime.Date == pd.to_datetime(dt)]
        firstRow.Date = pd.to_datetime(first_dt)
        lastRow = OneWellataTime.loc[OneWellataTime.Date == pd.to_datetime(dt2)]
        lastRow.Date = pd.to_datetime(last_dt)
        df2 = pd.concat([firstRow,OneWellataTime,lastRow])
        df3 = pd.concat([df3,df2])
    df3.Date = df3.Date.dt.strftime('%m/%d/%Y')
    df3.to_csv(os.path.join(inputDir, f'{file[:-4]}.dat'), sep = '\t', header=False, index=False)

    return None

def datbywell(inputDir, wellDict):
##separates mod2obs .dat output into separate files for each soil core.
##also calculates averate WT to replace in file "STOMP_column_list.csv"

    file = 'bore_sample_output.dat'
    print(file)

    cols = ['WellName', 'Date', 'Time', 'Groundwater level (m)']
    df = pd.read_csv(os.path.join(inputDir, file), delim_whitespace=True,
                     skipinitialspace=True, names=cols)
    df['Date'] = pd.to_datetime(df['Date'])

    average_WT = []

    for well_grp in wellDict.keys():
        print(well_grp)
        df2 = pd.DataFrame()
        for well in df.WellName.unique():
            if well.startswith(well_grp):
                OneWellataTime = df.loc[df.WellName == well]
                print(well)
                df2 = pd.concat([df2, OneWellataTime])
                average_WT.append([well_grp, df2['Groundwater level (m)'].mean()])
        df2['Groundwater level (m)'] = df2['Groundwater level (m)'].round(4)
        df2.Date = df2.Date.dt.strftime('%m/%d/%Y')

        ave = pd.DataFrame(average_WT)
        ave2 = ave.groupby(ave.iloc[:,0]).mean()
        ave2.index = ave2.index.map(wellDict)


        df2.to_csv(os.path.join(inputDir, f'{wellDict[well_grp]}.dat'), sep = '\t', header=False, index=False)
        print(f"Separated {file} into {wellDict[well_grp]}.dat")

        ave2.to_csv(os.path.join(inputDir, 'STOMP_ave_WT_python.csv'))

    return ave2


if __name__ == "__main__":


 ## when script is placed in scenario directory, inputdir and outputdir are simply cwd
    cwd = os.getcwd()

    wells = ['199-H4-83', '199-H4-84', '199-D5-151', '199-D5-160', '199-H4-86']

    ### Separate mod2obs .dat output file based on the following grouping:
    wellDict = {'H4-83':'100-H-RB',
                'H4-84':'100-H-SEB',
                'D5-151':'100-D-100',
                'D5-160':'100-D-56-2',
                'H4-86': '100-H-46'}


    ### Add 1SP at beginning of each STOMP cell to mod2obs .dat output file
    add_SP2mod2obs_ofile(cwd)

    ave2 = datbywell(cwd, wellDict)


