#STEP 0: Rename file
mv extractionwells_screen_summary_updated.csv screen_fracs.csv


#STEP 1: Post-process Cr concentrations at extraction wells:
#In Windows: mod2obs_d.exe < mod2obs.in
#In Linux: ./mod2obs_d.x < mod2obs.in

#STEP 2:
#In Linux and Windows: python 19_postprocess_simulated_conc_9L.py
