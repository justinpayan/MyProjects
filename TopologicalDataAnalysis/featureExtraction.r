
files <- list.files()
counter <- 1

featureMat <- lapply(files, function(x) {

	currFile <- read.csv(x)
	diagram1 <- ripsDiag(currFile,1,1000)$diagram
	
	featureVect <- rnorm(200)

	for (j in 1:100) {
		count <- 0

		for (k in 1:dim(diagram1)[1]) {
			if (diagram1[k,1] == 0) {
				if (diagram1[k,3] >= (10*j-1)+diagram1[k,2]) {
					count <- count + 1
				}
			}
		}

		featureVect[j] <- count
	}

	for (j in 1:100) {
		count <- 0

		for (k in 1:dim(diagram1)[1]) {
			if (diagram1[k,1] == 1) {
				if (diagram1[k,3] >= (10*j-1) + diagram1[k,2]) {
					count <- count + 1
				}
			}
		}

		featureVect[j+100] <- count
	}

	featureVect <- featureVect/dim(diagram1)[1]
	return(featureVect)
})
