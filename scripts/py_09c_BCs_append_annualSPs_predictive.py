"""
This script appends representative annual SP to the GHB, RIV, DRN packages
for predictive model, in this case from 2068 to 2125 (58 annual SPs)
Input files:
"C:\Github_100HR3\100HR3\scripts\output\boundary_conditions\100hr3to2067.ghb"
"C:\Github_100HR3\100HR3\scripts\output\boundary_conditions\100hr3to2067.riv"

Output files:
"C:\Github_100HR3\100HR3\scripts\output\boundary_conditions\100hr3to2125.ghb"
"C:\Github_100HR3\100HR3\scripts\output\boundary_conditions\100hr3to2125.riv"

author: mpedrazas

"""

import os
import shutil
import numpy as np

def append_yearlySP(input_dir, output_dir, ifiles, ofiles, SP, n):
    if copy_files:
        ### [Step 1] Copy files to edit in Step 2.
        for og, f in zip(ifiles,ofiles):
            print(f"Making a copy of {og}, named {f}")
            try:
                src = os.path.join(input_dir,og)
                dst = os.path.join(output_dir, f)
                with open(src, 'rb') as fda:
                    with open(dst, 'wb') as fdb:
                        shutil.copyfileobj(fda, fdb, length=64 * 1024 * 1)
            except:
                print(f'Could not copy {og}')

    ### [Step 2] Append yearly SP and -1s until end of model timespan n times.
    print(ofiles)
    for f in ofiles:
        print(f)
        lines, start, end = [], [], []
        file = open(os.path.join(output_dir, f), 'r+')
        # read every line in file to get lines related to {SP}
        for idx, line in enumerate(file):
            lines.append((idx, line)) #get tuple pair: index, and line info.
            if f"Stress Period {97+SP-1}" in line:
                start.append((idx, line))
            if f"Stress Period {97+SP}" in line:
                end.append((idx, line))
        print("Lines: ", len(lines))
        print("Start SP line: ", start[0][0])
        print("End SP line: ", end[0][0])
        if lines[-1][1].endswith('\n'):  # last line is return character, so dont add extra return character
            print("Last line has a return character already in file.")
        else:  # last line doesn't have a return character, so add return character
            file.write("\n")  # This is needed so that appending isn't in the last line, but last line + 1.
        for k in list(np.arange(start[0][0], end[0][0])):
            file.write(lines[k][1])
        print(f"Start line to copy:\n {lines[start[0][0]][1]}")
        file.write("-1\n" * n) #Append -1s for the following n SPs
        print(f"Updated: {f}\n")
        file.close()
    return None

if __name__ == "__main__":
    cwd = os.getcwd()
    input_dir = os.path.join(cwd, "output", "boundary_conditions")
    output_dir = os.path.join(cwd, "output", "boundary_conditions")

    ifiles = ["100hr3to2067.ghb", "100hr3to2067.riv"]
    ofiles = ["100hr3to2125.ghb", "100hr3to2125.riv"]
    SP = 26  #Based on central tendency analysis: SP26 - February, 2016
    n = 58 #this is how many times to repeat yearly SP chosen
    copy_files = False #If False, then you must manually make a copy of BCs and rename to 100hr3to2125.ghb and .riv.
    #I tend to copy-paste manually because files are pretty large at this point.
    append_yearlySP(input_dir, output_dir, ifiles, ofiles, SP, n)
