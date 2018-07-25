import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

# Setable parameters
image_directory = './ArcticSealsTrain1807221152/test'
num_images = 1000
pixel_height = 512 # Must be either 512 or 480

all_files = os.listdir(image_directory)
image_files = [x for x in all_files if (x.find('16BIT.PNG') != -1)]

# Grab a random permutation of the data
indices = np.arange(len(image_files),dtype=np.int)
np.random.shuffle(indices)
data_C = np.zeros((pixel_height,640,num_images))
data_S = np.zeros((pixel_height,640,num_images))
data_P = np.zeros((pixel_height,640,num_images))

s_count = 0
c_count = 0
p_count = 0
loaded = 0

for ix in range(len(image_files)):
    cur_file = os.path.join(image_directory, image_files[indices[ix]])
    cur_data = np.array(Image.open(cur_file))

    if cur_data.shape[0] == pixel_height:
        if cur_file.find('_C_') != -1:
            data_C[:, :, c_count] = cur_data
            c_count += 1
        elif cur_file.find('_S_') != -1:
            data_S[:, :, s_count] = cur_data
            s_count += 1
        elif cur_file.find('_P_') != -1:
            data_P[:, :, p_count] = cur_data
            p_count += 1
        loaded += 1

        if loaded == num_images:
            break

# Truncate array to just the found values
data_C = data_C[:, :, :c_count]
data_S = data_S[:, :, :s_count]
data_P = data_P[:, :, :p_count]

# Histogram counter on unique values
unique_C, unique_counts_C = np.unique(data_C, return_counts=True)
unique_S, unique_counts_S = np.unique(data_S, return_counts=True)
unique_P, unique_counts_P = np.unique(data_P, return_counts=True)

# Generate the histogram
plt.scatter(unique_C, unique_counts_C, s=10, marker='+', c='r')
plt.scatter(unique_S, unique_counts_S, s=10, marker='+', c='b')
plt.scatter(unique_P, unique_counts_P, s=10, marker='+', c='g')
plt.grid(True)
plt.show(block=True)
