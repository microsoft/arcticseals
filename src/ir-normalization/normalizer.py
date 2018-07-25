"""Functions for transforming 16-bit thermal images into 8-bits"""
# Imports
import argparse
import os
import sys
import numpy as np
from PIL import Image

# Functions
def lin_normalize_image(image_array, bottom=None, top=None):
    """Linear normalization for an image array
    Inputs:
        image_array: np.ndarray, image data to be normalized
        bottom: float, value to map to 0 in the new array
        top: float, value to map to 1 in the new array
    Output:
        scaled_image: nd.ndarray, scaled image between 0 and 255
    """
    if bottom is None:
        bottom = np.min(image_array)
    if top is None:
        top = np.max(image_array)

    scaled_image = (image_array - bottom) / (top - bottom)
    scaled_image[scaled_image < 0] = 0
    scaled_image[scaled_image > 1] = 1

    scaled_image = np.floor(scaled_image * 256).astype(np.uint8)

    return scaled_image

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
    parser.add_argument('--indir', type=str,
                        required=True, help='relative path to directory containing images')
    parser.add_argument('--outdir', type=str,
                        default=None, help='relative path to the output directory')
    # Parse
    args = parser.parse_args(sys_args)

    # Store values
    input_directory = args.indir

    if args.outdir is None:
        output_directory = input_directory
    else:
        output_directory = args.outdir

    return input_directory, output_directory

def curate_files(input_directory, output_directory):
    """Generates name lists for input and output images
    Inputs:
        input_directory: string, path to the input image directory
        output_directory: string, path to the output image directory
    Output:
        input_files: list, contains the file names of the incoming images
        output_files: list, contains the file names of the outgoing images
    """
    all_files = os.listdir(input_directory)

    input_files = [x for x in all_files if x.find('16BIT.PNG') != -1]
    output_files = [x.replace('16BIT', '8BIT-N') for x in input_files]

    input_files = [os.path.join(input_directory, x) for x in input_files]
    output_files = [os.path.join(output_directory, x) for x in output_files]

    return input_files, output_files

def parse_filename(filename):
    """Gets the camera position argument from filename
    Input:
        filename: string, name of the image file
    Output:
        camera_pos: string, capital letter position of the camera
    """
    tokens = os.path.basename(filename).split('_')
 
    for token in tokens:
      if token == 'P' or token == 'C' or token == 'S':
        camera_pos = token
        break
    else:
      print('Warning: Bad filename format %s' % filename)

    return camera_pos
 

def get_scaling_values(filename, num_rows):
    """Returns the bottom and top scaling parameters based on filename
    Inputs:
        filename: string, name of the file
        num_rows: int, number of rows in the image
    Outputs:
        bottom: int, number that maps to 0 in scaled image
        top: int, number that maps to 255 in scaled image
    """
    camera_pos = parse_filename(filename)
    
    if camera_pos == "P":
        if num_rows == 512:
            bottom = 53500
            top = 56500
        elif num_rows == 480:
            bottom = 50500
            top = 58500
    elif camera_pos == "C":
        bottom = 50500
        top = 58500
    else: #S and default
        bottom = 51000
        top = 57500

    return bottom, top

def main(sys_args):
    """Function that is called by the command line"""
    # Parses the arguments
    input_directory, output_directory = parse_arguments(sys_args[1:])
    input_files, output_files = curate_files(input_directory, output_directory)
    print('Found {} files for processing'.format(len(input_files)))
    
    successful = 0
    for index, in_file in enumerate(input_files):
        try:
            cur_data = np.array(Image.open(in_file))
            bottom, top = get_scaling_values(in_file, cur_data.shape[0])
            normalized = lin_normalize_image(cur_data, bottom, top)

            save_im = Image.fromarray(normalized)
            save_im.save(output_files[index])
            successful += 1
        except IOError:
            print('Unable to load {}'.format(output_files[index]))

    print('Completed converting {} files'.format(successful))

if __name__ == "__main__":
    main(sys.argv)
