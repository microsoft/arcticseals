import os

# For details of what each of these steps should take as input and produce as a result, please see:
# https://teams.microsoft.com/l/entity/com.microsoft.teamspace.tab.wiki/tab%3a%3abc2ceef2-46a1-4c0e-8deb-17fc1afc9983?label=Inference+%26+Validation+Pipeline+in+Wiki&context=%7b%0d%0a++%22subEntityId%22%3a+%22%7b%5c%22pageId%5c%22%3a2%2c%5c%22sectionId%5c%22%3a8%2c%5c%22origin%5c%22%3a2%7d%22%2c%0d%0a++%22canvasUrl%22%3a+%22https%3a%2f%2fteams.microsoft.com%2fl%2ftab%2f19%253adfaf4e05a29741fe8a2dc3cf8d0c8f57%2540thread.skype%2ftab%253a%253abc2ceef2-46a1-4c0e-8deb-17fc1afc9983%3flabel%3dWiki%26tenantId%3d72f988bf-86f1-41af-91ab-2d7cd011db47%22%2c%0d%0a++%22channelId%22%3a+%2219%3adfaf4e05a29741fe8a2dc3cf8d0c8f57%40thread.skype%22%0d%0a%7d&tenantId=72f988bf-86f1-41af-91ab-2d7cd011db47

# The folder starts out with 16-bit PNG thermal and JPG color imagery and the inference
# pipeline produces intermediate and final results in "hotspots.csv" in the same folder.
# See https://docs.python.org/2/library/csv.html for reading/writing CSV files.

# We will skip this step for now; the validation dataset can presume the thermal data is already 8-bit normalized (8BIT-N.JPG suffix)
#def convertThermal16bitTo8bit(folder):
#    print('Converting thermal data...')

def detectHotspots(folder):
    print('Detecting hotspots...')

def registerThermalAndColorImages(folder):
    print('Registering thermal and color images...')

    import sys
    sys.path.append('../image_registration/ir_to_rgb_registration')
    import image_registration

    file = folder + '\\..\\..\\data\\test.csv'
    fileOut = folder + '\\..\\..\\data\\testOut.csv'
    folderImages = folder + '\\..\\..\\data\\images\\'

    image_registration.registerThermalAndColorImages(file, fileOut, folderImages)


def extractThumbnails(folder):
    print('Extracting hotspot thumbnails from color images...')

def classifyThumbnails(folder):
    print('Classifying hotspot thumbnails...')
    # Couldn't figure out how to import different files, so need to set these parameters
    # Contact Jon Malsan for further questions
    function_name = '../ir-hotspot-rfc/hotspot_classifier.py'
    data_dir = './ArcticSealsData01_Thermal_N/'
    data_file = '../arcticseals/data/test.csv'
    model_file = 'pca_rfc_model_20180725_154906.p'
    out_file = '../ir-hotspot-rfc/output.csv'

    command = "python {} --datadir {} --datafile {} --modelfile {} --outfile {}".format(function_name,data_dir, data_file, model_file, out_file)
    os.system(command)

def validate(folder):
    print('Validating...')

cwd = os.getcwd()
#convertThermal16bitTo8bit(cwd)
detectHotspots(cwd)
registerThermalAndColorImages(cwd)
extractThumbnails(cwd)
classifyThumbnails(cwd)
validate(cwd)
