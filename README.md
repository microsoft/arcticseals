## Overview

This is the workspace for the Microsoft project [Find Arctic Seals with Deep Learning](https://garagehackbox.azurewebsites.net/hackathons/1214/projects/70402), which aims to automate the detection of arctic wildlife in aerial imagery collected by [NOAA Fisheries](https://www.fisheries.noaa.gov/).  To get write access to this repo, submit a request [here](https://github.com/orgs/Microsoft/teams/arcticseals/members).

## Imagery

Imagery is now available publicly on [lila.science](http://lila.science/datasets/arcticseals), an open data repository for labeled images related to conservation biology.

## Labels

The `data` directory contains the following label/metadata files:

* `train.csv` (5,110 records): Hotspot detection data for which we have all corresponding imagery data (see below). Currently all of these hotspots refer to images in dataset ArcticSealsData01.
* `test.csv` (1,314 records): Same format and distrbution of `train.csv`, suitable for cross-validation. 

Each record in the CSV files refers to a hotspot that the NOAA thermal detection system picked up and that was classified by a human into either "Animal" (true positive) or "Anomaly" (false positive). Each hotspot is unique (no duplicates). The column schema is as follows:

* `hotspot_id`: unique ID
* `timestamp`: GMT/UTC timestamp (always corresponds to thermal image timestamp)
* `filt_thermal16`: Filename of the 16-bit PNG containing the raw FLIR image data
* `filt_thermal8`: Filename of the 8-bit JPG containing the annotated FLIR image data (hotspots circled)
* `filt_color`: Filename of the 8-bit JPG containing a color image taken at or near the same time as the thermal image. The timestamp encoded in the filename may be different from the thermal timestamp by up to 60 seconds (but typically less than 1 second).
* `x_pos`/`y_pos`: Location of the hotspot in the thermal image
* `thumb_*`: Bounding box of the hotspot in the color image. **NOTE**: some of these values are negative, as the bounding box is always 512x512 even if the hotspot is at the edge of the image.
* `hotspot_type`: "Animal" or "Anomaly"
* `species_id`: "Bearded Seal", "Ringed Seal", "UNK Seal", "Polar Bear" or "NA" (for anomalies)

### Raw Hotspot Data

In the `data` directory there is also a `raw.csv` (14,910 records) containing all hotspot detections from the NOAA 2016 survey flights (includes more seals but also more types of animals, more anomalies, hotspots marked as duplicates, etc.).

## Code

The project is meant to accomodate many different approaches, frameworks, languages, etc. Linux is the primary supported dev environment, though some GUI tools are Windows-only.

### Organization

Team members are welcome to add whatever code you like to this repo, but please follow these guidelines:

* Put your source code in its own directory inside the `src` directory.
* Add a `README.md` file to your code directory explaining what your code does and how it works.
* If there are dependencies that need to be installed and/or build steps that need to be performed, add any necessary code to the `build.bat` script to run the relevant package manager commands, compile steps, etc., to ensure your code is fully runnable locally.
    * Alternatively, it is also ok if your code only builds from within an IDE; if so just make a note of that in your `README.md`.
* If applicable, add a script that runs your code to the root directory. If it takes command line arguments, please show help text if it is run without arguments.

# Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.
