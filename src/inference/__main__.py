import os

def convertThermal16bitTo8bit(folder):
    print('Converting thermal data...')

def detectHotspots(folder):
    print('Detecting hotspots...')

def registerThermalAndColorImages(folder):
    print('Registering thermal and color images...')

def extractThumbnails(folder):
    print('Extracting hotspot thumbnails from color images...')

def classifyThumbnails(folder):
    print('Classifying hotspot thumbnails...')

def validate(folder):
    print('Validating...')

cwd = os.getcwd()
convertThermal16bitTo8bit(cwd)
detectHotspots(cwd)
registerThermalAndColorImages(cwd)
extractThumbnails(cwd)
classifyThumbnails(cwd)
validate(cwd)
