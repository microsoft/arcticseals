# Image patch/thumbnail classification with transfer learning using ResNet18 & CNTK

This script is set up to use transfer learning to train an existing, pre-trained, ResNet18 classifier to classify seals and anomalies.

## Usage

usage: cntk_resnet18_tl.py [-h] [-datadir DATADIR] [-outputdir OUTPUTDIR]
                           [-logdir LOGDIR] [-n NUM_EPOCHS]
                           [-m MINIBATCH_SIZE] [-device DEVICE]

optional arguments:
  -h, --help            show this help message and exit
  -datadir DATADIR, --datadir DATADIR
                        Data directory where the seals dataset is located
  -outputdir OUTPUTDIR, --outputdir OUTPUTDIR
                        Output directory for checkpoints and models
  -logdir LOGDIR, --logdir LOGDIR
                        Log file
  -n NUM_EPOCHS, --num_epochs NUM_EPOCHS
                        Total number of epochs to train
  -m MINIBATCH_SIZE, --minibatch_size MINIBATCH_SIZE
                        Minibatch size
  -device DEVICE, --device DEVICE
                        Force to run the script on a specified device

## Data

When `datadir` is not specified, the script will use the relative path to itself and try to load the training testing data under seals_data\images. When `datadir` is specified the script will try to load the training and testing data under `datadir`\images. In either case, the images folder is expected to have the follwing structure:

\images
    \Test
        \Class1 (e.g. Animal)
            ... (class 1 images)
        \Class2 (e.g. Anomaly)
            ... (class 2 images)
        ...
        \ClassN
            ... (class n images)
    \Train
        \Class1 (e.g. Animal)
            ... (class 1 images)
        \Class2 (e.g. Anomaly)
            ... (class 2 images)
        ...
        \ClassN
            ... (class n images)

