import argparse
import sys
import os
import numpy as np
from PIL import Image

# Data directory
parser = argparse.ArgumentParser(description='Command line interface for thermal image normalization')
parser.add_argument('--dir', type=str, default=None, help='relative path to the directory containing the 8-bit images')
# Parse
args = parser.parse_args(sys.argv[1:])

directory = args.dir
all_files = os.listdir(directory)

image_files = [x for x in all_files if (x.find('8BIT-N.PNG') != -1)]

cur_data = np.array(Image.open(os.path.join(directory, image_files[0])))

print('Type of loaded data: {}'.format(type(cur_data)))
print('Data type of array: {}'.format(cur_data.dtype))
print('Dimensions of loaded data: {}'.format(cur_data.shape))
print('Maximum: {}, Minimum: {}'.format(np.max(cur_data), np.min(cur_data)))
