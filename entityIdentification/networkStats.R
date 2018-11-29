library(igraph)

rg <- read.csv("/home/alec/projects/thisSemester/nytimes-obituaries/entityIdentification/referentGraph.csv")

rgEdges <- unlist(lapply(t(rg[,c("Source","Target")]), as.character))
g <- make_undirected_graph(rgEdges)

E(g)$weight <- rg[,"weight"]

btw <- betweenness(g)
which(btw > 0.25*max(btw))

plot(degree.distribution(g)[1:100],type='l')