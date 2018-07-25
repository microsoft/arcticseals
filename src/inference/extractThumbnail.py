import os
import pathlib
import json
from PIL import Image

#arg - csv filename.
# Example: python extractThumbnail.py training.json F:\ E:\noaa\crop-img
jsonName = sys.argv[1]  
inDir =  sys.argv[2]  
outDir = sys.argv[3]  

# Read training.json to artic
with open(jsonName) as json_data:
    data = json.load(json_data)
    artic = data['Artic']

#define the path
inputDir = pathlib.Path(inDir)
outputDir = pathlib.Path(outDir)

for i in range(0,len(artic)):
    currentFullFilename = artic[i]['filt_color']
    inputFile = os.path.join(inputDir, currentFullFilename)
    currentFilename = os.path.splitext(currentFullFilename)[0] + "_HOTSPOT_" + artic[i]['hotspot_id'] + ".JPG"
    outputFile = os.path.join(outputDir, currentFilename)
    img = Image.open(inputFile)

    x1 = int(artic[i]['thumb_left'])
    y1 = int(artic[i]['thumb_top'])
    x2 = int(artic[i]['thumb_right'])
    y2 = int(artic[i]['thumb_bottom'])
    area=(x1,y1,x2,y2)
    crop_img = img.crop(area)
    crop_img.save(outputFile)