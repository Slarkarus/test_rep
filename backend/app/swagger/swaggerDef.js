module.exports = {
  openapi: '3.0.0',
  info: {
    title: 'Gas Analyzer API',
    version: '1.0.0',
    description: 'API для работы с данными газоанализаторов',
  },
  servers: [
    {
      url: 'http://localhost:3000',
      description: 'Development server',
    },
  ],
  tags: [
    {
      name: 'Measurements',
      description: 'Операции с данными измерений',
    },
  ],
  components: {
    schemas: {
      Measurement: {
        type: 'object',
        properties: {
          name: {
            type: 'string',
            example: 'temperature'
          },
          value: {
            type: 'number',
            example: 25.4
          },
          timestamp: {
            type: 'string',
            format: 'date-time',
            example: '2025-05-28T10:00:00Z'
          }
        }
      }
    }
  },
  
  paths: {}
};