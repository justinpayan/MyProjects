# Once you've generated the word2vec model and stored it in the variable "model"
# you can use it to augment the CSV file with features corresponding to the word2vec
# representations of the words

# We assume that all phrases are at most length 4

import csv
import os
import time
import gensim
import sys

model = gensim.models.Word2Vec.load('./finalw2vmodel')
maxNumWords = int(sys.argv[4])

with open(sys.argv[1]) as csvfile:
    with open(sys.argv[2],"w") as csvfile2:
        fileReader = csv.reader(csvfile,delimiter="\t")
        fileWriter = csv.writer(csvfile2,delimiter="\t")
        
        # Just get the column names in there
        # Right now we have 96 "words" in each row
        # Each of those has 62 elements, one word and 48 dependency features
        # As well as ten features that are the distance embedding vector
        # The one word will be expanded into 50 w2v features
        # At the end we have 30 WordNet synonyms and 30 WordNet hypernyms
        # for each of e1 and e2.

        if (sys.argv[3] == "appendToEnd"):
            titles = [""]
            w2v = ["w2v"]*50
            depFeat = ["depFeat"]*48
            wn = ["wn"]*6000
            for num in range(1,51):
                w2v[num-1] += str(num)
            for num in range(1,49):
                depFeat[num-1] += str(num)
            for num in range(1,6001):
                wn[num-1] += str(num)

            for num in range(1, maxNumWords+1):
                for i in range(0, 50):
                    toAdd = w2v[i] + "_" + str(num)
                    titles += [toAdd]
                titles += ["distE1_1","distE1_2","distE1_3","distE1_4","distE1_5"]
                titles += ["distE2_1","distE2_2","distE2_3","distE2_4","distE2_5"]
                for i in range(0, 48):
                    toAdd = depFeat[i] + "_" + str(num)
                    titles += [toAdd]

            titles += wn
            titles += ["outputClass"]
            titles += ["sentenceLength"]
            titles += ["headIndex"]

            fileWriter.writerow(titles)


            monitoringindex = 0

            for row in fileReader:
                if row[3] != "w2v4_1":

                    rowToWrite = []
                    foundWN = False
                    howFarWeveGone = 0
                    howFarWeNeedToGo = maxNumWords*108

                    # Write out things as they are, but when we come across a string, expand it into w2v representation

                    for index in range(0, len(row)):
                        if (row[index][:9] == "str_feat_"):
                            try:
                                # print(row[index][9:])
                                rowToWrite += map(str, model[row[index][9:].lower()])
                                howFarWeveGone = len(rowToWrite)
                            except KeyError:
                                rowToWrite += [0] * 50
                                howFarWeveGone = len(rowToWrite)
                        elif (row[index][:12] == "wn_str_feat_"):
                            if (not foundWN):
                                # Pad with 0's until we get enough
                                while (howFarWeveGone != howFarWeNeedToGo):
                                    rowToWrite += [0]
                                    howFarWeveGone = len(rowToWrite)
                                    # print("intermedrwrite " + str(len(rowToWrite)))
                                    # print("lenrow " + str(len(row)))
                                try:
                                    rowToWrite += map(str, model[row[index][12:].lower()])
                                    howFarWeveGone = len(rowToWrite)
                                except KeyError:
                                    rowToWrite += [0] * 50
                                    howFarWeveGone = len(rowToWrite)
                                foundWN = True
                            else:
                                try:
                                    rowToWrite += map(str, model[row[index][12:].lower()])
                                    howFarWeveGone = len(rowToWrite)
                                except KeyError:
                                    rowToWrite += [0] * 50
                                    howFarWeveGone = len(rowToWrite)
                        else:
                            rowToWrite += [str(row[index])]
                            howFarWeveGone = len(rowToWrite)

                    fileWriter.writerow(rowToWrite)
                    monitoringindex += 1
                    if monitoringindex%100 == 0:
                        print(monitoringindex)

        # If the appendToEnd flag is replaced by appendForEach,
        # we add 1 synonym and 1 hypernym from WordNet for each word, rather than
        # add them all at the end for e1 and e2.
        else:
            titles = [""]
            w2v = ["w2v"]*50
            depFeat = ["depFeat"]*48
            wn = ["wn"]*100
            #        namesOfFeatures = ["wvFeature"] * 600
            for num in range(1,51):
                w2v[num-1] += str(num)
            for num in range(1,49):
                depFeat[num-1] += str(num)
            for num in range(1,101):
                wn[num-1] += str(num)
            for num in range(1, maxNumWords+1):
                for i in range(0, 50):
                    toAdd = w2v[i] + "_" + str(num)
                    titles += [toAdd]
                for i in range(0, 100):
                    toAdd = wn[i] + "_" + str(num)
                    titles += [toAdd]
                titles += ["distE1_1","distE1_2","distE1_3","distE1_4","distE1_5"]
                titles += ["distE2_1","distE2_2","distE2_3","distE2_4","distE2_5"]
                for i in range(0, 48):
                    toAdd = depFeat[i] + "_" + str(num)
                    titles += [toAdd]

            titles += ["outputClass"]
            fileWriter.writerow(titles)


            monitoringindex = 0

            for row in fileReader:
                if row[3] != "w2v4_1":

                    rowToWrite = []
                    howFarWeveGone = 0
                    howFarWeNeedToGo = maxNumWords*208

                    # Write out things as they are, but when we come across a string, expand it into w2v representation

                    for index in range(0, len(row)):
                        if (row[index][:9] == "str_feat_"):
                            try:
                                rowToWrite += map(str, model[row[index][9:].lower()])
                            except KeyError:
                                rowToWrite += [0] * 50
                        elif (row[index][:12] == "wn_str_feat_"):
                            try:
                                rowToWrite += map(str, model[row[index][12:].lower()])
                            except KeyError:
                                rowToWrite += [0] * 50
                        else:
                            rowToWrite += [str(row[index])]
                        howFarWeveGone = len(rowToWrite)

                    # We need to pad with 0's
                    while (howFarWeveGone <= howFarWeNeedToGo):
                        rowToWrite += [0]
                        howFarWeveGone = len(rowToWrite)


                    if (howFarWeveGone > howFarWeNeedToGo):
                        print(howFarWeveGone)
                        print(howFarWeNeedToGo)
                    fileWriter.writerow(rowToWrite)
                    monitoringindex += 1
                    if monitoringindex%100 == 0:
                        print(monitoringindex)
                    
