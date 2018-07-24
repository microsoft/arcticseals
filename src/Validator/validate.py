import csv
import math 

'''
to dos: 
filter out anomalies in the csv we populate (results)
figure out why hotspotDistances doesn't have the complete length of 124; the Percent of hotspots found should be 100% since the two files have the same content right now

'''

# metrics:
falsePositives = 0
hotSpotDistances = []
registrationDistances = []
classificationTrue = 0
classificationFalse = 0
expectedTruePositives = 0
actualTruePositives = 0
# f1 = file('outputExample.csv', 'r')
with open('validationWithoutAnomalies.csv', 'r') as answers:
    ans = csv.reader(answers)

# col 5 and 6 = hotspot
# col 7-10 = registration
# col 12 = species_id 


    masterlist = list(ans)
    # dictionary with photoIds (thermal image names) and pointers to the rows with that image
    mydict = {}

    for i in range(len(masterlist)): 
        # assume thermal phone name is id and is in 3rd (index 2) column
        photoID = masterlist[i][2]
        expectedTruePositives = len(masterlist)
        rows = mydict.get(photoID, [])
        if (rows == []):
            mydict[photoID] = [i];
        else:
            if rows:
                mydict[photoID] = rows.append(i)
    with open('validationWithoutAnomalies.csv', 'r') as results:
        res = csv.reader(results)
        resList = list(res)
        # todo: filter out anomalies (skip first row of CSV ** asuming there is a title row **)
        for j in range(1, len(resList)): 
            resultRow = resList[j]
            photoID2 = resultRow[2]
            rows = mydict.get(photoID2, [])
            if (rows == []):
                falsePositives+=1
            else:
                if rows:
                    for i in rows:
                        row = masterlist[i]
                        x1 = int(row[5])
                        y1 = int(row[6])
                        x2 = int(resultRow[5])
                        y2 = int(resultRow[6])
                        dist = math.hypot(x2 - x1, y2 - y1)
                        # decide that detected hotspot if < 10
                        if dist < 10:
                            # check bounding boxes
                            midX1 = (int(row[7]) + int(row[9])) / 2
                            midY1 = (int(row[8]) + int(row[10])) / 2
                            midX2 = (int(resultRow[7]) + int(resultRow[9])) / 2
                            midY2 = (int(resultRow[8]) + int(resultRow[10])) / 2
                            dist2 = math.hypot(midX2 - midX1, midY2 - midY1)
                            hotSpotDistances.append(dist)
                            registrationDistances.append(dist2)
                            # classification accuracy
                            if (row[12] == resultRow[12]):
                                classificationTrue += 1 
                            else:
                                classificationFalse += 1
                        else:
                            falsePositives += 1
    print("Percent of hot spots found: " + str(len(hotSpotDistances) / expectedTruePositives))
    print("There were " + str(falsePositives) + " false positives.")
    if ((classificationTrue + classificationFalse) > 0):
        print("There was a classification accuracy of " + str((classificationTrue / (classificationTrue + classificationFalse)) * 100) + " percent.")
    if (len(hotSpotDistances) > 0):
        print("There was an average hot spot distance of " + str(sum(hotSpotDistances) / len(hotSpotDistances)))
    if (len(registrationDistances) > 0):
        print("There was an average registration distance of " + str(sum(registrationDistances) / len(registrationDistances)))
    
        
                        
                        
                
            

# f1.close()
# f3.close()