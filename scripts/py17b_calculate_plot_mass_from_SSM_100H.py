"""
This script extracts the mass rate (ug/day) for every Stress Period (SP) in the SSM package.
The length of each SP is then multiplied by the mass rate to obtain total mass (ug) per SP.
A figure of mass per time is then generated here.

input: path to SSM package
output: Timeseries plot of mass (.png)

author: mpedrazas

UPDATED FOR 2023 100H Rebound Study

"""

import os
import pandas as pd
import numpy as np
import sys
import matplotlib
matplotlib.use('Qt5Agg')

def calculate_mass_fromSSM(times, inputDir, ssmDir, ssmFile, outputDir):
    # import dates DF
    dates_df = pd.read_csv(os.path.join(inputDir, f"sp_{times}.csv"))

    # import source zonation file
    df_zon = pd.read_csv(os.path.join(ssmDir, "cr6_source_zones.dat"), delim_whitespace=True)
    # df_src = df_zon.loc[df_zon.Zone != 1]
    df_src = df_zon.loc[~df_zon['Zone'].isin(
        [1, 2, 5, 7, 8, 11, 15, 16, 17, 20, 21, 22, 23, 24])]  # tilde gives you opposite, so this is a NOT IN operation
    df_src['Group'] = df_src['Zone'].map(grpDict)  # group source zones into 5 groups based on waste site location
    df_src['R_C'] = df_src.Row.map(str) + '_' + df_src['Column'].map(str)

    # import ssm file
    lines = []
    file = open(os.path.join(ssmDir, ssmFile), 'r')  ##100HR3_2021_2125_transport_stomp2ssm_activLays.ssm
    # file = open(os.path.join(ssmDir, "pred_set5_full.ssm"), 'r') ## 100BC
    start, stop = [], []
    for idx, line in enumerate(file):
        lines.append(line)
        if line == ' 290\n':
            start.append((idx, line))
        if line == ' -1\n' and idx != 2:
            stop.append((idx, line))

    ssmDict = {}
    for i in range(len(start)):  # SPs
        print(i)
        if i not in ssmDict.keys():
            if i < (len(start) - 1):  # all SPs except the last
                data = lines[start[i][0] + 1:stop[i][0] - 1]
                ssmDict.update({i: data})
            elif i == (len(start) - 1):  # last SP
                data = lines[start[i][0] + 1:]
                # data2= [words for segments in data for words in segments.split()]
                ssmDict.update({i: data})

    finalDF = pd.DataFrame()
    for k in ssmDict.keys():
        print(k)
        temp = pd.DataFrame(data=ssmDict[k])
        myLst = []
        for cell in range(len(temp)):
            mystr = temp.iloc[cell, 0].split()
            lay = int(mystr[0])
            row = int(mystr[1])
            if len(mystr[2]) <= 3:
                col = int(mystr[2])
                rc = mystr[1] + "_" + mystr[2]
                value = float(mystr[3])
            else:
                col = int(mystr[2][:3])
                rc = mystr[1] + "_" + mystr[2][:3]
                value = float(mystr[2][3:])
            if value < 0:
                print(value)
            SP = k + 1
            myLst.append((lay, row, col, rc, value, SP))
        oneSPataTime = pd.DataFrame(data=myLst, columns=["Lay", "Row", "Col", "R_C", "Val", "SP"])
        #oneSPataTime = oneSPataTime.loc[oneSPataTime.Val > 0]
        myDF = pd.merge(oneSPataTime, df_src[["R_C", "Group", "Zone"]], on="R_C", how="left")
        finalDF = finalDF.append(myDF)


    finalDF2 = finalDF.merge(dates_df[["sp", "spLen", "tte"]], how="left", right_on="sp", left_on="SP")
    finalDF2["Mass (ug)"] = finalDF2.Val * finalDF2.spLen  # mass rate (ug/day) * time (days) = mass (ug)
    finalDF2["Mass (ug/month)"] = finalDF2["Mass (ug)"].copy()
    finalDF2["Mass (ug/month)"].loc[finalDF2.spLen > 31] = finalDF2["Mass (ug)"]/12 #is spLen > 31, it means it's yearly, so divide by 12
    #finalDF2.to_csv(os.path.join(outputDir, "paper_trail.csv"), index=False)

    ##########[Step 1] Calculate total amount of mass per SP for every group of source zone areas -  5 groups defined in dictioinary grpDict and wastesiteDict
    finalDF3 = pd.pivot_table(finalDF2, index=["Group", "SP", "tte"], values=["Mass (ug/month)"],
                              aggfunc=np.sum)
    finalDF3.reset_index(inplace=True)
    finalDF3["WasteSite"] = finalDF3["Group"].map(wastesiteDict)
    #finalDF3.to_csv(os.path.join(outputDir, "mass_calculated_fromSSM.csv"), index=False)


    ##########[Step 2] Calculate total yearly mass release for 100-H and 100-D Areas:
    finalDF4 = pd.pivot_table(finalDF2, index=["Group"], values=["Mass (ug)"],
                              aggfunc=np.sum)
    finalDF4["Total Mass (ug)"] = finalDF4["Mass (ug)"].copy() #rename after pivot
    finalDF4.reset_index(inplace=True)
    finalDF4["WasteSite"] = finalDF4["Group"].map(wastesiteDict)

    # if case.startswith('transport_NFA'):
    if year == 2125:
        years = 105   ##105 for plotting to 2125, 12 for plotting to 2032
    # elif case == 'transport_RPO_2032_wSSM':
    elif year == 2032:
        years = 12
    elif year == 2023: ## for rebound study, plot through end of july
        years = 9 + 7/12
    elif year == 2020: ## for rebound study, plot through end of july
        years = 7

    ## uncomment to calculate mass release for specific time range
    # t = finalDF2[finalDF2['SP'].isin(list(range(0, 217)))]
    # fdf5 = pd.pivot_table(t, index=["Group"], values=["Mass (ug)"],
    #                           aggfunc=np.sum)
    # fdf5["Total Mass (ug)"] = fdf5["Mass (ug)"].copy() #rename after pivot
    # fdf5.reset_index(inplace=True)
    # fdf5["WasteSite"] = fdf5["Group"].map(wastesiteDict)
    #
    # t2 = finalDF2[finalDF2['SP'].isin(list(range(216, 599)))]
    # fdf6 = pd.pivot_table(t2, index=["Group"], values=["Mass (ug)"],
    #                           aggfunc=np.sum)
    # fdf6["Total Mass (ug)"] = fdf6["Mass (ug)"].copy() #rename after pivot
    # fdf6.reset_index(inplace=True)
    # fdf6["WasteSite"] = fdf6["Group"].map(wastesiteDict)
    #
    # one = finalDF4.iloc[0:2, 2].sum()/1E9
    # two = fdf5.iloc[0:2, 2].sum()/1E9
    # three = fdf6.iloc[0:2, 2].sum() / 1E9

    totalyearlymass100D, totalyearlymass100H = 0,0
    totalmass100D, totalmass100H = 0,0
    for idx in range(len(finalDF4)):
        if finalDF4["WasteSite"].loc[idx].startswith("100-D"):
            totalyearlymass100D += (finalDF4["Total Mass (ug)"].loc[idx])/years #total mass divided by N simulation years = total yearly mass
            totalmass100D += (finalDF4["Total Mass (ug)"].loc[idx])
            print("100-D", finalDF4["Total Mass (ug)"].loc[idx])
        if "-H" in finalDF4["WasteSite"].loc[idx]:
            totalyearlymass100H += (finalDF4["Total Mass (ug)"].loc[idx])/years #total mass divided by N simulation years = total yearly mass
            totalmass100H += (finalDF4["Total Mass (ug)"].loc[idx])
            print("100-H", finalDF4["Total Mass (ug)"].loc[idx])

  #  finalDF4.to_csv(os.path.join(outputDir, "total_annual_mass_calculated_fromSSM.csv"), index=False)

