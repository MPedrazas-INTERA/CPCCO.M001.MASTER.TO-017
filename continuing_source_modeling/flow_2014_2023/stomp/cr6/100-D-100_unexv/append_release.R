library(dplyr)

dat<-readLines("gw_conc_1-24_east.dat",n=3)
write(dat,"gw_conc_1-24.dat",append=F)

#read surfaces
surf1<-read.delim("gw_conc_1-24_east.dat",sep="",skip=3,header=F)
#cumsum_surf1<-surf1$V5[nrow(surf1)]
surf2<-read.delim("gw_conc_1-24_west.dat",sep="",skip=3,header=F)

surf1$V5<-surf1$V5 + surf2$V5

surf1<-lapply(surf1, sprintf, fmt ="%12.6E")
write.table(surf1,file="gw_conc_1-24.dat",append=T,sep=" ",quote=F,row.names=F,col.names=F)

