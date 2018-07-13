# parse-labels

This tool reads NOAA hotspot CSV label data (via -f [file] argument) and can do two things:

* `stats`: Show statistics (number of hotspots, timestamp varation, etc.)
* `split`: Randomly divide the dataset (by thermal image) into two sets

To run, use `parse-labels.bat [command] [options]` in the repo's `scripts` dir. Run with no arguments to see full help text.