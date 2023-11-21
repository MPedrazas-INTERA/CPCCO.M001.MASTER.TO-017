#setwd(dpath)
library(dplyr)
library(lubridate)

sp_perl<-read.delim("stress_periods_2014-2023.csv",sep=",",header=TRUE)

#sp_perl$start<-strptime(sp_perl$start, "%Y%m%d")
sp_perl$start<-decimal_date(as.POSIXct(sp_perl$SPstart, format = "%m/%d/%Y %H:%M")) 

#sp_perl$end<-strptime(sp_perl$end, "%Y%m%d")
sp_perl$end<-decimal_date(as.POSIXct(sp_perl$SPend,  format = "%m/%d/%Y %H:%M"))

write.table(sp_perl,file="times_2014_2023_decimal.csv",sep=",",quote=F,row.names=F,col.names=T,append=F)