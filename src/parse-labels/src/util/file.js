let fs = require('fs');

const ensureDirExists = (dir) => {
    try {
        fs.mkdirSync(dir);
    } catch (err) {
        if (err.code !== 'EEXIST') {
            throw err;
      }
    }
};

module.exports.ensureDirExists = ensureDirExists;