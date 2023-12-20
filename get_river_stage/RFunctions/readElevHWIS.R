#===============================================================================
#' Read in well elevation info from the HWIS database.  Uses fread for speed.
#'
#' @param FILE the file name to read
#' @param WELL data.frame or data.table of Well ID and Well Name Data
#' 
#' @return the well elevation info from HWIS database
#'
#' @export
#' @import data.table
#===============================================================================
readElevHWIS <- function(FILE,WELL){
  
  #-----------------------------------------------------------------------------#
  #--Import Elevation Data--#
  E  <- fread(FILE, sep='|', header=TRUE, stringsAsFactors=FALSE)
  #-----------------------------------------------------------------------------#
  
  #-----------------------------------------------------------------------------#
  #--Rename Columns--#
  setnames(E, colnames(E), c('WELL_ID', "ELEVATION", "REFCOORDS"))
  #-----------------------------------------------------------------------------#
  
  #-----------------------------------------------------------------------------#
  #--Remove Zero Values--#
  E$REFCOORDS <- ifelse(E$REFCOORDS==0,NA,E$REFCOORDS)
  #-----------------------------------------------------------------------------#
  
  #-----------------------------------------------------------------------------#
  #--Convert Depth to Elevation--#
  setkey(WELL,'WELL_ID')
  setkey(E,'WELL_ID')
  E <- WELL[E]
  E$ELEVBOT <- E$REFCOORDS-E$TD
  #-----------------------------------------------------------------------------#
  
  #-----------------------------------------------------------------------------#
  #--Subset Screen Data--#
  E <- subset(E,select=c('NAME','ELEVBOT','REFCOORDS'))
  #-----------------------------------------------------------------------------#
  
  return(E)
}
#===============================================================================