##########[Step 3] Plotting results:
    plot = True
    if plot:
        print("Generating mass time series figure")
        import matplotlib.pyplot as plt
        plt.tick_params(labelsize=12)
        fig, ax = plt.subplots(1, 1, figsize=(8.5, 6))
        secondary_axis = False
        if secondary_axis:
            ax2 = ax.twinx()
            fig.patch.set_facecolor('white')
            ax.patch.set_facecolor('none')
            ax2.patch.set_facecolor('white')
            ax.set_zorder(2)
            ax2.set_zorder(1)
        # colorLst = ['forestgreen', 'slategray', 'dodgerblue', 'brown', 'darkorange']
        colorLst = ['dodgerblue', 'brown', 'darkorange']

        # for i, grp in enumerate(finalDF3.Group.unique()):
        for i, grp in enumerate(finalDF3.Group.unique()[2:]):  ## plotting only for 100H
            oneGrpataTime = finalDF3.loc[finalDF3.Group == grp]#.iloc[:588] #this is how you decide how many SPs to plot, comment out to plot all SPs in model
            #### make this all monthly or yearly!
            if nsp < 598:
                ax.scatter(oneGrpataTime.tte / 365.25, oneGrpataTime['Mass (ug/month)']/1e9, s = 5, color = colorLst[i], zorder=6)
                ax.plot(oneGrpataTime.tte / 365.25, oneGrpataTime['Mass (ug/month)'] / 1e9, linewidth=1.8, color=colorLst[i],
                    zorder=5, label = f"{wastesiteDict[grp]}")
            else:
                ax.plot(oneGrpataTime.tte / 365.25, oneGrpataTime['Mass (ug/month)'] / 1e9, linewidth=0.8,
                        color=colorLst[i], zorder=5, label=f"{wastesiteDict[grp]}")

        ax.legend(fontsize='medium', loc='upper left', ncol = 1).set_zorder(10) #title="Waset Sites")
        # Customize grid
        ax.grid(which='major', linestyle='-', linewidth='0.1', color='red', zorder=1)
        ax.grid(which='minor', linestyle=':',linewidth='0.1', color='black', zorder=2)
        ax.set_xlabel("Time (Years) Since 01/01/2014", fontsize=12)
        ax.set_ylabel("Mass Release from Continuing Source (kg/month)", fontsize=12)
        # ax.set_ylim([0, 0.8])
        ax.set_ylim([0, 0.2])  ## for 100H sites only
        # ax.set_xlim([13, 102])
        ax.set_xlim([0, 10])
        ax.minorticks_on()
        ax.tick_params(which='minor', direction='out')
        if secondary_axis:
            ax2.set_ylabel('Annual Mass Release Rate (kg/year)', fontsize=12)
            ax2.tick_params(which='minor', direction='out')
            ax2.set_ylim([0, 10])
            ax2.minorticks_on()

        mode = 'total' #'average' #'none' #Greg doesn't want average yearly mass, he wants total now.
        if mode == 'average':
            plt.figtext(0.75, 0.3, f"100-H Average Annual Mass \nRelease Rate: {round(totalyearlymass100H/1e9,1)} kg/year", fontsize=9)
            plt.figtext(0.75, 0.35, f"100-D Average Annual Mass \nRelease Rate: {round(totalyearlymass100D/1e9,1)} kg/year", fontsize=9)
        if mode == 'total':
            # if case.startswith("transport_NFA"):
            plt.figtext(0.75, 0.7, f"100-H Total Mass \nRelease: {round(totalmass100H/1e9,1)} kg", fontsize=9)
            # plt.figtext(0.75, 0.35, f"100-D Total Mass \nRelease: {round(totalmass100D/1e9,1)} kg", fontsize=9)
            # else:
        if mode == 'none':
            pass
        plt.title('Mass calculated from SSM in 100H')
        plt.show()
        fname = os.path.join(outputDir, f"mass_calculated_fromSSM_{times}_100H.png")
        fig.savefig(fname, dpi=800, transparent=False,
                    bbox_inches='tight')  # ,transparent = True) #facecolor=fig.get_facecolor())
    plt.close()

    return None

