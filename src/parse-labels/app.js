'use strict';

let fs = require('fs');
let path = require('path');
let os = require('os');
let program = require('commander');
let parse = require('csv-parse/lib/sync');
let readline = require('readline');

let imageUtil = require('./image-util');

const parseTimestamp = (t) => {
    // Example: '20160407235833.627GMT'
    if (t.length != 21 || t.slice(18, 21) != 'GMT') {
        return null;
    }
    let year = parseInt(t.slice(0, 4), 10);
    let month = parseInt(t.slice(4, 6), 10) - 1;
    let date = parseInt(t.slice(6, 8), 10);
    let hours = parseInt(t.slice(8, 10), 10);
    let minutes = parseInt(t.slice(10, 12), 10);
    let seconds = parseInt(t.slice(12, 14), 10);
    let ms = parseInt(t.slice(15, 18), 10);

    return new Date(Date.UTC(year, month, date, hours, minutes, seconds, ms));
};

const parseFilename = (f) => {
    // Example: 'CHESS_FL1_C_160407_235833.627_THERM-16BIT.PNG'
    let info = {};
    let e = f.split('_');
    info.survey = e[0];
    info.flight = e[1];
    info.camPos = e[2];
    info.timestamp = parseTimestamp(`20${e[3]}${e[4]}GMT`);
    info.camType = e[5].split('-')[0];
    let e5_1 = e[5].split('-')[1];
    info.bitDepth = e5_1 == '16BIT' ? 16 : (e5_1 == '8' ? 8 : 0);
    return info; 
};

const initImageFileStats = () => {
    return {
        uniqueImages: new Map(), // Image name to image info 
        timestampVariations: 0,
        sumTimestampVariationMs: 0,
        maxTimestampVariationMs: 0
    };
};

const initRecordStats = () => {
    return {
        uniqueHotspots: new Set(),
        totalHotspots: 0,

        uniqueTimestamps: new Set(),

        thermal16Stats: initImageFileStats(),
        thermal8Stats: initImageFileStats(),
        colorStats: initImageFileStats(),

        hotspotTypes: new Map(),
        speciesTypes: new Map(),

        errors: 0
    };
};

const updateTimestampVariation = (t1, t2, currMax) => {
    return variation > currMax ? variation : currMax;
};

const updateImageFileStats = (timestamp, f, imageStats) => {
    let info = parseFilename(f);
    if (!info.timestamp) {
        return false;
    }
    if (!imageStats.uniqueImages.has(f)) {
        imageStats.uniqueImages.set(f, { bboxes: [] });
    }
    if (info.timestamp.valueOf() != timestamp.valueOf()) {
        imageStats.timestampVariations++;
        let variation = Math.abs(info.timestamp.valueOf() - timestamp.valueOf());
        imageStats.sumTimestampVariationMs += variation;
        if (variation > imageStats.maxTimestampVariationMs) {
            imageStats.maxTimestampVariationMs = variation;
        }
    }
    return true;
};

const examineRecord = (r, stats) => {
    stats.uniqueHotspots.add(r.hotspot_id);
    stats.totalHotspots++;

    let timestamp = parseTimestamp(r.timestamp);
    if (!timestamp) {
        stats.errors++;
        return;
    }
    stats.uniqueTimestamps.add(timestamp.valueOf());
    if (!updateImageFileStats(timestamp, r.filt_thermal16, stats.thermal16Stats)) {
        stats.errors++;
        return;
    }
    if (!updateImageFileStats(timestamp, r.filt_thermal8, stats.thermal8Stats)) {
        stats.errors++;
        return;
    }
    if (!updateImageFileStats(timestamp, r.filt_color, stats.colorStats)) {
        stats.errors++;
        return;
    }
    const margin = 10; // Thermal bounding box margin
    stats.thermal16Stats.uniqueImages.get(r.filt_thermal16).bboxes.push({
        label: r.hotspot_type,
        left: parseInt(r.x_pos) - margin,
        top: parseInt(r.y_pos) - margin,
        right: parseInt(r.x_pos) + margin,
        bottom: parseInt(r.y_pos) + margin
    });
    stats.colorStats.uniqueImages.get(r.filt_color).bboxes.push({
        label: `${r.hotspot_type} (${r.species_id})`,
        left: parseInt(r.thumb_left),
        top: parseInt(r.thumb_top),
        right: parseInt(r.thumb_right),
        bottom: parseInt(r.thumb_bottom),
    });
    if (stats.hotspotTypes.has(r.hotspot_type)) {
        stats.hotspotTypes.set(r.hotspot_type, stats.hotspotTypes.get(r.hotspot_type) + 1);
    } else {
        stats.hotspotTypes.set(r.hotspot_type, 1);
    }
    if (stats.speciesTypes.has(r.species_id)) {
        stats.speciesTypes.set(r.species_id, stats.speciesTypes.get(r.species_id) + 1);
    } else {
        stats.speciesTypes.set(r.species_id, 1);
    }
};

const printImageFileStats = (imageStats) => {
    console.log(`  Unique images: ${imageStats.uniqueImages.size}`);
    console.log(`  Timestamp variations: ${imageStats.timestampVariations}`);
    console.log(`  Avg timestamp variation (ms): ${imageStats.timestampVariations > 0 ? imageStats.sumTimestampVariationMs/imageStats.timestampVariations: 0}`);
    console.log(`  Max timestamp variation (ms): ${imageStats.maxTimestampVariationMs}`);
};

