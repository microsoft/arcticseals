let fs = require('fs');
let path = require('path');
let csvUtil = require('../util/csv');
let imageUtil = require('../util/image');
let fileUtil = require('../util/file');

module.exports.registerCommand = (program) => {
    program
        .command('thumbs <file>')
        .option('-i, --imgdirs <dirs>', 'Comma-separated list of file paths containing thumb images')
        .option('-o, --outdir <dir>', 'Destination for output files')
        .description('Moves hotspot thumb images into folders by type')
        .action((file, command) => {
            let records = csvUtil.getCsvRecords(file);
            let stats = csvUtil.getCsvStats(records);
            let imageMap = imageUtil.getImageMap(command.imgdirs.split(','), 'hotspot');
            let filesMoved = 0;
            for (let image of imageMap.keys()) {
                let matches = image.match(new RegExp(/_HOTSPOT_(.*)\.JPG$/));
                if (matches.length == 2) {
                    let hotspotId = matches[1];
                    let hotspotInfo = stats.uniqueHotspots.get(hotspotId);
                    if (hotspotInfo) {
                        let hotspotTypeDir = path.join(command.outdir, hotspotInfo.hotspot_type);
                        fileUtil.ensureDirExists(hotspotTypeDir);
                        fs.renameSync(imageMap.get(image), path.join(hotspotTypeDir, image));
                        filesMoved++;
                    } else {
                        console.log(`No hotspot info for ${hotspotId}`)
                    }
                } else {
                    console.log(`No match for ${image}`);
                }
            }
            console.log(`Moved ${filesMoved} files.`);
        });
}
