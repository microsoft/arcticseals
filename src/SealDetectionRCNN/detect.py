import sys
import uuid
import os
import glob
import argparse
import pandas as pd
from api import PlasticDetector


def parse_args():
    parser = argparse.ArgumentParser(
        description='Given a directory path, scans thermal images and populates a csv file with bounding boxes of predicted seals')
    parser.add_argument('sourcePath',
                        help='Relative path to the input directory.')
    parsed_args = parser.parse_args(sys.argv[1:])
    return parsed_args


def generate_hotspot_record(img_name, bbox_params):
    return pd.Series({
        'hotspot_id': generate_hotspot_uid(img_name),
        'timestamp': '',
        'filt_thermal16': '',
        'filt_thermal8': img_name,
        'filt_color': img_name.replace('THERM', 'COLOR'),
        'x_pos': (bbox_params[0]+bbox_params[2])/2,
        'y_pos': (bbox_params[1]+bbox_params[3])/2,
        'thumb_left': '',
        'thumb_right': '',
        'thumb_top': '',
        'thumb_bottom': '',
        'hotspot_type': 'Animal',
        'species_id': ''
    })


def generate_hotspot_records(img_path, detector):
    img_name = os.path.basename(img_path)
    bboxes = detector.predict_bboxes(img_path)
    return pd.DataFrame(list(map(lambda bbox: generate_hotspot_record(img_name, bbox), bboxes)))


def generate_hotspot_uid(img_name):
    return str(uuid.uuid4())


def get_source_and_target_paths():
    args = parse_args()
    sourcePath = os.path.dirname(
        os.path.realpath(__file__)) + '/' + args.sourcePath

    if not os.path.exists(sourcePath):
        sys.exit("Given source path does not exist")

    return (sourcePath, '')

def scan_for_image_paths(sourcePath):
    filePattern = "*THERM-8B*.PNG"
    img_paths = glob.glob(sourcePath + '/' + filePattern)
    print("Image files scanned.")
    return img_paths


def load_detector(detectorPath):
    det = PlasticDetector(detectorPath, True)
    print('Model loaded.')
    return det


if __name__ == '__main__':
    (sourcePath, targetPath) = get_source_and_target_paths()
    img_paths = scan_for_image_paths(sourcePath)
    detector = load_detector('checkpoints/fasterrcnn_07251814_0.877517673670313')

    bboxes = pd.concat(list(
        map(lambda img_path: generate_hotspot_records(img_path, detector), img_paths)), axis=0)
    bboxes = bboxes.set_index('hotspot_id')
    bboxes.to_csv("hotspots.csv")
