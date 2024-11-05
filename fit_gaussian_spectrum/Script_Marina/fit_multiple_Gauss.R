##################################################################################################
# PURPOSE:
#    
# CALLING SEQUENCE:
#    
# INPUTS:
#    
# PARAMETERS:
#    
# OUTPUT:
#    
# REQUIRED SCRIPTS:
#   
##################################################################################################
read_data = T

if(read_data == T){
  remove(list = ls())
  library(bbmle)
  library(likelihood)
  read_data = T
}

norm_cont = T

################################
# Likelihood
################################
single_gauss <- function(lambda, flux, err, l0, s0, F0){
  model_line = F0 * exp(-(lambda - l0)**2 / (2 * s0**2)) / sqrt(2 * pi * s0**2)
  
  ln_p_i = -log(sqrt(2 * pi) * err) - (flux - model_line)**2 / (2 * err**2)
  lnlike = -sum(ln_p_i)
  return(lnlike)
}

two_gauss <- function(lambda, flux, err, l0_1, s0_1, F0_1, l0_2, s0_2, F0_2){
  line_1 = F0_1 * exp(-(lambda - l0_1)**2 / (2 * s0_1**2)) / sqrt(2 * pi * s0_1**2)
  line_2 = F0_2 * exp(-(lambda - l0_2)**2 / (2 * s0_2**2)) / sqrt(2 * pi * s0_2**2)
  model_line = line_1 + line_2

  ln_p_i = -log(sqrt(2 * pi) * err) - (flux - model_line)**2 / (2 * err**2)
  lnlike = -sum(ln_p_i)
  return(lnlike)
}

#######################################################
# FUNTION NORMALIZE CONTINUUM
#######################################################
nsig_up = 20
nsig_low = 2
degree = 3
span = 0.05
Nit = 20
fit_cont <- function(x, y, nsig_up, nsig_low, degree, span, Nit){
  if(missing(nsig_up)){nsig_up = 20}
  if(missing(nsig_low)){nsig_low = 2}
  if(missing(degree)){degree = 2}
  if(missing(span)){span = 0.1}
  if(missing(Nit)){Nit = 10}
  
  x2_temp = y
  x1_temp = x
  
  for(nn in 1:Nit){
    temp <- loess(x2_temp ~ x1_temp, degree = degree, span = span)
    xx.xx_temp1 = x2_temp - predict(temp) <= nsig_up * sd(x2_temp - predict(temp)) & x2_temp - predict(temp) >= 0
    xx.xx_temp2 = abs(x2_temp - predict(temp)) <= nsig_low * sd(x2_temp - predict(temp)) & x2_temp - predict(temp) < 0
    
    xx.xx_temp = xx.xx_temp1 | xx.xx_temp2
    
    x1_temp = x1_temp[xx.xx_temp]
    x2_temp = x2_temp[xx.xx_temp]
  }
  
  temp <- loess(x2_temp ~ x1_temp, degree = degree, span = span)
  
  return(temp)
}

# ---------------------------------------
# ---------------------------------------
# Spectrum
# ---------------------------------------
# ---------------------------------------
ex_gal = read.table('Script_Marina/0555-52266-0558.cxt') # I Zw 18
lam_ex = ex_gal$V1[ex_gal$V2 > 0]
flux_ex = ex_gal$V2[ex_gal$V2 > 0]
error_ex = ex_gal$V3[ex_gal$V2 > 0]; error_ex[] = 1
error_original = ex_gal$V3[ex_gal$V2 > 0]

if(norm_cont){
  temp <- fit_cont(x = lam_ex, y = flux_ex)
  mean_flux = predict(temp, newdata = data.frame(x1_temp = lam_ex))
  temp = flux_ex - mean_flux
  flux_original = flux_ex
  flux_ex = temp
}

################################
# MLE
################################
l0_line = 6562   # Hbeta ~ 4861; OIII ~ 5007; Halpha ~ 6562
xx.xx_line = lam_ex >= l0_line - 20 & lam_ex <= l0_line + 20

##########################
# SINGLE COMPONENT
##########################
fixed_i = list()
lower_i = list(l0 = l0_line - 10, s0 = 1, F0 = 5)
upper_i = list(l0 = l0_line + 10, s0 = 8, F0 = 1e4)
mle.result <- mle2(single_gauss, start = list(l0 = l0_line, s0 = 2, F0 = 4500),
                   fixed = fixed_i,
                   data = list(lambda = lam_ex[xx.xx_line], flux = flux_ex[xx.xx_line], err = error_ex[xx.xx_line]), 
                   method = "L-BFGS-B", skip.hessian = T,
                   lower = lower_i, upper = upper_i,
                   control = list(maxit = 1e5))
