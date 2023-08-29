"""
Compute extracted mass

PK 2/23/2016 : Significant bug fixes
               Report Zero C, Q, Mass when Q is below cutoff
               Verified against FORTRAN EXE
PK 3/23/2017 : c should be reported even when the well is not pumping
PK 7/21/2017 : Updates to mass calc
"""

import sys
import datetime as dt
import numpy as np 
import itertools as it
import struct
from math import fabs
import matplotlib.pyplot as plt
plt.switch_backend('agg')
import matplotlib.dates as mdates
from matplotlib.backends.backend_pdf import PdfPages
import os
import pandas as pd

def ReadWells(welfile):
    """
    Reads list of wells  from welfile
    """
    with open(welfile, 'r') as fin:
        fin.readline() #skip Header
        wells = []
        for line in fin.readlines():
            # print(line)
            well =line.strip('\n').split(',')[1]
            if not well.isupper():
                well = well.upper()
            wells.append(well)
    fin.close()
    print("Read in {} wells".format(len(wells)))
    return wells

def ReadLST(wells,listfile):
    """
    Reads the MODFLOW LIST File
    """
    dictLST ={}
    fin = open(listfile, 'r')
    flag = False
    header ='WELLID                NODE   Lay   Row   Col        Totim        Q-node         hwell         hcell    Seepage elev.'
    mnwend = '\n'
    for line in fin.readlines():
        if header in line:
            flag = True
        if mnwend == line:
            flag = False
        if flag: #Inside the LST rates
            try:
                items = line.split()
                well,lay,row,col,time,q = items[0],\
                    int(items[2]),int(items[3]),int(items[4]), \
                    float(items[5]), float(items[6])
                if well in wells:
                    rec1 = {lay:q}
                    rec2 = {time:{lay:q}}
                    if well in dictLST:
                        if time in dictLST[well]:
                            dictLST[well][time].update(rec1)
                        else:
                            dictLST[well].update(rec2)
                    else:
                        dictLST.update({well:rec2})
            except:
                continue
    fin.close()
    return dictLST
    
def ReadMNW2(mnw2file) :
    """
    Read and Process the MNW2 file
    """
    dictPTS = {}
    dictRates ={}
    dictLoc ={}
    
    # conv = (1/5.45) # Convert from cubic meters per day to gpm
    conv = 1.0 # Convert from cubic meters per day to gpm
    
    fin = open(mnw2file, 'r')
    
    fin.readline() #Header
    items = fin.readline().split()
    #Maxwells and Number of P&T Systems
    mnwmax,mxpts_mn = int(items[0]),int(items[3])
    for i in range(mnwmax):
        #Wellid and PTS number
        wellid,nnodes,ipts_mn = fin.readline().strip('\n').split()
        ipts_mn = int(ipts_mn)
        if ipts_mn in dictPTS:
            dictPTS[ipts_mn].append(wellid)
        else:
            dictPTS.update({ipts_mn: [wellid]})
        for j in range(2):
            fin.readline()
        items =fin.readline().rstrip('\n').split()
        row,col = int(items[2]), int(items[3])
        fin.readline()
        dictLoc.update({wellid:[row,col]})
    #Get all the rate info now
    flag = True
    sp = 0    
    while(flag):
        try:
            items = fin.readline().strip('\n').split()
            #Number of wells in current Stress period
            n = int(items[0])
            #Stress Period Number
            sp += 1
            for j in range(n):
                wellid,q = fin.readline().strip('\n').split()
                if wellid in dictRates:
                    dictRates[wellid].update({sp:float(q)*conv})
                else:
                    dictRates.update({wellid: {sp:float(q)*conv}})
        except:
            flag = False
    
    #Fill Gaps in the Well Rates Table
    nsp = sp
    for sp in range(1,nsp+1):
        for wellid in dictRates:
            if sp not in dictRates[wellid]:
                dictRates[wellid].update({sp:0.0})
    
    fin.close()
    
    return dictLoc,dictPTS, dictRates

