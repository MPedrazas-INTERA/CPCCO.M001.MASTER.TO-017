import os
import pandas as pd
import sys

""" THIS SCRIPT DOESNT WORK CORRECTLY. THE REACH NUMBER IS NOT IMPLEMENTED. GENERATE THE RIVER PACKAGE USING GWV FOR NOW"""
def gen_riv_package(wdir):
    ifile_path = os.path.join(cwd, 'RiverCSV', '04_River_2014_2023_correctK.csv')
    # ifile_path = os.path.join(cwd, 'RiverCSV', 'River_sp97to204_2014_2022_for_GWV.csv')
    df = pd.read_csv(ifile_path) #this df already has CORRECT Ks
    # template = "         2         1       251 117.27600 16000.000  114.9890         0 " #got this from old RIV
    df.SP = df.SP.astype(int)
    df.row = df.row.astype(int)
    df.col = df.col.astype(int)
    df.lay = df.lay.astype(int)
    fout = open(os.path.join(wdir, "100hr3_2023_MP_v2.riv"), 'w')
    fout.write("# MODFLOW2000 River Package\n")
    fout.write("PARAMETER  0  0\n")
    fout.write("     89034        50   AUX  IFACE\n")
    tmp = []
    for sp in df.SP.unique():
        print(sp)
        mydf = df.loc[df.SP == sp]
        tmp.append(len(mydf))
        fout.write(f"{len(mydf) :>10}{0 :>10}                      Stress Period {sp}\n")
        for idx in range(len(mydf)):
            # formatting :>10 means right aligned in the ten spaces allocated
            if (mydf.Cond.iloc[idx] < 100000) and (mydf.Cond.iloc[idx] > 10000):
                if mydf["RiverBottom"].iloc[idx] > 100:
                    fout.write(
                        f"""{mydf.lay.iloc[idx] :>10}{mydf.row.iloc[idx] :>10}{mydf.col.iloc[idx] :>10} {mydf["Stage"].iloc[idx]:.5f} {mydf["Cond"].iloc[idx]:.3f}  {mydf["RiverBottom"].iloc[idx]:.4f}         0  \n""")
                else:
                    fout.write(
                        f"""{mydf.lay.iloc[idx] :>10}{mydf.row.iloc[idx] :>10}{mydf.col.iloc[idx] :>10} {mydf["Stage"].iloc[idx]:.5f} {mydf["Cond"].iloc[idx]:.3f}   {mydf["RiverBottom"].iloc[idx]:.4f}         0  \n""")
            elif (mydf.Cond.iloc[idx] < 10000) and (mydf.Cond.iloc[idx] > 1000):
                if mydf["RiverBottom"].iloc[idx] > 100:
                    fout.write(
                        f"""{mydf.lay.iloc[idx] :>10}{mydf.row.iloc[idx] :>10}{mydf.col.iloc[idx] :>10} {mydf["Stage"].iloc[idx]:.5f} {mydf["Cond"].iloc[idx]:.4f}  {mydf["RiverBottom"].iloc[idx]:.4f}         0  \n""")
                else:
                    fout.write(
                        f"""{mydf.lay.iloc[idx] :>10}{mydf.row.iloc[idx] :>10}{mydf.col.iloc[idx] :>10} {mydf["Stage"].iloc[idx]:.5f} {mydf["Cond"].iloc[idx]:.4f}   {mydf["RiverBottom"].iloc[idx]:.4f}         0  \n""")
            elif (mydf.Cond.iloc[idx] < 1000) and (mydf.Cond.iloc[idx] > 100):
                if mydf["RiverBottom"].iloc[idx] > 100:
                    fout.write(
                        f"""{mydf.lay.iloc[idx] :>10}{mydf.row.iloc[idx] :>10}{mydf.col.iloc[idx] :>10} {mydf["Stage"].iloc[idx]:.5f} {mydf["Cond"].iloc[idx]:.5f}  {mydf["RiverBottom"].iloc[idx]:.4f}         0  \n""")
                else:
                    fout.write(
                        f"""{mydf.lay.iloc[idx] :>10}{mydf.row.iloc[idx] :>10}{mydf.col.iloc[idx] :>10} {mydf["Stage"].iloc[idx]:.5f} {mydf["Cond"].iloc[idx]:.5f}   {mydf["RiverBottom"].iloc[idx]:.4f}         0  \n""")
            else:
                print("ERROR. CONDUCTANCES ARE < 100! Check your dataframe.")
                #sys.exit()
    fout.close()
    print(f"Generated RIV Package, your maximum number of GHB cells for any given SP is {max(tmp)}")

if __name__ == "__main__":
    cwd = os.getcwd()
    wdir = cwd
    gen_riv_package(wdir)