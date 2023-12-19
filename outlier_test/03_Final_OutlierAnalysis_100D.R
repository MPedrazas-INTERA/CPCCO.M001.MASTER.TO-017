#--------------------------------------------------------------------------------------------------------------#
#--Performs Outlier Tests for AWLN and Manual Water-Level Data
#--Program created by: Erica DiFilippo
#-- Last run by hpham, 02/10/2022
#--------------------------------------------------------------------------------------------------------------#

#--------------------------------------------------------------------------------------------------------------#
#--Set working directory--#
#DIR <- 'c:/Users/hpham/OneDrive - INTERA Inc/projects/045_100AreaPT/t100areaPT/'
DIR <- 'd:/projects/CPCCO.M001.MASTER.TO-017/'

setwd(DIR)
#--------------------------------------------------------------------------------------------------------------#

#--------------------------------------------------------------------------------------------------------------#
#--Import R Libraries--#
library(data.table)
library(rgdal)
#--------------------------------------------------------------------------------------------------------------#

#--------------------------------------------------------------------------------------------------------------#
#--Import Raw Outlier Results--#
load('outlier_test/output//Raw_OutlierTests.Rdata')
#--------------------------------------------------------------------------------------------------------------#



#--Import Well Location and Screen Data--#
load('outlier_test/output/DATA_OUT.RData')

#--Import Well List--#
#WELLS <- AREA[OU %like% '100']
#WELLS <- WELLS[!OU == '1100-EM-1']

#--Combine AWLN Water-Levels with OU--#
#setkey(AWLN,'NAME')
#setkey(AREA,'NAME')
#AWLN2 <- AREA[AWLN]

#-----------------------------------------------------------------------------#
#--Remove Data not in River Corridor--#
#AWLN <- AWLN2[NAME %in% WELLS$NAME]
#-----------------------------------------------------------------------------#

#--Combine Mannual Water-Levels with OU--#
#setkey(MAN,'NAME')
#setkey(AREA,'NAME')
#MAN2 <- AREA[MAN]

#-----------------------------------------------------------------------------#
#--Remove Data not in River Corridor--#
#MAN <- MAN2[NAME %in% WELLS$NAME]
#-----------------------------------------------------------------------------#





#--------------------------------------------------------------------------------------------------------------#
#--Import Manual Adjustments from 2006 to 2021--# hpham
OUT <- fread('outlier_test/input/ManualAdjustmentsandOutliers_2006_2021.csv')
#--------------------------------------------------------------------------------------------------------------#

#--------------------------------------------------------------------------------------------------------------#
#--Adjust Dates for Manual Outliers--#
OUT$S_EVENT <- as.POSIXct(OUT$S_EVENT,format='%m/%d/%Y %H:%M', tz="GMT")
OUT$E_EVENT <- as.POSIXct(OUT$E_EVENT,format='%m/%d/%Y %H:%M', tz="GMT")
OUT$ADJ <- as.numeric(OUT$ADJ)
#--------------------------------------------------------------------------------------------------------------#

#--------------------------------------------------------------------------------------------------------------#
#--Set-up Final Data Structure--#
AWLN <- WLOUT$AWLN_OUT
MAN <- WLOUT$MAN_OUT

setnames(AWLN,'VAL','VAL_ORG')
setnames(MAN,'VAL','VAL_ORG')

AWLN$CONFIDENCE_ADJ <- AWLN$CONFIDENCE
AWLN$ADJ <- 0
AWLN$ADJ_TYPE <- 'No Adjustment'
AWLN$SSPAVAL <- AWLN$VAL_ORG
AWLN$MAPUSE <- ifelse(AWLN$CONFIDENCE %in% c('HIGH','ABSOLUTE'),TRUE,FALSE)
AWLN$VALID <- ifelse(AWLN$CONFIDENCE %in% c('HIGH','ABSOLUTE'),TRUE,FALSE)

