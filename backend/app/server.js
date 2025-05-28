const express = require('express');
const { InfluxDB, Point } = require('@influxdata/influxdb-client');
const swaggerJsdoc = require('swagger-jsdoc');
const swaggerUi = require('swagger-ui-express');
const http = require('http');
const path = require('path');
require('dotenv').config();

const app = express();
const port = 3000;

const swaggerDef = require('./swagger/swaggerDef');
const dataPostDoc = require('./swagger/data.post');
const dataGetDoc = require('./swagger/data.get');


const options = {
  definition: swaggerDef,
  apis: [                  
    path.resolve(__dirname, 'swagger/data.post.js'),
    path.resolve(__dirname, 'swagger/data.get.js')
  ],
};

const swaggerSpec = swaggerJsdoc(options);



app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerSpec));

app.use(express.json());

const waitForInfluxDB = () => {
  return new Promise((resolve) => {
    const check = () => {
      http.get(`${process.env.INFLUXDB_URL}/health`, (res) => {
        if (res.statusCode === 200) {
          console.log('InfluxDB is ready!');
          resolve();
        } else {
          console.log(`InfluxDB not ready yet (status: ${res.statusCode}), retrying...`);
          setTimeout(check, 2000);
        }
      }).on('error', (err) => {
        console.log(`InfluxDB connection error: ${err.message}, retrying...`);
        setTimeout(check, 2000);
      });
    };
    check();
  });
};

// Инициализация InfluxDB
let influxDB, writeApi;

const initInfluxDB = async () => {
  await waitForInfluxDB();
  
  influxDB = new InfluxDB({
    url: process.env.INFLUXDB_URL,
    token: process.env.INFLUXDB_TOKEN
  });

  writeApi = influxDB.getWriteApi(
    process.env.INFLUXDB_ORG, 
    process.env.INFLUXDB_BUCKET
  );
  
  console.log('InfluxDB client initialized');
};

app.post('/data', (req, res) => {
  const { device_id, measurements } = req.body;

  if (!device_id || !measurements || measurements.length === 0) {
    return res.status(400).json({ error: 'Missing required fields' });
  }

  try {
    measurements.forEach(measurement => {
      const point = new Point(measurement.name)
        .tag('device_id', device_id)
        .floatField('value', measurement.value)
        .timestamp(new Date(measurement.timestamp));
      writeApi.writePoint(point);
    });

    writeApi.flush().then(() => {
      res.status(200).json({ message: 'Data written successfully' });
    }).catch(err => {
      console.error('Write error', err);
      res.status(500).json({ error: 'Data write error' });
    });
  } catch (error) {
    console.error('Processing error', error);
    res.status(500).json({ error: 'Data processing error' });
  }
});

app.get('/data/:deviceId', async (req, res) => {
  const deviceId = req.params.deviceId;
  const { name, start = '-1h' } = req.query;

  try {
    const fluxQuery = `
      from(bucket: "${process.env.INFLUXDB_BUCKET}")
      |> range(start: ${start})
      |> filter(fn: (r) => r.device_id == "${deviceId}")
      ${name ? `|> filter(fn: (r) => r._measurement == "${name}")` : ''}
    `;

    const queryApi = influxDB.getQueryApi(process.env.INFLUXDB_ORG);
    const result = [];
    
    for await (const { values, tableMeta } of queryApi.iterateRows(fluxQuery)) {
      result.push(tableMeta.toObject(values));
    }
    
    res.json(result);
  } catch (error) {
    console.error('Query error', error);
    res.status(500).json({ error: 'Query execution error' });
  }
});

initInfluxDB().then(() => {
  app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
    console.log(`Swagger UI available at http://localhost:${port}/api-docs`);
  });
});