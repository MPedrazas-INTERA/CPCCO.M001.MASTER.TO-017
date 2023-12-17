#--------------------------------------------------------------------------------------------------------------#
#--Performs Outlier Tests for AWLN and Manual Water-Level Data
#--Program created by: Erica DiFilippo
#-- Last run by hpham, 02/07/2022
#--------------------------------------------------------------------------------------------------------------#

#--------------------------------------------------------------------------------------------------------------#
#--Set working directory--#
#DIR <- 'c:/Users/hpham/OneDrive - INTERA Inc/projects/045_100AreaPT/t100areaPT/'
#DIR <- 's:/AUS/CHPRC.C003.HANOFF/Rel.044/045_100AreaPT/d01_CY2021_datapack/'
#DIR <- 'c:/Users/hpham/Documents/100APT_CY22/'
DIR <- 'd:/projects/CPCCO.M001.MASTER.TO-017/'
setwd(DIR)

# c:\Users\hpham\Documents\100APT_CY22\00_Data\Well_Data\
#--------------------------------------------------------------------------------------------------------------#

#--------------------------------------------------------------------------------------------------------------#
#--Import R Libraries--#
library(data.table)
library(rgdal)
library(sspaHanfordMonthly)
#--------------------------------------------------------------------------------------------------------------#



#--------------------------------------------------------------------------------------------------------------#
# 
# #--Import Water-Level Data--#
# WL1 <- readManDB('0_Data/Water_Level_Data/DataPull_020222/qryManHEIS.txt')
# WL2 <- readManDB('0_Data/Water_Level_Data/DataPull_020222/qryManAWLN.txt')
# WL3 <- readAWLN('0_Data/Water_Level_Data/DataPull_020222/qryAWLNAWLN_1.txt')
# WL4 <- readAWLN('0_Data/Water_Level_Data/DataPull_020222/qryAWLNAWLN_2.txt')
# 
# head(WL2)
# head(WL3)
# 
# 
# #--------------------------------------------------------------------------------------------------------------#
# 
# 
# #--------------------------------------------------------------------------------------------------------------#
# #--Identify Data Sources--#
# WL1$Source <- 'HEIS'
# WL2$Source <- 'AWLN'
# WL3$Source <- 'AWLN'
# WL4$Source <- 'AWLN'
# #--------------------------------------------------------------------------------------------------------------#
# 
# #--------------------------------------------------------------------------------------------------------------#
# #--Combine Datasets--#
# WL <- rbind(WL1,WL2,WL3,WL4)
# head(WL)
# NAME      EVENT     VAL TYPE Source
# unique(WL$TYPE)
# # Take quite time to export the data. Do not do it!
# #write.csv(WL, file='0_Data/Water_Level_Data/WL_raw_check121223.csv', row.names=FALSE)

#--------------------------------------------------------------------------------------------------------------#


# hpham: read the processed data from py08a_plot_water_levels_100D.py
WL <- fread('scripts/output/water_level_data/obs_2021_Oct2023/measured_WLs_hourly_100D_reformatted.csv')

setnames(WL,'Date','EVENT')
setnames(WL,'ID','NAME')
setnames(WL,'Water Level (m)','VAL')

WL$VAL <- as.numeric(WL$VAL)

# REMOVE ENTRIES WITH NO VALUES
WL <- subset(WL,!is.na(WL$VAL))
WL$EVENT <- sub('EDT ', '', WL$EVENT)
WL$EVENT <- sub('EST ', '', WL$EVENT)

#WL$EVENT2 <- as.POSIXct(WL$EVENT, format = "%Y-%m-%d %H:%M:%S") 
EFORM='%m/%d/%Y %H:%M:%S'
WL$EVENT <- as.POSIXct(WL$EVENT, format=EFORM, tz='GMT')

#
#WL$TYPE <- 'XD'
WL$Source <- 'CPCCo'



#--------------------------------------------------------------------------------------------------------------#
#--Import Well Location And Screen Data--# 
WELL <- readWellHWIS('outlier_test/input/qryWellHWIS_07202023.txt')
ELEV <- readElevHWIS('outlier_test/input/qryElevHWIS.txt',WELL)
SCREEN <- readScreenHWIS('outlier_test/input/qryScreenHWIS.txt',W=copy(WELL),E=copy(ELEV))
ADJ_SCREEN <- fread('outlier_test/input/qry_AdjustedWellScreens.txt',sep='|')
save(WELL, ELEV, SCREEN, ADJ_SCREEN, file='outlier_test/output/WELL.RData')
#--------------------------------------------------------------------------------------------------------------#

