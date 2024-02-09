#-----------------------------------------------------------------------------#
#--River Control Points
#--By: E.DiFilippo
#--Modified on: 2/12/2021
#-- Last run by hpham, 01/28/2022
#-- 06/06/2023: Run for CY2022 calc
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#--Set Working Directory--#
#DIR <- 'c:/Users/hpham/OneDrive - INTERA Inc/projects/045_100AreaPT/t100areaPT/'
#DIR <- 's:/AUS/CHPRC.C003.HANOFF/Rel.044/045_100AreaPT/t100areaPT/'
DIR <- 'd:/projects/CPCCO.M001.MASTER.TO-017/get_river_stage/'

setwd(DIR)
#-----------------------------------------------------------------------------#
# --Specify a year for mapping -----------------------------------------------#
yr <- 2023

#-----------------------------------------------------------------------------#
#--Import R Libraries--#
library(data.table)
library(raster)
library(reshape2)
library(rgeos)
library(sp)
library(tidyr)
library(meuk2)
library(sspariverconvolve)
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#--Import User-Defined Functions--#
source('RFunctions/calcStageInterp.R')
source('RFunctions/calcRiverStage0.R')
source('RFunctions/ogata_predict0.R')


#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#--Import River Control Point Data--#
PTS <- fread('input/RiverPoints.csv') # hpham?
INTERP <- fread('input/interpfactor.csv') #hpham? 
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#--Calculate River Stage--#
#STAGE <- calcRiverStage(daily=TRUE) # Do not use, RS at D is 0.6 m higher. 
STAGE <- calcRiverStage0(daily=TRUE) # hpham modified
#write.csv(STAGE, file='0_Data/River_Stage/RiverStage_v051722.csv', row.names=FALSE)
write.csv(STAGE, file='output/RiverStage_v020624.csv', row.names=FALSE)

ofile <- paste('output/RiverStage_CY', yr ,'_v121923.Rdata',sep="")
save(STAGE,file=paste0(DIR,ofile))
#-----------------------------------------------------------------------------#




#-----------------------------------------------------------------------------#
#--Linear Interpolation of River Stage--#
STAGE2 <- subset(STAGE,select=c('EVENT','B_GAUGE','K_GAUGE','N_GAUGE','D_GAUGE','H_GAUGE','F_GAUGE','T_GAUGE'))

PRD <- subset(STAGE,select=c('EVENT','PRD'))
RS <- CalcStageInterp(STAGE2,PRD,PTS,INTERP)

# Extract river stage for RIV package (hpham) ----------------------------------
#STAGE3 <- subset(STAGE,select=c('EVENT','T_GAUGE','F_GAUGE','H_GAUGE','D_GAUGE','N_GAUGE','K_GAUGE','B_GAUGE','PRD'))
#STAGE3 <- STAGE3[year(EVENT) == yr]
                 


#RSSUB_RIV <- subset(RS,YYYY == yr & RSCP %in% c(2750, 3086))
#RSSUB_RIV <- RSSUB_RIV[order(RSCP),]


# end RIV river stage extraction ----------------------------------------------#

#-----------------------------------------------------------------------------#
#--Point Indexes to Keep Manually Chosen--# hpham? 
IDS <- c(1,55,480,610,701,787,960,1025,1245,1493,1664,1766,1801,1874,1890,1922,
         1995,2050,2131,2190,2313,2440,2495,2680,2815,2910,3006,3120,3159,3205,3320,
         3384,3419,3500,3602,3623,3676,3725,3789,3878,3986,4053,4300,4616)
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#--Create Empty Table--#
SUM <- NULL  
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#--Loop through each Month--#
for(i in 1:12){
  
  #-----------------------------------------------------------------------------#
  #--Subset Data by Year and Month--#
  RSSUB <- subset(RS,YYYY == yr & MON == i)
  #-----------------------------------------------------------------------------#
  
  
  
  #-----------------------------------------------------------------------------#
  #--Loop through each control point identified--#
  for(j in 1:(length(IDS)-1)){
    
    #-----------------------------------------------------------------------------#
    #--Extract Start and End Values for Control Points and Lines--#
    S <- subset(RSSUB,RSCP == IDS[j])
    E <- subset(RSSUB,RSCP == (IDS[j+1] - 1))
    #-----------------------------------------------------------------------------#
    
    #-----------------------------------------------------------------------------#
    #--Calculate the Mean River Stage for the Segment--#
    D <- mean(RSSUB$RS[IDS[j]:(IDS[j+1] - 1)])
    #-----------------------------------------------------------------------------#
    
    #-----------------------------------------------------------------------------#
    #--Create SUmmary Datatable--#
    SUB <- data.table(ID=j,
                      EVENT=i,
                      X1=S$XCOORDS,
                      X2=E$XCOORDS,
                      Y1=S$YCOORDS,
                      Y2=E$YCOORDS,
                      VAL=D)
    #-----------------------------------------------------------------------------#
    
    #-----------------------------------------------------------------------------#
    #--Combine with Previous Control points--#
    SUM <- rbind(SUM,SUB)
    #-----------------------------------------------------------------------------#
  }
  #-----------------------------------------------------------------------------#
  
}
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#--Reshape Datatable--#
SUM <- tidyr::spread(SUM, EVENT, VAL)
rownames(SUM) <- paste0('RIV', 1:NROW(SUM))
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#--Create Spatial Lines Object--#
TMP <- list()
for (i in 1:nrow(SUM)) {
  TMP[[i]] <-
    Lines(
      list(
        Line(matrix(c(SUM[[i,2]],SUM[[i,3]],SUM[[i,4]],SUM[[i,5]]),ncol=2))
      ),
      ID=paste0('RIV',i)
    )
}
ADD <- SpatialLines(TMP)
DAT <- data.frame(SUM[,(ncol(SUM)-11):ncol(SUM), with = FALSE],
                  row.names=paste0('RIV',1:NROW(SUM)))
