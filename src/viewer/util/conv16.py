import cv2
import numpy as np
import os
import pathlib

#define the path
inputDir = 'G:\\'
inputPath = pathlib.Path(inputDir)
outputDir = 'E:\\noaa\\conv-thermal'

for currentFile in inputPath.glob("*.png"):
    currentFilename = str(currentFile.name)
    inputFile = os.path.join(inputDir, currentFilename)
    #img = cv2.imread(inputFile, -cv2.IMREAD_ANYDEPTH).astype(np.uint8)
    img = cv2.imread(inputFile, cv2.IMREAD_LOAD_GDAL).astype(np.uint8)
    outputFile = os.path.join(outputDir, currentFilename)
    cv2.imwrite(outputFile, img)