tt <- coef(mle.result)
l0_bin = tt["l0"]
s0_bin = tt["s0"]
F0_bin = tt["F0"]
print(tt)

tt <- coef(mle.result)
k = length(tt)
bic_1 = BIC(mle.result)
aic_1 = AIC(mle.result)
print(c(bic_1, aic_1))
# aicc_s = AIC(mle.result) + 2 * k * (k + 1) / (Nsat - k - 1)

##########################
# TWO COMPONENTS
##########################
fixed_i = list()
lower_i = list(l0_1 = l0_line - 20, s0_1 = 1, F0_1 = 5, l0_2 = l0_line - 10, s0_2 = 1, F0_2 = 5)
upper_i = list(l0_1 = l0_line + 20, s0_1 = 8, F0_1 = 1e4, l0_2 = l0_line + 10, s0_2 = 10, F0_2 = 5e3)
mle.result <- mle2(two_gauss, start = list(l0_1 = l0_line, s0_1 = 2, F0_1 = 4500, l0_2 = l0_line + 10, s0_2 = 3, F0_2 = 2000),
                   fixed = fixed_i,
                   data = list(lambda = lam_ex[xx.xx_line], flux = flux_ex[xx.xx_line], err = error_ex[xx.xx_line]), 
                   method = "L-BFGS-B", skip.hessian = T,
                   lower = lower_i, upper = upper_i,
                   control = list(maxit = 1e8))
tt <- coef(mle.result)
l0_1_bin = tt["l0_1"]
s0_1_bin = tt["s0_1"]
F0_1_bin = tt["F0_1"]
l0_2_bin = tt["l0_2"]
s0_2_bin = tt["s0_2"]
F0_2_bin = tt["F0_2"]
print(tt)

tt <- coef(mle.result)
k = length(tt)
bic_2 = BIC(mle.result)
aic_2 = AIC(mle.result)
print(c(bic_2, aic_2))
# aicc_s = AIC(mle.result) + 2 * k * (k + 1) / (Nsat - k - 1)

##########################
# PLOT
##########################
par(mfrow = c(3, 1), mar = c(5, 5, 1, 1))
plot(lam_ex[xx.xx_line], flux_ex[xx.xx_line], type = 'l', xlab = 'lambda', ylab = 'Flux', lwd = 2)

model_line = F0_bin * exp(-(lam_ex - l0_bin)**2 / (2 * s0_bin**2)) / sqrt(2 * pi * s0_bin**2) 
lines(lam_ex, model_line, col = 'blue')

model_line_2 = F0_1_bin * exp(-(lam_ex - l0_1_bin)**2 / (2 * s0_1_bin**2)) / sqrt(2 * pi * s0_1_bin**2) +
  F0_2_bin * exp(-(lam_ex - l0_2_bin)**2 / (2 * s0_2_bin**2)) / sqrt(2 * pi * s0_2_bin**2)
lines(lam_ex, model_line_2, col = 'red', lty = 5)
 
val <- substitute(paste('(BIC = ' , a, ' , AIC = ', b, ')'), list(a = sprintf('%.0f', bic_1), b = sprintf('%.0f', aic_1))) 
leg_1 = do.call("expression", list(val))
val <- substitute(paste('(BIC = ' , a, ' , AIC = ', b, ')'), list(a = sprintf('%.0f', bic_2), b = sprintf('%.0f', aic_2))) 
leg_2 = do.call("expression", list(val))

legend('topleft', c('Observed', 'One component', leg_1, 'Two components', leg_2), 
       lty = c(1, 1, 1, 5, 1), col = c('black', 'blue', 'white', 'red', 'white'), bty = 'n', cex = 1.2, lwd = c(2, 1, 1, 1, 1))

# ---------------------

plot(lam_ex[xx.xx_line], error_original[xx.xx_line], type = 'l', xlab = 'lambda', ylab = 'Error', lwd = 2)

# ---------------------

plot(lam_ex[xx.xx_line], flux_ex[xx.xx_line] - model_line[xx.xx_line], type = 'l', col = 'blue', 
     xlab = 'lambda', ylab = expression(paste(Delta, 'Flux')))
lines(lam_ex[xx.xx_line], flux_ex[xx.xx_line] - model_line_2[xx.xx_line], col = 'red')
abline(h = 0, lty = 3)

