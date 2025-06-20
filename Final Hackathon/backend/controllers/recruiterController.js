const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const Recruiter = require('../models/recruiterModel');
const Job = require('../models/jobModel');
const { v4: uuidv4 } = require('uuid');
const communicationEvaluationModel = require('../models/communicationEvaluationModel');
const culturalFitEvaluationModel = require('../models/cultureFitModel');
const technicalEvaluationModel = require('../models/evaluationModel');

const signup = async (req, res) => {
  try {
    const { firstName, lastName, email, password, phone, company, yearsOfExperience, location } = req.body;

    // Check if recruiter already exists
    const existingRecruiter = await Recruiter.findOne({ email });
    if (existingRecruiter) {
      return res.status(400).json({ message: 'Recruiter with this email already exists' });
    }

    // Hash password
    const hashedPassword = await bcrypt.hash(password, 10);

    // Create new recruiter
    const recruiter = new Recruiter({
      recruiterId: uuidv4(),
      firstName,
      lastName,
      email,
      password: hashedPassword,
      phone,
      company,
      yearsOfExperience,
      location
    });

    await recruiter.save();

    // Generate JWT
    const token = jwt.sign({ recruiterId: recruiter.recruiterId }, process.env.JWT_SECRET, { expiresIn: '1h' });

    res.status(201).json({ token, recruiterId: recruiter.recruiterId });
  } catch (error) {
    res.status(500).json({ message: 'Error signing up recruiter', error: error.message });
  }
};

const login = async (req, res) => {
  try {
    const { email, password } = req.body;

    // Find recruiter
    const recruiter = await Recruiter.findOne({ email });
    if (!recruiter) {
      return res.status(401).json({ message: 'Invalid email or password' });
    }

    // Check password
    const isMatch = await bcrypt.compare(password, recruiter.password);
    if (!isMatch) {
      return res.status(401).json({ message: 'Invalid email or password' });
    }

    // Generate JWT
    const token = jwt.sign({ recruiterId: recruiter.recruiterId }, process.env.JWT_SECRET, { expiresIn: '1h' });

    res.status(200).json({ token, recruiterId: recruiter.recruiterId });
  } catch (error) {
    res.status(500).json({ message: 'Error logging in recruiter', error: error.message });
  }
};

const createJob = async (req, res) => {
  try {
    const { title, company, location, description, weight } = req.body;
    const recruiterId = req.body.recruiterId; // From JWT middleware

    // Verify recruiter exists
    const recruiter = await Recruiter.findOne({ recruiterId });
    if (!recruiter) {
      return res.status(404).json({ message: 'Recruiter not found' });
    }

    // Validate weight field
    if (weight && !Array.isArray(weight)) {
      return res.status(400).json({ message: 'Weight must be an array' });
    }

    if (weight) {
      for (const w of weight) {
        if (!w.key || !w.value || typeof w.value !== 'object') {
          return res.status(400).json({ message: 'Invalid weight format' });
        }
        const { technical, communication, cultural, optional } = w.value;
        if (
          typeof technical !== 'number' ||
          typeof communication !== 'number' ||
          typeof cultural !== 'number' ||
          typeof optional !== 'number' ||
          technical < 0 || technical > 1 ||
          communication < 0 || communication > 1 ||
          cultural < 0 || cultural > 1 ||
          optional < 0 || optional > 1
        ) {
          return res.status(400).json({ message: 'Weight values must be numbers between 0 and 1' });
        }
      }
    }

    // Create new job
    const job = new Job({
      jobId: uuidv4(),
      title,
      company,
      location,
      recruiterId,
      description,
      weight: weight || [{
        key: 'weights',
        value: {
          technical: 0.4,
          communication: 0.25,
          cultural: 0.25,
          optional: 0.1
        },
        description: '',
        type: 'default',
        enabled: true
      }]
    });

    await job.save();

    res.status(201).json({ message: 'Job created successfully', job });
  } catch (error) {
    res.status(500).json({ message: 'Error creating job', error: error.message });
  }
};

const getMyJobs = async (req, res) => {
  try {
    const { recruiterId } = req.body; 

    // Find jobs by recruiterId
    const jobs = await Job.find({ recruiterId });

    if (!jobs || jobs.length === 0) {
      return res.status(404).json({ message: 'No jobs found for this recruiter' });
    }

    res.status(200).json({ jobs });
  } catch (error) {
    res.status(500).json({ message: 'Error retrieving jobs', error: error.message });
  }
};

const getJobEvaluations = async (req, res) => {
  try {
    const { job_id } = req.body;

    console.log('Received job_id:', job_id);

    // Validate job_id format
    if (!job_id.match(/^[0-9a-fA-F]{24}$/)) {
      return res.status(400).json({ message: 'Invalid job ID format' });
    }

    // Find all evaluations matching the job_id
    const communicationEvaluations = await communicationEvaluationModel.find({ job_id });
    const culturalFitEvaluations = await culturalFitEvaluationModel.find({ job_id });
    const technicalEvaluations = await technicalEvaluationModel.find({ job_id });

    // Group evaluations by candidate_id
    const evaluationsByCandidate = {};

    // Helper function to group evaluations
    const groupByCandidate = (evaluations, type) => {
      evaluations.forEach(eval => {
        const candidateId = eval.candidate_id.toString();
        if (!evaluationsByCandidate[candidateId]) {
          evaluationsByCandidate[candidateId] = {
            candidate_id: candidateId,
            communication: [],
            cultural_fit: [],
            technical: []
          };
        }
        evaluationsByCandidate[candidateId][type].push(eval);
      });
    };

    // Group each type of evaluation
    groupByCandidate(communicationEvaluations, 'communication');
    groupByCandidate(culturalFitEvaluations, 'cultural_fit');
    groupByCandidate(technicalEvaluations, 'technical');

    // Convert object to array for response
    const evaluationsArray = Object.values(evaluationsByCandidate);

    // Check if any evaluations were found
    if (evaluationsArray.length === 0) {
      return res.status(404).json({ message: 'No evaluations found for this job ID' });
    }

    res.status(200).json({ job_id, evaluations: evaluationsArray });
  } catch (error) {
    res.status(500).json({ message: 'Error retrieving evaluations', error: error.message });
  }
};

