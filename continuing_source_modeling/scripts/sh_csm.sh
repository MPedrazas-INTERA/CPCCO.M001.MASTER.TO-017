## start in 100HR3/continuing_source_modeling/scripts

for sce in 'sce2_to2125_rr5'; do
	#mkdir ../scenarios/$sce
	cp -r ../flow_2023_2125_template/. ../scenarios/$sce ## blank slate scenario dir structure
	echo "$sce dir created and populated"

## run mod2obs -- first go to mod2obs_d_cell.in and change inputs as necesssary
	cd ../scenarios/$sce/bc_mod2obs
	echo "running mod2obs for $sce"
	./mod2obs_d.x < mod2obs_d_cell.in

## split mod2obs results
	## .dat file split into separate files for each bore
	 python py01_split_mod2obs_results.py
	 Rscript make_BC.R 

## populate STOMP .tpl file
	cd ..
	python 01_flow_to_stomp.py  ##make SURE directory names and structure match what is in script

## run STOMP
	cd ./stomp
	echo "running stomp shell script "run_transient.sh". patience..."
	./run_transient_v2.sh &
	wait		## need to wait until stomp is complete on all columns before moving on

## generate SSM
	## 1. copy data files to SSM dirs
	cd ..
	python 02_cp_dat_to_ssm.py
	cd ./ssm/cr6/stomp2ssm
	python batch_resample.py
	echo "SSM package successfully created."

##copy SSM to model_packages directory
	mkdir ../../../../../../model_packages/pred_2023_2125/ssm_"${sce}"
	cp ../100HR3_2023_2125_transport_stomp2ssm.ssm ../../../../../../model_packages/pred_2023_2125/ssm_"${sce}"
	echo "SSM package copied to model_packages/pred_2023_2125/ssm_${sce}."
	
done
	