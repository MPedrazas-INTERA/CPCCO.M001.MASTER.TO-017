"""
Postprocess Observations + Simulated Concentrations

Post-processing the simulated concentrations so they coincide
and can be compared with Observations
Script is compatible with Python2 and Python3.

@author: MPedrazas

"""
import pandas as pd;
import os;
import datetime as dt
import numpy as np

def ocn2csv(inputDir):
    fin = "STUFF.ocn"
    with open(os.path.join(inputDir, fin), 'r') as f:
        lines = f.read().splitlines()
    f.close()

    # get sp, ts, tts, and tte info
    sp = []
    ts = []
    tts = []
    tte = []
    nobs = []
    myrow = []
    datarow = []
    for cnt, line in enumerate(lines):
        if('STRESS PERIOD') in line:
            sp.append(int(line.strip().split(':')[1]))
        if('TIME STEP') in line:
            ts.append(int(line.strip().split(':')[1]))
        if('TRANSPORT STEP') in line:
            tts.append(int(line.strip().split(':')[1]))
        if('TOTAL ELAPSED TIME') in line:
            tte.append(float(line.strip().split(':')[1]))
            tteval = float(line.strip().split(':')[1])
        if((len(line.strip().split()) >= 8) & ('X_GRID' not in line) & ('No obs wells active' not in line)):
            datarow = line.strip().split()[0:8]
            datarow.append(tteval)  # append time
            myrow.append(datarow)
    df = pd.DataFrame(myrow, columns=[
                      'wellid', 'xgrid', 'ygrid', 'lay', 'row', 'col', 'spec', 'conc', 'tte'])

    # df should have 30381 -- check OK
    df.to_csv(os.path.join(inputDir, 'STUFF_OCN.csv'),
              index=False, columns=['wellid', 'tte', 'conc'])
    print('Saved: ' + str(os.path.join('STUFF_OCN.csv')))
    # dfsp=pd.DataFrame({'sp': sp, 'ts': ts, 'tts': tts, 'tte': tte, 'tteln': tteln})
    return None

def sim2obs_TOB(sim, obs):
    dfSim = pd.read_csv(sim)
    dfSim.tte = dfSim.tte.astype(int)
    dfObs = pd.read_csv(obs)
    dfObs.dropna(axis = 0, subset=["STD_VALUE_RPTD"], inplace=True)
    print("Monitoring wells in observations file: ", len(dfObs.SAMP_SITE_NAME.unique())) #33
    print("Monitoring wells in model output file: ", len(dfSim.wellid.unique())) #19

    dfMerge = dfObs.merge(dfSim, how="left", left_on = ['SAMP_SITE_NAME','tte'], right_on=['wellid','tte'])
    dfMerge.dropna(axis=0, subset=["conc"])
    dfMerge["conc2"] = (dfMerge['conc'].astype(float))/1000
    print(dfMerge.head())
    dfReturn = dfMerge[['SAMP_SITE_NAME', 'SAMP_DATE', 'conc2', 'tte']]


    ### [Step 4:]: Export observations averaged by SP
    fname = 'Cr_sim_bySPs.csv'
    dfReturn.to_csv(os.path.join(cwd, fname), index=False)
    print("Saved: {}".format(os.path.join(cwd, fname)))
    return dfReturn, dfObs

def read_file(ifile, mode ='transport'):
    if mode =='flow':
        cols = ['WellName', 'Date', 'Time', 'Groundwater level (m)']
    elif mode == 'transport':
        cols = ['WellName', 'Date', 'Time', 'Concentration']
    # Read
    df = pd.read_csv(ifile, delim_whitespace=True,
                     skipinitialspace=True, names=cols)
    df['Date'] = pd.to_datetime(df['Date'])
    return df

