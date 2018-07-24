let csvUtil = require('../util/csv');

module.exports.registerCommand = (program) => {
    program
        .command('stats <file>')
        .option('-f, --filters <conditions>', 'Comma-separated list of filter conditions, e.g. hotspot_type=Animal')
        .description('Show label stats')
        .action((file, command) => {
            let filters = csvUtil.parseFilters(command.filters);
            let records = csvUtil.getCsvRecords(file, filters);
            let stats = csvUtil.getCsvStats(records);
            csvUtil.printStats(stats);
        });
}
