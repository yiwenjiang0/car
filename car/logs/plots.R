data <- read.csv('./logs.csv')
res1lazy <- read.csv('./res1lazy.csv')
res1paper <- read.csv('./res1paper.csv')
res2lazy <- read.csv('./res2lazy.csv')
res2paper <- read.csv('./res2paper.csv')

res1lazy[is.na(res1lazy)] <- 0
res1paper[is.na(res1paper)] <- 0
res2lazy[is.na(res2lazy)] <- 0
res2paper[is.na(res2paper)] <- 0

ymin <- min(res1paper$Incumbent)
ymax <- max(res1paper$BestBd)
plot(res1paper[,1], res1paper$Incumbent, type="b", xlab="Iteration", ylab="Num. Spaces", col="black", ylim=c(ymin, ymax), cex=1, pch=0)
lines(res1paper[,1], res1paper$BestBd, type="b", xlab="Iteration", ylab="Iteration", col="red", cex=1, pch=2)
legend(18, 10, legend=c("Best Bd.", "Incumbent"), col=c("red", "black"), pch=0:2, lty=1:1, cex=1)

ymin <- min(res1lazy$Incumbent)
ymax <- max(res1lazy$BestBd)
plot(res1lazy[,1], res1lazy$Incumbent, type="b", xlab="Iteration", ylab="Num. Spaces", col="black", ylim=c(ymin, ymax), cex=1, pch=0)
lines(res1lazy[,1], res1lazy$BestBd, type="b", xlab="Iteration", ylab="Iteration", col="red", cex=1, pch=2)
legend(10, 10, legend=c("Best Bd.", "Incumbent"), col=c("red", "black"), pch=0:2, lty=1:1, cex=1)

ymin <- min(res2lazy$Incumbent)
ymax <- max(res2lazy$BestBd)
plot(res2lazy[,1], res2lazy$Incumbent, type="l", xlab="Iteration", ylab="Num. Spaces", col="black", ylim=c(ymin, ymax), cex=1, pch=0)
lines(res2lazy[,1], res2lazy$BestBd, type="l", xlab="Iteration", ylab="Iteration", col="red", cex=1, pch=2)
legend(46, 12, legend=c("Best Bd.", "Incumbent"), col=c("red", "black"), pch=0:2, lty=1:1)

ymin <- min(res2paper$Incumbent)
ymax <- max(res2paper$BestBd)
plot(res2paper[,1], res2paper$Incumbent, type="l", xlab="Iteration", ylab="Num. Spaces", col="black", ylim=c(ymin, ymax), cex=1, pch=0)
lines(res2paper[,1], res2paper$BestBd, type="l", xlab="Iteration", ylab="Iteration", col="red", cex=1, pch=2)
legend(2000, 12, legend=c("Best Bd.", "Incumbent"), col=c("red", "black"), pch=0:2, lty=1:1)
