

import os
import matplotlib
matplotlib.use('Qt5Agg')


sce_in = 'sce8a_rr1_to2125'
sce_out = 'sce9a_rr3_to2125'
times = '2023to2125'

# directories
cwd = os.getcwd()
idir = os.path.join("..", 'model_packages', 'pred_2023_2125', f'ssm_{sce_in}')
odir = os.path.join("..", 'model_packages', 'pred_2023_2125', f'ssm_{sce_out}')

fin = "100HR3_2023_2125_transport_stomp2ssm.ssm"
fout = "100HR3_2023_2125_transport_stomp2ssm_reduced.ssm"

## we want to apply a multiplier to SSM at a given point (i.e. after soil flushing) to reduce source strength
    ## (multiplier is a fudge factor on source)

multiplier = 0.5

newLines = []
counter = 0
mysp = []
with open(os.path.join(idir, fin), "r") as f_in, open(os.path.join(odir, fout), 'w') as f_out:
    lines = f_in.read().splitlines()
    for idx, line in enumerate(lines):
        if line == ' 290':
            counter += 1
            mysp.append(counter)  # get SPs
        if (idx >= 2) & (line != ' 290') & (line != ' -1'):
            mystr = line.split()
            mylayer = int(mystr[0])
            myrow = int(mystr[1])
            mycolumn = int(mystr[2])
            myval = float(mystr[3])
            if counter < 155:  # The SP after which we will add the mult factor
                newLine = "{0:10}{1:10}{2:10}{3:10.3e}{4:10}\n".format(mylayer, myrow, mycolumn, myval, mystr[4].rjust(10))
            else:
                newLine = "{0:10}{1:10}{2:10}{3:10.3e}{4:10}\n".format(mylayer, myrow, mycolumn, myval*multiplier, mystr[4].rjust(10))
            newLines.append(newLine)
            f_out.write(newLine)  # write out lines with updated layers = all the source cell lines
        else:
            f_out.write(line)  # write out original lines if nothing to do with source cell location
            f_out.write("\n")