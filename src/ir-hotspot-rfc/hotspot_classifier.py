"""Functions and Command line Script for classifying hotspots"""
# Standard Inputs
import argparse
import os
import sys
import pickle
# Pip Inputs
import pandas as pd
import numpy as np
from PIL import Image

def square_crop(image, x_pos, y_pos, size=35):
    """Returns a square crop of size centered on (x_pos, y_pos)
    Inputs:
        image: np.ndarray, image data in an array
        x_pos: int, x-coordinate of the hotspot
        y_pos: int, y-coordinate of the hotspot
        size: int, side length for the returned crop
    Outputs:
        cropped_image: np.ndarray, cropped image data of size (size x size)
    """
    size = (np.floor(size/2) * 2 + 1).astype(np.int) #Forces size to be odd
    offset = ((size - 1) / 2).astype(np.int)

    x_low = x_pos - offset
    x_high = x_pos + offset + 1

    y_low = y_pos - offset
    y_high = y_pos + offset + 1

    if x_low < 0:
        x_high = x_high - x_low
        x_low = 0

    if x_high > image.shape[1]:
        x_low = x_low - (x_high - image.shape[1])
        x_high = image.shape[1]

    if y_low < 0:
        y_high = y_high - y_low
        y_low = 0

    if y_high > image.shape[0]:
        y_low = y_low - (y_high - image.shape[0])
        y_high = image.shape[0]

    cropped_image = image[y_low:y_high, x_low:x_high]

    return cropped_image

def parse_arguments(sys_args):
    """Parses the input and output directories from the arguments
    Input:
        sys_args: list, the arguments to be parsed
    Output:
        input_directory: string, path to the input image directory
        output_directory: string, path to the output image directory
    """
    # Set up parse
    parser = argparse.ArgumentParser(
        description='Command line interface for thermal image normalization')
    parser.add_argument('--datadir', type=str,
                        required=True, help='relative path to directory containing images')
    parser.add_argument('--datafile', type=str,
                        default=None, help='path to the csv file containing identified hotspots')
    parser.add_argument('--modelfile', type=str,
                        default=None, help='path to the pickle dump of the trained classifier')
    parser.add_argument('--outfile', type=str,
                        default='output.csv', help='path to write the output csv to')
    # Parse
    args = parser.parse_args(sys_args)

    # Store values
    data_file = args.datafile
    data_directory = args.datadir
    model_file = args.modelfile
    output_file = args.outfile

    print('Using input csv: {}'.format(data_file))
    print('Using data directory for inputs: {}'.format(data_directory))
    print('Using classification model: {}'.format(model_file))
    print('Will write classifications to: {}'.format(output_file))

    return data_file, data_directory, model_file, output_file

def load_data(data_frame, data_directory):
    """Loads the flattened thumbnails for classification
    Inputs:
        data_frame: pandas df, the information about the data
        data_directory: string, the path to the directory for the images
    Outputs:
        data: np.ndarray, array with the image thumbnails where the
            row matches row in the data_frame and column is the flattened
            image data
    """
    thumb_size = 35
    data = np.zeros((len(data_frame), thumb_size**2))

    for index in range(len(data_frame)):
        try:
            file_name = os.path.join(data_directory, data_frame['filt_thermal16'][index])
            file_name = file_name.replace('16BIT', '8BIT-N')

            image = np.array(Image.open(file_name))
            cropped = square_crop(image, data_frame['x_pos'][index], data_frame['y_pos'][index])
            data[index, :] = cropped.flatten()
        except FileNotFoundError:
            print('Could not find: {}'.format(file_name))

    return data

def classify_data(data_file, data_directory, model_file, output_file):
    """Data loading, classifying and output logic. For compatibility with library inputs
    Inputs:
        data_file: string, path to the input csv file
        data_directory: string, path to the thermal images
        model_file: string, path to the classifier model
        output_file: string, path to the output csv file
    """
    print('Loading the data files...')
    df = pd.read_csv(data_file)
    data = load_data(df, data_directory)

    print('Loading the classifier...')
    clf = pickle.load(open(model_file, 'rb'))
    print('Beginning the classification...')
    y_predict = clf.predict(data)
    y_predict_proba = np.max(clf.predict_proba(data), axis=1)

    print('Writing the output...')
    y_predict_label = []
    labels = ['Anomaly', 'Animal']
    for _, prediction in enumerate(y_predict):
        y_predict_label.append(labels[prediction])

    df['hotspot_type'] = y_predict_label
    df['ir_confidence'] = y_predict_proba

    df.to_csv(output_file)

    print('Wrote classification to: {}'.format(output_file))

# Main Program
def main(sys_argv):
    """Classifies the hotspots in data_file and writes output_file from command line
    Example usage: python -W ignore hotspot_classifier.py --datadir ./ArcticSealsData01_Thermal_N/
                --datafile ../arcticseals/data/test.csv --modelfilepca_rfc_model_20180725_154906.p
    """
    data_file, data_directory, model_file, output_file = parse_arguments(sys_argv[1:])
    classify_data(data_file, data_directory, model_file, output_file)

if __name__ == '__main__':
    main(sys.argv)
