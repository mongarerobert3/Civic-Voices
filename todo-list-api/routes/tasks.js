// routes/tasks.js
const express = require('express');
const taskController = require('../controllers/taskController');
const verifyToken = require('../middleware/auth');
const router = express.Router();

/**
 * @swagger
 * tags:
 *   name: Tasks
 *   description: API endpoints for managing tasks
 */

/**
 * @swagger
 * /tasks:
 *   post:
 *     summary: Create a new task.
 *     tags: [Tasks]
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               title:
 *                 type: string
 *                 example: Task 1
 *               description:
 *                 type: string
 *                 example: Description of Task 1
 *     responses:
 *       201:
 *         description: Task created successfully.
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 task:
 *                   type: object
 *                   properties:
 *                     title:
 *                       type: string
 *                       example: Task 1
 *                     description:
 *                       type: string
 *                       example: Description of Task 1
 *       400:
 *         description: Bad request.
 */
router.post('/', verifyToken, taskController.createTask);

/**
 * @swagger
 * /tasks:
 *   get:
 *     summary: Get all tasks.
 *     tags: [Tasks]
 *     responses:
 *       200:
 *         description: Successfully retrieved tasks.
 *         content:
 *           application/json:
 *             schema:
 *               type: array
 *               items:
 *                 type: object
 *                 properties:
 *                   title:
 *                     type: string
 *                     example: Task 1
 *                   description:
 *                     type: string
 *                     example: Description of Task 1
 *       500:
 *         description: Internal server error.
 */
router.get('/', verifyToken, taskController.getTasks);

/**
 * @swagger
 * /tasks/{id}:
 *   put:
 *     summary: Update an existing task.
 *     tags: [Tasks]
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         description: The task ID.
 *         schema:
 *           type: string
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               title:
 *                 type: string
 *                 example: Updated Task Title
 *               description:
 *                 type: string
 *                 example: Updated task description.
 *     responses:
 *       200:
 *         description: Task updated successfully.
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 task:
 *                   type: object
 *                   properties:
 *                     title:
 *                       type: string
 *                       example: Updated Task Title
 *                     description:
 *                       type: string
 *                       example: Updated task description.
 *       400:
 *         description: Bad request.
 *       404:
 *         description: Task not found.
 */
router.put('/:id', verifyToken, taskController.updateTask);

/**
 * @swagger
 * /tasks/{id}:
 *   delete:
 *     summary: Delete a task.
 *     tags: [Tasks]
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         description: The task ID.
 *         schema:
 *           type: string
 *     responses:
 *       200:
 *         description: Task deleted successfully.
 *       400:
 *         description: Bad request.
 *       404:
 *         description: Task not found.
 */
router.delete('/:id', verifyToken, taskController.deleteTask);

module.exports = router;
