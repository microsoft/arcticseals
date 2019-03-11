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
import scipy.spatial.distance

def find_file_in_dirs(source_dirs, filename):
    return_file = None
    for source_dir in source_dirs:
        possible_file = os.path.join(source_dir, filename)
        if os.path.isfile(os.path.join(possible_file)):
            return_file = possible_file
    return return_file


def main():
    # CSV file with all the hotspot detections
    annotation_csv = '../../data/updated_labels.csv'
    # The list of images, which we want to select for the detection dataset
    # Please use basenames only, i.e. without the image type in the name
    # E.g., omnit from the file CHESS_FL12_C_160421_231526.530_COLOR-8-BIT.JPG, omnit
    # the tag _COLOR-8-BIT.JPG and put only CHESS_FL12_C_160421_231526.530 in the list
    # If None, then we'll use all image pairs from *annotation_csv*
    image_basename_list = None # '/data/sealdata_blob01_complete/train_clean.txt'
    # List of directories, where required files might be located
    source_dirs = list(glob.glob('/data/seals/seal_data_vott/sealdata_blob01_complete/train_color')) #+ list(glob.glob('/data/seal_blobs/thermal*')) # ['/datadrive/seal_blobs/color01', '/datadrive/seal_blobs/thermal01']
    # List of file tags to copy for each image, normalized and registered images will
    # be generated on the fly
    tags = ['_COLOR-8-BIT.JPG']#, '_THERM-16BIT.PNG', '_THERM-8-BIT.JPG'] # _THERM-REG-16BIT.JPG _THERM-8BIT-N.PNG 
    # Whether to compute and store the unregsitered normalized IR image, this will be 16 bit
    store_normalized_ir = False
    # Whether to compute and store the registered IR image, this will be normalized 16 bit format
    compute_registered_ir = False

    # Required registration accuracy, if the warped IR annotations are more than
    # *registration_rej_thr* times *object_width* away from the color bounding boxes
    # we discard the image.
    reg_rejection_thr = 1
    # The folder of the output directory
    output_dir = '/data/seals/seal_data_vott/sealdata_blob01_complete/train_color_updated'

    os.makedirs(output_dir, exist_ok=True)
    # Read csv
    ann = pd.read_csv(annotation_csv)
    ann.drop(ann[ann['status'] == 'removed'].index, inplace=True)
    has_update = ann.updated
    print('Using updated locations for', len(has_update), 'hotspots')
    ann.loc[has_update, 'thumb_left'] = ann.loc[has_update, 'updated_left']
    ann.loc[has_update, 'thumb_top'] = ann.loc[has_update, 'updated_top']
    ann.loc[has_update, 'thumb_right'] = ann.loc[has_update, 'updated_right']
    ann.loc[has_update, 'thumb_bottom'] = ann.loc[has_update, 'updated_bot']

    if image_basename_list:
        im_basenames = open(image_basename_list, 'rt').read().splitlines()
        im_basenames = [imb for imb in im_basenames if imb is not '']
    else:
        def useable_row(x):
            return x['hotspot_type'] in ['Evidence of Seal', 'Not Discernible', 'Animal']
        color_im_names = list(set(ann['filt_color'][ann.apply(useable_row, axis=1)].tolist()))
        im_basenames = [x[:x.rfind('_COLOR')] for x in color_im_names]
        im_basenames = list(filter(lambda x: find_file_in_dirs(source_dirs, x + '_COLOR-8-BIT.JPG') or 
                                             find_file_in_dirs(source_dirs, x + '_THERM-16BIT.PNG'), im_basenames))
        print('Found {} images with annotations'.format(len(im_basenames)))

    #for im_basename in pyprind.prog_bar(im_basenames): 
    def process_image(im_basename):
        print('Working on ', im_basename)
        # Get annotations for this image
        def get_animal_hotspots(x):
            correct_im = x['filt_thermal16'].startswith(im_basename) and \
                         x['filt_color'].startswith(im_basename)
            correct_type = x['hotspot_type'] in ['Evidence of Seal', 'Not Discernible', 'Animal']
            return correct_im and correct_type
        rel_ann = ann[ann.apply(get_animal_hotspots, axis=1)]
        # Write annotations
        if len(tags) < 2:
            ann_basename = im_basename + '.'.join(tags[0].split('.')[:-1])
        else:
            ann_basename = im_basename
        object_label = rel_ann['species_id']
        assert (object_label != 'Duplicate').all(), 'ERROR: This script does not handle annotation of type "Duplicate"'
        object_label.to_csv(os.path.join(output_dir, ann_basename + '.bboxes.labels.tsv'), index=False)
        object_bboxes = rel_ann[['thumb_left', 'thumb_top', 'thumb_right', 'thumb_bottom']]
        object_bboxes.to_csv(os.path.join(output_dir, ann_basename + '.bboxes.tsv'), 
                    index=False, header=False, sep=' ', float_format='%i')

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
                    # Check if transform is good using IR and color image anntoations
                    all_close = True
                    for _, x in rel_ann.iterrows():
                        warped_ir_hotspot = np.array(warpPoint([x.x_pos, x.y_pos], transform))
                        color_hotspot = np.array([x.object_centers_x, x.object_centers_y])
                        warping_error = np.linalg.norm(warped_ir_hotspot - color_hotspot)
                        all_close = all_close and warping_error < reg_rejection_thr * object_width
                    # Save warped image if successful
                    if all_close:
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
                        print('Registration is too inaccurate, skipping this image.')
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

    num_cores = multiprocessing.cpu_count()
    results = joblib.Parallel(n_jobs=num_cores, verbose=15)(joblib.delayed(process_image)(im_basename) for im_basename in im_basenames)
    #for im_basename in im_basenames:
    #    process_image(im_basename) 

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
            for idx, im_basename in pyprind.prog_bar(list(enumerate(im_basenames))):
                if image_count[idx] < max_count:
                    for file_to_delete in glob.glob(os.path.join(output_dir, im_basename + '*')):
                        print('Deleting', file_to_delete)
                        os.remove(file_to_delete)

    print('Finished!')


if __name__ == '__main__':
    main()
