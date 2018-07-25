# Environment

These instructions are for an ubuntu DSVM.


# Get the docker image and code

    git clone https://github.com/Microsoft/arcticseals.git


# Download data

Download the file sample_dataset_for_detection.zip from the Teams channel (via the "Files" tab) or use the URL:

    https://microsoft.sharepoint.com/teams/ArcticSealsHackathon2018/Shared%20Documents/General/sample_dataset_for_detection.zip
	
I'll assume in this tutorial that you unzipped this file to /data/sealdata.

This is just a pilot data set; we will upload the complete dataset with all seals and update this page.
	
	
# Build the Docker image

cd arcticseals/src/SealDetectionRCNN/docker;
sudo docker build -t sealdetection .


## If you get a build error…
	
I had an image that didn't work for me on Ubuntu 16, so I followed the steps here:
	
    https://docs.docker.com/install/linux/docker-ce/ubuntu/#install-docker-ce
			
…to update docker.
	
	
# Run the image with an interactive shell, mounting your data and code directories
	
This assumes you've put the data in /sealdata, and that you're currently in the repo directory.
	
    sudo nvidia-docker run -it -v /sealdata:/datadrive -v $(pwd):/code --ipc=host -p 8097:8097 sealdetection


# Download the base (vgg16) model file

    // You want to run the following in the "SealDetectionRCNN" directory.

    python misc/convert_caffe_pretrain.py && mv vgg16_caffe.pth data/


# Build some native components

Improves performance, not strictly necessary.  Run from the "SealDetectionRCNN" directory.

    conda install cython && cd model/utils/nms/ && python3 build.py build_ext --inplace


# Run the code 

First run the visdom server, which visualizes the training progress:
	
    nohup python -m visdom.server &

Then run the actual training from the "SealDetectionRCNN" directory with:

    chmod a+x ./run_training.sh
    ./run_training.sh

…I actually run it as the following, to open a logfile:
	
    ./run_training.sh 2>&1 | tee ~/logfile.txt
	

# Options

Default options are in:
	
    utils/config.py
		
Some options are overridden in the driver script (run_training.sh).
