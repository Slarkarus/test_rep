/**
 * @swagger
 * /data:
 *   post:
 *     summary: Запись данных измерений
 *     description: Сохраняет данные измерений от устройства в InfluxDB
 *     tags: [Measurements]
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               device_id:
 *                 type: string
 *                 example: "device-001"
 *               measurements:
 *                 type: array
 *                 items:
 *                   $ref: '#/components/schemas/Measurement'
 *     responses:
 *       200:
 *         description: Данные успешно записаны
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 message:
 *                   type: string
 *       400:
 *         description: Некоторые обязательные поля отсутствуют
 *       500:
 *         description: Ошибка сервера
 */
module.exports = {};