const AggregateScore = require('../models/aggregateModel');

const getAggregateScore = async (req, res) => {
  console.log('Request headers:', req.headers);
  console.log('Request body:', req.body);
  console.log('Request body type:', typeof req.body);
  
  try {
    const {
      technical_evaluation,
      communication_evaluation,
      cultural_evaluation,
      weights,
      candidate_id,
      job_id
    } = req.body;

    console.log('Received evaluations:', { 
      technical_evaluation, 
      communication_evaluation, 
      cultural_evaluation, 
      weights,
      candidate_id, 
      job_id 
    });

    // Validate input
    if (!technical_evaluation || !communication_evaluation || !cultural_evaluation || !weights || !candidate_id || !job_id) {
      return res.status(400).json({ message: 'Missing required fields' });
    }

    // Validate weights structure - it should be an object with technical, communication, cultura

    console.log('Weights received:', weights);

    // Fixed calculateScore function with proper operator precedence
    const calculateScore = (evaluation, weight) => {
      const score = (evaluation['technical_answers_score'] === 'High' ? 1 : 0) +
                    (evaluation['matched_skills'] ? 1 : 0);
      return score * weight;
    };

    const startTime = Date.now();

    // Calculate individual scores
    const technicalScore = calculateScore(technical_evaluation, weights.technical);
    const communicationScore = calculateScore(communication_evaluation, weights.communication);
    const culturalScore = calculateScore(cultural_evaluation, weights.cultural);

    const totalScore = technicalScore + communicationScore + culturalScore;
    const totalWeight = weights.technical + weights.communication + weights.cultural;
    
    // Normalize score to percentage (if weights are in decimal form 0-1)
    // If weights are percentages (like 40, 30, 30), divide by 100 first
    const isPercentage = weights.technical > 1 || weights.communication > 1 || weights.cultural > 1;
    
    let normalizedScore;
    if (isPercentage) {
      // Weights are percentages, normalize them
      const normalizedWeights = {
        technical: weights.technical / 100,
        communication: weights.communication / 100,
        cultural: weights.cultural / 100
      };
      const techScore = calculateScore(technical_evaluation, normalizedWeights.technical);
      const commScore = calculateScore(communication_evaluation, normalizedWeights.communication);
      const cultScore = calculateScore(cultural_evaluation, normalizedWeights.cultural);
      const totalNormalizedWeight = normalizedWeights.technical + normalizedWeights.communication + normalizedWeights.cultural;
      normalizedScore = totalNormalizedWeight > 0 ? ((techScore + commScore + cultScore) / totalNormalizedWeight) * 100 : 0;
    } else {
      // Weights are already decimals
      normalizedScore = totalWeight > 0 ? (totalScore / totalWeight) * 100 : 0;
    }

    const processingTime = Date.now() - startTime;

    // Calculate raw scores for breakdown
    const getRawScore = (evaluation) => {
      return (evaluation['technical_answers_score'] === 'High' ? 1 : 0) + 
             (evaluation['matched_skills'] ? 1 : 0);
    };

    // Prepare score breakdown
    const scoreBreakdown = {
      technical: {
        raw_score: getRawScore(technical_evaluation),
        weight: weights.technical,
        weighted_score: technicalScore,
        contribution: totalScore > 0 ? (technicalScore / totalScore) * 100 : 0
      },
      communication: {
        raw_score: getRawScore(communication_evaluation),
        weight: weights.communication,
        weighted_score: communicationScore,
        contribution: totalScore > 0 ? (communicationScore / totalScore) * 100 : 0
      },
      cultural: {
        raw_score: getRawScore(cultural_evaluation),
        weight: weights.cultural,
        weighted_score: culturalScore,
        contribution: totalScore > 0 ? (culturalScore / totalScore) * 100 : 0
      }
    };

    // Save to AggregateScore model
    const aggregateScore = new AggregateScore({
      candidate_id,
      final_score: normalizedScore,
      score_breakdown: scoreBreakdown,
      weights: weights,
      created_at: new Date().toISOString(),
      processing_time: processingTime,
      job_id
    });

    await aggregateScore.save();

    res.status(200).json({
      success: true,
      candidate_id,
      job_id,
      aggregate_score: normalizedScore,
      score_breakdown: scoreBreakdown,
      weights_used: weights,
      details: {
        technical: technical_evaluation,
        communication: communication_evaluation,
        cultural: cultural_evaluation
      },
      processing_time: processingTime
    });
  } catch (error) {
    console.error('Full error:', error);
    res.status(500).json({ 
      success: false,
      message: 'Error calculating aggregate score', 
      error: error.message 
    });
  }
};


module.exports = { signup, login, createJob, getMyJobs, getJobEvaluations, getAggregateScore };