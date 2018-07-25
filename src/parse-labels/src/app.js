'use strict';

let os = require('os');
let program = require('commander');

require('./cmd/stats').registerCommand(program);
require('./cmd/split').registerCommand(program);
require('./cmd/prep').registerCommand(program);
require('./cmd/thumbs').registerCommand(program);
require('./cmd/distill').registerCommand(program);
require('./cmd/normalize').registerCommand(program);

program
    .command('help <command>')
    .description('Show detailed help for <command>')
    .action((command) => {
        for (let commandObj of program.commands) {
            if (commandObj.name() == command) {
                process.stdout.write(commandObj.helpInformation());
                process.stdout.write(os.EOL);
                return;
            }
        }
    });

program.on('--help', () => {
    console.log('');
    console.log('For all commands, <file> is a CSV file of CHESS label data.');
    console.log('');
});

program
    .parse(process.argv);

if (!process.argv.slice(2).length) {
    program.outputHelp();
}
