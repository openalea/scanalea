#
#  infer stage, nmax, Smax, A1, A2 from one segmented/measured plantscan snapshot and a (given) estimated Nff
#
#
#
#source('Profil.R')
#
# estimate 'true' leaf rank' from a reference fit
#
infer_rank <- function(data,fitref, conv=0.01) {
  lws <- getLWS(fitref)
  #use only data for incresing S minus one
  dat <- data[data$pos < which.max(data$Area),]
  #test for 6 missing leaves
  dec <- 0:6
  rss <- sapply(dec,function(d) sum((dat$Area * conv - lws$S[d+dat$pos])**2))
  dec <- dec[which.min(rss)]
  data$pos + dec
}
#
# estimate lizfit
#
infer_fitS <- function(data, fitref, nff = 16,conv=0.01) {
  mat <- data.frame(n=data$rank,S=data$Area * conv,nFF=nff)
  fit <- fitref
  fit$nff <- nff
  fit$nmax <- getNmax(mat)
  #try to filter non mature leaves
  ncol <- max(mat$n+1) / 1.8 # phylocol = 1.8 phyloTip
  mat <- mat[mat$n <= min(fit$nmax, ncol),]
  fit$Smax <- fit$Smax * median(mat$S / predS(fit,mat$n))
  fit
}
#
#infer stage using nextcollar to appear, does not depend on phyl
infer_stage <- function(data,fitS,coef=1.8,conv=0.01) {
  phyl <- 1
  pvis <- data$Area*conv / predS(fitS,data$rank)
  ncol <- max(data$rank[pvis > 0.9])
  # update pvis for visible leaves by including 'stem leength"
  #stem <- c(0,diff(data$height[order(data$pos)]))
  #data$Area[data$rank > ncol] <-  data$Area[data$rank > ncol] * (1 +  stem[data$rank > ncol] / data$Width[data$rank > ncol])
  #pvis <- data$Area*conv / predS(fitS,data$rank)
  tip <- phyl*(ncol+1)
  ttcol <- coef*phyl*(ncol+1)
  tt <- ttcol-(1-pvis[which(data$rank==ncol+1)])*(ttcol-tip)
  data.frame(tip = tt / phyl, col = tt / phyl / coef)
}
#
#macro to be used in scanalea
#
infer_maize <- function(data, nff = 16, conv = 0.01) {
#
#reference curve : B73 MA11 WW
  fitref <- data.frame(nff=17.5, nmax=12.08, Smax = 975.77, A1 = -4.79, A2=0.18)
  #order along height
  data <- data[order(data$height),]
  data$pos <- seq(nrow(data))
  data$rank <- infer_rank(data,fitref)
  fitS <- infer_fitS(data, fitref, nff = nff)
  stage <- infer_stage(data,fitS)
  list(fitS=fitS,stage = stage,ranks = data.frame(Leaf_Number=data$Leaf_Number, pos=data$pos,rank=data$rank))
}
#
#
#
# to be developd later
if (0 > 1) {
  data <- read.csv("leaves_data.csv")
res <- infer_Plant(data)

    lws <- getLWS(fitS)

  plot(lws$n,lws$S/conv,type="l",col=2)
  points(data$rank,data$Area)


#find coef testing prediction for last vis
  coefs <- seq(1,2.5,0.1)
  stages <- sapply(coefs,function(x) infer_stage(data,fitS,x))
  p <- (stages / 6 - 0.8) / (coefs - 0.8)
  pvis <- data$Area*conv / predS(fitS,data$rank)
  best <- which.min(abs(p - pvis[5]))
  c <- coefs[best]
  stage <- stages[7]
}
