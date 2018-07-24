let fs = require('fs');
let csvUtil = require('../util/csv');

const getRandomIndices = (num, max) => {
    let indices = new Set();
    for (let i = 0; i < num; i++) {
        let index;
        do {
            index = Math.floor(Math.random() * max);
        } while(indices.has(index));
        indices.add(index);
    }
    return indices;
}

const getThermal16ImagesFromIndices = (stats, indices) => {
    let images = new Set();
    let i = 0;
    for (let image of stats.thermal16Stats.uniqueImages.keys()) {
        if (indices.has(i++)) {
            images.add(image);
        }
    }
    return images;
}

module.exports.registerCommand = (program) => {
    program
        .command('split <file>')
        .option('-f, --filters <conditions>', 'Comma-separated list of filter conditions, e.g. hotspot_type=Animal')
        .option('-n, --num <images>', 'Number of thermal images to include in first label set')
        .option('-a, --output1 <filename>', 'First output file name')
        .option('-b, --output2 <filename>', 'Second output file name')
        .description('Split labels into two disjoint sets')
        .action((file, command) => {
            let filters = csvUtil.parseFilters(command.filters);
            let records = csvUtil.getCsvRecords(file, filters);
            let stats = csvUtil.getCsvStats(records);
            let indices = getRandomIndices(parseInt(command.num), stats.thermal16Stats.uniqueImages.size);
            let images1 = getThermal16ImagesFromIndices(stats, indices);
            let writer1 = fs.createWriteStream(command.output1);
            let writer2 = fs.createWriteStream(command.output2);
            csvUtil.writeCsvHeader(writer1);
            csvUtil.writeCsvHeader(writer2);
            for (let r of records) {
                csvUtil.writeCsvRecord(images1.has(r.filt_thermal16) ? writer1 : writer2, r);
            }
        });
}
