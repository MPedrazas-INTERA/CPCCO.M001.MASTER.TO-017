##set user working directory to run script. TODO possible to make this a relative path?
#setwd("C:\Users\RWeatherl\OneDrive - INTERA Inc\Documents\GitHub\100HR3\continuing_source_modeling\flow_2014_2022\BC_mod2obs")

library(dplyr)
library(lubridate)

list_file<-read.csv("STOMP_column_list.csv",header=TRUE)
attach(list_file)

for (i in 1:nrow(list_file)) {
dat=read.delim(paste(site[i],".dat",sep=""),sep="",header=FALSE)
dat[,5]<-decimal_date(as.Date(dat[,2], "%m/%d/%Y"))
dat[,6]<-101325+(dat[,4]-base_center_elev[i])*9793.52
#dat[,6]<-101325+(dat[,4]-dat[,3])*9793.52
print(dat[,4])
dat[,7]<-paste(dat[,5],",yr,",dat[,6],",Pa,,,",sep="")
colnames(dat)<-c("Location","Date","Time","Head","Dec_year","Pressure","STOMP_BC")

write.csv(dat,file=paste("make_BC_",site[i],".csv",sep=""),row.names=FALSE)

}