#DIR <- 'c:/Users/hpham/Documents/100APT_CY22/'
#setwd(DIR)
#load('00_Data/Well_Data/WELL.RData')

#--------------------------------------------------------------------------------------------------------------#
#--Correct Screened Intervals--#
ADJ_SCREEN <- ADJ_SCREEN[!is.na(sspaScreenTopElevationUnique)]
ADJ_SCREEN <- subset(ADJ_SCREEN,select=c('WELL_NAME','sspaScreenTopElevationUnique','sspaScreenBottomElevationUnique'))
setnames(ADJ_SCREEN,names(ADJ_SCREEN),c('NAME','TOP','BOT'))

SCREEN <- SCREEN[!NAME %in% ADJ_SCREEN$WELL_NAME]
SCREEN <- rbind(SCREEN,ADJ_SCREEN)

# row1 <- which(SCREEN$NAME == '199-K-32A')
# row2 <- which(SCREEN$NAME == '199-K-36')
# 
# SCREEN$BOT[row1] <- 115.75
# SCREEN$TOP[row2] <- 123.48
# SCREEN$BOT[row2] <- 117.38
#--------------------------------------------------------------------------------------------------------------#

#--------------------------------------------------------------------------------------------------------------#
#--Import Well File--#
RK <- readOGR('outlier_test/input', 'rivKrigeHigh')
#--------------------------------------------------------------------------------------------------------------#

#--------------------------------------------------------------------------------------------------------------#
#--Import Manual Adjustments from 2015-2017--#
OUT <- fread('outlier_test/input/ManualAdjustmentsandOutliers_2006_2021.csv')
#--------------------------------------------------------------------------------------------------------------#

#--------------------------------------------------------------------------------------------------------------#
#--Adjust Dates for Manual Outliers--#
OUT$S_EVENT <- as.POSIXct(OUT$S_EVENT,format='%m/%d/%Y %H:%M', tz="GMT")
OUT$E_EVENT <- as.POSIXct(OUT$E_EVENT,format='%m/%d/%Y %H:%M', tz="GMT")
OUT$ADJ <- as.numeric(OUT$ADJ)
#--------------------------------------------------------------------------------------------------------------#

#--------------------------------------------------------------------------------------------------------------#
#--Extract Coordinates--#
COORDS <- writeWell(WELL, SCREEN, ELEV, RK, OUT=paste0(DIR,'outlier_test/output'))
#--------------------------------------------------------------------------------------------------------------#



#WL$TYPE[4] = 'MAN'
#WL$TYPE[5:8] = 'MAN'
#--------------------------------------------------------------------------------------------------------------#
#--Outlier Tests--# memory.limit(9999999999)
WLOUT <- outliers(WL[TYPE=='XD'], WL[TYPE=='MAN'], 
                  SCREEN, 
                  ELEVBOT=ELEV, 
                  COORDS, 
                  DIR=paste0(DIR,'outlier_test/output/'),
                  MAXZ=2, 
                  ROLLING=FALSE, 
                  NROLLM=3, 
                  MAXRNG=5, 
                  MAXDISP=10,
                  NROLLA=49, 
                  MAXDATEDIST=3, 
                  ROLLSAFETY=50, 
                  MAXCOMPARE=0.1,
                  REMOVE=FALSE)





WLOUT$MAN_OUT$TYPE <- 'MAN'
#--------------------------------------------------------------------------------------------------------------#

#--------------------------------------------------------------------------------------------------------------#
#--Save Raw Outlier Results--#
save(WLOUT,file=paste0(DIR,'outlier_test/output//Raw_OutlierTests.Rdata'))
#--------------------------------------------------------------------------------------------------------------#



#--------------------------------------------------------------------------------------------------------------#
#--Set-up Final Data Structure--#
AWLN <- WLOUT$AWLN_OUT
MAN <- WLOUT$MAN_OUT




setnames(AWLN,'VAL','VAL_ORG')
setnames(MAN,'VAL','VAL_ORG')

