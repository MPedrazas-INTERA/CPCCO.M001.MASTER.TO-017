"""
Postprocess Observations + Simulated Concentrations

Post-processing the simulated concentrations using mod2obs output as input
Averaging simulated concentrations by screen interval fractions in model layers, excluding dry layers in screen interval
Script is compatible with Python2 and Python3.

@author: MPedrazas

"""
import pandas as pd;
import os;
import datetime as dt
import numpy as np

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

    dff = pd.read_csv(os.path.join(cwd, 'screen_fracs.csv'), sep=',', skiprows=1, header=None,
                      names=['ID', 'scLen', 'lenL1', 'lenL2', 'lenL3', 'lenL4', 'lenL5', 'lenL6', 'lenL7', 'lenL8', 'lenL9',
                             'fL1', 'fL2', 'fL3', 'fL4', 'fL5', 'fL6', 'fL7', 'fL8', 'fL9'], index_col=False)

    df = read_file(os.path.join(cwd, file), mode='transport')
    df2 = pd.DataFrame() #restore full names
    for well in df.WellName.unique(): #['PW_4-L9']
        myNameDF = df.loc[df.WellName == well]
        myNameDF["FullName"] = "199-" + df["WellName"].str.strip().str[:-3]  #monitoring wells
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

if __name__ == "__main__":

    cwd = os.getcwd()
    mode = 'mod2obs'
    nlays = 9

    if mode == 'mod2obs':
        calc_conc_fracs() #Get a weighted average of conc based on fraction of screen intervals in each model layer


