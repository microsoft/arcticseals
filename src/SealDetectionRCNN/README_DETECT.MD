# About 

The detect.py script takes as its only command-line argument a path to a directory containing .PNG files that are supposed to be 8-bit normalized thermal images (only files matching the mask `*THERM-8B*.PNG` are processed). The script scans this directory runs hotspot detection on the images and produces a file hotspots.csv containing all the detected hotspots together with relevant metadata as speficied by the corresponding Wiki page on the Teams channel:

```
hotspots.csv (using same format as the CSVs in the repo's /data dir) containing candidate hotspots:
hotspot_id: a unique string that won't overlap with the NOAA ids (to eliminate any confusion between our inferred data set and our ground truth data set). Could be a GUID, or a series of sequential IDs, but in that case make sure it's prepended with something unique (e.g. "msft-").
timestamp: can be left blank, won't be used for validation
filt_thermal16: original 16-bit PNG filename
filt_thermal8: 8-bit PNG filename from previous stage
filt_color: color JPG filename
x_pos/y_pos: detected hotspot location
thumb_[left|right|top|bottom]: leave blank
hotspot_type: "Animal" (we only want to include hotspots we think are animals at this point)
species_id: leave blank
```

N.B. the script only populates some of these columns.

# Environment

Follow the steps of README.MD for the SealDetectionCRNN to build and run a docker image. Once the Docker is running make sure to download pandas by:

```
conda install pandas
```

# Running the code

Run the code by 

```
python detect.py ../relative/path/to/source_file/directory
```

Make sure that the source path that is passed is relative to the your current directory and that no trailing slashes are contained in the path. 

The code will generate the file hotspots.csv in the local directory. 

**TODO**: allow the user to specify the designated output file. 


