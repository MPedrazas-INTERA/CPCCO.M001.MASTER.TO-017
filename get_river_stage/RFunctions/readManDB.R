#===============================================================================
#' Read in manual measurements.  Uses fread for speed
#'
#' @param FILE the file name to read
#' @param EFORM the format for the dates (EVENT)
#'
#' @return the Manual data from AWLN database
#'
#' @export
#' @import data.table
#===============================================================================
readManDB <- function(FILE, EFORM='%m/%d/%Y %H:%M:%S'){

  # COLUMNS TO SELECT
  CLASS <- c('character','character','numeric','character')
  MAN <- fread(FILE, sep='|', header=TRUE,  colClasses=CLASS, stringsAsFactors=FALSE)

  N <- setdiff(names(MAN), c("WELL_ID", "TOC"))
  NM <- c("NAME","EVENT","VAL")
  MAN <- MAN[, N, with=FALSE]

  setnames(MAN, 1:3, NM)

  MAN$TYPE <- 'MAN'
  MAN <- subset(MAN,select=c('NAME', 'EVENT', 'VAL', 'TYPE'))

  if (any("REVIEW_QUALIFIER" %in% names(MAN))){
    MAN = subset(MAN,!MAN$REVIEW_QUALIFIER %in% c("R", "Z", "Y", "y"))
    MAN$REVIEW_QUALIFIER <- NULL
  }
  MAN$VAL <- as.numeric(MAN$VAL)

  # REMOVE ENTRIES WITH NO VALUES
  MAN <- subset(MAN,!is.na(MAN$VAL))
  MAN$EVENT <- sub('EDT ', '', MAN$EVENT)
  MAN$EVENT <- sub('EST ', '', MAN$EVENT)

  # CONVERT TO DATE FORMAT
  MAN$EVENT <- as.POSIXct(MAN$EVENT, format=EFORM, tz='GMT')

  return(MAN)
}
#===============================================================================