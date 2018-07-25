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
 # The average size of seal on color image is about 20 by 70 pixels. Assume an offset within
 # two time of the size of a seal is a successfull identificatio
sealSizeInPixels = 70
tolenceFactor = 2
locationOffsetTolerance = sealSizeInPixels * tolenceFactor

# metrics:
falsePositives = 0
falseNegatives = 0
hotSpotDistances = []
registrationDistances = []
classificationTrue = 0
classificationFalse = 0
expectedTruePositives = 0
hotspotLocationTrue = 0
registrationTrue = 0

# Sort images on thumb_left of the bounding box, if they have the same photoId
def getSortKey(item):
    return item[7]
    
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
        photoID = expectedList[i][4]
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
            resPhotoId = resList[j][4]
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
                falsePositives+=1
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

                # TODO: need to consider method to macth the spots when number of rows are different in result and ground truth
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

                for m in range(minLength):
                    resRow = resRowsData[m]
                    expectedRow = expectedRowsData[m]

                    # Check bounding box
                    # 1 is expected values; 2 is ouput values. 
                    midX1 = (int(expectedRow[7]) + int(expectedRow[9])) / 2
                    midY1 = (int(expectedRow[8]) + int(expectedRow[10])) / 2
                    midX2 = (int(resRow[7]) + int(resRow[9])) / 2
                    midY2 = (int(resRow[8]) + int(resRow[10])) / 2
                    dist = math.hypot(midX2 - midX1, midY2 - midY1)
                    
                    registrationDistances.append(dist)
                    # The average size of seal on color image is about 20 by 70 pixels. Assume an offset at the sale of 
                    # half the size of a seal won't affect the final result
                    if (dist < locationOffsetTolerance):
                        registrationTrue+=1
                    
                    # classification accuracy
                    if (expectedRow[12] == resRow[12]):
                        classificationTrue += 1 
                    else:
                        classificationFalse += 1

    # Print results on screen
    print("Accuracy assessment for color image classification")
    print("Number of hot spots found: " + str(len(resList)-1))
    print("Percent of hot spots found: " + str((classificationTrue + classificationFalse) / expectedTruePositives*100)  + " percent.")
    print("There were " + str(falsePositives) + " false positives.")
    print("There were " + str(falseNegatives) + " false negatives.")
    if ((classificationTrue + classificationFalse) > 0):
        print("There was a classification accuracy of " + str((classificationTrue / (classificationTrue + classificationFalse)) * 100) + " percent.")
    if (len(registrationDistances) > 0):
        print("There was an average registration distance of " + str(sum(registrationDistances) / len(registrationDistances)))
        print("There was an registration accuracy of " + str(classificationTrue / len(registrationDistances)*100) + " percent.")
        
    # Print result to a file
    with open('assessmentResults.txt', 'w') as f:
        print("Accuracy assessment for color image classification", file=f)
        print("Number of hot spots found: " + str(len(resList)-1), file=f)
        print("Percent of hot spots found: " + str((classificationTrue + classificationFalse) / expectedTruePositives*100)  + " percent.", file=f)
        print("There were " + str(falsePositives) + " false positives.", file=f)
        print("There were " + str(falseNegatives) + " false negatives.", file=f)
        if ((classificationTrue + classificationFalse) > 0):
            print("There was a classification accuracy of " + str((classificationTrue / (classificationTrue + classificationFalse)) * 100) + " percent.", file=f)
        if (len(registrationDistances) > 0):
            print("There was an average registration distance of " + str(sum(registrationDistances) / len(registrationDistances)), file=f)
            print("There was an registration accuracy of " + str(classificationTrue / len(registrationDistances)*100) + " percent.", file=f)
        