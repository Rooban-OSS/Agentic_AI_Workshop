const mongoose = require('mongoose');

const aggregateScoreSchema = new mongoose.Schema({
  _id: {
    type: mongoose.Schema.Types.ObjectId,
    default: () => new mongoose.Types.ObjectId()
  },
  candidate_id: {
    type: String,
    required: true,
    ref: 'Candidate'
  },
  final_score: {
    type: Number,
    required: true,
    min: 0,
    max: 100
  },
  score_breakdown: {
    technical: {
      score: {
        type: Number,
        required: true,
        min: 0,
        max: 100
      },
      weight: {
        type: Number,
        required: true,
        min: 0,
        max: 1
      },
      contribution: {
        type: Number,
        required: true
      }
    },
    communication: {
      score: {
        type: Number,
        required: true,
        min: 0,
        max: 100
      },
      weight: {
        type: Number,
        required: true,
        min: 0,
        max: 1
      },
      contribution: {
        type: Number,
        required: true
      }
    },
    cultural: {
      score: {
        type: Number,
        required: true,
        min: 0,
        max: 100
      },
      weight: {
        type: Number,
        required: true,
        min: 0,
        max: 1
      },
      contribution: {
        type: Number,
        required: true
      }
    },
    optional: {
      score: {
        type: Number,
        required: false,
        min: 0,
        max: 100
      },
      weight: {
        type: Number,
        required: false,
        min: 0,
        max: 1
      },
      contribution: {
        type: Number,
        required: false
      }
    }
  },
  weights: {
    technical: {
      type: Number,
      required: true,
      min: 0,
      max: 1
    },
    communication: {
      type: Number,
      required: true,
      min: 0,
      max: 1
    },
    cultural: {
      type: Number,
      required: true,
      min: 0,
      max: 1
    },
    optional: {
      type: Number,
      required: false,
      min: 0,
      max: 1
    }
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

module.exports = mongoose.model('AggregateScore', aggregateScoreSchema);
