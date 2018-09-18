import csv
import math 
from collections import defaultdict
import numpy as np

'''
about:
this code assumes that the output file (the result of our ML) matches the same csv schema as validation.csv, including the first row being collumn names
it loads the expected (validation.csv) grountTruth into a dictionnary and then checks whether ouput found them
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
groundTruthPositives = 0
hotspotLocationTrue = 0
registrationTrue = 0

# This set of metrics report accuracy when spatial location match of identified hot spots and ground truth is required.
falsePositivesLM = 0
falseNegativesLM = 0
truePositivesLM = 0

# Sort the rows on x_pos of the hot spot, if they have the same photoId(on same image)
def getSortKey(item):
    return item[5]
    
with open(groundTruthFile, 'r') as grountTruth:
    # col 5 and 6 = hotspot
    # col 7-10 = registration
    # col 12 = species_id 
    ans = csv.reader(grountTruth)
    ans1 = list(filter(lambda row: row[11] != 'Anomaly', ans))
    groundTruthList = list(ans1)

    # Dictionary with photoIds (thermal image names) and pointers to the rows with that image
    groundTruthDict = {}

    # fill the dictionary with the ground truth information
    # start from row 1 to exclude col-name row
    for i in range(1, len(groundTruthList)): 
        # assume thermal phone name is id and is in 3rd (index 2) column
        photoID = groundTruthList[i][2]
        # remove col-name row 
        groundTruthPositives = len(groundTruthList) - 1
        if photoID in groundTruthDict:
            groundTruthDict[photoID].append(i)
        else:
            groundTruthDict[photoID] = [i]
                
    with open(classificationResultsFile, 'r') as results:
        res = csv.reader(results)
        resList1 = list(res)
        # filter out anomalies
        resList = list(filter(lambda row: row[11] != 'Anomaly', resList1))
        resDict = {}

        # Start from the row 1 to exlude the title/col-name row
        for j in range(1, len(resList)):
            resPhotoId = resList[j][2]
            if resPhotoId in resDict:
                resDict[resPhotoId].append(j)
            else:
                resDict[resPhotoId] = [j]

        # Each image may have several hot spots identfied. 
        # Assuming the spacial distribution pattern of hotspots on classifcation results and ground truth are the same, sort the rows
        # on its x_positon, and macth the spots.
        # TODO: need to consider method to macth the spots when number of rows are different in result and ground truth
        for key in resDict:
            # if photo not in expected dictionary that means there were no animals in the entire photo so throw FalsePositive
            if key not in groundTruthDict:
                falsePositives+=len(resDict[key])
                falsePositivesLM+=len(resDict[key])
            else:
                resRows = resDict.get(key)
                gtRows = groundTruthDict.get(key)

                lengthDiff = len(resRows) - len(gtRows)
                minLength = min(len(resRows), len(gtRows))


                if (lengthDiff >= 0): 
                    # TODO: updated caculation method when ground truth includes 'Anormaly'
                    falsePositives+=lengthDiff
                    falsePositivesLM+=lengthDiff
                else:
                    falseNegatives+=lengthDiff
                    falseNegativesLM+=lengthDiff

                truePositives+=minLength

                # caldulate metrics with location match requirement
                resRowsData = []
                gtRowsData = []
                for k in resRows:
                    resRowsData.append(resList[k])

                if (len(resRowsData) > 1):
                    resRowsData.sort(key=getSortKey)

                for l in gtRows:
                    gtRowsData.append(resList[l])

                if (len(gtRowsData) > 1):
                    gtRowsData.sort(key=getSortKey)

                for g in gtRowsData:
                    minDist = 99999999
                    for r in resRowsData:
                        if r[1] != 'MatchesGroundTruth':
                            x1 = int(g[5])
                            y1 = int(g[6])
                            x2 = int(r[5])
                            y2 = int(r[6])
                            dist = math.hypot(x2 - x1, y2 - y1)
                            if dist < minDist:
                                minDist = dist
                                minResRow = r
                    
                    # Was there a detected hotspot within tolerance of this ground truth hotspot?
                    hotSpotDistances.append(minDist)
                    if minDist < locationOffsetTolerance:
                        truePositivesLM+=1
                        minResRow[1] = 'MatchesGroundTruth' # Hackily reuse the 'timestamp' field to indicate that we have a match
                        # if minResRow[13] == e[13]:
                        #     classificationTrue += 1
                        # else:
                        #     classificationFalse += 1

                for r in resRowsData:
                    if r[1] != 'MatchesGroundTruth':
                        falsePositivesLM += 1
                    
                # Remove double counting when ground truth has more hot spots
                if (minLength < 0):
                    falsePositivesLM += minLength

    # Print results on screen
    print('Accuracy assessment for hot spot detection on thermal images')
    print('Number of hot spots in grount truth: {}'.format(groundTruthPositives))
    print('Number of hot spots found: {}'.format(str(len(resList)-1)))
    print('True positive(count): {}      True positve(%): {}%'.format(truePositives, str(truePositives / groundTruthPositives * 100)))
    print('False positive count: {}'.format(falsePositives))
    print('False negative count: {}'.format(falseNegatives))
    print('\n')

    print('Accuracy assessment for hot spot detection with LOCATION MATCH on thermal images')
    print('Number of hot spots in ground truth: {}'.format(groundTruthPositives))
    print('Number of hot spots found: {}'.format(str(len(resList)-1)))
    print('True positive(count): {}      True positve(%): {}%'.format(truePositivesLM, str(truePositivesLM / groundTruthPositives * 100)))
    print('False positive count: {}'.format(falsePositivesLM))
    print('False negative count: {}'.format(falseNegativesLM))

    print('\n')
    print('Location offset for hot spots on thermal images')
    print('10th percentile: {} pixles'.format(np.percentile(hotSpotDistances, 10)))
    print('50th percentile: {} pixles'.format(np.percentile(hotSpotDistances, 50)))
    print('90th percentile: {} pixles'.format(np.percentile(hotSpotDistances, 90)))

    # Print result to a file
    with open('assessmentResults.txt', 'w') as f:
        print('Accuracy assessment for hot spot detection on thermal images', file=f)
        print('Number of hot spots in ground truth: {}'.format(groundTruthPositives), file=f)
        print('Number of hot spots found: {}'.format(str(len(resList)-1)), file=f)
        print('True positive(count): {}      True positve(%): {}%'.format(truePositives, str(truePositives / groundTruthPositives * 100)), file=f)
        print('False positive count: {}'.format(falsePositives), file=f)
        print('False negative count: {}'.format(falseNegatives), file=f)
        print('\n'*3, file=f)

        print('Accuracy assessment for hot spot detection with LOCATION MATCH on thermal images', file=f)
        print('Number of hot spots in ground truth: {}'.format(groundTruthPositives), file=f)
        print('Number of hot spots found: {}'.format(str(len(resList)-1)), file=f)
        print('True positive(count): {}      True positve(%): {}%'.format(truePositivesLM, str(truePositivesLM / groundTruthPositives * 100)), file=f)
        print('False positive count: {}'.format(falsePositivesLM), file=f)
        print('False negative count: {}'.format(falseNegativesLM), file=f)

        print('\n'*3, file=f)
        print('Location offset for hot spots on thermal images', file=f)
        print('10th percentile: {} pixles'.format(np.percentile(hotSpotDistances, 10)), file=f)
        print('50th percentile: {} pixles'.format(np.percentile(hotSpotDistances, 50)), file=f)
        print('90th percentile: {} pixles'.format(np.percentile(hotSpotDistances, 90)), file=f)

