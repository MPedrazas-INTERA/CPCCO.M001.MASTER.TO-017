'''
script to generate time discretization portion of DIS and BTN file for model construction

author: mpedrazas
modified by hpham for 2023_2125 pred model

'''

import pandas as pd
import os
import numpy as np

def gen_DIS(outputdir, df, run):
    ofile = os.path.join(outputdir, f"dis_{run}.txt")
    fid = open(ofile, 'w')
    for i in range(df.shape[0]):
        if (i == 0) and run == "2014_2023": #first SP should be steady-state, only calib model?
            if (df["spLen"].loc[i] <= 31):
                fid.write(f'  {int(df["spLen"].loc[i])}.000000  1  1.000000  SS\n')
            elif df["spLen"].loc[i] > 31:  # yearly SPs
                fid.write(f'  {int(df["spLen"].loc[i])}.00000  1  1.000000  SS\n')
        else:
            if df["spLen"].loc[i] <= 31: #monthly SPs
                fid.write(f'  {int(df["spLen"].loc[i])}.000000  1  1.000000  TR\n') #PERLEN, NSTP, TSMULT
            elif df["spLen"].loc[i] > 31: #yearly SPs
                fid.write(f'  {int(df["spLen"].loc[i])}.00000  1  1.000000  TR\n')
    fid.close()
    print(f"Saved {ofile}")
    print(f"Note: The first SP is steady-state, not transient")
    return None

def gen_BTN(outputdir, df, run):
    ofile = os.path.join(outputdir, f"btn_{run}.txt")
    fid = open(ofile, 'w')
    for i in range(df.shape[0]):
        if df["spLen"].loc[i] <= 31: #monthly SPs
            fid.write(f"  {int(df.spLen.loc[i])}.00000         1  1.000000  TR           {df.start_date.loc[i].month}/{df.start_date.loc[i].day}/{df.start_date.loc[i].year}\n")
            fid.write("1.0000e-01       500 1.300e+00 1.000e+02\n") #0.1 day time steps
        elif df["spLen"].loc[i] > 31: #yearly SPs
            fid.write(f"  {int(df.spLen.loc[i])}.0000         1  1.000000  TR           {df.start_date.loc[i].month}/{df.start_date.loc[i].month}/{df.start_date.loc[i].year}\n")
            fid.write("5.0000e+00       500 1.300e+00 1.000e+02\n") #5 day time steps
    fid.close()
    print(f"Saved {ofile}")
    return None

def gen_BTN_NPRS(outputdir, df, run):
    #NPRS < 0, simulation results will be printed or saved whenever the number of transport steps is an even multiple of NPRS.
    #NPRS > 0, simulation results will be printed to the standard output text file or saved to the UCN at times as specified
    # in record TIMPRS(NPRS) to be entered in the next record.
    # Fortran format is 8F10.0 floats, 8 entries per line, 10 digits long, right justified.

    monthly_threshold = 240 #save every SP until Year 2040 = SP 240 = df.sp.iloc[239]
    yearly_threshold = 588 # save only yearly after Year 2040 = SP 241 = df.sp.iloc[240] until 2070
    # from Year 2070 (SP 588) to Year 2125 (SP 644) save every output because it's already yearly
    myListofYears = list(np.arange(240)) + \
                    list(np.arange(monthly_threshold+11,yearly_threshold,12)) + \
                    list(np.arange(yearly_threshold, df.shape[0]))
    NPRS = len(myListofYears)
    if NPRS > 0:
        ofile = os.path.join(outputdir, f"btn_NRPS_{run}.txt")
        fid = open(ofile, 'w')
        print(f"Finished saving monthly SPs in UCN until SP {df.sp.iloc[239]} -> {df.SPend.iloc[239]}")
        print(f"Saving yearly SPs in UCN from SP {df.sp.iloc[239]} until end of simulation")
        for n, idx in enumerate(myListofYears): #idx will find the SPs we selected to be saved in UCN
            if df["tte"].loc[idx] < 100:
                fid.write(f"      {df.tte.loc[idx]}.0")
            elif (df["tte"].loc[idx]) >= 100 and (df["tte"].loc[idx] < 1000):
                fid.write(f"     {df.tte.loc[idx]}.0")
            elif (df["tte"].loc[idx] >= 1000) and (df["tte"].loc[idx] < 10000):
                fid.write(f"    {df.tte.loc[idx]}.0")
            elif df["tte"].loc[idx] >= 10000:
                fid.write(f"   {df.tte.loc[idx]}.0")
            if (n + 1) % 8 == 0: #this is why we keep n, to enumerate sequentially and hit return after every 8 values
                fid.write("\n")
            else:
                pass
        fid.close()
        print(f"Saved {ofile}")
        print(f"Your NPRS number to put in the BTN is {NPRS}")
    return None

