/**
 * @swagger
 * /data/{deviceId}:
 *   get:
 *     summary: Получение данных измерений
 *     description: Возвращает данные измерений для указанного устройства
 *     tags: [Measurements]
 *     parameters:
 *       - in: path
 *         name: deviceId
 *         required: true
 *         schema:
 *           type: string
 *         description: ID устройства
 *       - in: query
 *         name: name
 *         schema:
 *           type: string
 *         description: Название измерения
 *       - in: query
 *         name: start
 *         schema:
 *           type: string
 *           default: -1h
 *         description: Начало временного диапазона
 *     responses:
 *       200:
 *         description: Успешный запрос
 *         content:
 *           application/json:
 *             schema:
 *               type: array
 *               items:
 *                 type: object
 *                 properties:
 *                   _time:
 *                     type: string
 *                   _measurement:
 *                     type: string
 *                   _value:
 *                     type: number
 *                   device_id:
 *                     type: string
 *       500:
 *         description: Ошибка сервера
 */
module.exports = {};