AWLN$CONFIDENCE_ADJ <- AWLN$CONFIDENCE
AWLN$ADJ <- 0
AWLN$SSPAVAL <- AWLN$VAL_ORG
AWLN$MAPUSE <- ifelse(AWLN$CONFIDENCE %in% c('HIGH','ABSOLUTE'),TRUE,FALSE)

MAN$CONFIDENCE_ADJ <- MAN$CONFIDENCE
MAN$ADJ <- 0
MAN$SSPAVAL <- MAN$VAL_ORG
MAN$MAPUSE <- ifelse(MAN$CONFIDENCE %in% c('HIGH','ABSOLUTE'),TRUE,FALSE)
#--------------------------------------------------------------------------------------------------------------#

#--------------------------------------------------------------------------------------------------------------#
#--Remove Manual Manual Outliers--#
MAN_OUT <- OUT[TYPE=='MAN']
for (i in 1:nrow(MAN_OUT)){
  
  SUB <- MAN[NAME==MAN_OUT$NAME[i]]
  MAN <- MAN[!NAME==MAN_OUT$NAME[i]]
  
  start <- MAN_OUT$S_EVENT[i]
  end <-  MAN_OUT$E_EVENT[i]
  if(is.na(end)){
    end <- Sys.time()
    attributes(end)$tzone <- 'GMT'
  }
  
  ROW <- which(SUB$EVENT >= start & SUB$EVENT <= end)
  
  SUB <- SUB[ROW,CONFIDENCE_ADJ := MAN_OUT$CONFIDENCE[i]]
  
  if(MAN_OUT$CONFIDENCE[i] %in% c('ABSOLUTE','HIGH')){
    SUB <- SUB[ROW,MAPUSE := TRUE]
  } else {
    SUB <- SUB[ROW,MAPUSE := FALSE]
  }
  
  if(!is.na(MAN_OUT$ADJ[i])){
    SUB <- SUB[ROW,ADJ := MAN_OUT$ADJ[i]]
    SUB <- SUB[ROW,SSPAVAL := VAL_ORG + ADJ]
    SUB <- SUB[ROW,MAPUSE := TRUE]
  }
  
  MAN <- rbind(MAN,SUB)
  
}
#--------------------------------------------------------------------------------------------------------------#

#--------------------------------------------------------------------------------------------------------------#
#--Remove Manual AWLN Outliers--#
t_start <- Sys.time()
AWLN_OUT <- OUT[TYPE=='XD']
for (i in 1:nrow(AWLN_OUT)){
  
  SUB <- AWLN[NAME==AWLN_OUT$NAME[i]]
  AWLN <- AWLN[!NAME==AWLN_OUT$NAME[i]]
  
  start <- AWLN_OUT$S_EVENT[i]
  end <-  AWLN_OUT$E_EVENT[i]
  if(is.na(end)){
    end <- Sys.time()
    attributes(end)$tzone <- 'GMT'
  }
  
  ROW <- which(SUB$EVENT >= start & SUB$EVENT <= end)
  
  if(AWLN_OUT$CONFIDENCE[i] == 'ADJ'){
    
    SUB <- SUB[ROW,ADJ := AWLN_OUT$ADJ[i]]
    SUB <- SUB[ROW,SSPAVAL := VAL_ORG + ADJ]
    SUB <- SUB[ROW,MAPUSE := TRUE]
    
  } else {
    
    SUB <- SUB[ROW,CONFIDENCE_ADJ := AWLN_OUT$CONFIDENCE[i]] 
    if(AWLN_OUT$CONFIDENCE[i] %in% c('ABSOLUTE','HIGH')){
      SUB <- SUB[ROW,MAPUSE := TRUE]
    } else {
      SUB <- SUB[ROW,MAPUSE := FALSE]
    }
    
  }
  
  AWLN <- rbind(AWLN,SUB)
  
}
t_end <- Sys.time()
#--------------------------------------------------------------------------------------------------------------#

