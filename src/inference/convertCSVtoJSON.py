import os
import sys
import csv
import json
from collections import OrderedDict

#arg - csv filename.
# Example: python convertCSVtoJSON training
csvName = sys.argv[1]  

fieldnames = ("hotspot_id","timestamp","filt_thermal16","filt_thermal8","filt_color","x_pos","y_pos","thumb_left","thumb_top","thumb_right","thumb_bottom","hotspot_type","species_id")
csvfilename = csvName + '.csv'
jsonfilename = csvName + '.json'
entires = []

with open(csvfilename,'r') as csvfile:
    reader = csv.DictReader( csvfile, fieldnames)
    next(reader, None)
    for row in reader:
        entry = OrderedDict()
        for field in fieldnames:
            entry[field] = row[field]
        entires.append(entry)

output = {
    "Artic": entires
}

with open(jsonfilename, 'w') as jsonfile:
    json.dump(output, jsonfile, indent=4)
    jsonfile.write('\n')