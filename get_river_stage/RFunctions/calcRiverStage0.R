calcRiverStage0 <- function(OUT = NA,
         START = '1994-01-01',
         END = Sys.Date(),
         n = 80,
         int = 0.25,
         MIN15 = TRUE,
         daily=TRUE){
  
  #---------------------------------------------------------------------------------#
  #--Load Optimized Parameters--#
  PAR <- sspariverconvolve::PAR
  DIR <- 's:/AUS/CHPRC.C003.HANOFF/Rel.044/045_100AreaPT/t100areaPT/'
  ofile=paste(DIR,"0_Data/River_Stage/par15min_org_check.csv", sep="")
  #write.csv(PAR$`15-min`,file = ofile, append = TRUE)
  if(MIN15){
    PAR <- PAR$`15-min`
    #[0] B-River Gauge
    #PAR$`B-River Gauge`$`Subset 1`$MinDate <- '2007-10-1'
    #PAR$`B-River Gauge`$`Subset 1`$MaxDate <- '2010-11-14'
    #PAR$`B-River Gauge`$`Subset 1`$par <- c(86,6.57,9.15,0.862,118.5) #ecf
    
    #PAR$`B-River Gauge`$`Subset 2`$MinDate <- '2010-11-15'
    #PAR$`B-River Gauge`$`Subset 3`$MaxDate <- '2014-7-31'
    #PAR$`B-River Gauge`$`Subset 2`$par <- c(70.8,6.35,9.15,0.861,117.5)
    
    #[1] K-River
    #PAR$`K-River` <- c(45.7,6.22,12,0.887,116.6)
    
    #[2] N-River
    #PAR$`N-River Gauge`$`Subset 1`$par <- c(27.3,7.28,15.8,0.792,116.1)
    #PAR$`N-River Gauge`$`Subset 2`$par <- c(43.5,5.95,13.5,0.847,116.5)
    #PAR$`N-River Gauge`$`Subset 3`$par <- c(54.4,5.49,13.5,0.729,116.3)
    
    #[3] D-River
    PAR$`D-River Gauge`$`Subset 1`$MinDate <- '2007-10-01'
    PAR$`D-River Gauge`$`Subset 1`$MaxDate <- '2011-04-10'
    PAR$`D-River Gauge`$`Subset 1`$par <- c(42.8,6.68,15.3,0.679,116.2)
    
    PAR$`D-River Gauge`$`Subset 2`$MinDate <- '2011-04-11'
    PAR$`D-River Gauge`$`Subset 2`$MaxDate <- '2011-12-31'
    PAR$`D-River Gauge`$`Subset 2`$par <- c(63.2,6.79,15.3,0.686,116.2)
    
    PAR$`D-River Gauge`$`Subset 3`$MinDate <- '2012-01-01'
    PAR$`D-River Gauge`$`Subset 3`$MaxDate <- '2017-11-28'
    PAR$`D-River Gauge`$`Subset 3`$par <- c(53.5,7.56,15.3,0.675,115.6)
    
    #[4] H-River
    #PAR$`H-River Gauge`$`Subset 1`$par <- c(31.3,6.11,19.1,0.74,113.8)
    #PAR$`H-River Gauge`$`Subset 2`$par <- c(30.7,6.24,19.4,0.737,113.6)
    
    #[5] F-River
    #PAR$`F-River gauge`$`Subset 1`$par <- c(28.2,6.55,24.4,0.749,112)
    #PAR$`F-River gauge`$`Subset 2`$par <- c(29.1,6.39,22.5,0.779,111.3)
    #PAR$`F-River gauge`$`Subset 3`$par <- c(26.4,6.34,28.9,0.836,111.9)
    
    #[6] 300-River
    #PAR$`300-River gauge` <- c(43.25,5.14,50.643,0.531,104.1)    
  } else {
    #PAR <- PAR$Daily
    
    #[0] B-River Gauge
    #PAR$`B-River Gauge`$`Subset 1`$MinDate <- '2007-10-1'
    #PAR$`B-River Gauge`$`Subset 1`$MaxDate <- '2010-11-14'
    #PAR$`B-River Gauge`$`Subset 1`$par <- c(2064,157.68,8.65,0.82,120.2) #ecf
    
    #PAR$`B-River Gauge`$`Subset 2`$MinDate <- '2010-11-15'
    #PAR$`B-River Gauge`$`Subset 3`$MaxDate <- '2014-7-31'
    #PAR$`B-River Gauge`$`Subset 2`$par <- c(1699.2,152.4,9.65,0.84,119.3)
    
    #[1] K-River
    #PAR$`K-River` <- c(1096.8,149.28,9.65,0.85,118.4)
    
    #[2] N-River
    #PAR$`N-River Gauge`$`Subset 1`$par <- c(655.2,174.72,15.8,0.797,118)
    #PAR$`N-River Gauge`$`Subset 2`$par <- c(1044,142.32,14,0.782,118.3)
    #PAR$`N-River Gauge`$`Subset 3`$par <- c(1305.6,132,13,0.628,117.9)
    
    #[3] D-River
    #PAR$`D-River Gauge`$`Subset 1`$MinDate <- '2007-10-01'
    #PAR$`D-River Gauge`$`Subset 1`$MaxDate <- '2011-04-10'
    #PAR$`D-River Gauge`$`Subset 1`$par <- c(1027.2,160.56,14.8,0.637,117.6)

    #PAR$`D-River Gauge`$`Subset 2`$MinDate <- '2011-04-11'
    #PAR$`D-River Gauge`$`Subset 2`$MaxDate <- '2011-12-31'
    #PAR$`D-River Gauge`$`Subset 2`$par <- c(1519.2,100.08,15.8,0.68,117.6)
    
    #PAR$`D-River Gauge`$`Subset 3`$MinDate <- '2012-01-01'
    #PAR$`D-River Gauge`$`Subset 3`$MaxDate <- '2017-11-28'
    #PAR$`D-River Gauge`$`Subset 3`$par <- c(1284,180.96,15.8,0.646,117)
    
    #[4] H-River
    #PAR$`H-River Gauge`$`Subset 1`$par <- c(746.4,212.16,18.6,0.689,115.3)
    #PAR$`H-River Gauge`$`Subset 2`$par <- c(736.8,150,18.9,0.731,115.1)
    
    #[5] F-River
    #PAR$`F-River gauge`$`Subset 1`$par <- c(674.4,157.68,23.9,0.747,112.9)
    #PAR$`F-River gauge`$`Subset 2`$par <- c(698.4,153.6,22,0.761,112.9)
    #PAR$`F-River gauge`$`Subset 3`$par <- c(633.6,151.68,29.4,0.822,113.6)
    
    #[6] 300-River
    #PAR$`300-River Gauge` <- c(19536,3024,50.3,0.51,105.2)
    
    print(PAR$`D-River Gauge`$`Subset 2`$par)
  }
  #---------------------------------------------------------------------------------#
  DIR <- 's:/AUS/CHPRC.C003.HANOFF/Rel.044/045_100AreaPT/t100areaPT/'
  ofile=paste(DIR,"0_Data/River_Stage/par15min_mod_check.csv", sep="")
  paste()
  #write.csv(PAR,file = ofile, append = TRUE)
  
  
  #---------------------------------------------------------------------------------#
  #--Import River Stage Instanteous (15-min) Data--#
  START = '2007-1-1'
  END = Sys.Date()
  MIN15 = TRUE
  daily=TRUE
  n=80
  int=0.25
  RS <- downloadUSGSRS(START,END,SITE='12472800',PARAMETER='00065',MIN15=MIN15)
  #---------------------------------------------------------------------------------#
  
  #---------------------------------------------------------------------------------#
  #--Export Datasets--#
  DATE <- Sys.Date()
  if(is.na(OUT)){
    if(MIN15){
      FILE <- paste0('USGS_12472800_',DATE,'.txt')
    } else {
      FILE <- paste0('USGS_Daily_12472800_',DATE,'.txt')
    }
  } else {
    if(MIN15){
      FILE <- paste0(OUT,'USGS_12472800_',DATE,'.txt')
    } else {
      FILE <- paste0(OUT,'USGS_Daily_12472800_',DATE,'.txt')
    }
  }
  write.table(RS,FILE,sep='|',row.names=FALSE)
  #---------------------------------------------------------------------------------#
  
  #---------------------------------------------------------------------------------#
  #--Prepare and Lag Datasets--#
  x <- prepare_x(RS,n,x_name='INTERP')
  lagged <- prepare_lag_matrix( x, n )
  #---------------------------------------------------------------------------------#
  
  #---------------------------------------------------------------------------------#
  #--Set-up Empty List to Store Predicted River Stages for Each Gauge--#
  OB <- list()
  #---------------------------------------------------------------------------------#
  
  #---------------------------------------------------------------------------------#
  #--Loop through Each River Gauge--#
  for(i in 1:length(PAR)){
    
    #---------------------------------------------------------------------------------#
    #--Subset for River Gauge--#
    PAR_S <- PAR[[i]]
    #---------------------------------------------------------------------------------#
    
    #---------------------------------------------------------------------------------#
    #--Calculate River Stage For Each Parameterization Period--#
    if(class(PAR_S) == 'numeric'){
      
      #---------------------------------------------------------------------------------#
      #--Extract River Stage Name--#
      NM <- names(PAR)[i]
      #---------------------------------------------------------------------------------#
      
      #---------------------------------------------------------------------------------#
      #--Calculate River Stage--#
      pred <- ogata_predict0(PAR_S, x, y=NULL, lagged, n, int, predict=TRUE)
      #---------------------------------------------------------------------------------#
      
      #---------------------------------------------------------------------------------#
      #--Combine Predicted River Stage with Other River Gauge Data--#
      OB[[NM]] <- pred
      #---------------------------------------------------------------------------------#
      
    } else if(class(PAR_S) == 'list'){
      
      #---------------------------------------------------------------------------------#
      #--Extract River Stage Name--#
      NM <- names(PAR)[i]
      #---------------------------------------------------------------------------------#
      
      #---------------------------------------------------------------------------------#
      #--Set-up Empty List to STore Predicted River Stage--#
      pred_tot <- NULL
      #---------------------------------------------------------------------------------#
      
      #---------------------------------------------------------------------------------#
      #--Loop through Each Parameterization Period--#
      for (j in 1:length(PAR_S)){
        
        #---------------------------------------------------------------------------------#
        #--Extract Minimum Parameterization Period Date--#
        if(j == 1){
          MinDate <- as.Date(min(RS$datetime))
        } else {
          MinDate <- as.Date(PAR_S[[j-1]]$MaxDate) + 1
        }
        #---------------------------------------------------------------------------------#
        
        #---------------------------------------------------------------------------------#
        #--Extract Maximum Parameterization Period Date--#
        if(j == length(PAR_S)){
          MaxDate <- Sys.Date()
        } else {
          MaxDate <- as.Date(PAR_S[[j]]$MaxDate)
        }
        #---------------------------------------------------------------------------------#
        
        #---------------------------------------------------------------------------------#
        #--Calculate River Stage--#
        pred <- ogata_predict(PAR_S[[j]]$par, x, y=NULL, lagged, n, int, predict=TRUE)
        #---------------------------------------------------------------------------------#
        
        #---------------------------------------------------------------------------------#
        #--Subset Predicted Values Based on Min and Max Dates--#
        pred <- pred[as.Date(datetime) >= MinDate & as.Date(datetime) < MaxDate]
        #---------------------------------------------------------------------------------#
        
        #---------------------------------------------------------------------------------#
        #--Combine Predicted River Stage with other Parameterization Periods--#
        pred_tot <- rbind(pred_tot,pred)
        #---------------------------------------------------------------------------------#
        
      }
      #---------------------------------------------------------------------------------#
      
      #---------------------------------------------------------------------------------#
      #--Combine Predicted River Stage with Other River Gauge Data--#
      OB[[NM]] <- pred_tot
      #---------------------------------------------------------------------------------#
      
    }
    #---------------------------------------------------------------------------------#
    
  }
  #---------------------------------------------------------------------------------#
  
  if(daily){
    
    #---------------------------------------------------------------------------------#
    #--Subset PRD Dataset and Calculate Daily Average--#
    if(MIN15){
      RS$DATE <- as.Date(RS$datetime)
      RS_SUB <- data.table(RS)[,list(PRD=mean(INTERP)),by='DATE']
      setnames(RS_SUB,'DATE','EVENT')
    } else{
      setnames(RS,c('datetime','INTERP'),c('EVENT','PRD'))
      RS_SUB <- subset(RS,select=c('EVENT','PRD'))
    }
    #---------------------------------------------------------------------------------#
    
    #---------------------------------------------------------------------------------#
    #--Loop Through Each River Gauge--#
    for (k in 1:length(OB)){
      
      #---------------------------------------------------------------------------------#
      #--Extract River Gauge Name--#
      NM <- names(OB)[k]
      #---------------------------------------------------------------------------------#
      
      #---------------------------------------------------------------------------------#
      #--Create Column Name--#
      COLNM <- ifelse(NM %like% 'B','B_GAUGE',
                      ifelse(NM %like% 'K','K_GAUGE',
                             ifelse(NM %like% 'N','N_GAUGE',
                                    ifelse(NM %like% 'D','D_GAUGE',
                                           ifelse(NM %like% 'H','H_GAUGE',
                                                  ifelse(NM %like% 'F','F_GAUGE',
                                                         ifelse(NM %like% '300','T_GAUGE','VAL')))))))
      #---------------------------------------------------------------------------------#
      
      #---------------------------------------------------------------------------------#
      #--Calculate Daily Average River Stage--#
      SUB <- OB[[k]]
      SUB$EVENT <- as.Date(SUB$datetime)
      SUB <- data.table(SUB)[,list(VAL=mean(model,na.rm=TRUE)),by='EVENT']
      #---------------------------------------------------------------------------------#
      
      #---------------------------------------------------------------------------------#
      #--Combine Daily Average River Stage with Daily Average PRD--#
      setkey(SUB,'EVENT')
      setkey(RS_SUB,'EVENT')
      
      RS_SUB <- SUB[RS_SUB]
      #---------------------------------------------------------------------------------#
      
      #---------------------------------------------------------------------------------#
      #--Rename Colmns--#
      setnames(RS_SUB,'VAL',COLNM)
      #---------------------------------------------------------------------------------#
      
    }
    #---------------------------------------------------------------------------------#
    
  } else {
    
    #---------------------------------------------------------------------------------#
    #--Subset PRD Dataset--#
    RS_SUB <- subset(RS,select=c('datetime','INTERP'))
    setnames(RS_SUB,c('datetime','INTERP'),c('EVENT','PRD'))
    #---------------------------------------------------------------------------------#
    
    #---------------------------------------------------------------------------------#
    #--Combine Datasets--#
    for (k in 1:length(OB)){
      
      #---------------------------------------------------------------------------------#
      #--Extract River Gauge Name--#
      NM <- names(OB)[k]
      #---------------------------------------------------------------------------------#
      
      #---------------------------------------------------------------------------------#
      #--Create Column Name--#
      COLNM <- ifelse(NM %like% 'B','B_GAUGE',
                      ifelse(NM %like% 'K','K_GAUGE',
                             ifelse(NM %like% 'N','N_GAUGE',
                                    ifelse(NM %like% 'D','D_GAUGE',
                                           ifelse(NM %like% 'H','H_GAUGE',
                                                  ifelse(NM %like% 'F','F_GAUGE',
                                                         ifelse(NM %like% '300','T_GAUGE','VAL')))))))
      #---------------------------------------------------------------------------------#
      
      #---------------------------------------------------------------------------------#
      #--Combine River Stage with PRD Data--#
      SUB <- OB[[k]]
      SUB$EVENT <- SUB$datetime
      SUB <- subset(SUB,select=c('EVENT','model'))
      
      setkey(SUB,'EVENT')
      setkey(RS_SUB,'EVENT')
      
      RS_SUB <- SUB[RS_SUB]
      #---------------------------------------------------------------------------------#
      
      #---------------------------------------------------------------------------------#
      #--Rename Colmns--#
      setnames(RS_SUB,'model',COLNM)
      #---------------------------------------------------------------------------------#
      
    }
    #---------------------------------------------------------------------------------#
  }
  
  return(RS_SUB)
  
}
