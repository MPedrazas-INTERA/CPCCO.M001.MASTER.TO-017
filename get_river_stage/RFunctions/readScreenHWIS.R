#===============================================================================
#' Read in well screen info from the HWIS database.  Uses fread for speed.
#'
#' @param FILE the file name to read
#' @param W data.frame or data.table of Well ID and Well Name Data
#' @param E data.frame or data.table of Well Reference Elevations
#' 
#' @return the well screen info from HWIS database
#'
#' @export
#' @import data.table
#===============================================================================
readScreenHWIS <- function(FILE,W,E){
  
  #-----------------------------------------------------------------------------#
  #--Read in Screen Data--#
  S <- fread(FILE, sep='|', header=TRUE, stringsAsFactors=FALSE)
  #-----------------------------------------------------------------------------#
  
  #-----------------------------------------------------------------------------#
  #--Convert 0 Values to NA--#
  S$TOP <- ifelse(S$TOP==0,NA,S$TOP)
  S$BOT <- ifelse(S$BOT==0,NA,S$BOT)
  #-----------------------------------------------------------------------------#
  
  #-----------------------------------------------------------------------------#
  #--Find Lowest Screen for the Well--#
  S <- data.table(S)[,list(TOP = if(all(is.na(TOP))) NA else max(TOP, na.rm=TRUE),
                          BOT = if(all(is.na(BOT))) NA else max(BOT, na.rm=TRUE)),
                    by=c("WELL_ID")]
  #-----------------------------------------------------------------------------#
  
  #-----------------------------------------------------------------------------#
  #--Convert to Meters--#
  S$TOP <- S$TOP * 0.3048
  S$BOT <- S$BOT * 0.3048
  #-----------------------------------------------------------------------------#
  
  #-----------------------------------------------------------------------------#
  #--Convert Screen Depth to Elevation--#
  W <- copy(W)
  E <- copy(E)
  
  setkey(W,'WELL_ID')
  setkey(S,'WELL_ID')
  S <- W[S]
  
  setkey(S,'NAME')
  setkey(E,'NAME')
  S <- E[S]
  S$TOP <- S$REFCOORDS-S$TOP
  S$BOT <- S$REFCOORDS-S$BOT
  #-----------------------------------------------------------------------------#
  
  #-----------------------------------------------------------------------------#
  #--Subset Screen Data--#
  S <- subset(S,select=c('NAME','TOP','BOT'))
  #-----------------------------------------------------------------------------#
  
  return(S)
}
utils::globalVariables(c('TOP','BOT'))