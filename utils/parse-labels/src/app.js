'use strict';

let fs = require('fs');
let program = require('commander');
let parse = require('csv-parse/lib/sync');

program
    .option('-f, --file [filename]', 'CSV file of CHESS label data')
    .parse(process.argv);

if (!program.file) {
    program.outputHelp();
    process.exit();
}

let input = fs.readFileSync(program.file).toString();
let records = parse(input, {columns: true});
for (let i = 0; i < 10; i++) {
    console.log(JSON.stringify(records[i]));
}