# #--------------------------------------------------------------------------------------------------------------#
# #--Edits to 199-N-147--#
# SUB <- AWLN[NAME == '199-N-147']
# AWLN <- AWLN[!NAME == '199-N-147']
# 
# SUB$CONFIDENCE_ADJ <- ifelse(SUB$SSPAVAL < 117.39,'NONE',SUB$CONFIDENCE_ADJ)
# SUB$MAPUSE <- ifelse(SUB$SSPAVAL < 117.39,FALSE,SUB$MAPUSE)
# AWLN <- rbind(AWLN,SUB)
# #--------------------------------------------------------------------------------------------------------------#
# 
# #--------------------------------------------------------------------------------------------------------------#
# #--Add Drift for 199-B5-8--#
# start <- ISOdatetime(2017,10,12,00,00,00)
# 
# sub <- subset(AWLN,AWLN$NAME == '199-B5-8')
# sub_man <- subset(MAN,MAN$NAME == '199-B5-8' & MAN$EVENT > start)
# AWLN <- AWLN[!NAME == '199-B5-8']
# 
# row1 <- which(abs(sub_man$EVENT[1] - sub$EVENT) == min(abs(sub_man$EVENT[1] - sub$EVENT)))
# row2 <- which(abs(sub_man$EVENT[nrow(sub_man)] - sub$EVENT) == min(abs(sub_man$EVENT[nrow(sub_man)] - sub$EVENT)))
# 
# x1 <- sub_man$SSPAVAL[1] - sub$SSPAVAL[row1]
# x2 <- sub_man$SSPAVAL[nrow(sub_man)] - sub$SSPAVAL[row2]
# 
# fit <- lm(c(x1,x2) ~ as.numeric(c(sub_man$EVENT[1],sub_man$EVENT[nrow(sub_man)])))
# 
# slope <- as.numeric(fit$coefficients[2])
# int <- as.numeric(fit$coefficients[1])
# 
# sub$ADJ <- ifelse(sub$EVENT >= start, (as.numeric(sub$EVENT) * slope) + int,sub$ADJ)
# sub$SSPAVAL <- sub$VAL_ORG + sub$ADJ
# 
# AWLN <- rbind(AWLN,sub)
# #--------------------------------------------------------------------------------------------------------------#
# 
# #--------------------------------------------------------------------------------------------------------------#
# #--Add Drift for 199-D4-13--#
# start <- ISOdatetime(2018,01,01,00,00,00)
# 
# sub <- subset(AWLN,AWLN$NAME == '199-D4-13')
# sub_man <- subset(MAN,MAN$NAME == '199-D4-13' & MAN$EVENT > start)
# AWLN <- AWLN[!NAME == '199-D4-13']
# 
# row1 <- which(abs(sub_man$EVENT[1] - sub$EVENT) == min(abs(sub_man$EVENT[1] - sub$EVENT)))
# row2 <- which(abs(sub_man$EVENT[nrow(sub_man)] - sub$EVENT) == min(abs(sub_man$EVENT[nrow(sub_man)] - sub$EVENT)))
# 
# x1 <- sub_man$SSPAVAL[1] - sub$VAL_ORG[row1]
# x2 <- sub_man$SSPAVAL[nrow(sub_man)] - sub$VAL_ORG[row2]
# 
# fit <- lm(c(x1,x2) ~ as.numeric(c(sub_man$EVENT[1],sub_man$EVENT[nrow(sub_man)])))
# 
# slope <- as.numeric(fit$coefficients[2])
# int <- as.numeric(fit$coefficients[1])
# 
# sub$ADJ <- ifelse(sub$EVENT >= start, (as.numeric(sub$EVENT) * slope) + int,sub$ADJ)
# sub$SSPAVAL <- sub$VAL_ORG + sub$ADJ
# 
# AWLN <- rbind(AWLN,sub)
# #--------------------------------------------------------------------------------------------------------------#
# 
# #--------------------------------------------------------------------------------------------------------------#
# #--Add Drift for 699-97-48B--#
# start <- ISOdatetime(2015,10,01,00,00,00)
# 
# sub <- subset(AWLN,AWLN$NAME == '699-97-48B')
# sub_man <- subset(MAN,MAN$NAME == '699-97-48B' & MAN$EVENT > start)
# AWLN <- AWLN[!NAME == '699-97-48B']
# 
# row2 <- which(abs(sub_man$EVENT[nrow(sub_man)] - sub$EVENT) == min(abs(sub_man$EVENT[nrow(sub_man)] - sub$EVENT)))
# 
# x1 <- 0.25
# x2 <- sub_man$SSPAVAL[nrow(sub_man)] - sub$VAL_ORG[row2]
# 
# fit <- lm(c(x1,x2) ~ as.numeric(c(sub_man$EVENT[1],sub_man$EVENT[nrow(sub_man)])))
# 
# slope <- as.numeric(fit$coefficients[2])
# int <- as.numeric(fit$coefficients[1])
# 
# sub$ADJ <- ifelse(sub$EVENT >= start, (as.numeric(sub$EVENT) * slope) + int,sub$ADJ)
# sub$SSPAVAL <- sub$VAL_ORG + sub$ADJ
# 
# AWLN <- rbind(AWLN,sub)
# #--------------------------------------------------------------------------------------------------------------#
# 
# #--------------------------------------------------------------------------------------------------------------#
# #--Add Drift for 199-H3-2B--#
# start <- ISOdatetime(2016,02,24,14,00,00)
# 
# sub <- subset(AWLN,AWLN$NAME == '199-H3-2B')
# sub_man <- subset(MAN,MAN$NAME == '199-H3-2B' & MAN$EVENT > start)
# AWLN <- AWLN[!NAME == '199-H3-2B']
# 
# sub$ADJ <- ifelse(sub$EVENT > ISOdatetime(2017,04,21,07,00,00) & sub$EVENT < ISOdatetime(2017,12,28,00,00,00),-0.3083,0)
# sub$SSPAVAL <- sub$VAL_ORG + sub$ADJ
# 
# row1 <- which(abs(sub_man$EVENT[1] - sub$EVENT) == min(abs(sub_man$EVENT[1] - sub$EVENT)))
# row2 <- which(abs(sub_man$EVENT[6] - sub$EVENT) == min(abs(sub_man$EVENT[6] - sub$EVENT)))
# 
# x1 <- sub_man$SSPAVAL[1] - 114.8323
# x2 <- sub_man$SSPAVAL[6] - sub$SSPAVAL[row2]
# 
# fit <- lm(c(x1,x2) ~ as.numeric(c(sub_man$EVENT[1],sub_man$EVENT[6])))
# 
# slope <- as.numeric(fit$coefficients[2])
# int <- as.numeric(fit$coefficients[1])
# 
# sub$ADJ <- ifelse(sub$EVENT >= start & sub$EVENT <= ISOdatetime(2017,12,28,00,00,00), (as.numeric(sub$EVENT) * slope) + int,0)
# sub$SSPAVAL <- sub$SSPAVAL + sub$ADJ
# 
# sub$ADJ <- ifelse(sub$EVENT > ISOdatetime(2017,12,28,00,00,00),-0.3083,sub$ADJ)
# sub$SSPAVAL <- ifelse(sub$EVENT > ISOdatetime(2017,12,28,00,00,00),sub$ADJ + sub$VAL_ORG,sub$SSPAVAL)
# 
# row1 <- which(abs(sub_man$EVENT[7] - sub$EVENT) == min(abs(sub_man$EVENT[7] - sub$EVENT)))
# row2 <- which(abs(sub_man$EVENT[15] - sub$EVENT) == min(abs(sub_man$EVENT[15] - sub$EVENT)))
# 
# x1 <- sub_man$SSPAVAL[7] - sub$SSPAVAL[row1]
# x2 <- sub_man$SSPAVAL[15] - sub$SSPAVAL[row2]
# 
# fit <- lm(c(x1,x2) ~ as.numeric(c(sub_man$EVENT[7],sub_man$EVENT[15])))
# 
# slope <- as.numeric(fit$coefficients[2])
# int <- as.numeric(fit$coefficients[1])
# 
# sub$ADJ <- ifelse(sub$EVENT > ISOdatetime(2017,12,28,00,00,00),(as.numeric(sub$EVENT) * slope) + int,0)
# sub$SSPAVAL <- ifelse(sub$EVENT > ISOdatetime(2017,12,28,00,00,00),sub$ADJ + sub$SSPAVAL,sub$SSPAVAL)
# 
# sub$MAPUSE <- ifelse(sub$EVENT > ISOdatetime(2019,12,21,00,00,00),FALSE,sub$MAPUSE)
# 
# sub$ADJ <- sub$VAL_ORG - sub$SSPAVAL
# 
# AWLN <- rbind(AWLN,sub)
# #--------------------------------------------------------------------------------------------------------------#
# 
# #--------------------------------------------------------------------------------------------------------------#
# #--Add Drift for 199-K-111A--#
# sub <- subset(AWLN,AWLN$NAME == '199-K-111A')
# sub_man <- subset(MAN,MAN$NAME == '199-K-111A' & MAN$EVENT > ISOdatetime(2017,10,01,00,00,00))
# AWLN <- AWLN[!NAME == '199-K-111A']
# 
# row1 <- which(abs(sub_man$EVENT[1] - sub$EVENT) == min(abs(sub_man$EVENT[1] - sub$EVENT)))
# row2 <- which(abs(sub_man$EVENT[2] - sub$EVENT) == min(abs(sub_man$EVENT[2] - sub$EVENT)))
# 
# x1 <- sub_man$SSPAVAL[1] - sub$VAL_ORG[row1]
# x2 <- sub_man$SSPAVAL[2] - sub$VAL_ORG[row2]
# 
# fit <- lm(c(x1,x2) ~ as.numeric(c(sub_man$EVENT[1],sub_man$EVENT[2])))
# 
# slope <- as.numeric(fit$coefficients[2])
# int <- as.numeric(fit$coefficients[1])
# 
# sub$ADJ <- ifelse(sub$EVENT >= ISOdatetime(2017,10,29,12,00,00) & sub$EVENT <= sub_man$EVENT[2], (as.numeric(sub$EVENT) * slope) + int,sub$ADJ)
# sub$SSPAVAL <- sub$VAL_ORG + sub$ADJ
# 
# row1 <- which(abs(sub_man$EVENT[5] - sub$EVENT) == min(abs(sub_man$EVENT[5] - sub$EVENT)))
# row2 <- which(abs(sub_man$EVENT[11] - sub$EVENT) == min(abs(sub_man$EVENT[11] - sub$EVENT)))
# 
# # x1 <- sub_man$SSPAVAL[5] - sub$SSPAVAL[row1]
# x1 <- 0.2
# x2 <- sub_man$SSPAVAL[11] - sub$SSPAVAL[row2]
# 
# fit <- lm(c(x1,x2) ~ as.numeric(c(sub_man$EVENT[5],sub_man$EVENT[11])))
# 
# slope <- as.numeric(fit$coefficients[2])
# int <- as.numeric(fit$coefficients[1])
# 
# sub$ADJ <- ifelse(sub$EVENT >= ISOdatetime(2018,08,09,00,00,00),(as.numeric(sub$EVENT) * slope) + int,sub$ADJ)
# sub$SSPAVAL <- ifelse(sub$EVENT >= ISOdatetime(2018,08,09,00,00,00),sub$SSPAVAL + sub$ADJ,sub$SSPAVAL)
# 
# sub$SSPAVAL <- ifelse(sub$EVENT > ISOdatetime(2019,11,01,00,00,00),sub$VAL_ORG,sub$SSPAVAL)
# 
# AWLN <- rbind(AWLN,sub)
# #--------------------------------------------------------------------------------------------------------------#
# 
# #--------------------------------------------------------------------------------------------------------------#
# #--Add Drift for 199-K-142--#
# sub <- subset(AWLN,AWLN$NAME == '199-K-142')
# sub_man <- subset(MAN,MAN$NAME == '199-K-142' & MAN$EVENT > ISOdatetime(2017,10,01,00,00,00))
# AWLN <- AWLN[!NAME == '199-K-142']
# 
# x1 <- 0
# x2 <- 0.217289
# 
# fit <- lm(c(x1,x2) ~ as.numeric(c(ISOdatetime(2017,05,17,07,00,00),ISOdatetime(2018,01,01,00,00,00))))
# 
# slope <- as.numeric(fit$coefficients[2])
# int <- as.numeric(fit$coefficients[1])
# 
# sub$ADJ <- ifelse(sub$EVENT >= ISOdatetime(2017,05,17,07,00,00) & sub$EVENT <= ISOdatetime(2018,01,01,00,00,00), (as.numeric(sub$EVENT) * slope) + int,sub$ADJ)
# sub$SSPAVAL <- sub$VAL_ORG + sub$ADJ
# 
# AWLN <- rbind(AWLN,sub)
# #--------------------------------------------------------------------------------------------------------------#
# 
# #--------------------------------------------------------------------------------------------------------------#
# #--Add Drift for 199-N-34--#
# sub <- subset(AWLN,AWLN$NAME == '199-N-34')
# sub_man <- subset(MAN,MAN$NAME == '199-N-34' & MAN$EVENT > ISOdatetime(2017,01,01,00,00,00))
# AWLN <- AWLN[!NAME == '199-N-34']
# 
# row1 <- which(abs(sub_man$EVENT[1] - sub$EVENT) == min(abs(sub_man$EVENT[1] - sub$EVENT)))
# row2 <- which(abs(sub_man$EVENT[6] - sub$EVENT) == min(abs(sub_man$EVENT[6] - sub$EVENT)))
# row3 <- which(abs(sub_man$EVENT[nrow(sub_man)] - sub$EVENT) == min(abs(sub_man$EVENT[nrow(sub_man)] - sub$EVENT)))
# 
# x1 <- sub_man$SSPAVAL[1] - sub$VAL_ORG[row1]
# x2 <- sub_man$SSPAVAL[6] - sub$VAL_ORG[row2]
# x3 <- sub_man$SSPAVAL[nrow(sub_man)] - sub$VAL_ORG[row3]
# fit <- lm(c(0,0.2033) ~ as.numeric(c(ISOdatetime(2014,07,02,00,00,00),ISOdatetime(2016,12,21,00,00,00)))) # hpham
# #fit <- lm(c(0,0.2033),c(ISOdatetime(2014,07,02,00,00,00),ISOdatetime(2016,12,21,00,00,00))) # org did not work
# slope <- as.numeric(fit$coefficients[2])
# int <- as.numeric(fit$coefficients[1])
# sub$ADJ <- ifelse(sub$EVENT >= ISOdatetime(2014,07,02,00,00,00) & sub$EVENT < ISOdatetime(2017,01,01,00,00,00), (as.numeric(sub$EVENT) * slope) + int,0)
# 
# fit <- lm(c(x1,x2) ~ as.numeric(c(sub_man$EVENT[1],sub_man$EVENT[6])))
# 
# slope <- as.numeric(fit$coefficients[2])
# int <- as.numeric(fit$coefficients[1])
# 
# sub$ADJ <- ifelse(sub$EVENT >= ISOdatetime(2017,01,01,00,00,00) & sub$EVENT < ISOdatetime(2018,02,01,00,00,00), (as.numeric(sub$EVENT) * slope) + int,sub$ADJ)
# 
# fit <- lm(c(x2,x3) ~ as.numeric(c(sub_man$EVENT[6],sub_man$EVENT[nrow(sub_man)])))
# 
# slope <- as.numeric(fit$coefficients[2])
# int <- as.numeric(fit$coefficients[1])
# 
# sub$ADJ <- ifelse(sub$EVENT >= ISOdatetime(2018,02,01,00,00,00), (as.numeric(sub$EVENT) * slope) + int,sub$ADJ)
# 
# sub$ADJ <- ifelse(sub$EVENT >= ISOdatetime(2019,11,25,00,00,00),0,sub$ADJ)
# 
# sub$SSPAVAL <- sub$VAL_ORG + sub$ADJ
# 
# AWLN <- rbind(AWLN,sub)
# #--------------------------------------------------------------------------------------------------------------#

