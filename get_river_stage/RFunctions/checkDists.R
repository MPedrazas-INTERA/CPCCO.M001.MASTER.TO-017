#===============================================================================
#' Check Distance to Control Points
#'
#' @param X
#' @param MD
#'
#' @return 
#'
#' @export
#' @import data.table
#===============================================================================

checkDists <-function(X, MD=500){
  Z <- copy(X)  
  
  CP   <- Z[which(Z$TYPE=='CP')]
  OTH  <- Z[which(Z$TYPE!='CP')]
  
  P1 <- as.matrix(CP[,list(XCOORDS,YCOORDS)])
  P2 <- as.matrix(OTH[,list(XCOORDS,YCOORDS)])
  
  DISTS <- spDists(P1, P2, longlat=FALSE)
  
  return(rbind(OTH,CP[-which(rowMins(DISTS) < MD)]))
  
}