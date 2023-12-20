#===============================================================================
#' Calculate River Stage at River Control Points
#'
#' @param STAGE data.table or data.frame of Measured River Stage Data
#' @param PRD data.table or data.frame of Measured Priest Rapids Dam Data
#' @param YEAR numeric vector of year of interest
#' @param MONTH numeric vector of month of interest
#'
#' @return data.table of river control points by year and month
#'
#' @export
#' @import reshape2
#===============================================================================
CalcStageInterp <- function(STAGE, PRD, PTS, INTERP, YEAR=NULL, MONTH=NULL){
  
  #---------------------------------------------------------------------------------#
  #--Reshape River Stage Dataset--#
  STAGE <- melt(STAGE,id = 'EVENT')
  setnames(STAGE,c('variable','value'),c('GAUGE','RS'))
  #---------------------------------------------------------------------------------#
  
  #---------------------------------------------------------------------------------#
  #--Calculate Average Monthly River Stage--#
  STAGE$MON <- month(STAGE$EVENT)
  STAGE$YYYY <- year(STAGE$EVENT)

  AVG <- data.table(STAGE)[,list(RS_MEAN=mean(RS)),
                           by=c('GAUGE','YYYY','MON')]
  #---------------------------------------------------------------------------------#

  #---------------------------------------------------------------------------------#
  #--Calculate Average Monthly River Stage at PRD--#
  PRD$MON <- month(PRD$EVENT)
  PRD$YYYY <- year(PRD$EVENT)

  PRDAVG <- data.table(PRD)[,list(RS_MEAN=mean(PRD)),
                            by=c('YYYY','MON')]
  PRDAVG$GAUGE <- 'PRD'
  PRDAVG <- subset(PRDAVG,select=c('GAUGE','YYYY','MON','RS_MEAN'))
  #---------------------------------------------------------------------------------#

  #---------------------------------------------------------------------------------#
  #--Add in Additional Control Points--#
  YR <- sort(unique(AVG$YYYY))
  MO <- sort(unique(AVG$MON))

  ADD <- NULL
  for(i in 1:length(YR)){

    SUB <- subset(AVG,AVG$YYYY == YR[i])

    for(j in 1:length(MO)){

      SUB2 <- subset(SUB,SUB$MON == MO[j])

      A <- data.table(GAUGE=c('2750','3086'))
      A$YYYY <- YR[i]
      A$MON <- MO[j]

      A$RS_MEAN <- ifelse(A$GAUGE=='2750',(0.940722 * SUB2[GAUGE=='F_GAUGE']$RS_MEAN) + (0.059278 * SUB2[GAUGE=='T_GAUGE']$RS_MEAN),
                            (0.550258 * SUB2[GAUGE=='F_GAUGE']$RS_MEAN) + (0.449742 * SUB2[GAUGE=='T_GAUGE']$RS_MEAN))
      ADD <- rbind(ADD,A)
    }

  }
  ADD <- subset(ADD,!is.na(ADD$RS_MEAN))
  #---------------------------------------------------------------------------------#

  #---------------------------------------------------------------------------------#
  #--Combined Datasets and Add Order--#
  AVG <- rbind(PRDAVG,AVG,ADD)
  AVG$ORDER <- ifelse(AVG$GAUGE == 'PRD',1,
                      ifelse(AVG$GAUGE == 'B_GAUGE',2,
                             ifelse(AVG$GAUGE == 'K_GAUGE',3,
                                    ifelse(AVG$GAUGE == 'N_GAUGE',4,
                                           ifelse(AVG$GAUGE == 'D_GAUGE',5,
                                                  ifelse(AVG$GAUGE == 'H_GAUGE',6,
                                                         ifelse(AVG$GAUGE == 'F_GAUGE',7,
                                                                ifelse(AVG$GAUGE == '2750',8,
                                                                       ifelse(AVG$GAUGE == '3086',9,10)))))))))
  #---------------------------------------------------------------------------------#

  #---------------------------------------------------------------------------------#
  #--If Year and Month Specified--#
  if(!is.null(YEAR) & !is.null(MONTH)){

    #---------------------------------------------------------------------------------#
    #--Subset Measured Gauge Data by Year and Month--#
    AVGSUB <- subset(AVG,AVG$YYYY == YEAR & AVG$MON == MONTH)
    AVGSUB <- AVGSUB[order(ORDER),]
    #---------------------------------------------------------------------------------#

    #---------------------------------------------------------------------------------#
    #--Calculate River Stage at Each Control Point using Interpolation Factor--#
    d <- c()
    for(i in 1:nrow(PTS)){

      NM <- paste0('V',i)
      INTERP_SUB <- INTERP[[NM]]
      d <- c(d,sum(AVGSUB$RS_MEAN * INTERP_SUB))

    }
    #---------------------------------------------------------------------------------#

    #---------------------------------------------------------------------------------#
    #--Combine Stage and Location Data--#
    CPS <- cbind(PTS,d)
    CPS <- subset(CPS, select=c(OID_REVISED,XCOORDS,YCOORDS,d))
    setnames(CPS,c('OID_REVISED','d'),c('RSCP','RS'))
    CPS$YYYY <- YEAR
    CPS$MON <- MONTH
    #---------------------------------------------------------------------------------#

  } else {

    #---------------------------------------------------------------------------------#
    #--Create Empty Table for All Control Points--#
    CPS <- NULL
    #---------------------------------------------------------------------------------#

    #---------------------------------------------------------------------------------#
    #--Loop through each year--#
    for(i in 1:length(YR)){

      #---------------------------------------------------------------------------------#
      #--Loop through each month--#
      for(j in 1:length(MO)){

        #---------------------------------------------------------------------------------#
        #--Subset Measured Gauge Data by Year and Month--#
        AVGSUB <- subset(AVG,AVG$YYYY == YR[i] & AVG$MON == MO[j])
        AVGSUB <- AVGSUB[order(ORDER),]
        #---------------------------------------------------------------------------------#

        #---------------------------------------------------------------------------------#
        #--Calculate River Stage at Each Control Point using Interpolation Factor--#
        d <- c()
        for(k in 1:nrow(PTS)){

          NM <- paste0('V',k)
          INTERP_SUB <- INTERP[[NM]]
          d <- c(d,sum(AVGSUB$RS_MEAN * INTERP_SUB))

        }
        #---------------------------------------------------------------------------------#

        #---------------------------------------------------------------------------------#
        #--Combine Stage and Location Data--#
        CPS_SUB <- cbind(PTS,d)
        CPS_SUB <- subset(CPS_SUB, select=c(OID_REVISED,XCOORDS,YCOORDS,d))
        setnames(CPS_SUB,c('OID_REVISED','d'),c('RSCP','RS'))
        CPS_SUB$YYYY <- YR[i]
        CPS_SUB$MON <- MO[j]
        #---------------------------------------------------------------------------------#

        #---------------------------------------------------------------------------------#
        #--Combine All Control Points--#
        CPS <- rbind(CPS,CPS_SUB)
        #---------------------------------------------------------------------------------#

      }
      #---------------------------------------------------------------------------------#

    }
    #---------------------------------------------------------------------------------#

  }
  #---------------------------------------------------------------------------------#

  return(CPS)
  
}