def plot_pumping_rates_QA_v2(dictRates, dictLST, spfile):
    dictSP = {}
    fin = open(spfile, 'r')
    fin.readline()  #skip Header
    flag = True
    while flag:
        try:
            sp, cdays, start_date, end_date, tte = fin.readline().strip('\n').split(',')
            if sp not in dictSP:
                dictSP[int(sp)] = float(tte)
            else:
                dictSP.update({int(sp): float(tte)})
        except:
            flag = False

    pdf = PdfPages('QA_pumping_ActualVsSim.pdf')
    fig = plt.figure(figsize=(11, 8.5))
    wells = sorted(dictLST.keys()) #get list of wells from MNW2 or LST?!
    t1 = sorted(dictRates[wells[0]].keys()) #get times from one well in MNW2

    for well in wells:
        q1 = [dictRates[well][t] for t in t1] #get rates from MNW2
        t2 = sorted(dictLST[well].keys()) #get times from LST
        q2 = [] #get rates from LST
        for t in t2:
            q =0
            for lay in dictLST[well][t].keys():
                q -= dictLST[well][t][lay]
            q2.append(q)
        ax1 = fig.add_subplot(1,1,1)
        t1_tte = [dictSP[t] for t in t1]  # convert SP numbers to cumulative days

        sdate = pd.to_datetime('01/01/2023')
        plot_t1 = sdate + pd.Series(t1_tte).map(dt.timedelta)
        plot_t2 = sdate + pd.Series(t2).map(dt.timedelta)
        ax1.plot(plot_t1, abs(np.array(q1)), ls='-', c="#CC2A14", marker='None',
             label="Prescribed Rate (MNW2)")
        ax1.plot(plot_t2, abs(np.array(q2)), ls='--', marker='None', c="#3D6299",
             label="Actual Rate (LST)")
        ax1.grid(b=True, which='major', color='black', linestyle='-', alpha = 0.1)
        ax1.set_xlim(sdate, plot_t2.max())
        ax1.set_ylabel("Flow (m3/day)")
        ax1.set_xlabel("Date")
        ax1.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=4, mode="expand", borderaxespad=0, frameon='None',
               fontsize=10)
        # Text
        fig.suptitle(well)
        pdf.savefig()
        plt.clf()
    pdf.close()
    return None


