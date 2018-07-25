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

# metrics:
falsePositives = 0
hotSpotDistances = []
registrationDistances = []
classificationTrue = 0
classificationFalse = 0
expectedTruePositives = 0
    
with open('validationWithoutAnomalies.csv', 'r') as answers:
    # col 5 and 6 = hotspot
    # col 7-10 = registration
    # col 12 = species_id 
    ans = csv.reader(answers)
    expectedList = list(ans)
    # dictionary with photoIds (thermal image names) and pointers to the rows with that image
    expectedDict = {}

    # fill the dictionary with the expected information
    for i in range(len(expectedList)): 
        # assume thermal phone name is id and is in 3rd (index 2) column
        photoID = expectedList[i][2]
        # remove col-name row 
        expectedTruePositives = len(expectedList) - 1
        if photoID in expectedDict:
            expectedDict[photoID].append(i)
        else:
            expectedDict[photoID] = [i]
                
    with open('outputExample.csv', 'r') as results:
        res = csv.reader(results)
        resList1 = list(res)
        resList = list(filter(lambda row: row[11] != "Anomaly", resList1))
        # todo: filter out anomalies (skip first row of CSV ** asuming there is a title row **)
        for j in range(1, len(resList)): 
            resultRow = resList[j]
            photoID2 = resultRow[2]
            # if photo not in results dictionary that means there were no animals in the entire photo so throw FP
            if photoID2 not in expectedDict:
                falsePositives+=1
            else:
                rows = expectedDict.get(photoID2)
                matchedWithExpected = False
                for i in rows:
                    # 1 is expected values; 2 is ouput values
                    row = expectedList[i]
                    x1 = int(row[5])
                    y1 = int(row[6])
                    x2 = int(resultRow[5])
                    y2 = int(resultRow[6])
                    dist = math.hypot(x2 - x1, y2 - y1)
                    # randomly chose 5 but 10 is too big because made expected set find false positives in itself
                    if dist < 5:
                        # check bounding boxes
                        midX1 = (int(row[7]) + int(row[9])) / 2
                        midY1 = (int(row[8]) + int(row[10])) / 2
                        midX2 = (int(resultRow[7]) + int(resultRow[9])) / 2
                        midY2 = (int(resultRow[8]) + int(resultRow[10])) / 2
                        dist2 = math.hypot(midX2 - midX1, midY2 - midY1)
                        hotSpotDistances.append(dist)
                        registrationDistances.append(dist2)
                        matchedWithExpected = True
                        # classification accuracy
                        if (row[12] == resultRow[12]):
                            classificationTrue += 1 
                        else:
                            classificationFalse += 1
                if (matchedWithExpected == False):
                    falsePositives+=1
                

    print("Percent of hot spots found: " + str((classificationTrue + classificationFalse) / expectedTruePositives))
    print("There were " + str(falsePositives) + " false positives.")
    if ((classificationTrue + classificationFalse) > 0):
        print("There was a classification accuracy of " + str((classificationTrue / (classificationTrue + classificationFalse)) * 100) + " percent.")
    if (len(hotSpotDistances) > 0):
        print("There was an average hot spot distance of " + str(sum(hotSpotDistances) / len(hotSpotDistances)))
    if (len(registrationDistances) > 0):
        print("There was an average registration distance of " + str(sum(registrationDistances) / len(registrationDistances)))
