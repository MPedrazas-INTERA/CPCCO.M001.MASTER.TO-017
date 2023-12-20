#===============================================================================
#' Read in AWLN data from the AWLN database.  Uses fread for speed. Coercion of
#' EVENT to date is the bottle neck.
#'
#' @param FILE the file name to read
#' @param EFORM the format for the dates (EVENT)
#'
#' @return the AWLN data
#'
#' @export
#' @import data.table
#===============================================================================
readAWLNAWLN <- function(FILE, EFORM='%m/%d/%Y %H:%M:%S'){

  AWLN <- fread(FILE, sep='|', header=TRUE, stringsAsFactors=FALSE)

  AWLN$VAL <- as.numeric(AWLN$VAL)

  # REMOVE ENTRIES WITH NO VALUES
  AWLN <- subset(AWLN,!is.na(AWLN$VAL))

  # CONVERT STRING TO DATE
  AWLN$EVENT <- as.POSIXct(AWLN$EVENT, format=EFORM, tz="GMT")

  return(AWLN)
}
#===============================================================================