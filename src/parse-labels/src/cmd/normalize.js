let fs = require('fs');
let csvUtil = require('../util/csv');

module.exports.registerCommand = (program) => {
    program
        .command('normalize <file>')
        .description('Change filt_thermal8 in a CSV to reference normalized files')
        .action((file, command) => {
            let records = csvUtil.getCsvRecords(file);
            let writer = fs.createWriteStream(file);
            csvUtil.writeCsvHeader(writer);
            for (let record of records) {
                record.filt_thermal8 = `${record.filt_thermal16.slice(0, -9)}8BIT-N.PNG`;
                csvUtil.writeCsvRecord(writer, record);
            }
        });
}
