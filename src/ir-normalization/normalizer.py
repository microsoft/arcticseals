import os
import numpy as np
from PIL import Image

# Data directory
input_directory = './ArcticSealsData01'
output_directory = './normalizedImages'
all_files = os.listdir(input_directory)

image_files = [x for x in all_files if (x.find('16BIT.PNG') != -1)]
out_files = [x.replace('16BIT','8BIT-N') for x in image_files]

num_files = len(image_files)

# Corrections for the camera with 512 x 640 pixels
bottom512 = 51000
top512 = 60000

# Corrections for the camera with 480 x 640 pixels
bottom480 = 51000
top480 = 60000

successful = 0
for ix in range(num_files):
    try:
        in_file = os.path.join(input_directory,image_files[ix])
        out_file = os.path.join(output_directory, out_files[ix])
        cur_data = np.array(Image.open(in_file))

        if cur_data.shape[0] == 512:
            normalized = (cur_data - bottom512) / (top512 - bottom512)
        elif cur_data.shape[0] == 480:
            normalized = (cur_data - bottom480) / (top480 - bottom480)

        normalized = np.floor(normalized * 256).astype(np.uint8)  
        im = Image.fromarray(normalized)
        im.save(out_file)
        successful += 1
    except:
        print('Unable to load {}'.format(in_file))

print('Completed converting {} files'.format(successful))

