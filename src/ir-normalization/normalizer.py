import argparse
import os
import sys
import numpy as np
from PIL import Image

def lin_normalize_image(image_array, bottom=None, top= None):
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
    parser = argparse.ArgumentParser(description='Command line interface for thermal image normalization')
    parser.add_argument('--indir', type=str, required=True, help='relative path to directory containing images')
    parser.add_argument('--outdir', type=str, default=None, help='relative path to the output directory')
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

    input_files = [x for x in all_files if (x.find('16BIT.PNG') != -1)]
    output_files = [x.replace('16BIT','8BIT-N') for x in input_files]

    input_files = [os.path.join(input_directory, x) for x in input_files]
    output_files = [os.path.join(output_directory, x) for x in output_files]

    return input_files, output_files


def main(sys_args):
    # Parses the arguments
    input_directory, output_directory = parse_arguments(sys_args[1:])
    input_files, output_files = curate_files(input_directory, output_directory)
    
    # Corrections for the camera with 512 x 640 pixels
    bottom512 = 51000
    top512 = 59000

    # Corrections for the camera with 480 x 640 pixels
    bottom480 = 51000
    top480 = 59000

    successful = 0
    for ix in range(len(input_files)):
        try:
            cur_data = np.array(Image.open(input_files[ix]))

            if cur_data.shape[0] == 512:
                normalized = lin_normalize_image(cur_data, bottom512, top512)
            elif cur_data.shape[0] == 480:
                normalized = lin_normalize_image(cur_data, bottom480, top480)

            im = Image.fromarray(normalized)
            im.save(output_files[ix])
            successful += 1
        except:
            print('Unable to load {}'.format(output_files[ix]))

    print('Completed converting {} files'.format(successful))

if __name__ == "__main__":
    main(sys.argv)
