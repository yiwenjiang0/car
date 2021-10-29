
data <- read.csv('results.csv')
dataNO <- data[data$obstacles == 0,]

dataNOR1P <- dataNO[dataNO$model == "R1P",]
dataNOR1L <- dataNO[dataNO$model == "R1L",]
dataNOR2P <- dataNO[dataNO$model == "R2P",]
dataNOR2L <- dataNO[dataNO$model == "R2L",]
plot(dataNOR1L$area, dataNOR1L$runtime, type="b", col="red", xlab=expression(area (m^2)), ylab="runtime", lty=1)
lines(dataNOR2L$area, dataNOR2L$runtime,type="b", col="blue", lty=2)
lines(dataNOR1P$area, dataNOR1P$runtime, type="b", col="orange", lty=3)
lines(dataNOR2P$area, dataNOR2P$runtime, type="b", col="purple", lty=4)
legend(1450, 400, legend=c("Resolution 1, Lazy Constraints", "Resolution 2, Lazy Constraints", "Resolution 1, Flow Model", "Resolution 2, Flow Model"), lty=1:4, cex=0.8,
       col=c("red", "blue", "orange", "purple"))


data <- read.csv('results.csv')
dataNO <- data[data$obstacles > 0,]

dataNOR1P <- dataNO[dataNO$model == "R1P",]
dataNOR1L <- dataNO[dataNO$model == "R1L",]
dataNOR2P <- dataNO[dataNO$model == "R2P",]
dataNOR2L <- dataNO[dataNO$model == "R2L",]
plot(dataNOR1L$area, dataNOR1L$runtime, type="b", col="red", xlab=expression(area (m^2)), ylab="runtime", lty=1)
lines(dataNOR2L$area, dataNOR2L$runtime,type="b", col="blue", lty=2)
lines(dataNOR1P$area, dataNOR1P$runtime, type="b", col="orange", lty=3)
lines(dataNOR2P$area, dataNOR2P$runtime, type="b", col="purple", lty=4)
legend(1450, 400, legend=c("Resolution 1, Lazy Constraints", "Resolution 2, Lazy Constraints", "Resolution 1, Flow Model", "Resolution 2, Flow Model"), lty=1:4, cex=0.8,
       col=c("red", "blue", "orange", "purple"))


data <- read.csv('results.csv')
dataNO <- data[data$obstacles== 0,]

dataNOR1P <- dataNO[dataNO$model == "R1P",]
dataNOR1L <- dataNO[dataNO$model == "R1L",]
dataNOR2P <- dataNO[dataNO$model == "R2P",]
dataNOR2L <- dataNO[dataNO$model == "R2L",]
plot(dataNOR1L$area, dataNOR1L$objective, type="b", col="red", xlab=expression(area (m^2)), ylab="num. parking spaces", lty=1)
lines(dataNOR2L$area, dataNOR2L$objective,type="b", col="blue", lty=2)
lines(dataNOR1P$area, dataNOR1P$objective, type="b", col="orange", lty=3)
lines(dataNOR2P$area, dataNOR2P$objective, type="b", col="purple", lty=4)
legend(1400, 30, legend=c("Resolution 1, Lazy Constraints", "Resolution 2, Lazy Constraints", "Resolution 1, Flow Model", "Resolution 2, Flow Model"), lty=1:4, cex=0.8,
       col=c("red", "blue", "orange", "purple"))

data <- read.csv('results.csv')
dataNO <- data[data$obstacles > 0,]

dataNOR1P <- dataNO[dataNO$model == "R1P",]
dataNOR1L <- dataNO[dataNO$model == "R1L",]
dataNOR2P <- dataNO[dataNO$model == "R2P",]
dataNOR2L <- dataNO[dataNO$model == "R2L",]
plot(dataNOR1L$area, dataNOR1L$objective, type="b", col="red", xlab=expression(area (m^2)), ylab="num. parking spaces", lty=1)
lines(dataNOR2L$area, dataNOR2L$objective,type="b", col="blue", lty=2)
lines(dataNOR1P$area, dataNOR1P$objective, type="b", col="orange", lty=3)
lines(dataNOR2P$area, dataNOR2P$objective, type="b", col="purple", lty=4)
legend(1400, 20, legend=c("Resolution 1, Lazy Constraints", "Resolution 2, Lazy Constraints", "Resolution 1, Flow Model", "Resolution 2, Flow Model"), lty=1:4, cex=0.8,
       col=c("red", "blue", "orange", "purple"))

data <- read.csv('results.csv')
dataNO <- data[data$obstacles == 0,]

dataNOR1P <- dataNO[dataNO$model == "R1P",]
dataNOR1L <- dataNO[dataNO$model == "R1L",]
dataNOR2P <- dataNO[dataNO$model == "R2P",]
dataNOR2L <- dataNO[dataNO$model == "R2L",]
plot(dataNOR1L$area, dataNOR1L$num_lazy, type="b", col="red", xlab=expression(area (m^2)), ylab="num. lazy constraints", lty=1, ylim=c(0,15000))
lines(dataNOR2L$area, dataNOR2L$num_lazy,type="b", col="blue", lty=2)
#lines(dataNOR2P$area, dataNOR2P$runtime, type="b", col="orange", lty=3)
#lines(dataNOR2L$area, dataNOR2L$runtime, type="b", col="purple", lty=4)
legend(1450, 1300, legend=c("Resolution 1, Lazy Constraints", "Resolution 2, Lazy Constraints"), lty=1:4, cex=0.8,
       col=c("red", "blue", "orange", "purple"))