def plot_mass_compareCases(cases):
    print("Generating mass time series figure")
    import matplotlib.pyplot as plt

    plt.tick_params(labelsize=12)
    fig, ax = plt.subplots(1, 1, figsize=(12, 5))  # figsize=(8.5, 6)
    # colorLst = ['slategrey', 'brown', 'olivedrab', 'cornflowerblue', 'peru']
    colorLst = ['peru', 'navy', 'forestgreen', 'firebrick', "slategrey", "brown", "olivedrab"]
    # colorLst = ['royalblue', 'rebeccapurple','forestgreen', 'firebrick']
    lineStyleLst = ['-', '-', '--', '--', 'dashdot', 'dashdot']  # *8
    counter = 0
    for case in cases:
        inputDir = os.path.join("..", 'model_packages', 'pred_2023_2125', f'ssm_{case}')
        mySSM = pd.read_csv(os.path.join(inputDir, "mass_fromSSM", "mass_calculated_fromSSM.csv"))
        # for grp in [1,2]:  #(mySSM.Group.unique()):
        for grp in [3, 4, 5]:
            oneGrpataTime = mySSM.loc[
                mySSM.Group == grp]
            print(counter)
            if nsp < 598:
                ax.scatter((oneGrpataTime.tte / 365.25) + 2021, oneGrpataTime['Mass (ug/month)'] / 1e9, s=5,
                           color=colorLst[counter],
                           zorder=6)
                ax.plot((oneGrpataTime.tte / 365.25) + 2021, oneGrpataTime['Mass (ug/month)'] / 1e9, linewidth=1.75,
                        color=colorLst[counter], linestyle=lineStyleLst[counter],
                        zorder=5, label=f"{nameDict[case]}:\n{wastesiteDict[grp]}")
            else:
                ax.plot((oneGrpataTime.tte / 365.25) + 2023, oneGrpataTime['Mass (ug/month)'] / 1e9, linewidth=1,  # 0.5
                        color=colorLst[counter], zorder=5, label=f"{nameDict[case]}: {wastesiteDict[grp]}",
                        linestyle=lineStyleLst[counter])
            counter += 1

    ax.legend(fontsize='medium', loc='upper right', ncol=1).set_zorder(10)  # title="Waste Sites")
    # ax.legend(bbox_to_anchor = (1, 1), loc = "upper left")
    # Customize grid
    ax.grid(which='major', linestyle='-', linewidth='0.1', color='red', zorder=1)
    ax.grid(which='minor', linestyle=':', linewidth='0.1', color='black', zorder=2)
    ax.set_xlabel("Time (years)", fontsize=12)
    ax.set_ylabel("Mass Release from Continuing Source (kg/month)", fontsize=12)
    # ax.set_xlim([2023, 2126])  #full extent
    # ax.set_xlim([2023, 2040]) #zoomin1
    ax.set_xlim([2040, 2125])  # zoomin2
    ax.set_ylim([0, 0.06])  # CT + SF ylimit
    # ax.set_ylim([0, 35]) #superscenario SF ylimit
    # ax.set_ylim([0, 45]) #SF ylimit
    # ax.set_yscale('log')      ##use log for normal/no zoom
    ax.minorticks_on()
    ax.tick_params(which='minor', direction='out')
    # plt.show()
    # fname = os.path.join(outputDir, f"ECF_mass_calc_fromSSM_SF_2023_2040_grp{grp}_v2.png")
    fname = os.path.join(outputDir, f"mass_calc_fromSSM__2023_2125_sce2a_vs_sce4a_100H_all.png")
    fig.savefig(fname, dpi=800, transparent=False,
                bbox_inches='tight')  # ,transparent = True) #facecolor=fig.get_facecolor())
    plt.close()

    return None


