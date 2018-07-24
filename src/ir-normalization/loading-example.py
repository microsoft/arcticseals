import os
import numpy as np
from PIL import Image

# Data directory
input_directory = './normalizedImages'
all_files = os.listdir(input_directory)

image_files = [x for x in all_files if (x.find('8BIT-N.PNG') != -1)]

num_files = len(image_files)

cur_data = np.array(Image.open(os.path.join(input_directory, image_files[0])))

print('Type of loaded data: {}'.format(type(cur_data)))
print('Data type of array: {}'.format(cur_data.dtype))
print('Dimensions of loaded data: {}'.format(cur_data.shape))
print('Maximum: {}, Minimum: {}'.format(np.max(cur_data), np.min(cur_data)))
