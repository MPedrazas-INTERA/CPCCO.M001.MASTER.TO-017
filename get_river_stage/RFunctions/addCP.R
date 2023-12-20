#===============================================================================
#' Add Control Points
#'
#' @param EV 
#' @param MANALL
#' @param SDCUT
#'
#' @return 
#'
#' @export
#' @import data.table
#===============================================================================

addCP <- function(EV, MANALL, SDCUT=1.0, YYYY=2014){
  
  # TEMPORAL GAP FILLING
  # CALCULATE THE WATER LEVEL STANDARD DEVIATION FOR EACH WELL FROM THE MANUAL MEASUREMENTS
  SD <- MANALL[,list(DEV=sd(VAL),
                     LEN=length(VAL)), by=NAME]
  
  # SELECT ONLY WELLS WITH LOW SD 
  LOWSD <- SD[DEV <= SDCUT & LEN >= 5, list(NAME)]
  
  # SELECT THE CURRENT YEAR
  MANADD <- MANALL[year(EVENT) == YYYY]
  
  # DON'T USE VALUES FROM THE CURRENT MONTH: THESE ARE NOT CONTROL POINTS
  MANADD[, EVENT:=month(EVENT)]
  MANADD <- MANADD[EVENT != EV]
  
  # CALCULATE THE NUMBER OF MONTHS DIFFERENT
  MANADD[, DT:=abs(EVENT-EV)]
  
  # FIND THE CLOSEST VALUE TO THE CURRENT MONTH
  getClosest <- function(DATA, NM){
    DATA[NAME==NM, ][which.min(DT)]    
  }
  
  LOWSD <- LOWSD[, getClosest(MANADD,NAME), by=NAME]
  LOWSD[, NAME:=NULL]
  LOWSD[, DT:=NULL]
  LOWSD[, EVENT:=EV]
  LOWSD[, TYPE:="CP"]
  
  return(LOWSD)
}