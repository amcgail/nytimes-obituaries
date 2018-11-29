library(ggplot2)

d <- read.csv("~/projects/2017/spring/nytimes-obituaries/coding/thirdStabCoding.csv")
hist(d$confidence1, breaks=50)
length( d[d$confidence1 > 1, "confidence1"] )

countCodes <- table(d[d$confidence1 > 5, "code2"])
countCodes <- as.data.frame(countCodes)
countCodes <- countCodes[order(-countCodes$Freq),  ]
countCodes <- head( countCodes, n=25 )

countCodes

