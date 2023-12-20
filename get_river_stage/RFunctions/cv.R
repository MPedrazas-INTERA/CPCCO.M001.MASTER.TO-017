#===============================================================================
#' Kriging Cross Validation (Adapted from the gstat.cv function in the gstat library)
#'
#' @param object object of class gstat
#' @param nfold integer;  if larger than 1, then apply n-fold cross validation; 
#' if nfold equals nrow(data) (the default), apply leave-one-out cross validation; 
#' if set to e.g. 5, five-fold cross validation is done. To specify the folds, 
#' pass an integer vector of length nrow(data) with fold indexes
#' @param remove.all ogical; if TRUE, remove observations at cross validation 
#' locations not only for the first, but for all subsequent variables as well
#' @param verbose ogical; if FALSE, progress bar is suppressed
#' @param all.residuals ogical; if TRUE, residuals for all variables are 
#' returned instead of for the first variable only
#' @param fold subset of data for parallel processing
#'
#' @return 
#'
#' @export
#' @import data.table
#===============================================================================

crossValidation <- function (object, nfold = nrow(object$data[[1]]$data), remove.all = FALSE,
                             verbose = interactive(), all.residuals = FALSE, fold, ...){
  
  #------------------------------------------------------------------------#
  #--Return Error if object is not of class gstat--#
  if (!inherits(object, "gstat")) 
    stop("first argument should be of class gstat")
  #------------------------------------------------------------------------#
  
  #------------------------------------------------------------------------#
  #--Extract Variables, Data and Formula from gstat object--#
  var1 = object$data[[1]]
  data = var1$data
  formula = var1$formula
  #------------------------------------------------------------------------#
  
  #------------------------------------------------------------------------#
  #--Set-up residuals data.frame--# 
  if (all.residuals) {
    nc = length(object$data)
    ret = data.frame(matrix(NA, nrow(data), nc))[fold,]
  } else {
    cc = coordinates(data)[fold,]
    rownames(cc) = NULL
    df = data.frame(matrix(as.numeric(NA), nrow(data), 2))[fold,]
    ret = SpatialPointsDataFrame(cc, df)
    ret$NAME <- data$NAME[fold]
    ret$TYPE <- data$TYPE[fold]
  }
  #------------------------------------------------------------------------#
  
  #------------------------------------------------------------------------#
  #--Determine Row count if missing from Input--#
  if (missing(nfold)) 
    nfold = 1:nrow(data)
  #------------------------------------------------------------------------#
  
  #------------------------------------------------------------------------#
  #--Return list for residuals--#
  if (all.residuals || (remove.all && length(object$data) > 1)) {
    all.data = list()
    for (v in 1:length(object$data)) all.data[[v]] = object$data[[v]]$data
  }
  #------------------------------------------------------------------------#
  
  #------------------------------------------------------------------------#
  #--Display progress bar--#
  if (verbose){
    pb <- txtProgressBar(1, length(unique(fold)), style = 3)
  }
  #------------------------------------------------------------------------#
    
  #------------------------------------------------------------------------#
  #--Cross-Validation--#
  for (i in sort(unique(fold))) {
    
    #------------------------------------------------------------------------#
    #--Display Progress Bar--#
    if (verbose){
      setTxtProgressBar(pb, i)
    }
    #------------------------------------------------------------------------#
    
    #------------------------------------------------------------------------#
    #--Select Data to Remove for Cross-Validation--#
    sel = which(fold == i)
    object$data[[1]]$data = data[-sel, ]
    #------------------------------------------------------------------------#
    
    #------------------------------------------------------------------------#
    #--Subset for each Variable--#
    if (remove.all && length(object$data) > 1) {
      for (v in 2:length(object$data)) {
        varv = object$data[[v]]
        varv$data = all.data[[v]]
        atv = coordinates(varv$data)
        at1 = coordinates(data[sel, ])
        cc = rbind(atv, at1)
        rownames(cc) = NULL
        all = SpatialPoints(cc)
        zd = zerodist(all)
        skip = zd[, 1]
        object$data[[v]]$data = varv$data[-skip, ]
      }
    }
    #------------------------------------------------------------------------#
    
    #------------------------------------------------------------------------#
    #--Predict--#
#     x = predict(object, newdata = data[sel, ], ...)
    x = predict(object, newdata = data[sel, ])
    #------------------------------------------------------------------------#
    
    #------------------------------------------------------------------------#
    #--Extract Predicted Values--#
    if (all.residuals) {
      for (i in 1:length(object$data)) {
        var.i = object$data[[i]]
        data.i = all.data[[i]]
        formula.i = var.i$formula
        observed = gstat.formula(formula.i, data.i)$y[sel]
        pred.name = paste(names(object$data)[i], "pred", 
                          sep = ".")
        residual = as.numeric(observed - x[[pred.name]])
        ret[sel, i] = residual
      }
    } else {
      ret[[1]][sel] = x[[1]]
      ret[[2]][sel] = x[[2]]
    }
    #------------------------------------------------------------------------#
  }
  #------------------------------------------------------------------------#
  
  #------------------------------------------------------------------------#
  #--Display Progress Bar Break--#
  if (verbose) 
    cat("\n")
  #------------------------------------------------------------------------#

  #------------------------------------------------------------------------#
  #--Rename Object--#
  if (!all.residuals) {
    names(ret)[1:2] = names(x)[1:2]
    data <- data[fold,]
    ret$observed = gstat.formula(formula, data)$y
    pred.name = paste(names(object$data)[1], "pred", sep = ".")
    ret$residual = ret$observed - ret[[pred.name]]
    var.name = paste(names(object$data)[1], "var", sep = ".")
    ret$zscore = ret$residual/sqrt(ret[[var.name]])
    ret$fold = fold
  } else {
    names(ret) = names(object$data)
  }
  #------------------------------------------------------------------------#

  #------------------------------------------------------------------------#
  if (!is.null(object$locations)){ 
    ret = as.data.frame(ret)
  }
  #------------------------------------------------------------------------#
  
  return(ret)
}