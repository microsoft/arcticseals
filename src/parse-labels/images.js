let fs = require('fs');
let path = require('path');

const getImageMap = (dirs, type) => {
    let typeSuffix = 'COLOR-8-BIT.JPG';
    if (type == 'thermal') {
        typeSuffix = 'THERM-16BIT.PNG';
    }
    let map = new Map();
    for (let dir of dirs) {
        let files = fs.readdirSync(dir);
        for (let file of files) {
            if (file.endsWith(typeSuffix)) {
                map.set(file, path.join(dir, file));
            }
        }
    }
    return map;
}

module.exports.getImageMap = getImageMap;
