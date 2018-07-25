import sys
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

if __name__ == '__main__':
    args = parse_args()
    sourcePath = os.path.dirname(os.path.realpath(__file__)) + '/' + args.sourcePath
    filePattern = "*.PNG"

    if not os.path.exists(sourcePath):
        sys.exit("Given source path does not exist")
    
    img_paths = glob.glob(sourcePath + '/' + filePattern)

    print("Image files scanned.")

    det = PlasticDetector(
        'checkpoints/fasterrcnn_07251814_0.877517673670313', True)

    print('Model loaded.')

    bboxes = pd.DataFrame(list(map(lambda img_path: pd.Series({'img_name': os.path.basename(img_path), 'bboxes': det.predict_bboxes(img_path)}), img_paths)))
    print(bboxes)