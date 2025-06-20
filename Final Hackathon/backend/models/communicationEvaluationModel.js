const mongoose = require('mongoose');

const communicationEvaluationSchema = new mongoose.Schema({
  _id: {
    type: mongoose.Schema.Types.ObjectId,
    default: () => new mongoose.Types.ObjectId()
  },
  communication_score: {
    type: Number,
    required: true,
    min: 0,
    max: 100
  },
  clarity_assessment: {
    type: String,
    required: true
  },
  structure_assessment: {
    type: String,
    required: true
  },
  tone_assessment: {
    type: String,
    required: true
  },
  strengths: [{
    type: String,
    required: true
  }],
  weaknesses: [{
    type: String,
    required: true
  }],
  candidate_id: {
    type: String,
    required: true,
    ref: 'Candidate'
  },
  created_at: {
    type: String,
    required: true
  },
  processing_time: {
    type: Number,
    required: true,
    min: 0
  },
    job_id: {
    type: String,
    required: true,
    ref: 'Job'
  },
}, {
  timestamps: false
});

module.exports = mongoose.model('CommunicationEvaluation', communicationEvaluationSchema);