def ProcUCN(nlay, nrow, ncol, ucnfile, wells, dictLoc, dictLST, dictRates, precis, iavg):
    """
    Process the UCN file and calculate mass
    :param nlay:
    :param nrow:
    :param ncol:
    :param ucnfile:
    :param wells:
    :param dictLoc:
    :param dictMNWLST:
    :param dictRates:
    :param precis:
    :param iavg:
    :return:
    """
    wells = dictLST.keys()
    print len(wells)
    if precis.lower() == 'single':
        rtype = 'f'
        rsize = 4
    else:
        rtype = 'd'
        rsize = 8

    dictMass = {}
    dictQ = {}
    dictConc = {}
    dictMassLocal = {}
    dictQLocal = {}
    dictNodesWell = {}
    dictConcZeroQWells = {}

    fin = open(ucnfile, 'rb')

    # Read the UCN
    totimprev = 0.0  # Initialize
    first = True  # Flag for first time step
    conc_prev = {}
    totim = 0.0
    while (True):
        # while(totim <= 0.2):
        try:
            # Read the contents of the current timestep from UCN File
            buff = fin.read(12)
            kstp, ntrans, kper = struct.unpack('iii', buff)
            buff = fin.read(rsize)
            totim = struct.unpack(rtype, buff)[0]
            buff = fin.read(28)
            label, icol, irow, ilay = struct.unpack('16siii', buff)
            print kstp, ntrans, kper, totim, label, icol, irow, ilay
            buff = fin.read(irow * icol * rsize)
            sdum = str(irow * icol) + rtype
            conc = np.array(struct.unpack(sdum, buff)).reshape(nrow, ncol)
            # print totim,totimprev,ilay,nlay,ilay-nlay
            # Get the duration of the current concentration timestep
            t = totim - totimprev

            # Intialize q for mass calculation in the first layer
            if ilay == 1:
                dictQ_pos = {}
                dictQ_neg = {}

            # Store the time if we are in the last layer
            if ilay == nlay:
                totimprev = totim  # reset the totim value

            # Get flow and conc for each well by layer
            for well in wells:
                #print(well)

                if well not in dictQ_pos:
                    dictQ_pos[well] = 0.0
                if well not in dictQ_neg:
                    dictQ_neg[well] = 0.0

                # Get concentration
                row, col = dictLoc[well]
                c = conc[row - 1, col - 1]
                if c < 0.0:
                    c = 0.0

                # Get flow
                if well in dictLST:
                    times = sorted(dictLST[well])  # List of active pumping times
                    # if totim < times[0] or totim > times[len(times)-1]:
                    q_prescribed = dictRates[well][kper]
                    # if totim > times[len(times)-1] or totim < times[0]:
                    if q_prescribed == 0:
                        # well not active currently
                        q = 0.0
                        # c = 0.0
                        # Find the appropriate time for active well in LST file
                        for i in range(len(times)):
                            if totim <= times[i]:
                                # Match
                                break
                        # Check if the well is active in the current layer
                        if ilay in dictLST[well][times[i]]:
                            # update well nodes
                            if well in dictNodesWell:
                                num = c + dictConcZeroQWells[well] * dictNodesWell[well]
                                denom = dictNodesWell[well] + 1
                                dictConcZeroQWells.update({well: num / denom})
                                dictNodesWell.update({well: dictNodesWell[well] + 1})
                            else:
                                dictConcZeroQWells.update({well: c})
                                dictNodesWell.update({well: 1})
                    else:
                        # Find the appropriate time for active well in LST file
                        for i in range(len(times)):
                            if totim <= times[i]:
                                # Match
                                break
                        # print i
                        # Check if the well is active in the current layer
                        # print dictMNWLST[well][times[i]]
                        if ilay in dictLST[well][times[i]]:
                            # print ilay
                            # Get the pumping rate from LST file
                            q = dictLST[well][times[i]][ilay]

                            if q < 0:
                                if well in dictQ_neg:
                                    dictQ_neg.update({well: q + dictQ_neg[well]})
                                else:
                                    dictQ_neg.update({well: q})
                            elif q > 0:
                                if well in dictQ_pos:
                                    dictQ_pos.update({well: q + dictQ_pos[well]})
                                else:
                                    dictQ_pos.update({well: q})
                            # print q

                            # #Zero out injection
                            # if q > 0. or '_I_' in well.upper():
                            #     q = 0.
                            # elif q < 0:
                            #     #Change Extraction rate sign for reporting purposes
                            #     q = -q

                            # #Get the concentration
                            # row,col = dictLoc[well]
                            # c = conc[row-1,col-1]
                            # print c,q
                        else:
                            # print well + ' not active in layer: ' + str(ilay)
                            q = 0.0
                            # c =0.0
                else:
                    q = 0.0
                    # c =0.0
                    # Find the appropriate time for active well in LST file
                    for i in range(len(times)):
                        if totim <= times[i]:
                            # Match
                            break
                    # Check if the well is active in the current layer
                    if ilay in dictLST[well][times[i]]:
                        # update well nodes
                        if well in dictNodesWell:
                            num = c + dictConcZeroQWells[well] * dictNodesWell[well]
                            denom = dictNodesWell[well] + 1
                            dictConcZeroQWells.update({well: num / denom})
                            dictNodesWell.update({well: dictNodesWell[well] + 1})
                        else:
                            dictConcZeroQWells.update({well: c})
                            dictNodesWell.update({well: 1})

                # Calculate the mass extracted
                if iavg == 0:
                    # No averaging
                    if q > 0.0:
                        mass = 0.0 #injection well
                    else:
                        mass = c * q * t #extraction well
                else:
                    # Averaging
                    # print first
                    if (first):
                        if q > 0.0:
                            mass = 0.0
                        else:
                            mass = c * q * t  # Don't average for first timestep, ug/m3*m3*d = ug/d (mass rate)
                        # print mass
                    else:
                        if q > 0.0:
                            mass = 0.0
                        else:
                            # print conc_prev
                            # print conc_prev[ilay]
                            cprev = conc_prev[ilay][row - 1, col - 1]
                            if cprev < 0.0:
                                cprev = 0.0
                            mass = 0.5 * (c + cprev) * q * t  # Average

                # Update the local mass dictionary - Contains totals for this time
                # Note: This dict contains only the mass extracted but does not track the
                # mass recirculated
                if well in dictMassLocal:
                    dictMassLocal.update({well: mass + dictMassLocal[well]})
                    dictQLocal.update({well: q + dictQLocal[well]})
                else:
                    dictMassLocal.update({well: mass})
                    dictQLocal.update({well: q})

                # Update the global dictionaries with times
                if ilay == nlay:

                    mass_extracted = dictMassLocal[well]
                    if dictQ_neg[well] < 0.0:
                        blended_concentration = mass_extracted / (dictQ_neg[well] * t)
                    else:
                        blended_concentration = 0.0
                    if blended_concentration < 1e-350:
                        blended_concentration = 0.0
                    mass_recirculated = blended_concentration * dictQ_pos[well] * t
                    if mass_recirculated > 0:
                        print mass_recirculated
                    # Calculate net mass and reverse sign for reporting purposes
                    net_mass_extracted = -(mass_extracted + mass_recirculated)

                    if well in dictMass:
                        dictMass[well].update({totim: net_mass_extracted})
                        # Reverse Q sign for reporting purposes
                        dictQ[well].update({totim: -dictQLocal[well]})
                        if dictQLocal[well] == 0.0:
                            dictConc[well].update({totim: dictConcZeroQWells[well]})
                        else:
                            dictConc[well].update({totim: blended_concentration})
                    else:
                        dictMass.update({well: {totim: net_mass_extracted}})
                        # Reverse Q sign for reporting purposes
                        dictQ.update({well: {totim: -dictQLocal[well]}})
                        if dictQLocal[well] == 0.0:
                            dictConc.update({well: {totim: dictConcZeroQWells[well]}})
                        else:
                            dictConc.update({well: {totim: blended_concentration}})

                    # Error check
                    if (dictMass[well][totim] < 0.0 or dictConc[well][totim] < 0.0):
                        print 'Error-1', well, totim, dictQ[well][totim], dictConc[well][totim], dictMass[well][totim]

            # if (ilay == nlay and iavg ==1):
            if (iavg == 1):
                conc_prev.update({ilay: conc})  # store the concentration if required
            if (ilay == nlay and first):
                first = False
            if ilay == nlay:
                # Reset local Q, Mass, Conc counters
                dictMassLocal = {}
                dictQLocal = {}
                dictNodesWell = {}
                dictConcZeroQWells = {}

        except Exception, error:
            print Exception, error
            # print("I exited too soon or right on time?")
            break

    return dictMass, dictQ, dictConc
    fin.close()

