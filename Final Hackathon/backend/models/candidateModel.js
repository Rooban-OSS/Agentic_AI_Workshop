const mongoose = require('mongoose');

const candidateSchema = new mongoose.Schema({
  _id: {
    type: mongoose.Schema.Types.ObjectId,
    default: () => new mongoose.Types.ObjectId()
  },
  name: {
    type: String,
  },
  email: {
    type: String,
    required: true,
    match: /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  },
  password:{
    type: String,
    required: true
  },
  skills: {
    type: [String],
  },
  work_experience: [
    {
      company: {
        type: String,
      },
      role: {
        type: String,
      },
      duration: {
        type: String,
      },
      responsibilities: {
        type: [String],
      }
    }
  ],
  education: [
    {
      degree: {
        type: String,
      },
      institution: {
        type: String,
      },
      year: {
        type: String,
      }
    }
  ],
  certifications: [
    {
      name: {
        type: String,
      },
      issuer: {
        type: String,
        default: ''
      },
      year: {
        type: String,
        default: ''
      }
    }
  ],
  answers: [
    {
      text: {
        type: String,
      },
      type: {
        type: String,
      }
    }
  ],
  github_contributions: {
    type: Object,
    default: {}
  },
  created_at: {
    type: String,
  }
}, {
  timestamps: false 
});

module.exports = mongoose.model('Candidate', candidateSchema);