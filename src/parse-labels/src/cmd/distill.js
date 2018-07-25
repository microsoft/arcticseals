let fs = require('fs');
let path = require('path');
let csvUtil = require('../util/csv');
let imageUtil = require('../util/image');
let fileUtil = require('../util/file');

module.exports.registerCommand = (program) => {
    program
        .command('distill <file>')
        .option('-x, --exclude <csvs>', 'Comma-separated list of CSVs containg hotspots to ignore')
        .option('-i, --imgdirs <dirs>', 'Comma-separated list of file paths containing images')
        .option('-o, --outfile <file>', 'Output CSV file (in normalized format)')
        .description('Distill raw CSV file (only include hotspots w/ images)')
        .action((file, command) => {
            let allExcludeRecords = [];
            for (let excludeCsv of command.exclude.split(',')) {
                let excludeRecords = csvUtil.getCsvRecords(excludeCsv);
                allExcludeRecords.push(...excludeRecords);
            }
            let allExcludeStats = csvUtil.getCsvStats(allExcludeRecords);

            const filter = (record) => {
                // Don't care about duplicates, evidence of seal, etc.
                return record.hotspot_type === 'Animal' || record.hotspot_type === 'Anomaly'
            };
            let records = csvUtil.getCsvRecordsFromRawCsv(file, [filter]); 

            let imageMap = imageUtil.getImageMap(command.imgdirs.split(','), command.imgtype);

            let distilledRecords = [];
            let recordsExcluded = 0;
            let recordsIncluded = 0;
            let recordsIncludedWithoutColor = 0;
            let recordsIncludedNotInMaster = 0;
            for (let record of records) {
                if (imageMap.has(record.filt_thermal16)) {
                    if (allExcludeStats.uniqueHotspots.has(record.hotspot_id) || !imageMap.has(record.filt_color)) {
                        recordsExcluded++;
                    } else {
                        distilledRecords.push(record);
                        recordsIncluded++;
                    }
                } else {
                    recordsExcluded++;
                }
            }

            let writer = fs.createWriteStream(command.outfile);
            csvUtil.writeCsvHeader(writer);
            for (let distilledRecord of distilledRecords) {
                csvUtil.writeCsvRecord(writer, distilledRecord);
            }

            console.log(`${recordsIncluded} records included, ${recordsExcluded} records excluded.`);
    });
}
