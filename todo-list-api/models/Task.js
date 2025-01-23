const mongoose = require('mongoose');

const TaskSchema = new mongoose.Schema({
    userId: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
    text: { type: String, required: true },
    completed: { type: Boolean, default: false },
    deleted: { type: Boolean, default: false }
}, { timestamps: true });

TaskSchema.index({ userId: 1 });

module.exports = mongoose.model('Task', TaskSchema);