MAN$CONFIDENCE_ADJ <- MAN$CONFIDENCE
MAN$ADJ <- 0
MAN$ADJ_TYPE <- 'No Adjustment'
MAN$SSPAVAL <- MAN$VAL_ORG
MAN$MAPUSE <- ifelse(MAN$CONFIDENCE %in% c('HIGH','ABSOLUTE'),TRUE,FALSE)
MAN$VALID <- ifelse(MAN$CONFIDENCE %in% c('HIGH','ABSOLUTE'),TRUE,FALSE)
#--------------------------------------------------------------------------------------------------------------#

#--------------------------------------------------------------------------------------------------------------#
#--Remove Erroneous Values--#
AWLN$SSPAVAL <- ifelse(AWLN$SSPAVAL < 0,NA,AWLN$SSPAVAL)
AWLN <- AWLN[!is.na(SSPAVAL)]
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
  SUB <- SUB[ROW,VALID := MAN_OUT$VALID[i]]
  
  if(MAN_OUT$CONFIDENCE[i] %in% c('ABSOLUTE','HIGH')){
    SUB <- SUB[ROW,MAPUSE := TRUE]
  } else {
    SUB <- SUB[ROW,MAPUSE := FALSE]
  }
  
  if(!is.na(MAN_OUT$ADJ[i])){
    SUB <- SUB[ROW,ADJ := MAN_OUT$ADJ[i]]
    SUB <- SUB[ROW,SSPAVAL := VAL_ORG + ADJ]
    SUB <- SUB[ROW,MAPUSE := TRUE]
    SUB <- SUB[ROW,ADJ_TYPE := 'Offset']
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
    SUB <- SUB[ROW,VALID := TRUE]
    SUB <- SUB[ROW,ADJ_TYPE := 'Offset']
    
  } else {
    
    SUB <- SUB[ROW,CONFIDENCE_ADJ := AWLN_OUT$CONFIDENCE[i]] 
    SUB <- SUB[ROW,VALID := AWLN_OUT$VALID[i]] 
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



#--------------------------------------------------------------------------------------------------------------#
#--Add Drift for 199-D2-11--#
start <- ISOdatetime(2018,07,10,00,00,00)

sub <- subset(AWLN,AWLN$NAME == '199-D2-11')
sub_man <- subset(MAN,MAN$NAME == '199-D2-11' & MAN$EVENT > start)
AWLN <- AWLN[!NAME == '199-D2-11']

row1 <- which(abs(sub_man$EVENT[1] - sub$EVENT) == min(abs(sub_man$EVENT[1] - sub$EVENT)))
row2 <- which(abs(sub_man$EVENT[nrow(sub_man)] - sub$EVENT) == min(abs(sub_man$EVENT[nrow(sub_man)] - sub$EVENT)))

x1 <- sub_man$SSPAVAL[1] - sub$VAL_ORG[row1]
x2 <- sub_man$SSPAVAL[nrow(sub_man)] - sub$VAL_ORG[row2]

fit <- lm(c(x1,x2) ~ as.numeric(c(sub_man$EVENT[1],sub_man$EVENT[nrow(sub_man)])))

slope <- as.numeric(fit$coefficients[2])
int <- as.numeric(fit$coefficients[1])

sub$ADJ <- ifelse(sub$EVENT >= start, (as.numeric(sub$EVENT) * slope) + int,sub$ADJ)
sub$ADJ_TYPE <- ifelse(sub$EVENT >= start,'Drift',sub$ADJ_TYPE)
sub$VALID <- ifelse(sub$EVENT >= start,TRUE,sub$VALID)
sub$SSPAVAL <- sub$VAL_ORG + sub$ADJ

AWLN <- rbind(AWLN,sub)
#--------------------------------------------------------------------------------------------------------------#



#--------------------------------------------------------------------------------------------------------------#
#--Add Drift for 199-D4-13--# (1st drift correction)
start <- ISOdatetime(2018,01,01,00,00,00)
end_date <- ISOdatetime(2019,10,25,10,00,00)

sub <- subset(AWLN,AWLN$NAME == '199-D4-13')
sub_man <- subset(MAN,MAN$NAME == '199-D4-13' & MAN$EVENT > start)
AWLN <- AWLN[!NAME == '199-D4-13']

row1 <- which(abs(sub_man$EVENT[1] - sub$EVENT) == min(abs(sub_man$EVENT[1] - sub$EVENT)))
#row2 <- which(abs(sub_man$EVENT[nrow(sub_man)] - sub$EVENT) == min(abs(sub_man$EVENT[nrow(sub_man)] - sub$EVENT)))
row2 <- which(abs(sub_man$EVENT[8] - sub$EVENT) == min(abs(sub_man$EVENT[8] - sub$EVENT)))

x1 <- sub_man$SSPAVAL[1] - sub$VAL_ORG[row1]
x2 <- sub_man$SSPAVAL[8] - sub$VAL_ORG[row2]

fit <- lm(c(x1,x2) ~ as.numeric(c(sub_man$EVENT[1],sub_man$EVENT[8])))

slope <- as.numeric(fit$coefficients[2])
int <- as.numeric(fit$coefficients[1])

sub$ADJ <- ifelse(sub$EVENT >= start & sub$EVENT <= end_date, (as.numeric(sub$EVENT) * slope) + int,sub$ADJ)
sub$ADJ_TYPE <- ifelse(sub$EVENT >= start& sub$EVENT <= end_date,'Drift',sub$ADJ_TYPE)
sub$VALID <- ifelse(sub$EVENT >= start& sub$EVENT <= end_date,TRUE,sub$VALID)
sub$SSPAVAL <- sub$VAL_ORG + sub$ADJ

AWLN <- rbind(AWLN,sub)
#--------------------------------------------------------------------------------------------------------------#


#--------------------------------------------------------------------------------------------------------------#
#--Add Drift for 199-D4-13--# (2nd time, hpham)
start <- ISOdatetime(2019,10,25,10,30,00)

sub <- subset(AWLN,AWLN$NAME == '199-D4-13')
sub_man <- subset(MAN,MAN$NAME == '199-D4-13' & MAN$EVENT > start)
AWLN <- AWLN[!NAME == '199-D4-13']

row1 <- which(abs(sub_man$EVENT[1] - sub$EVENT) == min(abs(sub_man$EVENT[1] - sub$EVENT)))
row2 <- which(abs(sub_man$EVENT[5] - sub$EVENT) == min(abs(sub_man$EVENT[5] - sub$EVENT)))

x1 <- sub_man$SSPAVAL[1] - sub$VAL_ORG[row1]
x2 <- sub_man$SSPAVAL[5] - sub$VAL_ORG[row2]

fit <- lm(c(x1,x2) ~ as.numeric(c(sub_man$EVENT[1],sub_man$EVENT[5])))

slope <- as.numeric(fit$coefficients[2])
int <- as.numeric(fit$coefficients[1])

sub$ADJ <- ifelse(sub$EVENT >= start , (as.numeric(sub$EVENT) * slope) + int,sub$ADJ)
sub$ADJ_TYPE <- ifelse(sub$EVENT >= start,'Drift',sub$ADJ_TYPE)
sub$VALID <- ifelse(sub$EVENT >= start,TRUE,sub$VALID)
sub$SSPAVAL <- sub$VAL_ORG + sub$ADJ

AWLN <- rbind(AWLN,sub)
#--------------------------------------------------------------------------------------------------------------#



#--------------------------------------------------------------------------------------------------------------#
#--Add Drift for 699-97-48B--#
start <- ISOdatetime(2015,10,01,00,00,00)

sub <- subset(AWLN,AWLN$NAME == '699-97-48B')
sub_man <- subset(MAN,MAN$NAME == '699-97-48B' & MAN$EVENT > start)
AWLN <- AWLN[!NAME == '699-97-48B']

row2 <- which(abs(sub_man$EVENT[nrow(sub_man)] - sub$EVENT) == min(abs(sub_man$EVENT[nrow(sub_man)] - sub$EVENT)))

x1 <- 0.25
x2 <- sub_man$SSPAVAL[nrow(sub_man)] - sub$VAL_ORG[row2]

fit <- lm(c(x1,x2) ~ as.numeric(c(sub_man$EVENT[1],sub_man$EVENT[nrow(sub_man)])))

slope <- as.numeric(fit$coefficients[2])
int <- as.numeric(fit$coefficients[1])

sub$ADJ <- ifelse(sub$EVENT >= start, (as.numeric(sub$EVENT) * slope) + int,sub$ADJ)
sub$ADJ_TYPE <- ifelse(sub$EVENT >= start,'Drift',sub$ADJ_TYPE)
sub$VALID <- ifelse(sub$EVENT >= start,TRUE,sub$VALID)
sub$SSPAVAL <- sub$VAL_ORG + sub$ADJ

AWLN <- rbind(AWLN,sub)
#--------------------------------------------------------------------------------------------------------------#




#--hpham added for testing
#sub_test <- subset(sub, sub$EVENT > ISOdatetime(2017,04,01,07,00,00)) # temp
#sub_test <- subset(sub, sub$EVENT > ISOdatetime(2019,1,1,07,00,00)) # temp

# hpham uncommented the below three lines
#sub$ADJ <- ifelse(sub$EVENT > ISOdatetime(2017,12,28,00,00,00),-0.3083,sub$ADJ)
#sub$ADJ_TYPE <- ifelse(sub$EVENT > ISOdatetime(2017,12,28,00,00,00),'Offset',sub$ADJ_TYPE)
#sub$SSPAVAL <- ifelse(sub$EVENT > ISOdatetime(2017,12,28,00,00,00),sub$ADJ + sub$VAL_ORG,sub$SSPAVAL)

row1 <- which(abs(sub_man$EVENT[7] - sub$EVENT) == min(abs(sub_man$EVENT[7] - sub$EVENT)))
row2 <- which(abs(sub_man$EVENT[15] - sub$EVENT) == min(abs(sub_man$EVENT[15] - sub$EVENT)))

x1 <- sub_man$SSPAVAL[7] - sub$SSPAVAL[row1]
x2 <- sub_man$SSPAVAL[15] - sub$SSPAVAL[row2]

fit <- lm(c(x1,x2) ~ as.numeric(c(sub_man$EVENT[7],sub_man$EVENT[15])))

slope <- as.numeric(fit$coefficients[2])
int <- as.numeric(fit$coefficients[1])

sub$ADJ <- ifelse(sub$EVENT > ISOdatetime(2017,12,28,00,00,00)& sub$EVENT < ISOdatetime(2019,12,21,00,00,00),(as.numeric(sub$EVENT) * slope) + int,0)
sub$ADJ_TYPE <- ifelse(sub$EVENT > ISOdatetime(2017,12,28,00,00,00)& sub$EVENT < ISOdatetime(2019,12,21,00,00,00),'Drift',sub$ADJ_TYPE)
sub$SSPAVAL <- ifelse(sub$EVENT > ISOdatetime(2017,12,28,00,00,00)& sub$EVENT < ISOdatetime(2019,12,21,00,00,00),sub$ADJ + sub$SSPAVAL,sub$SSPAVAL)
sub$VALID <- ifelse(sub$EVENT > ISOdatetime(2017,12,28,00,00,00)& sub$EVENT < ISOdatetime(2019,12,21,00,00,00),TRUE,sub$VALID)

# OK, got it. 
sub$MAPUSE <- ifelse(sub$EVENT > ISOdatetime(2019,12,21,00,00,00) & sub$EVENT < ISOdatetime(2020,12,31,00,00,00),FALSE,sub$MAPUSE)
sub$VALID <- ifelse(sub$EVENT > ISOdatetime(2019,12,21,00,00,00) & sub$EVENT < ISOdatetime(2020,12,31,00,00,00),FALSE,sub$VALID)
sub$ADJ_TYPE <- ifelse(sub$EVENT > ISOdatetime(2019,12,21,00,00,00) & sub$EVENT < ISOdatetime(2020,12,31,00,00,00),'No Adjustment',sub$ADJ_TYPE)

sub$ADJ <- sub$VAL_ORG - sub$SSPAVAL

AWLN <- rbind(AWLN,sub)
#--------------------------------------------------------------------------------------------------------------#




#--------------------------------------------------------------------------------------------------------------#
#--Combine Data--#
DATA <- list(AWLN=AWLN,
             MAN=MAN)
#--------------------------------------------------------------------------------------------------------------#




#--------------------------------------------------------------------------------------------------------------#
#--Save Dataset--#
t_start_save <- Sys.time()
save(DATA,file='outlier_test/output/DATA_FINAL.RData')
t_end_save <- Sys.time()
#--------------------------------------------------------------------------------------------------------------#


t_end - t_start
t_end_save - t_start_save






# -- Extract data for 100-A ----
# -- hpham added these lines 3/9/2022 -----------------------------------------#
#--Import Water-Level Data from HEIS and AWLN Databases--#
load('outlier_test/output/DATA_FINAL.RData')

#--Import Well Location and Screen Data--#
load('outlier_test/output/WELL.RData')

#--Import Well List--#
#WELLS <- AREA[OU %like% '100']
#WELLS <- WELLS[!OU == '1100-EM-1']

#--Combine AWLN Water-Levels with OU--#
#AWLN <- DATA$AWLN
#setkey(AWLN,'NAME')
##setkey(AREA,'NAME')
#AWLN2 <- AREA[AWLN]

#-----------------------------------------------------------------------------#
#--Remove Data not in River Corridor--#
#AWLN <- AWLN2[NAME %in% WELLS$NAME]
#-----------------------------------------------------------------------------#

#--Combine Mannual Water-Levels with OU--#
#MAN <- DATA$MAN
#setkey(MAN,'NAME')
#setkey(AREA,'NAME')
#MAN2 <- AREA[MAN]

#-----------------------------------------------------------------------------#
#--Remove Data not in River Corridor--#
#MAN <- MAN2[NAME %in% WELLS$NAME]

#-----------------------------------------------------------------------------#
#OUs <- c('100-HR-3-D', '100-HR-3-H','100-KR-4')
#AWLN <- AWLN[OU %in% OUs]
#MAN <- MAN[OU %in% OUs]

#--Combine Data--#
DATA <- list(AWLN=AWLN,
             MAN=MAN)
#--Save Dataset--#
#save(DATA,file='1a_AWLN_Outlier_Analysis/Output/DataPull_020222/DATA_FINAL_100Area.RData')

AWLN <- AWLN[EVENT >= ISOdatetime(2023,1,1,00,00,00)]
MAN <- MAN[EVENT >= ISOdatetime(2023,1,1,00,00,00)]



#-----------------------------------------------------------------------------#

#-- Generate offset table ----------------------------------------------------#

#load('1a_AWLN_Outlier_Analysis/Output/DataPull_020222/DATA_FINAL_100Area.RData')
Data_all <- rbind(AWLN,MAN)
#Data_all <- Data_all[OU %in% OUs]
data_offset <- Data_all[ADJ_TYPE=="Offset",list(NAME,EVENT,TYPE,SSPAVAL)]
#unique(Data_all$ADJ_TYPE)
#unique(Data_all$OU)

#AWLN <- DATA$AWLN[MAPUSE == TRUE, list(NAME,EVENT,TYPE,SSPAVAL)]


# -- Table B-4. AWLN Data Excluded Based on Outlier Tests ---------------------
AWLN_excluded <- AWLN[MAPUSE == FALSE,list(NAME,EVENT,TYPE,SSPAVAL)]

# -- Table B-5. Manual Water Level Data Excluded Based on Outlier Tests -------
MAN_excluded <- MAN[MAPUSE == FALSE,list(NAME,EVENT,TYPE,SSPAVAL)]

# -- Write table to csv files -------------------------------------------------
#run_ver <- 'v121923'
OUT <- paste("outlier_test/output/csv/", sep="")
write.table(data_offset,file=paste0(OUT,'offset_corrections.csv'),sep=',',row.names=FALSE)
write.table(AWLN_excluded,file=paste0(OUT,'AWLN_excluded.csv'),sep=',',row.names=FALSE)
write.table(MAN_excluded,file=paste0(OUT,'MAN_excluded.csv'),sep=',',row.names=FALSE)




