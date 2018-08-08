import pandas as pd
import shutil
import os
import sys
sys.path.append('../ir-normalization')
sys.path.append('../image_registration/ir_to_rgb_registration')
from image_registration import *
import normalizer
import numpy as np
import pyprind
import glob
import joblib
import multiprocessing
import png

def find_file_in_dirs(source_dirs, filename):
    return_file = None
    for source_dir in source_dirs:
        possible_file = os.path.join(source_dir, filename)
        if os.path.isfile(os.path.join(possible_file)):
            return_file = possible_file
    return return_file


def main():
    # CSV file with all the hotspot detections
    annotation_csv = '/datadrive/Research/arcticseals/src/dataset-generator/raw.csv'
    # The list of images, which we want to select for the detection dataset
    # Please use basenames only, i.e. without the image type in the name
    # E.g., omnit from the file CHESS_FL12_C_160421_231526.530_COLOR-8-BIT.JPG, omnit
    # the tag _COLOR-8-BIT.JPG and put only CHESS_FL12_C_160421_231526.530 in the list
    image_basename_list = '/datadrive/sealdata_blob01_complete/test_clean.txt'
    # List of directories, where required files might be located
    source_dirs = ['/datadrive/seal_blobs/color01', '/datadrive/seal_blobs/thermal01']
    # List of file tags to copy for each image
    tags = ['_COLOR-8-BIT.JPG', '_THERM-16BIT.PNG', '_THERM-8-BIT.JPG'] # _THERM-REG-16BIT.JPG _THERM-8BIT-N.PNG 
    # Whether to compute and store the unregsitered normalized IR image, this will be 16 bit
    store_normalized_ir = True
    # Whether to compute and store the registered IR image, this will be normalized 16 bit format
    compute_registered_ir = True

    # In the seals data, the provdied bounding boxes are not tight around the object, 
    # actually we only have object centers, but we need tight bounding boxes for training and 
    # evaluation. Specify the mean object width/height of the foreground objects
    object_width = 128
    # The folder of the output directory
    output_dir = '/datadrive/sealdata_blob01_complete/test'

    
    # Read csv
    ann = pd.read_csv(annotation_csv)
    object_radius = object_width // 2
    object_centers_x = (ann['thumb_left'] + ann['thumb_right']) / 2
    object_centers_y = (ann['thumb_top'] + ann['thumb_bottom']) / 2
    ann['thumb_left'] = object_centers_x - object_radius
    ann['thumb_right'] = object_centers_x + object_radius
    ann['thumb_top'] = object_centers_y - object_radius
    ann['thumb_bottom'] = object_centers_y + object_radius

    im_basenames = open(image_basename_list, 'rt').read().splitlines()
    im_basenames = [imb for imb in im_basenames if imb is not '']
    #for im_basename in pyprind.prog_bar(im_basenames):
    def process_image(im_basename):
        # Normalize raw image and store in *output_dir*
        if store_normalized_ir:
            in_file_n = find_file_in_dirs(source_dirs, im_basename + '_THERM-16BIT.PNG')
            out_file_n = os.path.join(output_dir, im_basename + '_THERM-16BIT-N.PNG')
            if in_file_n:
                normalizer.process_file(1, False, 1, 1, in_file_n, out_file_n, 1)
            else:
                print('ERROR: Cannot compute normalized IR image, because the 16 bit raw IR ' + 
                      'image is missing for ' + im_basename)

        # Register IR image to RGB image space and store the warped image
        # Uses the normalized image, if we can get it 
        if compute_registered_ir:
            # use normalzied image as input
            in_file_ir_reg = find_file_in_dirs(source_dirs, im_basename + '_THERM-16BIT.PNG')
            out_file_ir_reg = os.path.join(output_dir, im_basename + '_THERM-REG-16BIT.PNG')
            in_file_color_reg = find_file_in_dirs(source_dirs, im_basename + '_COLOR-8-BIT.JPG')
            # If we have all input files for registration
            if os.path.isfile(out_file_ir_reg):
                print('Registered IR image for {} already exists, skipping...'.format(im_basename))
            elif find_file_in_dirs(source_dirs, os.path.basename(out_file_ir_reg)):
                print('Registered IR image for {} exists in the source directories, copying...'.format(im_basename))
                shutil.copy(find_file_in_dirs(source_dirs, os.path.basename(out_file_ir_reg)), output_dir)
            elif in_file_ir_reg and in_file_color_reg:
                # Read input images
                image_ir_n = imreadIR(in_file_ir_reg)[0]
                image_to_warp = imreadIR(out_file_n)[1]
                image_color = cv2.imread(in_file_color_reg)
                # compute transform
                ret, transform, inliers = computeTransform(image_color, image_ir_n)
                if ret:
                    image_warped = cv2.warpPerspective(image_to_warp, transform, (image_color.shape[1], image_color.shape[0]))
                    #cv2.imwrite(out_file_ir_reg, image_warped)
                    with open(out_file_ir_reg, 'wb') as f:
                        writer = png.Writer(width=image_warped.shape[1],
                                height=image_warped.shape[0],
                                bitdepth=16,
                                greyscale=True)
                        pixel_list = image_warped.tolist()
                        writer.write(f, pixel_list)
                else:
                    print("Failed to register {}".format(im_basename))

            else:
                print('Couldn\'t find color and IR images for {} for registration.'.format(im_basename))

        # Copy all images related to *im_basename* to *output_dir*
        for source_dir in source_dirs:
            for tag in tags:
                source_file = os.path.join(source_dir, im_basename + tag)
                if os.path.isfile(source_file):
                    shutil.copy(source_file, output_dir)
        # Get annotations for this image
        mask = ann['color_image_name'].str.startswith(im_basename)
        mask = np.logical_and(mask, np.logical_or(np.logical_or(ann['hotspot_type'] == 'Animal', 
                                                                ann['hotspot_type'] == 'Evidence of Seal'),
                                                  ann['hotspot_type'] == 'Duplicate'))
        rel_ann = ann[mask]
        # Write annotations
        object_label = rel_ann['species_id']
        object_label.to_csv(os.path.join(output_dir, im_basename + '.bboxes.labels.tsv'), index=False)
        object_bboxes = rel_ann[['thumb_left', 'thumb_top', 'thumb_right', 'thumb_bottom']]
        object_bboxes.to_csv(os.path.join(output_dir, im_basename + '.bboxes.tsv'), 
                    index=False, header=False, sep=' ', float_format='%i')

    num_cores = multiprocessing.cpu_count()
    results = joblib.Parallel(n_jobs=num_cores, verbose=15)(joblib.delayed(process_image)(im_basename) for im_basename in im_basenames)

    # Check if we have all files for all images
    # We do this by making sure that we have the same number of files for each basename
    image_count = []
    for im_basename in pyprind.prog_bar(im_basenames):
        image_count.append(len(glob.glob(os.path.join(output_dir, im_basename + '*'))))
    max_count = np.max(image_count)
    failed_image_count = np.sum(np.array(image_count, int) != max_count)
    print("For each image, we should have {} files.".format(max_count)) 
    if failed_image_count > 0:
        print("{} images have less files.".format(failed_image_count))
        response = input("Shall we delete those non-complete images? [y/n]")
        while response.lower() not in ['y','n']:
            response = input("Please respond only with either 'Y' or 'N'. Try again: ")
        if response.lower() == 'y':
            for idx, im_basename in pyprind.prog_bar(enumerate(im_basenames)):
                if image_count[idx] < max_count:
                    for file_to_delete in glob.glob(os.path.join(output_dir, im_basename + '*')):
                        print('Deleting', file_to_delete)
                        os.remove(file_to_delete)

    print('Finished!')


if __name__ == '__main__':
    main()
