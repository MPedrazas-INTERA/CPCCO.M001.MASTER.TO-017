
import numpy as np
import os
import flopy.utils.binaryfile as bf
import pandas as pd
import matplotlib.pyplot as plt
import sys

def calc_maxConc_fromUCN(area, ucnfile, precis, conv, plot = False):
    ucnobj = bf.UcnFile(ucnfile, precision=precis)
    times = ucnobj.get_times()

    myConcDF = pd.DataFrame()
    nlays = 1 #MP edit to not iterate through all layers
    for lay in [0,1,2,3,8]: # #lay = 0 #range(nlays): #
        oneConcMaxataTime,oneConcMaxLocataTime = [],[]
        print(lay)
        for time in times:#time = times[0]
            print(time)
            oneConcArrayataTime = ucnobj.get_data(mflay=lay, totim=time)*conv
            if area == '100D':
                myConcArray = oneConcArrayataTime[:ncols, :division]
            elif area == '100H':
                myConcArray = oneConcArrayataTime[: ncols, division:]
            if (no_src_cells) and (lay == 0):
                index = np.where(myConcArray == myConcArray.max())
                myRC = str(index[0][0]) + '_' + str(index[1][0])
                df_src['R_C'] = df_src.Row.map(str) + '_' + df_src['Column'].map(str)
                while df_src['R_C'].str.contains(myRC).any():
                    print("Peak conc on a souce cell.")
                    myConcArray[np.where(myConcArray == myConcArray.max())] = 0.0
                    index = np.where(myConcArray == myConcArray.max())
                    myRC = str(index[0][0]) + '_' + str(index[1][0])
                else:
                    print("Peak conc not on a source cell.")
            oneConcMaxataTime.append(myConcArray.max())
            if lay == 0 and check_locs:
                #### Check location of maximum concentration values #### #Update 09/30/22
                index = np.where(myConcArray == myConcArray.max())
                listofIndices = str(index[0][0]) + '_' + str(index[1][0])
                oneConcMaxLocataTime.append(listofIndices)
            else:
                pass
        myConcDF["Times"] = times
        myConcDF["Years"] = round(myConcDF["Times"]/365.25, 2)
        myConcDF[f"L{lay+1}"] = oneConcMaxataTime
        if check_locs:
            myConcDF[f"Locs_Lay1"] = oneConcMaxLocataTime #only for layer 1, QC purposes

    # if not os.path.isdir(os.path.join(outputdir, case)):
    #     os.makedirs(os.path.join(outputdir, case))
    if (check_locs==True) and (no_src_cells==False):
        myConcDF.to_csv(os.path.join(outputdir, f"{area}_MaxConcAq_checkLocs_{case}.csv"), index=False)
    elif (check_locs == True) and (no_src_cells == True):
        myConcDF.to_csv(os.path.join(outputdir, f"{area}_MaxConcAq_NoSourceCells_checkLocs_{case}.csv"), index=False)
    elif (check_locs == False) and (no_src_cells == True):
        myConcDF.to_csv(os.path.join(outputdir, f"{area}_MaxConcAq_NoSourceCells_{case}.csv"), index=False)
    else:
        myConcDF.to_csv(os.path.join(outputdir, f"{area}_MaxConcAq_{case}.csv"), index=False)
    print(f"Generated CSV with Max Aq Conc for layers specified for {case}")

    if plot:
        fig, ax = plt.subplots(1, 1, figsize=(12, 5))
        plt.tick_params(labelsize=12)
        colorLst = ['firebrick', 'orangered', 'gold', 'forestgreen', 'darkviolet']
        for i, lay in enumerate([0,1,2,3,8]): #range(nlays):
            myConcDF.plot(ax=ax, x='Years', y=f"L{lay+1}", grid=True, color = colorLst[i],
                        linewidth=2, alpha=1, zorder=9, label=f"Layer {lay+1}")
        ax.axhline(y=10, linewidth = 1, color='k', linestyle = '--', label = '10 ug/L')
        ax.axhline(y=48, linewidth = 1, color='k', linestyle = '--', label = '48 ug/L')
        ax.set_title(f"Maximum Concentrations in each layer: {area}", fontsize=14)
        ax.set_ylabel('Cr(VI) (ug/L)', fontsize=14)
        ax.set_xlabel('Time (years)', fontsize=14)
        ax.tick_params(axis='y')
        ax.minorticks_on()
        ax.grid(which='major', linestyle='-',
                linewidth='0.1', color='red')
        # # Customize the minor grid
        ax.grid(which='minor', linestyle=':',
                linewidth='0.1', color='black')
        plt.legend()
        # plt.show()
        fname = os.path.join(outputdir, f"{area}_MaxConc.png")
        # fig.savefig(fname, dpi=800, transparent=False,
        #             bbox_inches='tight')
        print("Figure generated, csv stored :)")
    return None

