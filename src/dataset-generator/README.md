# Dataset creator

## Introduction
This directory contains scripts for generating datasets in the format used by our machine learning frameworks during training and evaluation. We use an arbitrary number of source directories, a list of image basenames, and the raw.csv containing the annotations as input. Please see the comments in the `main()` function of `detection_dataset_creator.py` for further configuration options. 

## Requirements
The scripts were written using Python 3.6. The following Python packages are required:

 - opencv
 - pyprind
 - pypng
 - pandas
 - joblib

## License
Please see the LICENSE file in the root of the repository.
