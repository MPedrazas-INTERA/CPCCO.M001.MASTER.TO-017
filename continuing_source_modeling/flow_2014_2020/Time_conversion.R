#setwd(dpath)
library(dplyr)
library(lubridate)

sp_perl<-read.delim("stress_periods_2014-2020.csv",sep=",",header=TRUE)

#sp_perl$start<-strptime(sp_perl$start, "%Y%m%d")
sp_perl$start<-decimal_date(as.POSIXct(sp_perl$start, format = "%m/%d/%Y %H:%M")) 

#sp_perl$end<-strptime(sp_perl$end, "%Y%m%d")
sp_perl$end<-decimal_date(as.POSIXct(sp_perl$end,  format = "%m/%d/%Y %H:%M"))

write.table(sp_perl,file="stress_periods_2014-2020_decimal.csv",sep=",",quote=F,row.names=F,col.names=T,append=F)

	
	
	