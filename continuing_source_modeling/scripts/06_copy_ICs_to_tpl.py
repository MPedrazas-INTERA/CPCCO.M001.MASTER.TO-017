
import os
import shutil

wdir = os.path.dirname(os.getcwd())

## initial conditions from calibration run -- will not change
# calib_dir = os.path.join(wdir, 'scenarios', 'flow_2014_2022', 'stomp', 'cr6')

## set destination directory
sc = 'sce9a_rr3_to2125'
source_dir = os.path.join(wdir, 'scenarios', sc, '2023_2035', 'stomp', 'cr6')
dest_dir = os.path.join(wdir, 'scenarios', sc, '2035_2125', 'stomp', 'cr6')


source_zones = os.listdir(source_dir)

## copy restart files (i.e. initial conditions) from calibration scenario to predictive scenario into separate directories.
def copy_ic_dat():
    for zone in source_zones:
        try:
            ic_dat_file = os.path.join(source_dir, zone, '100D-2035-ics.dat')
            dest = os.path.join(dest_dir, zone, '100D-2035-ics.dat')
            shutil.copy2(ic_dat_file, dest)
        except:
            print(f'Could not copy restart files')

    return None


if __name__ == "__main__":

    # copy_ic_dat()


    ## insert initial conditions from prior run into template file for subsequent run
    for zone in source_zones:
        with open(os.path.join(dest_dir, zone, '100D-2035-ics.dat'), 'r') as ic_file:
            ic_lines = ic_file.readlines()[8:]
        with open(os.path.join(dest_dir, zone, 'archive', 'input_cycle2_new.tpl'), 'r') as tpl_file:
            tpl_lines = tpl_file.read()

        marker_strings = ['~Initial Conditions Card\n', 'Aqueous Pressure,Gas Pressure,\n', '0,\n']
        marker = ''.join(marker_strings)
        location = tpl_lines.find(marker)

        if location != -1:
            updated_tpl = tpl_lines[:location + len(marker)] + ''.join(ic_lines) + tpl_lines[location + len(marker):]

            with open(os.path.join(dest_dir, zone, 'input_cycle2_new.tpl'), 'w') as new_tpl:
                new_tpl.write(updated_tpl)

        with open(os.path.join(dest_dir, zone, 'input_cycle2_new.tpl'), 'r') as new_tpl:
            lines = new_tpl.readlines()

            for i in range(len(lines)):
                if 'Aqueous Pressure,Gas Pressure,\n' in lines[i]:
                    print(lines[i+1])
                    newval = str(len(ic_lines)) + ',\n'
                    lines[i+1] = newval
        with open(os.path.join(dest_dir, zone, 'input_cycle2_new.tpl'), 'w') as new_tpl:
            new_tpl.writelines(lines)
