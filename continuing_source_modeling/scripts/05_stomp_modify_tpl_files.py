"""
script to:

edit .tpl file for updated predictive case and any subsequent needed updates. This will update .tpl files in all
subdirectories under the destination directory. Script is file-specific

Things to keep in mind:

The code block starting with "for number, line in enumerate(lines):" is used to remove ranges of lines in the .tpl file.
    Every time such a code block is run, the line numbers below this are altered. This is why code blocks are separated
    so that updated line numbers are accounted for.

Always a good idea to write out a new file rather than overwriting existing file, in case of mistakes or incremental changes.

author: rweatherl

"""

import os
import shutil

wdir = os.path.dirname(os.getcwd())

## initial conditions from calibration run -- will only change when calib run is changed
# calib_dir = os.path.join(wdir, 'scenarios', 'flow_2014_2022', 'stomp', 'cr6')

## set destination directory
sc = 'sce9a_rr3_to2125'
source_dir = os.path.join(wdir, 'scenarios', sc, '2023_2035', 'stomp', 'cr6')
dest_dir = os.path.join(wdir, 'scenarios', sc, '2035_2125', 'stomp', 'cr6')

## source zones are equiv for all scenarios, so this just creates a list that can be used across the board
source_zones = os.listdir(source_dir)
## use for isolating zones in 100-H or 100-D
H = list(filter(lambda x: '100-H' in x, source_zones))
D = list(filter(lambda x: '100-D' in x, source_zones))

for zone in H:
    with open(os.path.join(source_dir, zone, 'input_cycle2.tpl'), 'r') as template_file:
    # with open(os.path.join(source_dir, zone, 'input_cycle2.tpl'), 'r' as template_file:
        lines = template_file.readlines()
        # ## good general practice to change editor name and dates for traceability
        lines[5] = 'August 25 2023,\n'
        lines[6] = '11:00 CST,\n'
        lines[21] = '2023.,yr,2035.8329,yr,1.0e-06,d,1,d,1.25,8,1.e-6,'
        # lines[21] = '2035.8328,yr,2126.,yr,1.0e-06,d,1,d,1.25,8,1.e-6,\n'
        #
        # ## delete extra recharge values and write-out values
        # rech_del_start = '2022,yr,-46.000,mm/yr,,,,,,,,,,,\n'
        # rech_del_end = '2034,yr,-46.000,mm/yr,,,,,,,,,,,\n'
        rech_del_start = '2036,yr,' ## partial string match
        rech_del_end = '2125,yr,' ## partial string match
        # plot_yr_1 = '2023.000000,yr,\n'
        # plot_yr_2 = '2035.000000,yr,\n'
        # for number, line in enumerate(lines):
        #     if rech_del_start in line:
        #         start_number = number
        #     if rech_del_end in line:
        #         end_number = number
        # del lines[start_number:end_number+1]
        #
        # for number, line in enumerate(lines):
        #     if plot_yr_1 in line:
        #         last_year = number
        #     if plot_yr_2 in line:
        #         cut = number
        # del lines[last_year:cut]

        ## changes based on string patterns -- line numbers for specific info change as we go further down the file
        ## 1. Rech boundary conditions
        for i in range(len(lines)):
            if lines[i].startswith('2035.8328,yr,2126.,yr,1.0e-06,d,1,d,1.25,8,1.e-6,'):
                lines[i] = '2035.8329,yr,2126.,yr,1.0e-06,d,1,d,1.25,8,1.e-6,\n'
            # if lines[i].startswith('1,1,1,1,1, 24,27,\n'):
            #     lines[i] = '1,1,1,1,121,121,27,\n'
            # if lines[i].startswith('1,1,1,1,119,119,207,\n'):
            #     lines[i] = '1,1,1,1,119,119,27,\n'
            if lines[i].startswith('5\n') & lines[i].endswith('5\n'):
                lines[i] = '19,\n'
            if lines[i].startswith('11:00 CST\n'):
                lines[i] = '11:00 CST,\n'

        ## removing source card
        # source_1 = '# Added by MDWilliams, Intera 4/27/2023\n'
        # source_2 = '2035.8329, year,  0.000, gal/min,\n'
        # sf = '~Surface Flux Card\n'
        # for number, line in enumerate(lines):
        #     if source_1 in line:
        #         s1 = number
        #     if source_2 in line:
        #         s2 = number
        # del lines[s1:s2+1]
        #
        # for number, line in enumerate(lines):
        #     if sf in line:
        #         s3 = number
        # del lines[s3-2:s3]

    with open(os.path.join(dest_dir, zone, 'input_cycle2_new.tpl'), 'w') as template_file:
        template_file.writelines(lines)

        template_file.close()

print('template files edited! check that all is in order!')

