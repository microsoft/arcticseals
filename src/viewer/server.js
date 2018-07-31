const express = require('express');
const app = express();
const router = express.Router();
const $ = jQuery = require('./jquery.js');
var csv = require('./jquery.csv.js');
var exec = require('child_process').exec;
const fs = require('fs');

const port = 3000;

app.use('/', express.static('app'));


app.use('/data', express.static('data'));

app.use('/img', express.static('E:\\noaa\\small-color'));

app.use('/thumb-img', express.static('E:\\noaa\\thumb-color'));

app.use('/thumb-thermal', express.static('E:\\noaa\\thumb-thermal'));

app.use('/crop-img', express.static('E:\\noaa\\crop-img'));

// using router.get() to prefix our path
// url: http://localhost:3000/api/CHESS_FL1_C_160408_000830.513_COLOR-8-BIT_HOTSPOT_17486.JPG
app.get('/api/:id', (request, response) => {
	var filename = 'E:\\noaa\\crop-img\\' + request.params.id;
	fs.copyFileSync(filename, 'D:\\github\\seals\\src\\viewer\\util\\cnn\\cur\\cur.jpg');
	console.log(request.params.id);
	exec('python D:\\github\\seals\\src\\viewer\\util\\cnn\\SealCurrent.py', {cwd:'D:\\github\\seals\\src\\viewer\\util\\cnn'}, function callback(error, stdout, stderr){
		var lines = stdout.split('\n');
		//console.log(lines[4]);
		response.json({message: lines[4]});
	});
});

// set the server to listen on port 3000
app.listen(port, () => console.log(`Listening on port ${port}`));