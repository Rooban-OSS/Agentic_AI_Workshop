const mongoose = require('mongoose');

const jobSchema = new mongoose.Schema({
  jobId: {
    type: String,
    required: true,
    unique: true
  },
  title: {
    type: String,
    required: true,
    minlength: 1,
    maxlength: 100
  },
  company: {
    type: String,
    required: true,
    minlength: 1,
    maxlength: 100
  },
  location: {
    type: String,
    required: true,
    minlength: 1,
    maxlength: 100
  },
  recruiterId: {
    type: String,
    required: true,
    ref: 'Recruiter'
  },
  description: {
    type: String,
    maxlength: 500
  },
  postedDate: {
    type: Date,
    default: Date.now
  },
  weight: [{
    key: {
      type: String,
      required: true
    },
    value: {
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
        required: true,
        min: 0,
        max: 1
      }
    },
    description: {
      type: String,
      default: ''
    },
    type: {
      type: String,
      default: 'default'
    },
    enabled: {
      type: Boolean,
      default: true
    }
  }]
}, {
  timestamps: true
});

module.exports = mongoose.model('Job', jobSchema);