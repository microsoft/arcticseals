# parse-labels

This tool reads NOAA hotspot CSV label data and can do these things:

* `stats`: Show statistics (number of hotspots, timestamp varation, etc.)
* `split`: Randomly divide the dataset (by thermal image) into two sets
* `prep`: Generate a training or test set by selecting images and generating corresponding bounding box and label files

To run, use `pl <command> <file> [options]` in the repo's root dir. Run with no arguments to see full help text.