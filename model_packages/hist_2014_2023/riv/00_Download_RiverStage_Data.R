#---------------------------------------------------------------------------------#
#--Importing Data for Hanford Monthly Reports
#--By: Jonathan Kennel
#--Modified by: Erica DiFilippo (on 7/17/2014)
#---------------------------------------------------------------------------------#

#---------------------------------------------------------------------------------#
#--Load SSPA Package--#
library(data.table)
library(sspariverconvolve)
#---------------------------------------------------------------------------------#

#---------------------------------------------------------------------------------#
#--Set Working Directory--#
DIR <- 'C:/100HR3-Rebound/model_packages/hist_2014_2023/riv'
setwd(DIR)
#---------------------------------------------------------------------------------#

#---------------------------------------------------------------------------------#
#--New River Stage Calculation--#
#STAGE_new <- calcRiverStage(MIN15=FALSE, daily=TRUE)
STAGE_new <- calcRiverStage(MIN15=TRUE, daily=TRUE)
#---------------------------------------------------------------------------------#

#---------------------------------------------------------------------------------#
#--Load Old River Stage from 2020 P&T Report--#
load('Z:/1639_HANFORD_FY2021/66007-61_Annual_100_PnT_Report/0_Data/River Stage/RiverStage_01162021.RData')
#---------------------------------------------------------------------------------#

#---------------------------------------------------------------------------------#
#--Compare Datasets--#
dt_comp <- copy(STAGE_new)
dt_comp <- subset(dt_comp,select=c('EVENT','PRD','D_GAUGE'))
dt_comp <- dt_comp[year(EVENT) == 2020]

old_comp <- copy(STAGE)
old_comp <- subset(old_comp,select=c('EVENT','PRD','D_GAUGE'))
old_comp <- old_comp[year(EVENT) == 2020]
setnames(old_comp,c('PRD','D_GAUGE'),c('PRD_old','D_GAUGE_old'))

setkey(dt_comp,'EVENT')
setkey(old_comp,'EVENT')
dt_comp <- old_comp[dt_comp]

dt_comp$Difference <- dt_comp$D_GAUGE - dt_comp$D_GAUGE_old
dt_comp$PRD_diff <- dt_comp$PRD - dt_comp$PRD_old
mu <- mean(dt_comp$Difference)
mu2 <- mean(dt_comp$PRD_diff)
#---------------------------------------------------------------------------------#

#---------------------------------------------------------------------------------#
#--Save and Export Data--#
#write.table(STAGE_new,file=paste0(DIR,'/RiverStage_05092022_daily_hp_check.csv'),sep=',',row.names=FALSE)
write.table(STAGE_new,file=paste0(DIR,'/00_RiverStage_daily.csv'),sep=',',row.names=FALSE)
#write.table(dt_comp,file=paste0(DIR,'/RiverStageComparison_05092022.csv'),sep=',',row.names=FALSE)
#save(STAGE_new,file=paste0(DIR,'/RiverStage_05092022.RData'))
#save(dt_comp,file=paste0(DIR,'/RiverStageComparison_05092022.RData'))
#---------------------------------------------------------------------------------#