if __name__ == "__main__":

    # dictionaries to relate waste site groups to source zone areas:
    wastesiteDict = {1: '100-D-100 Sidewall', 2: '100-D-56-2 Pipeline', 3: '100-H-46 Waste Site',
                     5: '107-H Retention Basin', 4: '183-H Solar Evaporation Basins'}
    grpDict = {3: 1, 4: 1, 14: 1, 19: 2, 6: 2, 18: 2, 9: 3, 10: 4, 13: 5, 25: 5, 12: 5}


    year = 2023

    #model attributes
    if year == 2032:
        nr, nc, nlay, nsp = 433, 875, 9, 144
    elif year == 2125:
        nr, nc, nlay, nsp = 433, 875, 9, 598
    elif year == 2023:
        nr, nc, nlay, nsp = 433, 875, 9, 115
    elif year == 2020:
        nr, nc, nlay, nsp = 433, 875, 9, 84

    case = "calib_2014_2023"
    times = '2014_2023'
    # times = '2014_2020'

    # directories
    cwd = os.getcwd()
    inputDir = os.path.join(cwd, "input")

    ssmDir = os.path.join("..", 'model_packages', 'hist_2014_2023', 'ssm')
    ssmFile = "100HR3_2014_2023_transport_stomp2ssm.ssm"
    # ssmDir = os.path.join("..", 'model_packages', 'hist_2014_2020', 'ssm')
    # ssmFile = "100HR3_2014_2020_transport_stomp2ssm_activLays.ssm"

    outputDir = os.path.join(os.path.dirname(cwd), 'scripts', 'output', 'mass_calc_ssm', f"{case}")
    # outputDir = os.path.join(ssmDir,"mass_fromSSM")
    if not os.path.isdir(outputDir):
        os.makedirs(outputDir)

    calculate_mass_fromSSM(times, inputDir, ssmDir, ssmFile, outputDir)

    ##Plot mass releases from output CSV of previous function.
    # cases = ['sce4b_rr1_to2125', 'sce11b_rr1_to2125', 'sce11b_rr2_to2125', 'sce11b_rr3_to2125'] #chemical treatment comparison

    # nameDict = {'sce4b_rr1_to2125':"0% CT",
    #              'sce11b_rr1_to2125':"30% CT",
    #              'sce11b_rr2_to2125':"50% CT",
    #              'sce11b_rr3_to2125':"80% CT",
    #              'sce9a_rr1_to2125': "0% CT + SF",
    #              'sce9a_rr2_to2125': "30% CT + SF",
    #              'sce9a_rr3_to2125': "50% CT + SF",
    #              'sce9a_rr4_to2125': "80% CT + SF",
    #             'sce10a_rr1_to2125': "SF"
    #             }

    # nameDict = {'sce2a_rr1_to2125': 'Alternative 1',
    #             'sce4a_rr6_to2125':'Alternative 2'}
    #
    # ## Neutral directory for comparison cases:
    # outputDir = os.path.join('output', 'mass_calc_ssm_comparison')
    # if not os.path.isdir(outputDir):
    #     os.makedirs(outputDir)
  #  plot_mass_compareCases(cases)



