import csv
import math 
from collections import defaultdict

'''
about:
this code assumes that the output file (the result of our ML) matches the same csv schema as validation.csv, including the first row being collumn names
it loads the expected (validation.csv) answers into a dictionnary and then checks whether ouput found them
the metrics compute the distance and false positives
to dos: 
Note: outputExample and validationWithoutAnomalies are identical right now
'''
# const:
assessmentResultsOutputFile = 'assessmentResults.txt'
groundTruthFile = 'validationWithoutAnomalies.csv'
classificationResultsFile = 'classificationResults.csv'
# The average size of seal on thermal image is about 2 by 5 pixels. Assume hot spot detedted within 
# two times the size of a seal is a success detection.
sealSizeInPixels = 4
tolenceFactor = 2
locationOffsetTolerance = sealSizeInPixels * tolenceFactor

# metrics:
falsePositives = 0
falseNegatives = 0
hotSpotDistances = []
registrationDistances = []
truePositives = 0
classificationTrue = 0
classificationFalse = 0
expectedTruePositives = 0
hotspotLocationTrue = 0
registrationTrue = 0

# Sort images on x_pos of the bounding box, if they have the same photoId
def getSortKey(item):
    return item[5]
    
with open(groundTruthFile, 'r') as answers:
    # col 5 and 6 = hotspot
    # col 7-10 = registration
    # col 12 = species_id 
    ans = csv.reader(answers)
    expectedList = list(ans)
    # dictionary with photoIds (thermal image names) and pointers to the rows with that image
    expectedDict = {}

    # fill the dictionary with the expected information
    for i in range(1, len(expectedList)): 
        # assume thermal phone name is id and is in 3rd (index 2) column
        photoID = expectedList[i][2]
        # remove col-name row 
        expectedTruePositives = len(expectedList) - 1
        if photoID in expectedDict:
            expectedDict[photoID].append(i)
        else:
            expectedDict[photoID] = [i]
                
    with open(classificationResultsFile, 'r') as results:
        res = csv.reader(results)
        resList1 = list(res)
        # filter out anomalies
        resList = list(filter(lambda row: row[11] != "Anomaly", resList1))
        resDict = {}

        # Start from the seconde row to exlude the title/col-name row
        for j in range(1, len(resList)):
            resPhotoId = resList[j][2]
            if resPhotoId in resDict:
                resDict[resPhotoId].append(j)
            else:
                resDict[resPhotoId] = [j]

        # Each image may have several hot spots identfied. 
        # Assuming the spacial distribution pattern of hotspots on classifcation results and ground true are the same, sort the rows
        # on its x_positon, and macth the spots.
        # TODO: need to consider method to macth the spots when number of rows are different in result and ground truth
        for key in resDict:
            # if photo not in expected dictionary that means there were no animals in the entire photo so throw FalsePositive
            if key not in expectedDict:
                falsePositives+=len(resDict[key])
            else:
                resRows = resDict.get(key)
                expectedRows = expectedDict.get(key)

                lengthDiff = len(resRows) - len(expectedRows)
                minLength = min(len(resRows), len(expectedRows))


                if (lengthDiff >= 0): 
                    # TODO: updated caculation method when ground truth includes "Anormaly"
                    falsePositives+=lengthDiff
                else:
                    falseNegatives+=lengthDiff

                # TODO: need to consider method to macth the spots when numbers of rows are different in classifed result and ground truth
                resRowsData = []
                expectedRowsData = []
                for k in resRows:
                    resRowsData.append(resList[k])

                if (len(resRowsData) > 1):
                    resRowsData.sort(key=getSortKey)

                for l in expectedRows:
                    expectedRowsData.append(resList[l])

                if (len(expectedRowsData) > 1):
                    expectedRowsData.sort(key=getSortKey)

                for e in expectedRowsData:
                    minDist = 99999999
                    for r in resRowsData:
                        if r[1] != 'MatchesGroundTruth':
                            x1 = int(expectedRow[5])
                            y1 = int(expectedRow[6])
                            x2 = int(resRow[5])
                            y2 = int(resRow[6])
                            dist = math.hypot(x2 - x1, y2 - y1)
                            if dist < minDist:
                                minDist = dist
                                minResRow = r
                    
                    # Was there a detected hotspot within tolerance of this ground truth hotspot?
                    if minDist < locationOffsetTolerance:
                        truePositives += 1
                        minResRow[1] = 'MatchesGroundTruth' # Hackily reuse the "timestamp" field to indicate that we have a match
                        if minResRow[13] == e[13]:
                            classificationTrue += 1
                        else
                            classificationFalse += 1

                for r in resRowsData:
                    if r[1] != 'MatchesGroundTruth':
                        falsePositives += 1
                    else:
                        if r[13] == 


    # Print results on screen
    print("Accuracy assessment for thermal image classification")
    print("Number of hot spots found: " + str(len(resList)-1))
    print("Percent of hot spots found: " + str(truePositives / expectedTruePositives*100)  + " percent.")
    print("There were " + str(falsePositives) + " false positives.")
    print("There were " + str(falseNegatives) + " false negatives.")
    if ((truePositives) > 0):
        print("There was a classification accuracy of " + str((classificationTrue / (classificationTrue + classificationFalse)) * 100) + " percent.")
            
    # Print result to a file
    with open('assessmentResults.txt', 'w') as f:
        print("Accuracy assessment for thermal image classification", file=f)
        print("Number of hot spots found: " + str(len(resList)-1), file=f)
        print("Percent of hot spots found: " + str((truePositives) / expectedTruePositives*100)  + " percent.", file=f)
        print("There were " + str(falsePositives) + " false positives.", file=f)
        print("There were " + str(falseNegatives) + " false negatives.", file=f)
        if ((truePositives) > 0):
            print("There was a classification accuracy of " + str((truePositives / (truePositives)) * 100) + " percent.", file=f)
        if (len(hotSpotDistances) > 0):
            print("There was an average hot spot distance of " + str(sum(hotSpotDistances) / len(hotSpotDistances)), file=f)        
            print("There was an hot spot location detection accuracy of " + str(hotspotLocationTrue / len(hotSpotDistances)*100)  + " percent.", file=f)
  