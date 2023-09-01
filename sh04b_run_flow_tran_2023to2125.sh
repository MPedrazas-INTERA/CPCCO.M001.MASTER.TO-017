#!/bin/bash
# You are at /home/hpham/100HR3 or similar path
# You will sumbit job using htcondor: condor_submit r5xxx.sub
# Remember to zip input files if you make changes
# run: r0_zipfile_first.sh

opt_run_flow='yes'
opt_run_tran='no' 

mkdir 100HR3
tar zxvf flow_2023_2125.tar -C 100HR3

mkdir 100HR3/b2
tar -xf b2.tar.gz -C 100HR3/b2

mkdir 100HR3/b3
tar -xf b3.tar.gz -C 100HR3/b3

cd scripts


wdir="$PWD" 
#for sce in 'sce1' 'sce3' 'sce4'; do
mkdir ../mruns
for i in 'sce3a'; do            # change herr for a new sce (e.g., sce2, nfa)
    sce="${i}_to2125_rr3_rwtest"  # change here if testing a scenario multiple times
    # Create a working directory for sce
    mkdir ../mruns/$sce

    # [01] Run flow ==============================================================
    if [ $opt_run_flow = 'yes' ]
    then
		run_dir_flow=$sce/flow_2023to2125
		echo run_sce=$run_dir_flow
		mkdir ../mruns/$run_dir_flow
		cp -rf ../model_files/flow_2023_2125/*.* ../mruns/$run_dir_flow/
		rm -f ../mruns/$run_dir_flow/*.mnw2
		cp ../model_packages/pred_2023_2125/mnw2_"${i}"/100hr3_2023to2125.mnw2 ../mruns/$run_dir_flow/
		cd ../mruns/$run_dir_flow/
		7za e 100hr3_2023to2125.riv.7z # Extract file using 7za, in head node only
		7za e 100hr3_2023to2125.rch.7z
		7za e 100hr3_2023to2125.ghb.7z
		#rm *.7z
		#bash run_flow.sh > outlog.txt
		#../../../executables/linux/mf2k-mst-cpcc09dpl.x 100hr3_2023to2125.nam > run.log
		../../../executables/linux/mf2k-mst-cpcc09dpl.x 100hr3.nam > run.log
		#cd ../../../scripts/
		cd $wdir
    fi    

    # [03] Run transport =========================================================
    if [ $opt_run_tran = 'yes' ]
    then  
        run_dir_tran=$sce/tran_2023to2125
        mkdir ../mruns/$run_dir_tran
        echo run_sce=$run_dir_tran
        cp -rf ../model_files/tran_2023_2125/* ../mruns/$run_dir_tran/
		#cp -r ../model_files/tran_2023_2125/shoreline_stats ../mruns/$run_dir_tran/
		#cp -r ../model_files/tran_2023_2125/post_process ../mruns/$run_dir_tran/
		#cp -f ../model_files/tran_2023_2125/calculate_mass_recovered.py ../mruns/$run_dir_tran/
        cd ../mruns/$run_dir_tran/
        #bash run_tran.sh > outlog.txt
        ../../../executables/linux/mt3d-mst-cpcc09dpl.x 100hr3.nam DRY1 DRY2 > run.log
        #conda activate b3
		# Activate the environment. This adds `my_env/bin` to your path
		cd $wdir
		source ../b3/bin/activate
		cd ../mruns/$run_dir_tran/
		python ucn_precision_swapper.py
		cd post_process/ucn2png
		# copy shp files of sys wells (later)        
        python main.py # Get plume maps
                
        # Script to cal mass recovery
        cd $wdir
        cd ../mruns/$run_dir_tran/
        cd post_process/mass_recovery
        echo "running mod2obs"
        python gen_input_mod2obs.py mnw2_"${i}" "${wdir}"
        cp $wdir/output/well_info/mnw2_$i/extractionwells_screen_summary.csv .
        ../../../../../../executables/linux/mod2obs_d.x < mod2obs.in
        echo "post-processing concentrations"
        python postprocess_simulated_conc_9L.py
		python calculate_mass_recovered.py mnw2_"${i}" "${wdir}"

        # MP: Add script to generate shoreline length contaminated
        cd $wdir
		source ../b2/bin/activate
		cd ../mruns/$run_dir_tran/
		cd post_process/shoreline_stats
		python calc_highriv_shoreline_py2.py
		
		#conda activate b3
		cd $wdir
		source ../b3/bin/activate
		cd ../mruns/$run_dir_tran/
		cd post_process/shoreline_stats
		python plot_highriv_shoreline.py
		
		cd $wdir
    fi
done
