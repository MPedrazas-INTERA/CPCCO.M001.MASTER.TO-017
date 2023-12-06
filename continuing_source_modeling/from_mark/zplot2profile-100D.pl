#!/usr/bin/perl -w
# zplot2profile-100D.pl
# 
# Created by MDWilliams, INTERA 11-8-2020
#	This program creates z profiles of plot variables from
#	stomp plot files for ease of plotting
#
#	uses xy coords for profile location
#
#   fixed bug on 1-23-2018, Dennis Fryar Caught: p = (pi-1)
#
#   Copied ca-zplot2profile-xy.pl to here on 8/4/2023
#   changed x,y selection to I,J
#   outputing I,J,K also to csv file (first three fields).
#

$inf = shift @ARGV;
$iplt = shift @ARGV;
#$px = shift @ARGV;
#$py = shift @ARGV;
$pi = shift @ARGV;
$pj = shift @ARGV;
$oprf = shift @ARGV;

# load input file
# find Rock Names
$flag=0;
$nrock=0;
@rock=[];
open(IN,"<$inf") || die "Can't open $inf file $!\n";
$line=<IN>;
chomp($line);
while ($flag == 0) {
        if (lc($line) =~ m/~rock\/soil/) {
                $flag=1;
                # skip two lines to get to names
                $line=<IN>;
                $line=<IN>;
                $line=<IN>;
                chomp($line);
                while (substr($line,0,1) ne "#") {
                        @a=split(",",$line);
                        $rname=lc($a[0]);
                        $rname=~ s/^\s+|\s+$//g;
                        $nrock++;
                        $rock[$nrock] = $rname;
                        $line=<IN>;
                        chomp($line);
                }
        } else {
                $line=<IN>;
                chomp($line);
                if (eof(IN)) {
                        printf("Error - couldn't find rock/soil cards\n");
                        exit(0);
                }
        }
}
close(IN);
printf("NROCK = $nrock\n");
for ($i=1;$i<=$nrock;$i++) {
	printf("$rock[$i]\n");
}

open(IP,"<$iplt") || die "Can't open $iplt file $!\n";

# scan STOMP Plot File
# find time line
$flag = 1;
while($flag) {
	$line = <IP>;
	chomp($line);
	if (substr($line,0,4) eq "Time") {
		$timeline=$line;
		$flag = 0;
	}
}

#extract year 
@a=split(" ",$timeline);
print("$a[7]\n");
@a=split(",",$a[7]);
$yr=sprintf("%d",$a[0]);
$opf = $oprf."-".$yr.".csv";
$ogeo = $oprf."-geo.csv";
$olab = $oprf."-labels.gnu";

open(OP,">$opf") || die "Can't open $opf file $!\n";
open(OG,">$ogeo") || die "Can't open $ogeo file $!\n";
open(OL,">$olab") || die "Can't open $olab file $!\n";
printf( OP "# $iplt\n");
printf( OP "# I=$pi, J=$pj\n");
printf( OP "# $timeline\n");


# find number of nodes
$flag = 1;
while($flag) {
	$line= <IP>;
	chomp($line);
	  if (substr($line,0,7) eq "Number ") {
		@a = split(" = ",$line);
		$nx = $a[1];
		$line= <IP>;
        	chomp($line);
		@a = split(" = ",$line);
                $ny = $a[1];
		$line= <IP>;
        	chomp($line);
		@a = split(" = ",$line);
                $nz = $a[1];
                $line= <IP>;
                chomp($line);
                @a = split(" = ",$line);
#                $xo = $a[1];
                $line= <IP>;
                chomp($line);
                @a = split(" = ",$line);
#                $yo = $a[1];
                $line= <IP>;
                chomp($line);
                @a = split(" = ",$line);
#                $zo = $a[1];
		# skip blank before data
		$line = <IP>;
		$flag=0;
	}
}
print(" nx,ny,nz = $nx,$ny,$nz\n");

$nn = $nx*$ny*$nz;
$d=0;
while ($line = <IP>) {
	chomp($line);
	@a=split(", ",$line);
	if (! defined $a[1]) {
		$line=$a[0];
	} else {
		$line=$a[0]." (".$a[1].")";
	}
# Find Rock/Soil Type (dgf 9-17-18)
	if ($a[0] eq "Rock/Soil Type")  {
		$rscol=$d;
	} 
	if ($a[0] eq "X-Direction Node Positions") {
		$xcol=$d;
	}
        if ($a[0] eq "Y-Direction Node Positions") {
                $ycol=$d;
        }
        if ($a[0] eq "Z-Direction Node Positions") {
                $zcol=$d;
        }
# End change
	# check for "," in $line. Put () around what comes after
	@a=split(",",$line);
	if (scalar(@a) > 1) {
		$line=$a[0]." (".$a[1].")";
		printf("\ncomma in header, corrected with ()\n");
	}
	$line =~ s/\s+/ /g;
	$h[$d]=$line;
	print ("\nLoading ... $line");
	$i = 0;
	while ($i < $nn) {
		$line=<IP>;
		chomp($line);
		@a = split(" ",$line);
		$j=scalar(@a);
		for ($k=0;$k<$j;$k++) {
			$r[$d][$i+$k]=$a[$k];
		}
		$i+=$j;
	}
	$d++;
	# skip blank
	$line = <IP>;
}
close(IP);
printf("\n X,Y,Z cols = $xcol,$ycol,$zcol\n");

# find pi and pj from px and py
#$pi = -1;
#$xmin=9.0E+10;
#for ($i=1;$i<=$nx;$i++) {
#	$p=$i-1;
#	$dx=abs($px-$r[$xcol][$p]);
#	if ($dx < $xmin) {
#		$xmin=$dx;
#		$pi=$i;
#	}
#
#}
#$pj = -1;
#$ymin=9.0E+10;
#for ($j=1;$j<=$ny;$j++) {
#	$p=($pi-1) + (($j-1)*$nx);
#	$dy=abs($py-$r[$ycol][$p]);
#	if ($dy < $ymin) {
#		$ymin=$dy;
#		$pj=$j;
#	}
#}

#printf("\n $px,$py Coords translated to I,J = $pi,$pj\n");
print("\nWriting profile output file...");

# now write profile to output file
# column headers
printf(OP "I,J,K,");
for ($i=0;$i<$d;$i++) {
	printf(OP "$h[$i], ");
}
printf(OP "Unit-name,\n");
$lcode=0;
for ($k=1;$k<=$nz;$k++) {
	$p=($pi-1) + (($pj-1)*$nx) + (($k-1)*($nx*$ny));
	printf(OP "%d, %d, %d, ",$pi,$pj,$k);
# if statement added to skip output if Rock/Soil Type = 0 (dgf 9-17-18)
	$rcode=$r[$rscol][$p];
	#	if($rcode != 0) {		
	    for ($i=0;$i<$d;$i++) {
			printf(OP "$r[$i][$p], ");
	    }
	    printf(OP "$rock[$rcode]\n");
	    if (($rcode!=$lcode) && ($lcode!=0)) {
		#write out a plot line for change in rock type
		$zu=$r[$zcol][$p];
		printf(OG "0,$zu\n");
		printf(OG "1,$zu\n");
		printf(OG "0,$zu\n");
		printf(OL "set label \"\\n $rock[$lcode]\" at 0,$zu left font \"Arial,8\" front\n");
		$zlab=$zu+2.00;
		printf(OL "set label \"\\n $rock[$rcode]\" at 0,$zlab left font \"Arial,8\" front\n");
	    }
	    $lcode=$rcode;
	    #	} 
}
close(OP);
close(OG);
close(OL);

print("\n");
