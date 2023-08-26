"""
script to:

1. copy restart file from calibration case to scenario case into zones of interest directories (generally only run once unless calib. model changes)
2. copy .tpl files from calibration case or baseline predictive case into zones of interest directories
3. edit .tpl file for updated predictive case and any subsequent needed updates.

Part 3 is file-specific, may require referring to STOMP online documentation to follow along.

author: rweatherl

"""

import os
import shutil

wdir = os.path.dirname(os.getcwd())

## clean, empty directory to use as baseline structure for all scenarios
source_dir = os.path.join(wdir, 'scenarios', 'flow_2023_2125_template', 'stomp', 'cr6')
## keep track of where we are pulling original files from!
# source_dir = os.path.join("S:/", "AUS", "CHPRC.C003.HANOFF", "Rel.147", "ECF-100HR3-22-0119-check-review",
#                              "model-files-after-check-review", "continuing_source_modeling",
#                              "flow_NFA_2125_rev_ghb_mnw2_V2", "stomp", "cr6")
# source_zones
source_zones = next(os.walk(source_dir))[1]

## set destination directory
sc = 'sce2_to2125_rerun3'
dest_dir = os.path.join(wdir, 'scenarios', sc, 'stomp', 'cr6')


## copy/edit input template file for different scenarios
## .tpl files are copied from current baseline predictive case (2023-2125)
def copy_tpl_file():

    for zone in source_zones:
        try:
            template_file = os.path.join(source_dir, zone, 'input_cycle2.tpl')
            # template_file = os.path.join(calib_dir, zone, 'input_cycle2.tpl')
            dest = os.path.join(dest_dir, zone, 'input_cycle2.tpl')
            shutil.copy2(template_file, dest)
        except:
            print(f'Could not copy template files')

    return None

def edit_tpl_file():

    for zone in source_zones:
        with open(os.path.join(dest_dir, zone, 'input_cycle2.tpl'), 'r') as template_file:
            lines = template_file.readlines()
            ## good general practice to change editor name and dates for traceability
            lines[5] = 'March 29 2023,\n'
            lines[6] = '11:00 CST,\n'
            lines[15] = '2023.,yr,2126.0,yr,1.0e-06,d,1,d,1.25,8,1.e-6,\n'

            ## changes based on string patterns -- line numbers for specific info change as we go further down the file

            for i in range(len(lines)):
                if lines[i].startswith('1,1,1,1,1, 24,645,\n'):  ## refers to number of SPs. In STOMP, this is always SP+1 to include 01-01-2026
                    lines[i] = '1,1,1,1,1, 24,599,\n'
                if lines[i].startswith('2021.000000,yr,'):      ## change output control card to write out 2023 as first year
                    lines[i] = '2023.000000,yr,\n'

            ## shave off recharge boundary conditions that are no longer needed/outside of simulation period
            strings_to_remove = ['2020,yr,-46.000,mm/yr,,,,,,,,,,,\n',
                                 '2021,yr,-46.000,mm/yr,,,,,,,,,,,\n',
                                 '2022,yr,-46.000,mm/yr,,,,,,,,,,,\n',
                                 '2020,yr,  0.000,mm/yr,,,,,,,,,,,\n',
                                 '2021,yr,  0.000,mm/yr,,,,,,,,,,,\n',
                                 '2022,yr,  0.000,mm/yr,,,,,,,,,,,\n'
                                 ]
            lines = [line for line in lines if not any(string in line for string in strings_to_remove)]
            ## adjust number of entries for recharge boundary conditions and retain one 2022 entry -- will be 207 instead of 211
            for i in range(len(lines)):
                if lines[i].startswith('1,1,1,1,119,119,211,\n'):
                    lines[i] = '1,1,1,1,119,119,207,\n2022,yr,-46.000,mm/yr,,,,,,,,,,,\n'
                if lines[i].startswith('1,1,1,1,121,121,211,\n'):
                    lines[i] = '1,1,1,1,121,121,207,\n2022,yr,-46.000,mm/yr,,,,,,,,,,,\n'
                if lines[i].startswith('1,1,1,1,75,75,211,\n'):
                    lines[i] = '1,1,1,1,75,75,207,\n2022,yr,-46.000,mm/yr,,,,,,,,,,,\n'

            ## above snippet removed both entries for 2022, but we need to retain one of them. Here we re-insert it as
                ## the first entry below recharge boundary conditions.
            # ## (side note: after 2022 initial condition,
            # string_to_find = '1,1,1,1,119,119,207,'
            # index = next((i for i, line in enumerate(lines) if string_to_find in line), None)
            # if index is not None:
            #     new_line = '2022,yr,-46.000,mm/yr,,,,,,,,,,,\n'
            #     lines.insert(index + 1, new_line)

        with open(os.path.join(dest_dir, zone, 'input_cycle2.tpl'), 'w') as template_file:
            template_file.writelines(lines)

            template_file.close()

    print('template files edited! check that all is in order!')

    return None

if __name__ == "__main__":

    copy_tpl_file()

    # edit_tpl_file()


