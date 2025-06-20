const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const Candidate = require('../models/candidateModel');
const Job = require('../models/jobModel');
const { v4: uuidv4 } = require('uuid');
const mongoose = require('mongoose');

const Candidatesignup = async (req, res) => {
  try {
    const { email, password } = req.body;

    // Check if candidate already exists
    const existingCandidate = await Candidate.findOne({ email });
    if (existingCandidate) {
      return res.status(400).json({ message: 'Candidate with this email already exists' });
    }

    // Hash password
    const hashedPassword = await bcrypt.hash(password, 10);

    // Create new candidate
    const candidate = new Candidate({
      _id: new mongoose.Types.ObjectId(),
      email,
      password: hashedPassword,
      created_at: new Date().toISOString()
    });

    await candidate.save();

    // Generate JWT
    const token = jwt.sign({ candidateId: candidate._id }, process.env.JWT_SECRET, { expiresIn: '1h' });

    res.status(201).json({ token, candidateId: candidate._id });
  } catch (error) {
    res.status(500).json({ message: 'Error signing up candidate', error: error.message });
  }
};

const CandidateLogin = async (req, res) => {
  try {
    const { email, password } = req.body;

    // Find candidate
    const candidate = await Candidate.findOne({ email });
    if (!candidate) {
      return res.status(401).json({ message: 'Invalid email or password' });
    }

    // Check password
    const isMatch = await bcrypt.compare(password, candidate.password);
    if (!isMatch) {
      return res.status(401).json({ message: 'Invalid email or password' });
    }

    // Generate JWT
    const token = jwt.sign({ candidateId: candidate._id }, process.env.JWT_SECRET, { expiresIn: '1h' });

    res.status(200).json({ token, candidateId: candidate._id });
  } catch (error) {
    res.status(500).json({ message: 'Error logging in candidate', error: error.message });
  }
};

const getAllJobs = async (req, res) => {
  try {
    // Find all jobs
    const jobs = await Job.find();

    if (!jobs || jobs.length === 0) {
      return res.status(404).json({ message: 'No jobs found' });
    }

    res.status(200).json({ jobs });
  } catch (error) {
    res.status(500).json({ message: 'Error retrieving jobs', error: error.message });
  }
};

module.exports = { Candidatesignup, CandidateLogin, getAllJobs };