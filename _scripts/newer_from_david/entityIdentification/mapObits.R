csvF <- "/home/alec/projects/thisSemester/nytimes-obituaries/entityIdentification/obitLocations.csv"
d <- read.csv(csvF)

hist(d$lat, breaks=50)
# us lon...
hist(d[d$lat >= 20 & d$lat <= 60, "lon"], breaks=50)

#euro lat
hist(d[d$lon >= 0 & d$lon <= 50, "lat"], breaks=15)

# united states
plot(newmap, xlim = c(-120, -70), ylim = c(20, 60), asp = 1)
points(d$lon, d$lat, col = "red", cex = .5)

# rest of the world
plot(newmap, xlim = c(-10, 30), ylim = c(40, 60), asp = 1)
points(d$lon, d$lat, col = "red", cex = .5)


# could "just" cluster the points...
nclusters = 5

d.scale <- scale( d[,c("lat","lon")] )
d.kmeans <- kmeans( d.scale, nclusters )
library(cluster)
clusplot(d.scale, d.kmeans$cluster)

for (c in 1:nclusters) {
  c.d <- d[ d.kmeans$cluster == c, ]
  c.minlat = min(c.d$lat)
  c.maxlat = max(c.d$lat)
  
  c.minlon = min(c.d$lon)
  c.maxlon = max(c.d$lon)
  
  plot(newmap, xlim = c(c.minlon, c.maxlon), ylim = c(c.minlat, c.maxlat), asp = 1)
  points(d$lon, d$lat, col = "red", cex = .5)
}
