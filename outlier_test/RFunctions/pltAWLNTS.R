pltAWLNTS <- function(x,y,BOT,TOP,BOS,TOS,mindate=ISOdate(2017,01,01),maxdate=ISOdate(2019,12,31),ts='Monthly'){
  
  #--------------------------------------------------------------------------------------------------------------#
  #--User-defined x-axis grid--#
  dates <- c(as.Date(mindate),as.Date(maxdate))
  xaxt <- timeserieslim(dates,POSIXct=FALSE,ts=ts)
  if(ts == 'Yearly'){
    minor <- timeserieslim(dates,POSIXct=FALSE,ts='Monthly')
  }
  #--------------------------------------------------------------------------------------------------------------#

  #--------------------------------------------------------------------------------------------------------------#
  #--User-defined y-axis limits--#
  yaxt <- linearloglim(c(x$VAL_ORG,x$SSPAVAL),log=FALSE,round=1,seq=1)
  #--------------------------------------------------------------------------------------------------------------#
  
  #--------------------------------------------------------------------------------------------------------------#
  #--Plot Values by Color Based on Confidence Classification--#
  x$COLOR1 <- rgb(135,206,255,255,maxColorValue=255)
  y$COLOR1 <- rgb(160,32,240,255,maxColorValue=255)
  x$bg1 <- rgb(135,206,255,150,maxColorValue=255)
  y$bg1 <- rgb(160,32,240,150,maxColorValue=255)
  
  x$COLOR2 <- ifelse(!is.na(x$ADJ) & abs(x$ADJ) > 0 & x$MAPUSE == TRUE, rgb(124,205,124,255,maxColorValue=255),
                     ifelse(x$MAPUSE==TRUE,rgb(135,206,255,255,maxColorValue=255),rgb(255,0,0,255,maxColorValue=255)))
  y$COLOR2 <- ifelse(y$MAPUSE==TRUE,rgb(160,32,240,255,maxColorValue=255),rgb(255,165,0,255,maxColorValue=255))
  x$bg2 <- ifelse(!is.na(x$ADJ) & abs(x$ADJ) > 0  & x$MAPUSE== TRUE, rgb(124,205,124,150,maxColorValue=255),
                     ifelse(x$MAPUSE==TRUE,rgb(135,206,255,150,maxColorValue=255),rgb(255,0,0,255,maxColorValue=255)))
  y$bg2 <- ifelse(y$MAPUSE==TRUE,rgb(160,32,240,150,maxColorValue=255),rgb(255,165,0,150,maxColorValue=255))
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
         legend = c('AWLN',
                    'AWLN: Rejected',
                    'AWLN: Adjusted',
                    'AWLN: Original',
                    'Manual - AWLN',
                    'Manual - AWLN: Rejected',
                    'Manual - HEIS',
                    'Manual - HEIS: Rejected',
                    NA,NA,NA,
                    'Well Screen'), 
         col= c(rgb(135,206,255,255,maxColorValue=255),
                rgb(255,0,0,255,maxColorValue=255),
                rgb(124,205,124,255,maxColorValue=255),
                'grey54',
                rgb(160,32,240,255,maxColorValue=255),
                rgb(255,165,0,255,maxColorValue=255),
                rgb(160,32,240,255,maxColorValue=255),
                rgb(255,165,0,255,maxColorValue=255),
                NA,NA,NA,'black'),
         pch = c(21,21,21,NA,22,22,24,24,NA,NA,NA,22),
         lty = c(NA,NA,NA,1,NA,NA,NA,NA,NA,NA,NA,NA),
         bty = "n",
         lwd = 1,
         cex = 0.8,
         pt.bg = c(rgb(135,206,255,150,maxColorValue=255),
                   rgb(255,0,0,150,maxColorValue=255),
                   rgb(124,205,124,150,maxColorValue=255),
                   NA,
                   rgb(160,32,240,150,maxColorValue=255),
                   rgb(255,165,0,150,maxColorValue=255),
                   rgb(160,32,240,150,maxColorValue=255),
                   rgb(255,165,0,150,maxColorValue=255),
                   NA,NA,NA,'bisque'),
         pt.cex = 1,
         ncol = 3)
  #--------------------------------------------------------------------------------------------------------------#
  
  #--------------------------------------------------------------------------------------------------------------#
  #--Plot Orginal Data--#
  
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
    #--Create Linear Timeseries Plot--#
    par(mar=c(5,5,0,1), mgp=c(1.8,0.3,0))
    plttimeseries(xaxt,yaxt,ylab='Water-Level (m amsl)',ts=ts)
    if(ts=='Yearly'){
      axis(1,at=minor,labels=NA,tck=1,col='white',lty=3)
      box()
    }
    text(as.Date(mindate),max(yaxt$range),'Adjusted Dataset',pos=4, cex=0.7)
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
    #--Extract Data that have been adjusted--#
    # xsub <- subset(x,is.na(x$ADJ))
    # xsub <- xsub[order(EVENT),]
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
