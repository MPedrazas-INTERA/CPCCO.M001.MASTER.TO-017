#===============================================================================
#' Read in well info from the HWIS database.  Uses fread for speed.
#'
#' @param FILE the file name to read
#' 
#' @return the well info from HWIS database
#'
#' @export
#' @import data.table
#===============================================================================
readWellHWIS <- function(FILE){
  
  # READ IN TABLE
  W  <- fread(FILE, sep='|', header=TRUE, stringsAsFactors=FALSE)
  
  # CONVERT TO METERS AND REMOVE VALUES THAT ARE 0 FOR THE BOTTOM OF THE HOLE
  W$TD <- ifelse(W$TD==0,NA,W$TD)
  W$BOH <- ifelse(W$BOH==0,NA,W$BOH)
  W$ZCOORDS <- ifelse(W$ZCOORDS==0,NA,W$ZCOORDS)
  W$TD  <- W$TD * 0.3048
  W$BOH <- W$BOH * 0.3048
  
#   W[TD == 0, TD := NA]
#   W[BOH == 0, BOH := NA]
#   W[ZCOORDS == 0, ZCOORDS := NA]
#   W[, TD := TD * 0.3048]
#   W[, BOH := BOH * 0.3048]
#   W[OU == "", OU := NA_character_]
  
  
  # CERTAIN WELLS HAVE THE WRONG OU ASSOCIATED WITH THEM AND NEED TO BE ADJUSTED
  W$OU <- ifelse(W$NAME %in% c('199-K-131','199-K-159','199-K-160','199-K-164'),'100-KR-4',W$OU)
  W$OU <- ifelse(W$NAME %in% c('299-W17-3'),'200-ZP-1',W$OU)
#   W[NAME %in% c('199-K-131','199-K-159','199-K-160','199-K-164'), OU:= '100-KR-4']
#   W[NAME %in% c('299-W17-3'), OU := '200-ZP-1']

  return(W)
}
#===============================================================================