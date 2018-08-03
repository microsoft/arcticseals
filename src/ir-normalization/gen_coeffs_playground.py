import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import pickle


# Setable parameters
image_directory = './ArcticSealsData01_Thermal'
num_images = 5000
pixel_height = 512 # Must be either 512 or 480

all_files = os.listdir(image_directory)
image_files = [x for x in all_files if (x.find('16BIT.PNG') != -1)]

if not os.path.exists('hist_dump.p'):
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

    dump_object = {}
    dump_object['unique_C'] = unique_C
    dump_object['unique_S'] = unique_S
    dump_object['unique_P'] = unique_P
    dump_object['unique_counts_C'] = unique_counts_C
    dump_object['unique_counts_S'] = unique_counts_S
    dump_object['unique_counts_P'] = unique_counts_P

    pickle.dump(dump_object, open('hist_dump.p', 'wb'))

else:
    dump_object = pickle.load(open('hist_dump.p', 'rb'))
    unique_C = dump_object['unique_C']
    unique_S = dump_object['unique_S']
    unique_P = dump_object['unique_P']
    unique_counts_C = dump_object['unique_counts_C']
    unique_counts_S = dump_object['unique_counts_S']
    unique_counts_P = dump_object['unique_counts_P']
    
# Generate the histogram
plt.scatter(unique_C, unique_counts_C, s=10, marker='+', c='r')
plt.scatter(unique_S, unique_counts_S, s=10, marker='+', c='b')
plt.scatter(unique_P, unique_counts_P, s=10, marker='+', c='g')
plt.grid(True)
plt.show(block=True)

# Generate the relational scaling components using C as the reference
cdf_C = np.cumsum(unique_counts_C) / np.sum(unique_counts_C)
cdf_S = np.cumsum(unique_counts_S) / np.sum(unique_counts_S)
cdf_P = np.cumsum(unique_counts_P) / np.sum(unique_counts_P)

plt.plot(unique_C, cdf_C, c='r')
plt.plot(unique_S, cdf_S, c='b')
plt.plot(unique_P, cdf_P, c='g')
plt.grid(True)
plt.show(block=True)

# C vs. S
percentiles = np.linspace(0.01, 1, num=100)
mapping = np.zeros((len(percentiles), 2))

cur_per = 0
for ix in range(len(unique_C)):
    if cdf_C[ix] > percentiles[cur_per]:
        mapping[cur_per, 0] = unique_C[ix]
        cur_per += 1

cur_per = 0
for ix in range(len(unique_S)):
    if cdf_S[ix] > percentiles[cur_per]:
        mapping[cur_per, 1] = unique_S[ix]
        cur_per += 1

plt.scatter(mapping[:,0], mapping[:,1])
plt.xlabel('C - red')
plt.ylabel('S - blue')
plt.grid(True)
plt.show(block=True)


fit_coeffs = np.polyfit(mapping[:,0], mapping[:,1], 1)

print(fit_coeffs)


