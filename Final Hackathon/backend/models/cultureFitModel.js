const mongoose = require('mongoose');

const cultureFitSchema = new mongoose.Schema({
  _id: {
    type: mongoose.Schema.Types.ObjectId,
    default: () => new mongoose.Types.ObjectId()
  },
  cultural_fit_score: {
    type: Number,
    required: true,
    min: 0,
    max: 100
  },
  matched_cultural_attributes: [{
    attribute: {
      type: String,
      required: true
    },
    jd_requirement: {
      type: String,
      required: true
    },
    evidence: {
      type: String,
      required: true
    }
  }],
  behavioral_answers_assessment: {
    type: String,
    required: true
  },
  github_indicators_assessment: {
    type: String,
    required: true
  },
  cultural_fit_report: {
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
  coverage_percentage: {
    type: Number,
    required: true,
  },
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
  }
}, {
  timestamps: false
});

module.exports = mongoose.model('CultureFit', cultureFitSchema);