setnames(DAT,names(DAT),as.character(1:12))
RIVER <- SpatialLinesDataFrame(SpatialLines(TMP), DAT)
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#--Create Clipping Grid (Some Points are Hard Coded)--#
BOUND <- Lines(
  list(
    Line(matrix(c(coordinates(RIVER)[[1]][[1]][1,1],
                  563781,576689,582146,591748,591748,
                  coordinates(RIVER)[[nrow(RIVER)]][[1]][2,1],
                  coordinates(RIVER)[[1]][[1]][1,2],
                  132236,132236,124785,118864,109422,
                  coordinates(RIVER)[[nrow(RIVER)]][[1]][2,2]),ncol=2))
  ),
  ID=paste0('CLIP',1)
)

BOUND <- SpatialLines(list(BOUND))
BOUND <- rbind(ADD, BOUND)
BOUND <- gLineMerge(BOUND)
LINELIST <- slot(BOUND, "lines")
BOUND <- SpatialPolygons(lapply(LINELIST, function(x) {
  Polygons(list(Polygon(slot(slot(x, "Lines")[[1]], "coords"))),
           ID=slot(x, "ID"))
}))
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#--Create River Data.table--#
RIVERDF <- linesToDataTable(RIVER)
RIVERDF$NAME <- paste0('RIV_CP_', sprintf("%02d", 1:NROW(RIVERDF)))
RIVERDF$TERM <- 1:NROW(RIVERDF)
RIVERDF <- as.data.table(copy(gather(RIVERDF, EVENT, VAL, -c(X1,X2,Y1,Y2,NAME,TERM))))
RIVERDF$EVENT <- as.numeric(RIVERDF$EVENT)
RIVERDF[, GROUP := 1]
RIVERDF[, VAL := 1]
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#--Write the River Shapefile--#
writeOGR(RIVER, "00_Data/River_Control_Points/Runs_060623", "RIVER_2022", driver="ESRI Shapefile",overwrite=TRUE)
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#--Write Boundary Shapefiles--#
writeOGR(SpatialPolygonsDataFrame(BOUND, data.frame(IN=1)),
         "00_Data/River_Control_Points/Runs_060623", "RIVER_CLIP_2022", driver="ESRI Shapefile",overwrite=TRUE)
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#--Write River Lines Dataset--#
write.csv(RIVERDF, file='00_Data/River_Control_Points/Runs_060623/RIVER_2022.csv', row.names=FALSE)
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#--Calculate the River Stages for Conrtold Points--#
RP <- data.table(as.data.frame(RIVER), NAME=paste0('RIV_CP_', sprintf("%02d", 1:NROW(RIVER))))
RP$XCOORDS <- sapply(coordinates(RIVER), function(X){
  mean(X[[1]][,1])
})
RP$YCOORDS <- sapply(coordinates(RIVER), function(X){
  mean(X[[1]][,2])
})
RP <- as.data.table(copy(gather(RP, EVENT, VAL, -c(NAME,XCOORDS,YCOORDS))))
RP$EVENT <- as.numeric(RP$EVENT)
RP <- RP[,TYPE:='RIV_CP']
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
#--Write River Control Points--#
write.csv(RP, file='output/RIVER_POINTS_2023.csv', row.names=FALSE)
#-----------------------------------------------------------------------------#

