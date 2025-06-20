const mongoose = require('mongoose');

const recruiterSchema = new mongoose.Schema({
  recruiterId: {
    type: String,
    required: true,
    unique: true,
  },
  firstName: {
    type: String,
    required: true,
    minlength: 1,
    maxlength: 50
  },
  lastName: {
    type: String,
    required: true,
    minlength: 1,
    maxlength: 50
  },
  email: {
    type: String,
    required: true,
    match: /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  },
  password: {
    type: String,
    required: true,
  },
  phone: {
    type: String,
    match: /^\+?[1-9]\d{1,14}$/
  },
  company: {
    type: String,
    required: true,
    minlength: 1,
    maxlength: 100
  },
  yearsOfExperience: {
    type: Number,
    min: 0,
    default: 0
  },
  location: {
    type: String,
    minlength: 1,
    maxlength: 100
  }
}, {
  timestamps: true
});

module.exports = mongoose.model('Recruiter', recruiterSchema);