#setwd("E:/100K_GWM/PEST/vista5n/BC_for_waste_sites_STOMP")

library(dplyr)
library(lubridate)

list_file<-read.csv("STOMP_column_list.csv",header=TRUE)
attach(list_file)

for (i in 1:nrow(list_file)) {
dat=read.delim(paste(site[i],".dat",sep=""),sep="",header=FALSE)
dat[,5]<-decimal_date(as.Date(dat[,2], "%m/%d/%Y"))
dat[,6]<-101325+(dat[,4]-base_center_elev[i])*9793.52
dat[,7]<-paste(dat[,5],",yr,",dat[,6],",Pa,,,",sep="")
colnames(dat)<-c("Location","Date","Time","Head","Dec_year","Pressure","STOMP_BC")

write.csv(dat,file=paste("make_BC_",site[i],".csv",sep=""),row.names=FALSE)

}
