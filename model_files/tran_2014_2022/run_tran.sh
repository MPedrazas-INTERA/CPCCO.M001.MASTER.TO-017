# rm *.ucn
# rm *.out
# rm *.DRY
# rm *.MAS
# rm *.ocn
# rm *.pst
#cd ./stomp2ssm/
#python3 batch_resample.py
#cd ../
#source activate mypython3
#python 02_get_uppermost_activecells_flow.py
./mt3d-mst-chprc08dpl.x 100hr3.nam DRY1 DRY2 > runt.log &
# cd ./mod2obs_pred2125/
# ./mod2obs_d.x < mod2obs.in
# python3 19_postprocess_simulated_conc_9L.py
