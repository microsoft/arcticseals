'use strict';

let fs = require('fs');
let program = require('commander');
let parse = require('csv-parse/lib/sync');

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
        uniqueImages: new Set(),
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
    imageStats.uniqueImages.add(f);
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

program
    .option('-f, --file [filename]', 'CSV file of CHESS label data')
    .parse(process.argv);

if (!program.file) {
    program.outputHelp();
    process.exit();
}

let input = fs.readFileSync(program.file).toString();
let records = parse(input, {columns: true});
let stats = initRecordStats();
for (let r of records) {
    examineRecord(r, stats);
}
printStats(stats);