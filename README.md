# Arctic Seals Hackathon Project

This is the workspace for the Microsoft 2018 OneWeek Hackathon project [Find Arctic Seals with Deep Learning](https://garagehackbox.azurewebsites.net/hackathons/1214/projects/70402). Other background materials (presentations, etc.) can be found in our [Arctic Seals Hackathon Team](https://teams.microsoft.com/l/team/19%3adfaf4e05a29741fe8a2dc3cf8d0c8f57%40thread.skype/conversations?groupId=6cbb37ab-68c8-408e-9e7e-a3a87706dfe5&tenantId=72f988bf-86f1-41af-91ab-2d7cd011db47).

## Data

The `data` directory contains two files: `training.csv` (6,624 records) and `validation.csv` (272 records). These contain the labels for the fully annotated dataset we received from NOAA. We may further split off a "dev" set from the training set for hyperparameter tuning, but the validation set should not be used for training or tuning.

Each record in the CSV files refers to a hotspot that the NOAA thermal detection system picked up and that was classified by a human into either "Animal" (true positive) or "Anomaly" (false positive). Each hotspot is unique (no duplicates). The column schema is as follows:

* `hotspot_id`: unique ID
* `timestamp`: GMT/UTC timestamp (always corresponds to thermal image timestamp)
* `filt_thermal16`: Filename of the 16-bit PNG containing the raw FLIR image data
* `filt_thermal8`: Filename of the 8-bit JPG containing the annotated FLIR image data (hotspots circled)
* `filt_color`: Filename of the 8-bit JPG containing a color image taken at or near the same time as the thermal image. The timestamp encoded in the filename may be different from the thermal timestamp by up to 60 seconds (but typically less than 1 second).
* `x_pos`/`y_pos`: Location of the hotspot in the thermal image
* `thumb_*`: Bounding box of the hotspot in the color image. **NOTE**: some of these values are negative, which we are still working to clarify/understand
* `hotspot_type`: "Animal" or "Anomaly"
* `species_id`: "Bearded Seal", "Ringed Seal", "UNK Seal", "Polar Bear" or "NA" (for anomalies)

The actual image files are located in Azure storage. You can get the datasets by downloading the following virtual disks:

* https://arcticseals.blob.core.windows.net/imagery/ArcticSealsData01_Color.vhdx (89GB)
* https://arcticseals.blob.core.windows.net/imagery/ArcticSealsData01_Thermal.vhdx (1.3GB)

In Windows, you can easily mount these as drives on your machine by double-clicking the .vhdx files. We also have the ArcticSealsData01 files as individual files in Azure storage that can be accessed as follows, for example:

* https://arcticseals.blob.core.windows.net/imagery/ArcticSealsData01/CHESS_FL12_C_160421_221418.760_COLOR-8-BIT.JPG

However, if you are going to do any bulk operations it's more efficient to download the virtual disks.

All of the labeled datasets refer to files in this first dataset (ArcticSealsData01). We are also getting additional unlabeled data from NOAA that will be in ArcticSealsDataXX.

Finally, if you want to use [Azure Storage Explorer](https://azure.microsoft.com/en-us/features/storage-explorer) (for example) to access the entire blob container, use this connection string:

`BlobEndpoint=https://arcticseals.blob.core.windows.net/;SharedAccessSignature=sv=2017-11-09&ss=b&srt=sco&sp=rl&se=2019-06-13T07:12:17Z&st=2018-06-13T23:12:17Z&spr=https&sig=2v7zAzhq2cw1%2BWseuNAKiTp5Qc4zzBclw3LqdDnANYg%3D`

## Code

The project is meant to accomodate many different approaches, frameworks, languages, etc. (though it is somewhat biased towards  Windows to maximize collaboration, since it is likely the lowest common dev machine denominator for all project members - though you're free to check in Mac/Linux specific code if that's how you roll).

### Prerequisites

This section lists the one-time installations of core tools that the project depends on. As you add code that requires certain runtimes or what-not, please add them to this list:

* Node.js (https://nodejs.org/en/)

### Organization

You are welcome to add whatever code you like to this repo, but please follow these guidelines:

* Put your source code in its own directory inside the `src` directory.
* Add a `README.md` file to your code directory explaining what your code does and how it works.
* If there are dependencies that need to be installed and/or build steps that need to be performed, add any necessary code to the `scripts\build.bat` script to run the relevant package manager commands, compile steps, etc., to ensure your code is fully runnable locally.
    * Alternatively, it is also ok if your code only builds from within an IDE; if so just make a note of that in your `README.md`.
* If applicable, add a script to the `scripts` directory that runs your code. If it takes command line arguments, please show help text if it is run without arguments.

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
