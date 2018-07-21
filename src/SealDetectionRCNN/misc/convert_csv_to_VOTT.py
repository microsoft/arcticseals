import argparse
import csv
import json
import numpy as np
import os
import pandas as pd


image_height = 1080
image_width = 1920

boxes_suffix = '.bboxes.tsv'
labels_suffix = '.bboxes.labels.tsv'


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--csv', default='../pilot_images_and_annotations/grogol-pilot-classifications.csv', help='Path to the Zooniverse annotations in csv format')
    parser.add_argument('-o', '--output_dir', default='../pilot_images_and_annotations/csv_out', help='Path to directory to place the annotation files in VOTT format')
    args = parser.parse_args()

    if args.output_dir:
        os.makedirs(args.output_dir, exist_ok=True)

    csv = pd.read_csv(args.csv)

    num_rows = len(csv)

    for i in range(num_rows):
        subject_data = json.loads(csv.loc[i, 'subject_data'])
        subject_data = list(subject_data.values())

        if len(subject_data) != 1:  # TODO check that length of this dict is always 1
            print('WARNING row {}, subject_data length != 1, skipped row'.format(i))
            continue

        if 'Filename' not in subject_data[0]:
            print('WARNING row {}, Filename not present in subject_data, skipped row'.format(i))
            continue

        image_fname = subject_data[0]['Filename'].split('.')[0].replace(' ', '_')

        annotations = json.loads(csv.loc[i, 'annotations'])

        boxes_arr = []
        labels_arr = []

        # TODO check that the x, y is the top left coordinate
        for annotation in annotations:
            if annotation['task'] in ['T1', 'T2']:
                for label in annotation['value']:
                    xmin, ymin = int(round(label['x'])), int(round(label['y']))
                    xmax = min(int(round(xmin + label['width'])), image_width)
                    ymax = min(int(round(ymin + label['height'])), image_height)

                    tool_label = label['tool_label'].lower()
                    if tool_label.startswith('plastic'):
                        class_label = 'plastic'
                    elif tool_label.startswith('organic'):
                        class_label = 'organic'
                    else:
                        continue

                    boxes_arr.append([xmin, ymin, xmax, ymax])
                    labels_arr.append(class_label)

        if len(labels_arr) > 0:
            boxes_tsv_name = image_fname + boxes_suffix
            labels_tsv_name = image_fname + labels_suffix

            boxes_arr = np.asarray(boxes_arr)
            np.savetxt(os.path.join(args.output_dir, boxes_tsv_name), boxes_arr, fmt='%i', delimiter=' ')

            labels_arr = np.asarray(labels_arr)
            np.savetxt(os.path.join(args.output_dir, labels_tsv_name), labels_arr, fmt='%s', delimiter=' ')

        else:
            print('WARNING row {} has no valid annotations'.format(i))