#--------------------------------------------------------------------------------------------------------------#
#--Combine Data--#
DATA <- list(AWLN=AWLN,
             MAN=MAN)
#--------------------------------------------------------------------------------------------------------------#

comb_WL <- rbind(AWLN, MAN)

# sort columns  
keycol <- c("NAME","EVENT")
#comb_WL_sorted <- comb_WL[order(match(names(comb_WL), column_order))]
#setorder(comb_WL, match(names(comb_WL), column_order))
comb_WL_sorted <- setorderv(comb_WL, keycol)

#plot(comb_WL_sorted$VAL_ORG)
#plot(comb_WL_sorted$SSPAVAL)
# Save to file
write.csv(comb_WL_sorted, file='outlier_test/output/WL_outlier_v121623.csv', row.names=FALSE)

# Write WL without outliers
comb_WL_sorted2  <- comb_WL_sorted[MAPUSE==TRUE]
comb_WL_sorted2 <- subset(comb_WL_sorted2, select= c('NAME', 'EVENT', 'SSPAVAL'))

#Change col names
setnames(comb_WL_sorted2,'EVENT','Date')
setnames(comb_WL_sorted2,'NAME','ID')
setnames(comb_WL_sorted2,'SSPAVAL','Water Level (m)')

write.csv(comb_WL_sorted2, file='outlier_test/output/WL_no_outlier_v121723.csv', row.names=FALSE)



