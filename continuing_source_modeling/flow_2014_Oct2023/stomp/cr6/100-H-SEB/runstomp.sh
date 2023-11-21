# Remove all the restart/plot/output files from old run
rm -f restart*
rm -f plot*
rm -f *.out
rm -f *.srf
rm -f *.dat

cp input_cycle2 input

../../stomp-w-r-cgsq-chprc04i.x

perl ../../surfaceTo.pl -a Tecplot gw_conc_1-24_east.dat gw_conc_1-24_east.srf
perl ../../surfaceTo.pl -a Tecplot gw_conc_1-24_west.dat gw_conc_1-24_west.srf

Rscript append_release.R

rm dir_list.txt

prefix="restart"

ls -c $prefix.* > dir_list.txt

x=

for x in $(cat dir_list.txt)
do
break
done

echo "found restart file $x"

cp $x restart

