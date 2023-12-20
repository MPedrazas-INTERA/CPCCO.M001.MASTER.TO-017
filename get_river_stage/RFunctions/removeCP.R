#===============================================================================
#' Remove Control Points
#'
#' @param CP
#' @param MAN
#' @param MDCP
#'
#' @return 
#'
#' @export
#' @import data.table
#===============================================================================

removeCP <- function(CP, MAN, MDCP){
  CP  <- copy(CP)
  SD  <- copy(MAN[, list(SD=sd(VAL)), by=NAME])
  setkey(SD, NAME)
  setkey(CP, NAME)
  CP  <- SD[CP]
  setkey(CP, SD)
  DIST   <- spDists(as.matrix(CP[,list(XCOORDS,YCOORDS)]))
  WHA <- 1
  for(i in 1:nrow(DIST)){
    WH <- which(DIST[i,] < MDCP)
    WHA <- c(WHA, min(WH))
  }
  WHA <- unique(WHA)
  return(CP[WHA])
}