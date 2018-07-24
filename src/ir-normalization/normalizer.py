import os
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

# Data directory
directory = './ArcticSealsData01'
image_files = os.listdir(directory)
num_files = len(image_files)

bottom = 51000
top = 60000

successful = 0
for ix in range(num_files):
    try:
        cur_file = os.path.join(directory,image_files[ix])
        cur_data = np.array(Image.open(cur_file))
        if cur_data.shape[0] == 512:
            normalized = (cur_data - bottom) / (top - bottom)
            normalized = np.floor(normalized * 256).astype(np.uint8)
            successful += 1
    except:
        print('Unable to load {}'.format(cur_file))

print('Completed converting {} files'.format(successful))