#Plot figure to compare cases:
def plot_maxConcFromCSV(area, cases):
    end_year = 2126
    fig, ax = plt.subplots(1, 1, figsize=(12, 5))
    plt.tick_params(labelsize=10)
    fs = 12 #fontsize for labels and title
    plot_title = False #flag to plot title
    colorLst1 = ['firebrick', 'forestgreen', 'darkviolet', 'orangered', 'gold', ]
    colorLst2 = ['tomato', 'limegreen', 'fuchsia', 'darkorange', 'darkgoldenrod']

    for idx, case in enumerate(cases):
        if case == "sce3a_rr12_to2125":
            outputdir = os.path.join(root,"mruns",f"{case}","tran_2023to2125_ws", "post_process", "max_aq_conc")
        else:
            outputdir = os.path.join(root,"mruns",f"{case}","tran_2023to2125", "post_process", "max_aq_conc")
        if no_src_cells:
            myConcDF = pd.read_csv(os.path.join(outputdir, f"{area}_MaxConcAq_NoSourceCells_{case}.csv"))
        else:
            myConcDF = pd.read_csv(os.path.join(outputdir, f"{area}_MaxConcAq_{case}.csv"))
        myConcDF["Date"] = myConcDF.Years + 2023

        for i, lay in enumerate([0, 1, 2, 3, 8]):  # range(nlays):
            col = (np.random.random(), np.random.random(), np.random.random())  # create random colors for each well
            if len(cases) > 1:
                if idx == 0:
                    myConcDF.plot(ax=ax, x='Date', y=f"L{lay + 1}", grid=True, color=colorLst1[i],
                              linewidth=1, linestyle = '-', alpha=1, zorder=9, label=f"{case}: L{lay + 1}")
                                #label=f"{case[10:]}:\nL{lay + 1}")
                elif idx == 1:
                    myConcDF.plot(ax=ax, x='Date', y=f"L{lay + 1}", grid=True, color=colorLst2[i],
                                  linewidth=1, linestyle = '--', alpha=1, zorder=10, label=f"{case}: L{lay + 1}")
                                #label=f"{case[10:]}:\nL{lay + 1}")
            elif len(cases) == 1:
                myConcDF.plot(ax=ax, x='Date', y=f"L{lay + 1}", grid=True, color=colorLst1[i],
                              linewidth=1, linestyle='-', alpha=1, zorder=9, label=f"L{lay + 1}")
                                # label=f"{case[10:]}:\nL{lay + 1}")
    ax.axhline(y=10, linewidth=1, color='k', linestyle='--', label='10 µg/L')
    ax.axhline(y=48, linewidth=1, color='k', linestyle='--', label='48 µg/L')
    if len(myConcDF) > 144:
        ax.axvline(x=2033.0, linewidth=1, color='k', linestyle='-', zorder=5, alpha = 0.5)
    if plot_title:
        ax.set_title(f"Maximum Concentrations for {case}: {area}", fontsize=fs)
    ax.set_ylabel('Cr(VI) (µg/L)', fontsize=fs)
    ax.set_xlabel('Time (years)', fontsize=fs)
    ax.tick_params(axis='y')
    ax.minorticks_on()
    ax.grid(which='major', linestyle='-',
            linewidth='0.1', color='red')
    # # Customize the minor grid
    ax.grid(which='minor', linestyle=':',
            linewidth='0.1', color='black')
    # if no_src_cells:
        # plt.legend(loc="upper right", ncol=2)
    # else:
    # plt.legend(bbox_to_anchor=(1,1), loc="upper left")
    plt.legend(loc="upper right")

    ax.set_xlim([2023,end_year]) #2126 #2033
    # ax.set_ylim([0,3500]) #with L1
    # ax.set_ylim([0, 500])  # no L1 until 2032
    if len(cases) > 1:
        compCases_outputdir = os.path.join(cwd, "output", "compare_max_aq_conc")
        if not os.path.isdir(compCases_outputdir):
            os.makedirs(compCases_outputdir)
        if no_src_cells:
            fname = os.path.join(compCases_outputdir, f"{area}_MaxConc_{cases[0]}_{cases[1]}_NoSourceCells_until{end_year}.png")
        else:
            fname = os.path.join(compCases_outputdir, f"{area}_MaxConc_{cases[0]}_{cases[1]}_until{end_year}.png")
    elif len(cases) == 1:
        fname = os.path.join(outputdir, f"{area}_MaxConc_{cases[0]}_until{end_year}.png")
    fig.savefig(fname, dpi=800, transparent=False,
                bbox_inches='tight')
    print("Figure generated :)")
    return None

