const mongoose = require('mongoose');

const evaluationSchema = new mongoose.Schema({
  _id: {
    type: mongoose.Schema.Types.ObjectId,
    default: () => new mongoose.Types.ObjectId()
  },
  technical_evaluation: {
    matched_skills: [{
      skill: {
        type: String,
        required: true
      },
      jd_requirement: {
        type: String,
        required: true
      },
      proficiency: {
        type: String,
        required: true,
        enum: ['Beginner', 'Intermediate', 'Advanced']
      },
      evidence: {
        type: String,
        required: true
      }
    }],
    project_evaluation: [{
      type: String
    }],
    technical_answers_score: {
      type: String,
      required: true,
      enum: ['Low', 'Medium', 'High']
    },
    overall_technical_fit: {
      type: String,
      required: true,
      enum: ['Low', 'Medium', 'High']
    },
    coverage_percentage: {
      type: Number,
      required: true,
      min: 0,
    }
  },
  communication_evaluation: {
    error: {
      type: String,
      default: ''
    }
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
  },
}, {
  timestamps: false
});

module.exports = mongoose.model('Evaluation', evaluationSchema);