def WriteAllWells(wells, dictMass, dictQ, dictConc, cutoff):
    """
    """
    # Report Mass calculations
    fout = open('AllWells_mass.out', 'w')
    foutQ = open('AllWells_Q.out', 'w')
    foutC = open('AllWells_conc.out', 'w')
    dumstr = '{:>20s}'.format('TIME')
    for well in wells:
        dumstr += '{:>21s}'.format(well)
    fout.write(dumstr + '\n')
    foutQ.write(dumstr + '\n')
    foutC.write(dumstr + '\n')
    times = sorted(dictMass[wells[0]].keys())

    for time in times:
        dumstr = '{:20.12e}'.format(time)
        dumstrQ = '{:20.12e}'.format(time)
        dumstrC = '{:20.12e}'.format(time)
        for well in wells:
            if dictQ[well][time] < cutoff:
                dumstr += '{:21.12e}'.format(0.0)
                dumstrQ += '{:21.12e}'.format(0.0)
                # dumstrC += '{:21.12e}'.format(0.0)
            else:
                dumstr += '{:21.12e}'.format(dictMass[well][time])
                dumstrQ += '{:21.12e}'.format(dictQ[well][time])
            dumstrC += '{:21.12e}'.format(dictConc[well][time])
            if (dictConc[well][time] < 0.0 or dictMass[well][time] < 0.0):
                print 'Error: ', well, time, dictQ[well][time], dictConc[well][time], dictMass[well][time]

        fout.write(dumstr + '\n')
        foutQ.write(dumstrQ + '\n')
        foutC.write(dumstrC + '\n')
    fout.close()
    foutQ.close()
    foutC.close()
    print 'Finished writing Mass Extracted for all wells to AllWells_Mass.out'
    print 'Finished writing Q Extracted for all wells to AllWells_Q.out'
    print 'Finished writing concentration Extracted for all wells to AllWells_conc.out'

    massDF = pd.read_csv("AllWells_mass.out", delimiter="\s+")
    #massDF = massDF.iloc[:336] ### Here you can calculate mass recovered for a certain timeperiod, not until end of simulation
    mass_DF_sum = pd.DataFrame(massDF.cumsum().iloc[-1,:])
    mass_DF_sum.drop(index="TIME", inplace=True)
    mass_DF_sum.reset_index(inplace=True)
    mass_DF_sum.rename(columns={mass_DF_sum.columns[0]: "Well", mass_DF_sum.columns[1]: "Mass (ug)"}, inplace=True)
    mass_DF_sum["Mass (kg)"] = mass_DF_sum["Mass (ug)"]/1e9
    mass_DF_sum.sort_values(by="Mass (kg)", ascending=False, inplace=True)
    mass_DF_sum.to_csv("TotalMassRecovered_byWell.csv", index=False)
    print 'Finished writing Total Mass Recovered for all wells to TotalMassRecovered_byWell.csv'
    return mass_DF_sum
    
