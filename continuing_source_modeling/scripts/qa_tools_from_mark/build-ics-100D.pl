#!/usr/bin/perl -w
# build-ics-100D.pl
# 
# build STOMP IC's for Concentration from a zprofile-100D csv output file.
# By M.D.Williams on 8/4/2023, INTERA INC
# Inputs:
# 	zplot2profile-100D.pl output csv file
# 	Column Number for concentrations
# 	output file name for STOMP IC Cards
# 
#	Version 1.1 - Initial
#
$vers="1.1";
$dtstamp = localtime();

$inf = shift @ARGV;     # input zplot2profile-100D csv file name
$inc = shift @ARGV;	# column of cr6+ aqueous volumetric concentration in file
$sfac = shift @ARGV;	# concentration scaling factor
$oin = shift @ARGV;	# output file name for STOMP IC cards

open(IN,"<$inf") || die "Can't open $inf file $!\n";
open(IC,">$oin") || die "Can't open $oin file $!\n";


printf(IC "# Generated from $inf on $dtstamp build-ics-100D.pl, Version = $vers\n");
printf(IC "# data from Column number $inc\n");
printf(IC "# Concentration scale factor = $sfac\n");
printf(IC "#\n");
printf(IC "Comments from input file:\n");
$line=<IN>;
while (substr($line,0,1) eq "#") {
	printf(IC "#$line");
	$line=<IN>;
}

# get headings
chomp($line);
printf("Heading Line=$line\n");
@h=split(",",$line);
printf("\n");
printf("Extracting Column = $h[$inc-1]\n");
printf("It better be a cr6 aqueous concentration!\n");
printf("\n");

while ($line=<IN>) {
	chomp($line);
	@a=split(",",$line);
	$k=$a[2];
	$val=$a[$inc-1]*$sfac;
	printf(IC "Overwrite Solute Aqueous Concentration,");
	printf(IC "cr6, $val, 1/m^3, , , , , , ,");
	printf(IC "1,1,1,1,$k,$k,\n");
}


close(IN);
close(IC);