def calc_conc_fracs():
    file = 'bore_sample_output.dat'
    print(file)

    dff = pd.read_csv(os.path.join(cwd, 'extractionwells_screen_summary_updated.csv'), sep=',', skiprows=1, header=None,
                      names=['ID', 'scLen', 'lenL1', 'lenL2', 'lenL3', 'lenL4', 'lenL5', 'lenL6', 'lenL7', 'lenL8', 'lenL9',
                             'fL1', 'fL2', 'fL3', 'fL4', 'fL5', 'fL6', 'fL7', 'fL8', 'fL9'], index_col=False)

    df = read_file(os.path.join(cwd, file), mode='transport')
    df2 = pd.DataFrame()
    for well in df.WellName.unique(): #['PW_4-L9']
        myNameDF = df.loc[df.WellName == well]
        if 'PW' not in well:
            if 'D' in well:
                myNameDF["FullName"] = "199-" + df["WellName"].str.strip().str[:-3] + '_E_DX'
            elif 'H' in well:
                myNameDF["FullName"] = "199-" + df["WellName"].str.strip().str[:-3] + '_E_HX'
            elif '97-61' in well:
                myNameDF["FullName"] = "699-" + df["WellName"].str.strip().str[:-3] + '_E_DX'
        else: #PW_FY2023_1 from PW_1
            myNameDF["FullName"] = df["WellName"].str.strip().str[:3] + 'FY2023_' + df["WellName"].str.strip().str[3]
        myNameDF["Layer"] = df["WellName"].str.strip().str[-1].astype(int)
        df2 = df2.append(myNameDF)

    myDF = pd.DataFrame()
    for well in dff.ID.unique():
        oneFracAtaTime = dff.loc[dff.ID == well]
        oneConcAtaTime = df2.loc[df2.FullName == well]
        for lay in range(nlays):
            myfrac = oneFracAtaTime["fL{}".format(lay+1)].iloc[0]
            if np.isnan(myfrac):
                myfrac = 0
            # print(myfrac)
            oneLayAtaTime = oneConcAtaTime.loc[oneConcAtaTime.Layer == lay+1]
            oneLayAtaTime["Frac"] = myfrac
            myDF = myDF.append(oneLayAtaTime)
    print("Got fractions for all wells")
    #print(myDF.head())
    myDF.reset_index(inplace=True)
    print(myDF.head())
    myList = []
    for well in myDF.FullName.unique():
        for date in myDF.Date.unique():
            print(well, date)
            concDF = myDF.loc[(myDF.FullName == well) & (myDF.Date == date)]
            print(concDF.head())
            concDF["WeightedConc"] = concDF.Frac * concDF.Concentration
            concDF["Frac2"] = concDF.Frac

            activeConcDF = concDF.loc[(concDF.Concentration > 0) & (concDF.Frac > 0)] #active layers
            dryConcDF = concDF.loc[(concDF.Concentration < 0) & (concDF.Frac > 0)] #dry layers
            if len(dryConcDF) > 0:
                # print("dry")
                dryFrac = sum(dryConcDF.Frac) #sum fractions in dry layers
                if len(activeConcDF) > 0:
                    distributeWeight = dryFrac/len(activeConcDF) #distribute evenly among active layers
                for i in range(len(activeConcDF)):
                    activeConcDF["Frac2"].iloc[i] = activeConcDF.Frac.iloc[i]+distributeWeight
                    activeConcDF["WeightedConc"].iloc[i] = activeConcDF.Frac2.iloc[i] * activeConcDF.Concentration.iloc[i]
                value = sum(activeConcDF.WeightedConc)
            elif len(dryConcDF) > 0 and len(activeConcDF) == 0: #no active layers, but there is a dry layer
                value = 0
            else: #no dry cells
                value = sum(activeConcDF.WeightedConc)
            myList.append([well,date,value/1000]) #convert from model units - ug/m3 to ug/L

    finalDF = pd.DataFrame(myList, columns=["SAMP_SITE_NAME", "SAMP_DATE", "WeightedConc"])
    finalDF["SAMP_DATE"] = pd.to_datetime(finalDF["SAMP_DATE"])
    print(finalDF.head())
    finalDF.to_csv(os.path.join(cwd, "simulated_conc_mod2obs.csv"), index=False)
    return None

def sim2obs_mod2obs(sim, obs):
    dfSim = pd.read_csv(sim)
    dfSim.SAMP_DATE = pd.to_datetime(dfSim.SAMP_DATE)
    #print(dfSim.SAMP_DATE)
    sdate = dt.datetime(2014, 1, 1)
    sdate = pd.to_datetime(sdate)
    #print(sdate)
    ok = (dfSim.SAMP_DATE - sdate) #.dt.days
    #print(ok)
    #print(len(dfSim))
    #dfSim["tte"] = (dfSim.SAMP_DATE - dt.datetime(2014, 1, 1)).dt.days
    dfSim["tte"] = pd.Series(ok)
    print(dfSim.head())
    #dfSim.tte = dfSim.tte.astype(int)
    dfSim.tte = (dfSim.tte / np.timedelta64(1, 'D')).astype(int)
    print(dfSim.head())
    dfObs = pd.read_csv(obs)
    dfObs.SAMP_DATE = pd.to_datetime(dfObs.SAMP_DATE)
    #print(dfObs.head())
    dfObs.dropna(axis = 0, subset=["STD_VALUE_RPTD"], inplace=True)
    print("Monitoring wells in observations file: ", len(dfObs.SAMP_SITE_NAME.unique())) #33
    print("Monitoring wells in model output file: ", len(dfSim.SAMP_SITE_NAME.unique())) 

    dfMerge = dfObs.merge(dfSim, how="left", on = ['SAMP_SITE_NAME','tte'])
    dfMerge.dropna(axis=0, subset=["WeightedConc"])
    dfReturn = dfMerge[['SAMP_SITE_NAME', 'SAMP_DATE_x', 'WeightedConc', 'tte']]
    dfReturn.rename(columns={'SAMP_DATE_x':'SAMP_DATE'}, inplace=True)
    print(dfReturn.head())

    ### [Step 4:]: Export observations averaged by SP
    fname = 'Cr_sim_bySPs.csv'
    dfReturn.to_csv(os.path.join(cwd, fname), index=False)
    print("Saved: {}".format(os.path.join(cwd, fname)))
    return dfReturn, dfObs

if __name__ == "__main__":

    cwd = os.getcwd()
    obs = os.path.join(cwd, 'Cr_obs_avg_bySPs.csv')
    mode = 'mod2obs'
    nlays = 9
    if mode == "TOB":
        #[Step 1]: Make OCN file into CSV (OCN file is TOB output)
        ocn2csv(cwd)
        #[Step 2]: Compare observed vs simulated for each well
        sim_TOB = os.path.join(cwd,'STUFF_OCN.csv')
        dfSim, dfObs = sim2obs_TOB(sim_TOB, obs)
    if mode == 'mod2obs':
        # [STEP 1]: Get a weighted average of conc based on fraction of screen intervals in each model layer
        calc_conc_fracs()
        # [Step 2]: Compare observed vs simulated for each well, output overlap for PEST
    #    sim_mod2obs = os.path.join(cwd, 'simulated_conc_mod2obs.csv')
        #dfSim, dfObs = sim2obs_mod2obs(sim_mod2obs, obs)

