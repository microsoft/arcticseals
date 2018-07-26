# Arctic Seals Hackathon Project

This is the workspace for the Microsoft 2018 OneWeek Hackathon project [Find Arctic Seals with Deep Learning](https://garagehackbox.azurewebsites.net/hackathons/1214/projects/70402). Other background materials (presentations, etc.) can be found in our [Arctic Seals Hackathon Team](https://teams.microsoft.com/l/team/19%3adfaf4e05a29741fe8a2dc3cf8d0c8f57%40thread.skype/conversations?groupId=6cbb37ab-68c8-408e-9e7e-a3a87706dfe5&tenantId=72f988bf-86f1-41af-91ab-2d7cd011db47).

To get write access to this repo, submit a request [here](https://github.com/orgs/Microsoft/teams/arcticseals/members).

## Data

The `data` directory contains the following dataset files from NOAA: 

* `train.csv` (5,256 records): Hotspot detection data for which we have all corresponding imagery data (see below). Currently all of these hotspots refer to images in dataset ArcticSealsData01.
* `test.csv` (1,368 records): Same format and distrbution of `train.csv`, suitable for cross-validation. 

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

In the `data` directory there is also a `raw.csv` (15,454 records) containing all hotspot detections from the NOAA 2016 survey flights (includes more seals but also more types of animals, more anomalies, hotspots marked as duplicates, etc.). **We do not yet have the imagery corresponding to all of these hotspots, only about 2.5TB out of 19TB.**

## Imagery

The actual image files are located in Azure storage, grouped into datasets each containing thousands of either color or thermal images. You can get these as .tar archives or .vhdx virtual disks; each contains the same data.

* `ArcticSealsData01_Color` (88GB): [tar](https://arcticseals.blob.core.windows.net/imagery/ArcticSealsData01_Color.tar) [vhdx](https://arcticseals.blob.core.windows.net/imagery/ArcticSealsData01_Color.vhdx)
* `ArcticSealsData02_Color` (89GB): [tar](https://arcticseals.blob.core.windows.net/imagery/ArcticSealsData02_Color.tar) [vhdx](https://arcticseals.blob.core.windows.net/imagery/ArcticSealsData02_Color.vhdx)
* `ArcticSealsData03_Color` (269GB): [tar](https://arcticseals.blob.core.windows.net/imagery/ArcticSealsData03_Color.tar) [vhdx](https://arcticseals.blob.core.windows.net/imagery/ArcticSealsData03_Color.vhdx)
* `ArcticSealsData04_Color` (648GB): [tar](https://arcticseals.blob.core.windows.net/imagery/ArcticSealsData04_Color.tar) [vhdx](https://arcticseals.blob.core.windows.net/imagery/ArcticSealsData04_Color.vhdx)
* `ArcticSealsData05_Color` (627GB): [tar](https://arcticseals.blob.core.windows.net/imagery/ArcticSealsData05_Color.tar) [vhdx](https://arcticseals.blob.core.windows.net/imagery/ArcticSealsData05_Color.vhdx)
* `ArcticSealsData06_Color` (535GB): [tar](https://arcticseals.blob.core.windows.net/imagery/ArcticSealsData06_Color.tar) [vhdx](https://arcticseals.blob.core.windows.net/imagery/ArcticSealsData06_Color.vhdx)
* `ArcticSealsData07_Color` (219GB): [tar](https://arcticseals.blob.core.windows.net/imagery/ArcticSealsData07_Color.tar) [vhdx](https://arcticseals.blob.core.windows.net/imagery/ArcticSealsData07_Color.vhdx)

The thermal data, since it's relatively small, has been combined into fewer files. Note that there is more thermal data than we have corresponding color data for.

* `ArcticSealsData01_Thermal` (1GB): [tar](https://arcticseals.blob.core.windows.net/imagery/ArcticSealsData01_Thermal.tar) [vhdx](https://arcticseals.blob.core.windows.net/imagery/ArcticSealsData01_Thermal.vhdx)
* `ArcticSealsData02-07_Thermal` (31GB): [tar](https://arcticseals.blob.core.windows.net/imagery/ArcticSealsData02-07_Thermal.tar) [vhdx](https://arcticseals.blob.core.windows.net/imagery/ArcticSealsData02-07_Thermal.vhdx)
* `ArcticSealsData08-99_Thermal` (41GB): [tar](https://arcticseals.blob.core.windows.net/imagery/ArcticSealsData08-99_Thermal.tar) [vhdx](https://arcticseals.blob.core.windows.net/imagery/ArcticSealsData08-99_Thermal.vhdx)

In Windows, you can easily mount the .vhdx files on your machine by double-clicking them.

The timestamp pattern embedded in the filenames has two possible forms - you may see, for example, either `160408_020848.724` or `20160408020848.724GMT`. In all cases you should use the filename-embedded timestamp to sequence/correlate images, not whatever timestamp your file system claims.

We also have the ArcticSealsData01 files as individual files in Azure storage that can be accessed as shown below. However, if you are going to do any bulk operations it's more efficient to download the tar/vhdx files.

* https://arcticseals.blob.core.windows.net/imagery/ArcticSealsData01/CHESS_FL12_C_160421_221418.760_COLOR-8-BIT.JPG

Finally, if you want to use [Azure Storage Explorer](https://azure.microsoft.com/en-us/features/storage-explorer) (for example) to access the entire blob container, use this connection string:

`BlobEndpoint=https://arcticseals.blob.core.windows.net/;SharedAccessSignature=sv=2017-11-09&ss=b&srt=sco&sp=rl&se=2019-06-13T07:12:17Z&st=2018-06-13T23:12:17Z&spr=https&sig=2v7zAzhq2cw1%2BWseuNAKiTp5Qc4zzBclw3LqdDnANYg%3D`

## Code

The project is meant to accomodate many different approaches, frameworks, languages, etc. Linux is the primary supported dev environment, though some GUI tools are Windows-only.

### Organization

Hackathon members are welcome to add whatever code you like to this repo, but please follow these guidelines:

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
