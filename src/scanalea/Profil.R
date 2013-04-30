#
#                          Essai fit profil LAI fournier 1998 in data ma06
#
#
# Find nmax by fitting parabola to log(S). If not possible estimate nmax as 0.67*Nt
#
getNmax <- function(mat) {
  mat <- na.omit(mat)
  nFF <-  mat$nFF[1]
  nmax <- 0.67 * nFF
  if (nrow(mat) >=2 & any(mat$n < nmax) & any(mat$n > nmax)) {
    fit <- lm(log(S)~ n + I(n*n),mat)
    parfit <- data.frame(a=fit$coefficients[3],b=fit$coefficients[2], c=fit$coefficients[1])
    fnmax <-  with(parfit, -b / (2*a))
    if (!is.na(fnmax))
      if (fnmax > 0.4*nFF & fnmax < 0.9*nFF)
        nmax <- fnmax
  }
  nmax
}
#
# add leaf 1 to force fitting
#
addL1 <- function(mat,LW1) {
  F1 <- mat[1,]
  F1$n <- 1
  F1$L <- LW1[1]
  F1$W <- LW1[2]
  F1$S <- LW1[1]*LW1[2]*0.75
  rbind(F1,mat)
}

#
# Fit lizaso on an individual plant
#
fitLiz <- function(plant,nmax,LW1=c(50,15)) {
  res <- NULL
  plant <- na.omit(plant)
  if (nrow(plant) >=1) {
    #add leaf one if missing
    if (!1%in%plant$n) 
      plant <- addL1(plant,LW1)
    # normalise ranks
    plant$xn <- with(plant,(n - nmax) / (nmax - 1))
    # try fit degree 3
    fit <- lm(log(S) ~ I(xn*xn) + I(xn*xn*xn), plant)
    Smax <- exp(fit$coefficients[1])
    A1 <- fit$coefficients[2]
    A2 <- fit$coefficients[3]
    A2 <- ifelse(is.na(A2),0,A2)
    res <- data.frame(Smax=Smax,A1=A1,A2=A2)
  }
  res
}
#
# Fit Lizaso plus LW on a set of plants with nmax,smax references to normalise
#
fitLizNorm <- function(plants,nmax,Smax,LW1=c(50,15)) {
  for (i in seq(plants)){
    plant <- na.omit(plants[[i]])
    #add leaf one if missing
    if (!1%in%plant$n)
      plant <- addL1(plant,LW1)
    plant$xn <-  (plant$n - nmax[i]) / (nmax[i] - 1)
    plant$Sn <-  plant$S  / Smax[i]
    plants[[i]] <- plant
  }
  dat <- na.omit(do.call('rbind',plants))
  fit <- lm(log(Sn) ~ 0 + I(xn*xn) + I(xn*xn*xn), dat)
  A1 <- fit$coefficients[1]
  A2 <- fit$coefficients[2]
  A2 <- ifelse(is.na(A2),0,A2)
 # degrade to degree 2 if bad fit (inflexion before end)
  x <- c(median(dat$nFF) - 1, median(dat$nFF)) / (median(nmax) - 1)
  if (diff(exp(A1*x^2+A2*x^3)) > 0) {
    fit <- lm(log(Sn) ~ 0 + I(xn*xn), dat)
    A1 <- fit$coefficients[1]
    A2 <- 0
  }
  data.frame(A1=A1,A2=A2)
}

#
# determine if data are fitable
#
checkfit <- function(mat) {
  mat <- na.omit(mat)
  nrow(mat) >=1
}
#
# Fit lisazo for a set of plant and return Lisazo parameters
#
fitLizPlot <- function(plants,L1=50,W1=15) {
  res <- NULL
  check <- sapply(plants,checkfit)
  if (any(check)) {
    plants <- plants[check]
    # find nff,Smax, nmax
    nff <- sapply(plants,function(x) x$nFF[1])
    nmax <- sapply(plants,getNmax)
    fitplants <- mapply(fitLiz,plants,nmax,MoreArgs=list(LW1=c(L1,W1)),SIMPLIFY=FALSE)
    Smax <- sapply(fitplants,function(fit) fit$Smax)
    #fit lizaso to pooled normalised data to get A1 and A2
    fit <- fitLizNorm(plants,nmax,Smax,LW1=c(L1,W1))
    res <- data.frame(nff=median(nff),nmax=median(nmax),Smax=median(Smax),A1=fit$A1,A2=fit$A2)
  }
  res
}
#
# predict S at arbitrary ranks
#
predS <- function(fit,n) {
  xn <- (n - fit$nmax) / (fit$nmax - 1)
  fit$Smax * exp(fit$A1 * xn^2 + fit$A2 * xn^3)
}

#
# Re-Scale a fit to data by varying Smax only
#
scaleSmax <- function(fit,dat) {
 sc <- median(unlist(sapply(dat,function(x) x$S / predS(fit,x$n),simplify=FALSE)),na.rm=TRUE)
 fit$Smax * sc
}
#
# Partial fit of Lizaso model on scarce data
#
fitLizPlotWith <- function(plants, fit, fitSmax = TRUE, fitNff = TRUE, fitNmax = FALSE) {
    res <- fit
    if (fitNmax)
      res$nmax <- median(na.omit(sapply(plants,getNmax)))
    if (fitSmax)
      res$Smax <- scaleSmax(res,plants)
    if (fitNff)
      res$nff <- median(na.omit(sapply(plants,function(x) x$nFF[1])))
    res
}
#
# Build n,L,W,S tables from fits
#
getLWS <- function(fit,LW=0.1) {
  res <- NULL
  if (!is.null(fit)) {
    n <- seq(fit$nff)
    xn <- (n - fit$nmax) / (fit$nmax - 1)
    S <- fit$Smax * exp(fit$A1 * xn^2 + fit$A2 * xn^3)
    L <- sqrt(S/LW)
    W <- S / L
    res<- data.frame(n=n, L=L, W=W, S=S)
  }
  res
}
#
# visu
#
vfit <- function(fits,lab,db) {
  #par(mfrow=c(3,3),mar=c(2,2,4,1))
  gg <- unique(lab$genotype)
  if (length(gg) > 9)
    gg <- sample(,9)
  for (g in gg) {
    fitg <- fits[lab$genotype==g]
    lws <- lapply(fitg,getLWS)
    dbg <- db[lab$genotype==g]
    plot(c(0,20),c(0,1e3),type='n',main=g)
    for (i in seq(fitg)) {
      if (!is.null(lws[[i]])) lines(lws[[i]]$n,lws[[i]]$S,col=i)
      dat <- dbg[[i]]
      if (!is.data.frame(dbg[[i]]))
        dat <- do.call("rbind",dbg[[i]])
      
      points(dat$n,dat$S,pch=16,col=i)
    }
  }
}
