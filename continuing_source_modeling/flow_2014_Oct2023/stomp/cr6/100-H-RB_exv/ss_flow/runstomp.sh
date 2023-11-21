# Remove all the restart/plot/output files from old run
rm -f restart*
rm -f plot*
rm -f *.out
rm -f *.srf
rm -f *.dat

cp input_100-H-RB_hist input

stomp-w-r-cgsq-chprc04i.x

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
