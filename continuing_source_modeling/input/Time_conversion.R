#setwd(dpath)
library(dplyr)
library(lubridate)

sp_perl<-read.delim("stress_periods_2023-2125_decimal.csv",sep=",",header=TRUE)

#sp_perl$start<-strptime(sp_perl$start, "%Y%m%d")
sp_perl$start<-decimal_date(as.POSIXct(sp_perl$start_date, format = "%m/%d/%Y %H:%M")) 

#sp_perl$end<-strptime(sp_perl$end, "%Y%m%d")
sp_perl$end<-decimal_date(as.POSIXct(sp_perl$end_date,  format = "%m/%d/%Y %H:%M"))

write.table(sp_perl,file="times_2023_2125_decimal.csv",sep=",",quote=F,row.names=F,col.names=T,append=F)