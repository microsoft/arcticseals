import argparse
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

# Data directory
# Assumes that the files are in the same directory
parser = argparse.ArgumentParser(description='Command line interface for thermal image normalization')
parser.add_argument('--dir', type=str, default=None, help='relative path to the directory containing the 8-bit images')
# Parse
args = parser.parse_args(sys.argv[1:])

directory = args.dir
all_files = os.listdir(directory)

original_files = [x for x in all_files if (x.find('16BIT.PNG') != -1)]
normalized_files = [x.replace('16BIT.PNG', '16BIT-N.PNG') for x in original_files]

original = np.array(Image.open(os.path.join(directory, original_files[0])))
normalized = np.array(Image.open(os.path.join(directory, normalized_files[0])))

unique_original = np.unique(original)
unique_normalized = np.unique(normalized)

print('Number of unique in original: {}'.format(len(unique_original)))
print('Number of unique in normalized: {}'.format(len(unique_normalized)))

transform = np.polyfit(unique_original, unique_normalized, 1)
print('Slope of transform: {}'.format(transform[0]))
print('Offset of transform: {}'.format(transform[1]))

rev_transform = (normalized - transform[1]) / transform[0]
difference = original - rev_transform

plt.imshow(difference)
plt.colorbar()
plt.title('Original - (Un-transformed normalized) ')
plt.show(block=True)

print('Mean change of transform: {}'.format(np.mean(difference)))
print('STD of difference: {}'.format(np.std(difference, ddof=1)))