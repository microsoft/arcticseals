import pandas as pd
import shutil
import os
import numpy as np
import pyprind

def main():
    # CSV file with all the hotspot detections
    annotation_csv = '/data/data/Research/arcticseals/src/detection-dataset-generator/raw.csv'
    # The list of images, which we want to select for the detection dataset
    # Please use basenames only, i.e. without the image type in the name
    # E.g., omnit from the file CHESS_FL12_C_160421_231526.530_COLOR-8-BIT.JPG, omnit
    # the tag _COLOR-8-BIT.JPG and put only CHESS_FL12_C_160421_231526.530 in the list
    image_basename_list = '/data/data/sealdata_blob01_complete/test_clean.txt'
    # List of directories, where required files might be located
    source_dirs = ['/data/data/sealdata_blob01_complete/test']
    # List of file tags to copy for each image
    tags = ['_THERM-REG-16BIT.JPG', '_COLOR-8-BIT.JPG', '_THERM-16BIT.PNG', '_THERM-8-BIT.JPG', 
            '_THERM-8BIT-N.PNG', '_THERM-REG-16BIT.JPG']

    # In the seals data, the provdied bounding boxes are not tight around the object, 
    # actually we only have object centers, but we need tight bounding boxes for training and 
    # evaluation. Specify the mean object width/height of the foreground objects
    object_width = 32
    # The folder of the output directory
    output_dir = '/data/data/sealdata_blob01_complete/test_w_annotations'

    
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
    for im_basename in pyprind.prog_bar(im_basenames):
        if im_basename is not '':
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

if __name__ == '__main__':
    main()
