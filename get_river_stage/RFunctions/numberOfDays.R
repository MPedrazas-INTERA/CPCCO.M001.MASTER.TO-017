#===============================================================================
#' Returns The Number of Days Per Month
#'
#' @param DATE is the date
#' 
#' @return Number of Days Per Month
#'
#' @export
#===============================================================================

numberOfDays <- function(DATE) {
  
  m <- month(DATE)
  
  while (month(DATE) == m){
    DATE <- DATE + 1
  }
  
  return(as.integer(format(DATE - 1, format="%d")))
}