def plot_pumping_rates_QA(dictQ, dictLST, dictConc, dictMass):
    pdf = PdfPages('QA_pumping_calcmass.pdf')
    fig = plt.figure(figsize=(11, 8.5))
    wells = sorted(dictQ.keys())
    t1 = sorted(dictQ[wells[0]].keys())

    for well in wells:
        q1 = [dictQ[well][t] for t in t1] #dictQ is
        t2 = sorted(dictLST[well].keys())
        q2 = []
        for t in t2:
            q =0
            for lay in dictLST[well][t].keys():
                q -= dictLST[well][t][lay]
            q2.append(q)
        ax1 = fig.add_subplot(2,1,1)
        sdate = pd.to_datetime('01/01/2023')
        plot_t1 = sdate + pd.Series(t1).map(dt.timedelta)
        plot_t2 = sdate + pd.Series(t2).map(dt.timedelta)
        ax1.plot(plot_t1, q1, ls='-', c="#CC2A14", marker='None',
             label="CalcMass_Q")
        ax1.plot(plot_t2, q2, ls='--',  c="#3D6299",
             label="LST_Q")

        ax1.grid(b=True, which='major', color='black', linestyle='-', alpha = 0.1)
        # ax1.grid(b=True, which='minor', color='grey', linestyle=':')
        # ax1.set_xlim(0, 366)
        # ax1.set_ylim(0)
        ax1.set_ylabel("Flow (m3/day)")
        ax1.set_xlabel("Date")
        ax1.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=4, mode="expand", borderaxespad=0, frameon='None',
               fontsize=10)

        m1 = [dictMass[well][t] for t in t1]
        c1 = [dictConc[well][t] for t in t1]
        ax2 = fig.add_subplot(2,1,2)
        ax2.plot(plot_t1, np.array(m1)/1e9, ls='-', c="#CC2A14", marker='None',
             label="Mass (kg)") #conversion from ug to kg
        ax2.grid(b=True, which='major', color='black', linestyle='-', alpha = 0.1)
        h1, l1 = ax2.get_legend_handles_labels()
        ax3 = ax2.twinx()
        ax3.plot(plot_t1, c1, ls='--', c="#3D6299", marker='None',
                 label="Conc")

        h2, l2 = ax3.get_legend_handles_labels()
        ax2.legend(h1+h2, l1+l2, loc=2)
        ax2.set_ylabel("Mass (kg)")
        ax1.set_xlabel("Date")
        ax3.set_ylabel("Conc  (ug/m3)")
        # Text
        fig.suptitle(well)
        pdf.savefig()
        plt.clf()
    pdf.close()
    print("Finished plotting timeseries in PDF.")