const printStats = (stats) => {
    console.log(`Total hotspots: ${stats.totalHotspots}`);
    console.log(`Unique hotspots: ${stats.uniqueHotspots.size}`);
    console.log(`Unique timestamps: ${stats.uniqueTimestamps.size}`);
    console.log('Thermal16 stats:');
    printImageFileStats(stats.thermal16Stats);
    console.log('Thermal8 stats:');
    printImageFileStats(stats.thermal8Stats);
    console.log('Color stats:');
    printImageFileStats(stats.colorStats);
    console.log(`Hot spot types:`);
    for (let hotspotType of stats.hotspotTypes.keys()) {
        console.log(`  ${hotspotType}: ${stats.hotspotTypes.get(hotspotType)}`);
    } 
    console.log(`Species types:`);
    for (let speciesType of stats.speciesTypes.keys()) {
        console.log(`  ${speciesType}: ${stats.speciesTypes.get(speciesType)}`);
    }
};

const getCsvRecords = (filename, filters) => {
    let input = fs.readFileSync(filename).toString();
    let records = parse(input, {columns: true});
    return records.filter((record) => {
        return !filters || filters.every((filter) => filter(record));
    });
};

const getCsvStats = (records) => {
    let stats = initRecordStats();
    for (let r of records) {
        examineRecord(r, stats);
    }
    return stats;
};

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

const writeCsvHeader = (writer) => {
    writer.write(`"hotspot_id","timestamp","filt_thermal16","filt_thermal8","filt_color","x_pos","y_pos","thumb_left","thumb_top","thumb_right","thumb_bottom","hotspot_type","species_id"${os.EOL}`);
};

const writeCsvRecord = (writer, r) => {
    writer.write(`"${r.hotspot_id}","${r.timestamp}","${r.filt_thermal16}","${r.filt_thermal8}","${r.filt_color}",${r.x_pos},${r.y_pos},${r.thumb_left},${r.thumb_top},${r.thumb_right},${r.thumb_bottom},"${r.hotspot_type}","${r.species_id}"${os.EOL}`);
};

program
    .command('stats <file>')
    .description('Show label stats')
    .action((file) => {
        let filters = parseFilters(program.filters);
        let records = getCsvRecords(file, filters);
        let stats = getCsvStats(records);
        printStats(stats);
    });

program
    .command('split <file>')
    .option('-n, --num <images>')
    .option('-a, --output1 <filename>')
    .option('-b, --output2 <filename>')
    .description('Split labels into two disjoint sets')
    .action((file, command) => {
        let filters = parseFilters(program.filters);
        let records = getCsvRecords(file, filters);
        let stats = getCsvStats(records);
        let indices = getRandomIndices(parseInt(command.num), stats.thermal16Stats.uniqueImages.size);
        let images1 = getThermal16ImagesFromIndices(stats, indices);
        let writer1 = fs.createWriteStream(command.output1);
        let writer2 = fs.createWriteStream(command.output2);
        writeCsvHeader(writer1);
        writeCsvHeader(writer2);
        for (let r of records) {
            writeCsvRecord(images1.has(r.filt_thermal16) ? writer1 : writer2, r);
        }
    });

const parseFilters = (filters) => {
    if (!filters)
        return [];
    return filters.split(',').map((filter) => {
        let split = filter.split('=');
        let field = split[0];
        let value = split[1];
        return (record) => {
            return record[field] === value; 
        };
    });
};

program
    .command('prep <file>')
    .option('-i, --imgdirs <dirs>')
    .option('-t, --imgtype <type>')
    .option('-n, --num <images>')
    .option('-b, --bboxes')
    .option('-o, --outdir <dir>')
    .description('Prepare label and image data for training')
    .action((file, command) => {
        if (!command.imgtype) {
            command.imgtype = 'thermal';
        }
        let imageMap = imageUtil.getImageMap(command.imgdirs.split(','), command.imgtype);
        let filters = parseFilters(program.filters);
        let imagesNotFound = 0;
        filters.push((record) => {
            let image = record[command.imgtype == 'thermal' ? 'filt_thermal16' : 'filt_color'];
            if (imageMap.has(image)) {
                return true;
            }
            imagesNotFound++;
            return false;
        });
        let records = getCsvRecords(file, filters);
        if (command.num) {
            records = records.slice(0, parseInt(command.num) + 1);
        }
        let stats = getCsvStats(records);
        let images;
        if (command.imgtype == 'thermal') {
            images = Array.from(stats.thermal16Stats.uniqueImages.keys());
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
            imageUtil.copyImageFilesToDir(images, imageMap, command.outdir);
            if (command.bboxes) {
                for (let image of images) {
                    let uniqueImages = command.imgtype == 'thermal' ? stats.thermal16Stats.uniqueImages : stats.colorStats.uniqueImages;
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

program.on('--help', () => {
    console.log('');
    console.log('For all commands, <file> is a CSV file of CHESS label data.');
    console.log('');
    console.log('split options:');
    console.log('');
    console.log('    -n, --num <images>         Number of thermal images to include in first label set');
    console.log('    -a, --output1 <filename>   First output file name');
    console.log('    -b, --output2 <filename>   Second output file name');
    console.log('');
    console.log('prep options:');
    console.log('');
    console.log('    -i, --imgdirs <dirs>       Comma-separated list of file paths containing images');
    console.log('    -t, --imgtype <type>       "thermal" or "color" (defaults to "thermal")');
    console.log('    -n, --num <images>         Number of thermal images to (non-randomly) select for inclusion');
    console.log('    -b, --bboxes               Whether to output .bboxes[.labels].tsv files next to images');
    console.log('    -o, --outdir <dir>         Destination for output files');
    console.log('');
});

program
    .option('-f, --filters <conditions>', 'Comma-separated list of filter conditions, e.g. hotspot_type=Animal')
    .parse(process.argv);

if (!process.argv.slice(2).length) {
    program.outputHelp();
}
