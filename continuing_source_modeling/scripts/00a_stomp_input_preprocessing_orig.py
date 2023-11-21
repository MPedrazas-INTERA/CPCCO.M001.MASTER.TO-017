"""
script to:

1. copy final restart file from calibration case (or base case) to scenario case into zones of interest directories (generally only run once unless calib. model changes)
2. copy .tpl files from calibration case or baseline case into zones of interest directories
3. edit .tpl file for updated case with any needed text changes

Part 3 is file-specific, may require referring to STOMP online documentation to follow along.

author: rweatherl

"""

import os
import shutil

wdir = os.path.dirname(os.getcwd())

## initial conditions from calibration run
calib_dir = os.path.join(wdir, 'flow_2014_2023', 'stomp', 'cr6')

## set destination directory
sc = 'flow_2014_Oct2023'
dest_dir = os.path.join(wdir, sc, 'stomp', 'cr6')

source_zones = os.listdir(calib_dir)  ## source zones are equiv for all scenarios, so this just creates a list that can be used across the board
source_zones = [k for k in source_zones if '100' in k]

## copy restart files (i.e. initial conditions) from calibration scenario to predictive scenario into separate directories.
def copy_restart_file():
    for zone in source_zones:
        try:
            restart_file = os.path.join(calib_dir, zone, 'restart')
            dest = os.path.join(dest_dir, zone, 'calib_restart', 'restart')
            shutil.copy2(restart_file, dest)
        except:
            print(f'Could not copy restart files')

    return None

## copy/edit input template file for different scenarios
## for the first copy-over, .tpl files are copied from previous baseline STOMP model and edited accordingly
## for consequent copies for different scenarios, .tpl files are copied from current baseline predictive case (2023-2125)
## 2023 EDIT: This can now be carried out through shell script within /stomp/cr6 directory. This function can still be used for a quick re-copy when needed
def copy_tpl_file():

    ## keep track of where we are pulling original files from!
    source_files = os.path.join("S:/", "AUS", "CHPRC.C003.HANOFF", "Rel.150", "100HR3",
                                 "continuing_source_modeling", "scenarios", "flow_2014_2022", "stomp", "cr6")

    for zone in source_zones:
        try:
            template_file = os.path.join(source_files, zone, 'input_cycle2.tpl')
            dest = os.path.join(dest_dir, zone, 'input_cycle2.tpl')
            shutil.copy2(template_file, dest)
        except:
            print(f'Could not copy template files')

    return None

def edit_tpl_file():

    ## when writing lines into stomp, basically EVERY line EXCEPT for card titles must finish with a comma! ,

    for zone in source_zones:
        with open(os.path.join(dest_dir, zone, 'input_cycle2.tpl'), 'r') as template_file:
            lines = template_file.readlines()
            ## Header lines. Good general practice to change editor name and dates for traceability
            lines[5] = 'November 21, 2023,\n'
            lines[6] = '10:00 CST,\n'
            lines[15] = '2014.,yr,2023.748,yr,1.0e-06,d,1,d,1.25,8,1.e-6,\n'

            ## changes based on string patterns -- line numbers for specific info change as we go further down the file

            for i in range(len(lines)):
                # if lines[i].startswith('1,1,1,1,1, 24,109,\n'): ## changing BC header for water levels -- number of SPs + 1
                if lines[i] == '1,1,1,1,1, 24,116,\n':
                    lines[i] = '1,1,1,1,1, 24,119,\n'
                # if lines[i].startswith('2012.0,yr,-46.00000000,mm/yr,,,,,,,,,,,\n'): ## changing BC header for recharge
                #     lines[i] = '2014.0,yr,-46.00000000,mm/yr,,,,,,,,,,,\n'
                # if lines[i].startswith('2023.0,yr,-46.00000000,mm/yr,,,,,,,,,,,\n'):
                #     lines[i] = '2024.0,yr,-46.00000000,mm/yr,,,,,,,,,,,\n'

            ## shave off conditions that are no longer needed/outside of simulation period. Can be a list of strings.
            # strings_to_remove = ['2012.100000,yr,']
            # lines = [line for line in lines if not any(string in line for string in strings_to_remove)]
            #
            # ## insert lines after line string_to_find
            # string_to_find = '2022.000000,yr,'
            # index = next((i for i, line in enumerate(lines) if string_to_find in line), None)
            # if index is not None:
            #     new_line = '2023.581000,yr,\n'
            #     lines.insert(index + 1, new_line)

            ## --- extra snippets -- ##
            # ## adjust number of entries for recharge boundary conditions -- will be 207 instead of 211
            # for i in range(len(lines)):
            #     if lines[i].startswith('1,1,1,1,119,119,211,\n'):
            #         lines[i] = '1,1,1,1,119,119,207,'

            ## above snippet removed both entries for 2022, but we need to retain one of them. Here we re-insert it as
                ## the first entry below recharge boundary conditions.
            # string_to_find = '1,1,1,1,119,119,207,'
            # index = next((i for i, line in enumerate(lines) if string_to_find in line), None)
            # if index is not None:
            #     new_line = '\n2022,yr,-46.000,mm/yr,,,,,,,,,,,\n'
            #     lines.insert(index + 1, new_line)

        with open(os.path.join(dest_dir, zone, 'input_cycle2.tpl'), 'w') as template_file:
            template_file.writelines(lines)

            template_file.close()

    print('template files edited! check that all is in order!')

    return None

if __name__ == "__main__":

    # copy_restart_file()

    copy_tpl_file()
    edit_tpl_file()


