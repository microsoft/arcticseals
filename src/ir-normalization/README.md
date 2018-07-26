## IR Image Normalization 

This directory contains the code for normalizing 16-bit IR images into 8-bit IR images. This is being done through a linear transformation based on each camera used during the image campaign. The normalization is done as follows: 
`normalized_image = (original_image - bottom) / (top - bottom) * 255`
Where:
* original_image is the data from the 16 bit image
* bottom is the value that is mapped to zero in the normalization
* top is the value that is mapped to 255 in the normalization
* normalized_image is the output data represented as 8-bit numbers 
Based on the training data that we have evaluated, we determined the bottom and top parameters as:

| Position | # Rows | Bottom | Top |
|:--------:| ------ | ------ | --- |
|P|512|53500|56500|
|C|512|50500|58500|
|S|512|51000|57500|
|P|480|53000|59000|


### Required Packages
The following are requirements represented by requirements.txt
1. Python 3
1. Numpy
1. pillow (fork of PIL)
1. Matplotlib

### To Operate
The following steps should be done to run this script
1. Install Dependencies: `pip install -r requirements.txt`
1. Run the script `python normalizer.py --indir /path/to/input/images --outdir /path/to/output/location`
1. After running the process, you can test the output images using `python loading-example.py --dir /path/to/output/location`. You should expect to see that the type of data in the array is uint8.
