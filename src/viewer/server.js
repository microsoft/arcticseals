const express = require('express');
const app = express();
const router = express.Router();
const $ = jQuery = require('./jquery.js');
var csv = require('./jquery.csv.js');
const port = 3000;

app.use('/', express.static('app'));


app.use('/data', express.static('data'));

app.use('/img', express.static('E:\\noaa\\small-color'));

app.use('/thumb-img', express.static('E:\\noaa\\thumb-color'));

app.use('/thumb-thermal', express.static('E:\\noaa\\thumb-thermal'));

app.use('/crop-img', express.static('E:\\noaa\\crop-img'));

// using router.get() to prefix our path
// url: http://localhost:3000/api/
app.get('/api', (request, response) => {
  response.json({message: 'Hello, welcome to my server'});
});

// set the server to listen on port 3000
app.listen(port, () => console.log(`Listening on port ${port}`));