def gen_BTN_NPRS2(outputdir, df, run): # for 2023_2125 BTN file
    #NPRS < 0, simulation results will be printed or saved whenever the number of transport steps is an even multiple of NPRS.
    #NPRS > 0, simulation results will be printed to the standard output text file or saved to the UCN at times as specified
    # in record TIMPRS(NPRS) to be entered in the next record.
    # Fortran format is 8F10.0 floats, 8 entries per line, 10 digits long, right justified.

    monthly_threshold = 216 #save every SP until 12/1/2040 = SP 216 = df.sp.iloc[239]
    yearly_threshold = 540 # save only yearly after Year 2040, until 12/1/2067
    # from Year 2068 (SP 541) to Year 2125 (SP 644) save every output because it's already yearly
    myListofYears = list(np.arange(240)) + \
                    list(np.arange(monthly_threshold+11,yearly_threshold,12)) + \
                    list(np.arange(yearly_threshold, df.shape[0]))
    NPRS = len(myListofYears)
    if NPRS > 0:
        ofile = os.path.join(outputdir, f"btn_NRPS_{run}.txt")
        fid = open(ofile, 'w')
        #print(f"Finished saving monthly SPs in UCN until SP {df.sp.iloc[239]} -> {df.SPend.iloc[239]}")
        #print(f"Saving yearly SPs in UCN from SP {df.sp.iloc[239]} until end of simulation")
        for n, idx in enumerate(myListofYears): #idx will find the SPs we selected to be saved in UCN
            if df["tte"].loc[idx] < 100:
                fid.write(f"      {df.tte.loc[idx]}.0")
            elif (df["tte"].loc[idx]) >= 100 and (df["tte"].loc[idx] < 1000):
                fid.write(f"     {df.tte.loc[idx]}.0")
            elif (df["tte"].loc[idx] >= 1000) and (df["tte"].loc[idx] < 10000):
                fid.write(f"    {df.tte.loc[idx]}.0")
            elif df["tte"].loc[idx] >= 10000:
                fid.write(f"   {df.tte.loc[idx]}.0")
            if (n + 1) % 8 == 0: #this is why we keep n, to enumerate sequentially and hit return after every 8 values
                fid.write("\n")
            else:
                pass
        fid.close()
        print(f"Saved {ofile}")
        print(f"Your NPRS number to put in the BTN is {NPRS}")
    return None

if __name__ == "__main__":
    cwd = os.getcwd()

    df = pd.read_csv(os.path.join(cwd, "input", "sp_2014_2023.csv"))
    df['start_date']=pd.to_datetime(df['start_date'])
    df['end_date']=pd.to_datetime(df['end_date'])

    outputdir = os.path.join(cwd, "output")

    runList = ['2014_Oct2023']
    for run in runList:
        print(run)
        gen_DIS(outputdir, df, run)
       # gen_BTN(outputdir, df, run) # MP, for calib 2014_2023
        # gen_BTN_NPRS2(outputdir, df, run) # HP, for BTN 2023_2125  ###not recommended because UCN needs to have data for every SP.
