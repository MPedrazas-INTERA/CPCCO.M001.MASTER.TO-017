python regenerate_in_files.py
cp ../../06_support_software/utilities/ConcTarg2/ConcTarg2.exe .
./ConcTarg2.exe conc-targs_CY2022_CTET_600.in2
./ConcTarg2.exe conc-targs_CY2022_Nitrate.in2
python plot_obs_sim_conc_mon_wells_v1.py
