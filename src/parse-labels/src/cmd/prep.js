let fs = require('fs');
let os = require('os');
let path = require('path');
let readline = require('readline');
let csvUtil = require('../util/csv');
let imageUtil = require('../util/image');
let fileUtil = require('../util/file');

module.exports.registerCommand = (program) => {
    program
        .command('prep <file>')
        .option('-f, --filters <conditions>', 'Comma-separated list of filter conditions, e.g. hotspot_type=Animal')
        .option('-i, --imgdirs <dirs>', 'Comma-separated list of file paths containing images')
        .option('-t, --imgtype <type>', '"thermal16", "thermal8" or "color" (defaults to "thermal8")')
        .option('-n, --num <hotspots>', 'Number of hotspots to (non-randomly) select for inclusion')
        .option('-b, --bboxes', 'Whether to output .bboxes[.labels].tsv files next to images')
        .option('-o, --outdir <dir>', 'Destination for output files')
        .description('Prepare label and image data for training')
        .action((file, command) => {
            if (!command.imgtype) {
                command.imgtype = 'thermal8';
            }
            let imageMap = imageUtil.getImageMap(command.imgdirs.split(','), command.imgtype);
            let filters = csvUtil.parseFilters(command.filters);
            let imagesNotFound = 0;
            filters.push((record) => {
                let image = record[command.imgtype == 'thermal16' ? 'filt_thermal16' : (command.imgtype == 'thermal8' ? 'filt_thermal8' : 'filt_color')];
                if (imageMap.has(image)) {
                    return true;
                }
                imagesNotFound++;
                return false;
            });
            let records = csvUtil.getCsvRecords(file, filters);
            if (command.num) {
                records = records.slice(0, parseInt(command.num) + 1);
            }
            let stats = csvUtil.getCsvStats(records);
            let images;
            if (command.imgtype == 'thermal16') {
                images = Array.from(stats.thermal16Stats.uniqueImages.keys());
            } else if (command.imgtype == 'thermal8') {
                images = Array.from(stats.thermal8Stats.uniqueImages.keys());
            } else {
                images = Array.from(stats.colorStats.uniqueImages.keys());
            }
            let prompt = readline.createInterface(process.stdin, process.stdout);
            if (imagesNotFound > 0) {
                console.log(`Warning: ${imagesNotFound} were not found`);
            }
            prompt.question(`About to copy ${images.length} images to ${command.outdir}, are you sure? [y/n] `, (answer) => {
                prompt.close();
                if (answer !== 'y') {
                    return;
                }
                fileUtil.ensureDirExists(command.outdir);
                imageUtil.copyImageFilesToDir(images, imageMap, command.outdir);
                if (command.bboxes) {
                    for (let image of images) {
                        let uniqueImages = command.imgtype == 'thermal16' ? stats.thermal16Stats.uniqueImages : (command.imgtype == 'thermal8' ? stats.thermal8Stats.uniqueImages : stats.colorStats.uniqueImages);
                        let bboxes = uniqueImages.get(image).bboxes;
                        let bboxesWriter = fs.createWriteStream(path.join(command.outdir, `${image.slice(0, -4)}.bboxes.tsv`));
                        let bboxesLabelWriter = fs.createWriteStream(path.join(command.outdir, `${image.slice(0, -4)}.bboxes.labels.tsv`));
                        for (let bbox of bboxes) {
                            bboxesWriter.write(`${bbox.left}\t${bbox.top}\t${bbox.right}\t${bbox.bottom}${os.EOL}`);
                            bboxesLabelWriter.write(`${bbox.label}${os.EOL}`);
                        }
                    }
                }
            });
        });
}