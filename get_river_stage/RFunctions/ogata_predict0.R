ogata_predict0 <- function(par,x,y=NULL,lagged,n,int,predict=FALSE ){
  #source('1_Water_Level_Mapping/RFunctions/ogata_predict0.R')
  #---------------------------------------------------------------------------------#
  #--Copy Dataset--#
  ind_dt <- copy(x)
  #---------------------------------------------------------------------------------#
  
  #---------------------------------------------------------------------------------#
  #--Extract Ogata-Banks Parameters--#
  dispersion <- par[1]
  velocity   <- par[2]
  x_dist     <- par[3]
  #---------------------------------------------------------------------------------#
  
  #---------------------------------------------------------------------------------#
  #--Extract Scaling Parameters--#
  scale      <- par[4]
  offset     <- par[5]
  
  # Write output for checking
  #DIR <- 's:/AUS/CHPRC.C003.HANOFF/Rel.044/045_100AreaPT/t100areaPT/'
  #ofile=paste(DIR,"0_Data/River_Stage/par_ogata_check.csv", sep="")
  #write.csv(par, file = ofile, append = TRUE)
  #print(par)
  
  #---------------------------------------------------------------------------------#
  
  #---------------------------------------------------------------------------------#
  #--Calculate the Response Function--#
  wave_vec <- lagged %*% ogata_banks_1961( dispersion, velocity, 1, x_dist, t=0:(n-1)*int ) +
    ind_dt$lag_cumul
  ind_dt[, wave := wave_vec]
  #---------------------------------------------------------------------------------#
  
  #---------------------------------------------------------------------------------#
  #--Scale Response--#
  ind_dt[, model:= scale * wave + offset] 
  #---------------------------------------------------------------------------------#
  
  #---------------------------------------------------------------------------------#
  #--Combine Observed and Predicted Datasets and Calculate Residuals--#
  if(!is.null(y)){
    
    setkey(ind_dt,'datetime')
    setkey(y,'EVENT')
    
    if( predict ) {
      comb_dt <- y[ind_dt]
    } else {
      # comb_dt <- ind_dt[y, roll='nearest']
      comb_dt <- ind_dt[y]
    }
    comb_dt[, residual:=model-y]
  }
  #---------------------------------------------------------------------------------#
  
  if(is.null(y)){
    return(ind_dt)
  } else {
    return(comb_dt)
  }
  
}
