pltAWLNTS_Final <- function(x,y,OU,BOT,TOP,BOS,TOS,mindate=ISOdate(2017,01,01),maxdate=ISOdate(2019,12,31),ts='Monthly'){
  
  #--------------------------------------------------------------------------------------------------------------#
  #--User-defined x-axis grid--#
  dates <- c(as.Date(mindate),as.Date(maxdate))
  xaxt <- timeserieslim(dates,POSIXct=FALSE,ts=ts)
  if(ts == 'Yearly'){
    dates <- c(dates[1] - 365,dates[2] + 365)
    minor <- timeserieslim(dates,POSIXct=FALSE,ts='Monthly')
  }
  #--------------------------------------------------------------------------------------------------------------#

  #--------------------------------------------------------------------------------------------------------------#
  #--User-defined y-axis limits--#
  if(max(c(x$VAL_ORG,x$SSPAVAL)) - min(c(x$VAL_ORG,x$SSPAVAL)) < 1){
    yaxt <- linearloglim(c(x$VAL_ORG,x$SSPAVAL),log=FALSE,round=0.1,seq=0.1)
  } else {
    yaxt <- linearloglim(c(x$VAL_ORG,x$SSPAVAL),log=FALSE,round=1,seq=1)
  }
  #--------------------------------------------------------------------------------------------------------------#
  
  #--------------------------------------------------------------------------------------------------------------#
  #--Plot Values by Color Based on Confidence Classification--#
  x$COLOR1 <- rgb(135,206,255,255,maxColorValue=255)
  y$COLOR1 <- rgb(160,32,240,255,maxColorValue=255)
  x$bg1 <- rgb(135,206,255,150,maxColorValue=255)
  y$bg1 <- rgb(160,32,240,150,maxColorValue=255)
  
  x$COLOR2 <- ifelse(x$VALID == FALSE,rgb(255,0,0,255,maxColorValue=255),
                     ifelse(x$ADJ_TYPE == 'No Adjustment',rgb(135,206,255,255,maxColorValue=255),
                            ifelse(x$ADJ_TYPE == 'Offset',rgb(124,205,124,255,maxColorValue=255),
                                   ifelse(x$ADJ_TYPE == 'Drift',rgb(255,255,0,255,maxColorValue=255),'black'))))
  y$COLOR2 <- ifelse(y$VALID == FALSE,rgb(255,165,0,255,maxColorValue=255),rgb(160,32,240,255,maxColorValue=255))
  x$bg2 <- ifelse(x$VALID == FALSE,rgb(255,0,0,150,maxColorValue=255),
                     ifelse(x$ADJ_TYPE == 'No Adjustment',rgb(135,206,255,150,maxColorValue=255),
                            ifelse(x$ADJ_TYPE == 'Offset',rgb(124,205,124,150,maxColorValue=255),
                                   ifelse(x$ADJ_TYPE == 'Drift',rgb(255,255,0,150,maxColorValue=255),'black'))))
  y$bg2 <- ifelse(y$VALID == FALSE,rgb(255,165,0,150,maxColorValue=255),rgb(160,32,240,150,maxColorValue=255))
  #--------------------------------------------------------------------------------------------------------------#
  
  #--------------------------------------------------------------------------------------------------------------#
  #--Set Manual Symbology by Data Source--#
  y$pch <- ifelse(y$Source == 'AWLN',22,24)
  #--------------------------------------------------------------------------------------------------------------#
  
  #--------------------------------------------------------------------------------------------------------------#
  #--New Plot Set-up--#
  layout(matrix(c(1,2,3),nrow=3,ncol=1),heights=c(1,4,4))
  #--------------------------------------------------------------------------------------------------------------#
  
  #--------------------------------------------------------------------------------------------------------------#
  #--Plot Title and Legend--#
  par(mar=c(0, 0, 0, 0))
  plot.new()
  title(x$NAME[1],line=-1)
  legend(x = "center",
         legend = c('AWLN: No Adjustment',
                    'AWLN: Offset Applied',
                    'AWNL: Drift Applied',
                    'AWLN: Rejected',
                    'AWLN: Original',
                    'Manual - AWLN',
                    'Manual - AWLN: Rejected',
                    'Manual - HEIS',
                    'Manual - HEIS: Rejected',
                    NA,NA,NA,NA,
                    'Well Screen'), 
         col= c(rgb(135,206,255,255,maxColorValue=255),
                rgb(124,205,124,255,maxColorValue=255),
                rgb(255,255,0,255,maxColorValue=255),
                rgb(255,0,0,255,maxColorValue=255),
                'grey54',
                rgb(160,32,240,255,maxColorValue=255),
                rgb(255,165,0,255,maxColorValue=255),
                rgb(160,32,240,255,maxColorValue=255),
                rgb(255,165,0,255,maxColorValue=255),
                NA,NA,NA,NA,'black'),
         pch = c(21,21,21,21,NA,22,22,24,24,NA,NA,NA,NA,22),
         lty = c(NA,NA,NA,NA,1,NA,NA,NA,NA,NA,NA,NA,NA,NA),
         bty = "n",
         lwd = 1,
         cex = 0.8,
         pt.bg = c(rgb(135,206,255,150,maxColorValue=255),
                   rgb(124,205,124,150,maxColorValue=255),
                   rgb(255,255,0,150,maxColorValue=255),
                   rgb(255,0,0,150,maxColorValue=255),
                   NA,
                   rgb(160,32,240,150,maxColorValue=255),
                   rgb(255,165,0,150,maxColorValue=255),
                   rgb(160,32,240,150,maxColorValue=255),
                   rgb(255,165,0,150,maxColorValue=255),
                   NA,NA,NA,NA,'bisque'),
         pt.cex = 1,
         ncol = 3)
  #--------------------------------------------------------------------------------------------------------------#
  
  #--------------------------------------------------------------------------------------------------------------#
  #--Plot Original Data--#
  
    #--------------------------------------------------------------------------------------------------------------#
    #--Create Linear Timeseries Plot--#
    par(mar=c(1,5,3,1), mgp=c(1.8,0.3,0))
    plttimeseries(xaxt,yaxt,ylab='Water-Level (m amsl)',axis=FALSE,ts=ts)
    if(ts=='Yearly'){
      axis(1,at=minor,labels=NA,tck=1,col='white',lty=3)
      box()
    }
    text(as.Date(mindate),max(yaxt$range),'Original Dataset',pos=4, cex=0.7)
    #--------------------------------------------------------------------------------------------------------------#
    
    #--------------------------------------------------------------------------------------------------------------#
    #--Plot Rectangle for Screened Interval--#
    if(!is.na(BOS) & !is.na(TOS)){
      XMIN <- as.Date(mindate - 30*60*60*24)
      XMAX <- as.Date(mindate)
      rect(XMIN,BOS,XMAX,TOS,bg="white",col='bisque')
      rect(XMIN,BOS,XMAX,TOS,density=5,angle=0)
    }
    #--------------------------------------------------------------------------------------------------------------#
    
    #--------------------------------------------------------------------------------------------------------------#
    #--Plot Data Points--#
    points(as.Date(x$EVENT),x$VAL_ORG,pch=21,bg=x$bg1,col=x$COLOR1,cex=0.5)
    points(as.Date(y$EVENT),y$VAL_ORG,pch=y$pch,bg=y$bg1,col=y$COLOR1,cex=0.5)
    box()
    #--------------------------------------------------------------------------------------------------------------#
  #--------------------------------------------------------------------------------------------------------------#
  
  #--------------------------------------------------------------------------------------------------------------#
  #--Plot Adjusted Data--#
    
    #--------------------------------------------------------------------------------------------------------------#
    #--Reset y-axis limits--#
    if(OU == '100-HR-3-D' & max(x$VAL_ORG) > 121){
      yaxt <- linearloglim(c(min(c(x$VAL_ORG,x$SSPAVAL)),121),log=FALSE,round=1,seq=1)
      label <- 'Extreme Outliers Not Shown'
    } else if(OU == '100-HR-3-H' & max(x$VAL_ORG) > 119){
      yaxt <- linearloglim(c(min(c(x$VAL_ORG,x$SSPAVAL)),119),log=FALSE,round=1,seq=1)
      label <- 'Extreme Outliers Not Shown'
    } else if(OU == '100-KR-4' & max(x$VAL_ORG) > 127){
      yaxt <- linearloglim(c(min(c(x$VAL_ORG,x$SSPAVAL)),127),log=FALSE,round=1,seq=1)
      label <- 'Extreme Outliers Not Shown'
    } else if(x$NAME[1] == '699-37-47A'){
      yaxt <- linearloglim(c(121,122.5),log=FALSE,round=0.1,seq=0.1)
      label <- 'Extreme Outliers Not Shown'
    } else if(x$NAME[1] == '299-W13-1'){
      yaxt <- linearloglim(c(123,135),log=FALSE,round=1,seq=1)
      label <- 'Extreme Outliers Not Shown'
    } else if(x$NAME[1] == '299-W15-30'){
      yaxt <- linearloglim(c(134,138),log=FALSE,round=1,seq=1)
      label <- 'Extreme Outliers Not Shown'
    } else if(x$NAME[1] == '299-W15-32'){
      yaxt <- linearloglim(c(130,137),log=FALSE,round=1,seq=1)
      label <- 'Extreme Outliers Not Shown'
    } else if(x$NAME[1] == '299-W11-42'){
      yaxt <- linearloglim(c(133,136),log=FALSE,round=1,seq=1)
      label <- 'Extreme Outliers Not Shown'
    } else {
      label <- NA
    }
    #--------------------------------------------------------------------------------------------------------------#
    
    #--------------------------------------------------------------------------------------------------------------#
    #--Create Linear Timeseries Plot--#
    par(mar=c(5,5,0,1), mgp=c(1.8,0.3,0))
    plttimeseries(xaxt,yaxt,ylab='Water-Level (m amsl)',ts=ts)
    if(ts=='Yearly'){
      axis(1,at=minor,labels=NA,tck=1,col='white',lty=3)
      box()
    }
    text(as.Date(mindate),max(yaxt$range),'Adjusted Dataset',pos=4, cex=0.7)
    if(!is.na(label)){
      text(as.Date(maxdate),max(yaxt$range),label,pos=4, cex=0.7)
    }
    #--------------------------------------------------------------------------------------------------------------#
    
    #--------------------------------------------------------------------------------------------------------------#
    #--Plot Rectangle for Screened Interval--#
    if(!is.na(BOS) & !is.na(TOS)){
      XMIN <- as.Date(mindate - 30*60*60*24)
      XMAX <- as.Date(mindate)
      rect(XMIN,BOS,XMAX,TOS,bg="white",col='bisque')
      rect(XMIN,BOS,XMAX,TOS,density=5,angle=0)
    }
    #--------------------------------------------------------------------------------------------------------------#
    
    #--------------------------------------------------------------------------------------------------------------#
    #--Plot Data Points--#
    lines(as.Date(x$EVENT),x$VAL_ORG,col='grey54')
    points(as.Date(x$EVENT),x$SSPAVAL,pch=21,bg=x$bg2,col=x$COLOR2,cex=0.3)
    points(as.Date(y$EVENT),y$SSPAVAL,pch=y$pch,bg=y$bg2,col=y$COLOR2,cex=0.5)
    box()
    #--------------------------------------------------------------------------------------------------------------#
  #--------------------------------------------------------------------------------------------------------------#
    
}