def calc_Conc_specificSP_fromUCN(ucnfile, precis, case, cdays = 1095.0):
    ucnobj = bf.UcnFile(ucnfile, precision=precis)
    print(f"Reading in UCN file for {case}")
    times = ucnobj.get_times()
    myConcDF = pd.DataFrame()
    oneConcMaxataTime = []
    nlays = 1 #MP edit to not iterate through all layers
    for lay in range(nlays): #lay = 0
        oneConcLocataTime = pd.DataFrame()
        print(lay)
        for time in [cdays]: #times[0:2]
            print(time)
            oneConcArrayataTime = ucnobj.get_data(mflay=lay, totim=time)*conv
            myConcArray = oneConcArrayataTime.flatten()
            myRCs = []
            for row in range(nrows):
                for col in range(ncols):
                    myRCs.append([row, col])
            myFinalConcArray = np.array((myConcArray, np.array(myRCs)[:, 0], np.array(myRCs)[:, 1]), order='F').T
            myConcDF = myConcDF.append(pd.DataFrame(myFinalConcArray))
        myConcDF.rename(columns={0: f"Conc_L{lay+1}", 1: "Row", 2: "Col"}, inplace=True)
        myConcDF["R_C"] = myConcDF.Row.astype(int).astype('str') + '_' + myConcDF['Col'].astype(int).astype('str')
        myConcDF.sort_values(by=f"Conc_L{lay+1}", ascending=False, inplace=True)
    myConcDF.to_csv(os.path.join(outputdir, f"{round((cdays/365.25),1)}Yr_MaxConc_{case}.csv"), index=False)

    return None

if __name__ == "__main__":

    cwd = os.getcwd() #C:/100HR3/scripts/
    root = os.path.dirname(cwd) #C:/100HR3/

    nrows, ncols, nlays = 433, 875, 9
    division = 355 #column division between 100D and 100H
    precis = 'double'
    conv = 1.0e-03
    areas = ['100D', '100H']

    cases = ['sce6a_rr1_to2125', 'sce6a_rr2_to2125'] #, 'sce6_rr1_to2125'] #'sce6a_rr2_to2125', 
    #cases = ['sce3a_rr12_to2125', 'sce5a_rr1_to2125', 'sce4a_rr1_to2125', 'sce6a_rr1_to2125']
    # cases = [sys.argv[1]]

    ###IGNORE these two flags, unless you need to run these diagnostics.
    check_locs = False #toggle if you would like to add peak cell location for L1 to CSV. Only works if you run calc_maxConc_fromUCN on Layer 1.
    no_src_cells = False #toggle if you would like peak conc cells in layer 1 that are located in source cells to be excluded.
    if no_src_cells:
        df_zon = pd.read_csv(os.path.join("input", "cr6_source_zones.dat"), delim_whitespace=True)
        df_src = df_zon.loc[~df_zon['Zone'].isin(
            [1, 2, 5, 7, 8, 11, 15, 16, 17, 20, 21, 22, 23, 24])]  # tilde gives you opposite, so this is a NOT IN operation

    #Step 1: Calculate Max Aq Concentration per Area in 100HR3:
    UcnDict = {}
    for case in cases:
        if case not in UcnDict.keys(): #os.path.join(os.path.dirname(cwd), 'model_files', case, 'MT3D001.UCN')
            if case == "sce3a_rr12_to2125":
                UcnDict.update({case:os.path.join(root,"mruns",f"{case}","tran_2023to2125_ws", "MT3D001.UCN")})
                outputdir = os.path.join(root,"mruns",f"{case}","tran_2023to2125_ws", "post_process", "max_aq_conc")
                print("using _ws UCN")
            else:
                UcnDict.update({case:os.path.join(root,"mruns",f"{case}","tran_2023to2125", "MT3D001.UCN")})
                outputdir = os.path.join(root,"mruns",f"{case}","tran_2023to2125", "post_process", "max_aq_conc")
            if not os.path.isdir(outputdir):
                os.makedirs(outputdir)
        for area in areas:
            print(case, area)
            #calc_maxConc_fromUCN(area, UcnDict[case], precis, conv, plot = True)

    #Step 2: OPTIONAL. Compare Max Aq Concentration per Area for different Cases:
    for area in areas:
        plot_maxConcFromCSV(area, cases)

    #IGNORE FOR NOW.
    # OPTIONAL Step 3: Only look at highest 20 cell concentrations for a specific time (in cum days)
    # UcnDict = {}
    # for case in cases:
    #     if case not in UcnDict.keys():
    #         UcnDict.update({case: os.path.join(os.path.dirname(cwd), 'predictive_model_2125', case, 'MT3D001.UCN')})
    #     calc_Conc_specificSP_fromUCN(UcnDict[case], precis, case, cdays= 1095.0)