def system_totals(wellinfodir):

    mySumDF_all = pd.read_csv("TotalMassRecovered_byWell.csv")
    wellinfo = pd.read_csv(os.path.join(wellinfodir, 'extractionwells_master.csv'),
                           usecols = ['Deepest_Lay', 'ID', 'Function', 'System'], index_col = 'ID')  # , index_col=0)
    wellinfo.index = wellinfo.index.str.upper() #make sure they're uppercase in case mnw2 is behind LST file
    print "wells in mnw2: {}, wells in LST: {}".format(len(wellinfo.index), len(mySumDF_all.Well))
    mySumDF_all.set_index('Well', inplace = True, drop = True)

    ## combine all into one DF and calculate total mass recovery by system
    df = pd.concat([wellinfo, mySumDF_all],
                   axis=1)  ##concat is an outer join i.e. keeps all indices/wells of all dfs by default

    df['Aq'] = df['Deepest_Lay'].map({1: 'Unconfined', 2: 'Unconfined', 3: 'Unconfined', 4: 'Unconfined', 9: 'RUM'})
    sums = df.groupby(['System', 'Aq']).sum()

    sums.to_csv("TotalMassRecovered_bySystem.csv")
    print "Wrote out TotalMassRecovered_bySystem.csv, ignore column Deepest_Lay because it got aggregated, we care about System and Aq"

    return sums
    
    
if __name__ =="__main__":

    sce = sys.argv[1]
    #sce = 'mnw2_sce4a_rr6'

    model_dirs = os.listdir(os.path.join("..", "..", ".."))
    for dir in model_dirs:
        if dir.startswith("flow"):
            flowdir = os.path.join("..","..", "..", dir)
        else:
            pass

    #Get the main input file
    infile = 'CalculateMass.in'
    with open(infile, 'r') as fin:
        #Name of MNW2 file
        mnw2file = fin.readline().rstrip('\n')
        mnw2file = os.path.join(flowdir, mnw2file)
        #Name of MODFLOW LST file
        listfile = fin.readline().rstrip('\n')
        listfile = os.path.join(flowdir, listfile)
        # Name of UCN file
        ucnfile, precis = fin.readline().rstrip('\n').split()[0:2]
        ucnfile = os.path.join("..", "..", ucnfile)
        #ucnfile = r"/home/mpedrazas/100HR3/mruns/sce3a_to2125_rr5/tran_2023to2125/MT3D001.UCN"
        #Model structure
        nlay,nrow,ncol = map(int,fin.readline().rstrip('\n').split())
        # Read Averaging option
        iavg = int(fin.readline().rstrip('\n').split()[0])
        # Read Q cutoff
        q_cutoff = float(fin.readline().rstrip('\n').split()[0])
    fin.close()

    #Read the list of wells
    root = os.path.join("..","..","..","..","..","scripts")
    # root = r'C:/100HR3/scripts'
    
    wellinfodir = os.path.join(root, 'output', 'well_info', sce)
    welfile = os.path.join(wellinfodir, 'extractionwells_IJ_XYZ.csv')
    wells = ReadWells(welfile)

    # print 'Finished reading list of wells from ' + welfile
    
    # Read the MNW2 file
    dictLoc,dictPTS,dictRates = ReadMNW2(mnw2file)
    print 'Finished reading MNW2 File: ' + mnw2file
    
    #Read the MNW2 rates from the MODFLOW LIST file
    dictLST = ReadLST(wells,listfile)
    print 'Finished reading the MODFLOW LST file: ' + listfile

    #Plot rates (QA)
    spfile = os.path.join(root,'input',"sp_2023to2125.csv")

    print 'Processing UCN File: ' + ucnfile
    wells = dictLST.keys() ###Just in case mnw2 doesn't match LST wells (sce3a mnw2 could've been updated for a different rerun)
    dictMass, dictQ, dictConc = ProcUCN(nlay, nrow, ncol, ucnfile, wells, dictLoc, dictLST, dictRates, precis, iavg)
    print(len(dictMass.keys()))
    #Write mass for all the required wells
    totalMassbyWell = WriteAllWells(wells, dictMass, dictQ, dictConc, q_cutoff)

    #Plot rates (QA)
    plot_pumping_rates_QA(dictQ, dictLST, dictConc, dictMass)

    sums = system_totals(wellinfodir)
    ############# Checking MP (Ignore) #############
    ### MNW vs LST
    # l1 = sorted(dictLST.keys())  # 77 in LST
    # l2 = sorted(dictRates.keys())  # 82 in MNW2
    # lst = set(l1)
    # d = [x for x in l2 if x not in lst]
    # print(d)
