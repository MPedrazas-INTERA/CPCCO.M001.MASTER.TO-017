"""
This script repeats the GHB and RIV packages
for calibrated time period N more times for a total of N+1 cycles to generate
the monthly SP portion of predictive model BC packages.
In this case, recycling BCs for years 2014 to 2022.

Input files:
"C:\Github_100HR3\100HR3\model_files\flow_2014_2022\100hr3.ghb"
"C:\Github_100HR3\100HR3\model_files\flow_2014_2022\100hr3.riv"

Output files:
"C:\Github_100HR3\100HR3\scripts\output\boundary_conditions\100hr3to2067.ghb"
"C:\Github_100HR3\100HR3\scripts\output\boundary_conditions\100hr3to2067.riv"

author: mpedrazas

"""
import os
import shutil
import sys

def repeatBCs(input_dir, output_dir, n, ifiles, ofiles):
    ### [Step 1] Copy files to edit in Step 2. You can also do the copy-paste manually and move to Step 2 directly.
    if copy_files:
        for og, f in zip(ifiles,ofiles):
            print(f"Making a copy of {og}, named {f}")
            try:
                src = os.path.join(input_dir,og)
                dst = os.path.join(output_dir, f)
                with open(src, 'rb') as fda:
                    with open(dst, 'wb') as fdb:
                        shutil.copyfileobj(fda, fdb, length=64 * 1024 * 1)
            except:
                print(f'Could not copy {og}. Exiting.')
                sys.exit()

    ### [Step 2] Append "n" times to BCs:
    for f in ofiles: #ofiles:
        lines = []
        file = open(os.path.join(output_dir, f),'r+')
        for idx, line in enumerate(file):
            lines.append(line)

        for i in range(n):
            if lines[-1].endswith('\n'): #last line is return character, so dont add extra return character
                print("Last line has a return character already in file.")
            else: #last line doesn't have a return character, so add return character
                file.write("\n") #This is needed so that appending isn't in the last line, but last line + 1.
            for j in range(3, len(lines)):  #the first three lines are header lines, do not repeat.
                if j == len(lines)-1:
                    print(f"Start line to copy:\n", j)
                    print("Len lines: ", len(lines))
                    print(lines[-1])
                file.write(lines[j])
        print(f"Updated: {f}\n")
        file.close()
    return None

if __name__ == "__main__":
    cwd = os.getcwd()

    # Read in files and make a copy of originals:
    input_dir = os.path.join(os.path.dirname(cwd), "model_files", "flow_2014_2022")
    output_dir = os.path.join(cwd, "output", "boundary_conditions")
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)
    copy_files = True
    ifiles = ["100hr3.ghb","100hr3.riv"]
    ofiles = ["100hr3to2067.ghb","100hr3to2067.riv"] #an old version of ofiles should be removed if copy_files = True.

    n = 4 #n is number of repeats, in this case append BCs n more times for a total of n + 1
    repeatBCs(input_dir, output_dir, n, ifiles, ofiles)
