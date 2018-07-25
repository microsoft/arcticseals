let fs = require('fs');
let path = require('path');

const getImageMap = (dirs, type) => {
    let typeSubstr = null;
    if (type == 'color') {
        typeSubstr = 'COLOR-8-BIT.JPG';
    } else if (type == 'thermal16') {
        typeSubstr = 'THERM-16BIT.PNG';
    } else if (type == 'thermal8') {
        typeSubstr = 'THERM-8BIT-N.PNG';
    } else if (type == 'hotspot') {
        typeSubstr = '_HOTSPOT_';
    }
    let map = new Map();
    for (let dir of dirs) {
        let files = fs.readdirSync(dir);
        for (let file of files) {
            if (!typeSubstr || file.indexOf(typeSubstr) >= 0) {
                map.set(file, path.join(dir, file));
            }
        }
    }
    return map;
}

const copyImageFilesToDir = (images, imageMap, dir) => {
    let i = 0;
    for (let image of images) {
        fs.copyFile(imageMap.get(image), path.join(dir, image), (err) => {
            if (err) {
                console.log(`Failed to copy ${image}: ${err}`);
            }
            if (++i % 1000 == 0) {
                console.log(`${i} images copied`);
            }
        });
    }
}

module.exports.getImageMap = getImageMap;
module.exports.copyImageFilesToDir = copyImageFilesToDir;
