const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const Candidate = require('../models/candidateModel');
const Job = require('../models/jobModel');
const mongoose = require('mongoose');
const axios = require('axios');
const FormData = require('form-data');
const multer = require('multer');
const communicationEvaluationModel = require('../models/communicationEvaluationModel');
const evaluationModel = require('../models/evaluationModel');
const cultureFitModel = require('../models/cultureFitModel');

// Configure multer for file upload (in-memory storage for simplicity)
const storage = multer.memoryStorage();
const upload = multer({
  storage,
  limits: { fileSize: 5 * 1024 * 1024 }, // Limit file size to 5MB
  fileFilter: (req, file, cb) => {
    if (file.mimetype === 'application/pdf') {
      cb(null, true);
    } else {
      cb(new Error('Only PDF files are allowed'), false);
    }
  }
}).single('resume');

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

const evaluateCandidate = async (req, res) => {
  upload(req, res, async (err) => {
    try {
      if (err) {
        return res.status(400).json({ message: 'Error uploading resume: ' + err.message });
      }

      const { answers, github_url, job_description, candidateID } = req.body;
      const resume = req.file;

      // Validate required fields
      if (!resume || !answers || !job_description || !candidateID) {
        return res.status(400).json({ 
          message: 'Missing required fields: resume, answers, job_description, and candidateID are required' 
        });
      }

      // Validate answers_array format
      let parsedAnswers;
      try {
        parsedAnswers = typeof answers === 'string' ? JSON.parse(answers) : answers;
        if (!Array.isArray(parsedAnswers) || !parsedAnswers.every(item => 
          typeof item === 'object' && item.text && typeof item.text === 'string' && item.type && typeof item.type === 'string'
        )) {
          return res.status(400).json({ 
            message: 'Invalid answers format: must be an array of objects with text and type fields' 
          });
        }
      } catch (error) {
        return res.status(400).json({ 
          message: 'Invalid answers: must be valid JSON', 
          error: error.message 
        });
      }

      // Find matching job based on job description
      const matchingJob = await Job.findOne({
        $or: [
          { description: { $regex: job_description, $options: 'i' } },
          { title: { $regex: job_description, $options: 'i' } },
          { requirements: { $in: [new RegExp(job_description, 'i')] } }
        ]
      });

      if (!matchingJob) {
        return res.status(404).json({ 
          message: 'No matching job found for the provided job description' 
        });
      }

      // Log the input for debugging
      console.log('Sending to Python endpoint /evaluate_candidate:', {
        resume: resume.originalname,
        answers: parsedAnswers,
        github_url: github_url || '',
        job_description,
        candidateID,
        matched_job_id: matchingJob._id
      });

      // Create FormData for the POST request to /evaluate_candidate
      const formData = new FormData();
      formData.append('resume', resume.buffer, {
        filename: resume.originalname,
        contentType: resume.mimetype
      });
      formData.append('answers', JSON.stringify(parsedAnswers));
      formData.append('github_url', github_url || '');
      formData.append('job_description', job_description);

      // Make POST request to the /evaluate_candidate endpoint
      const response = await axios.post('http://localhost:5000/evaluate_candidate', formData, {
        headers: {
          ...formData.getHeaders()
        }
      });

      const evaluationData = response.data;

      // Extract skills from matched_skills in technical_evaluation
      const extractedSkills = evaluationData.technical_evaluation?.matched_skills?.map(skillObj => skillObj.skill) || [];

      // Extract work experience from resume_data if available, otherwise use empty array
      const extractedWorkExperience = evaluationData.resume_data?.work_experience || [];

      // Extract education from resume_data if available, otherwise use empty array
      const extractedEducation = evaluationData.resume_data?.education || [];

      // Extract GitHub contributions/projects from technical evaluation
      const githubContributions = evaluationData.technical_evaluation?.project_evaluation || [];

      // Update Candidate with evaluation results and resume data
      const candidateUpdate = {
        answers: parsedAnswers,
        github_contributions: githubContributions,
        created_at: evaluationData.created_at || new Date().toISOString(),
        skills: extractedSkills,
        work_experience: extractedWorkExperience,
        education: extractedEducation,
        github_url: github_url || ''
      };

      console.log('Candidate update data:', candidateUpdate);

      const updatedCandidate = await Candidate.findByIdAndUpdate(
        candidateID,
        candidateUpdate,
        { new: true }
      );

      if (!updatedCandidate) {
        return res.status(404).json({ 
          message: 'Candidate not found with the provided candidateID' 
        });
      }

      console.log('Updated candidate:', updatedCandidate);

      // Save Communication Evaluation with job_id
      const communicationEval = new communicationEvaluationModel({
        communication_score: evaluationData.communication_evaluation?.communication_score || 0,
        clarity_assessment: evaluationData.communication_evaluation?.clarity_assessment || '',
        structure_assessment: evaluationData.communication_evaluation?.structure_assessment || '',
        tone_assessment: evaluationData.communication_evaluation?.tone_assessment || '',
        strengths: evaluationData.communication_evaluation?.strengths || [],
        weaknesses: evaluationData.communication_evaluation?.weaknesses || [],
        candidate_id: candidateID,
        job_id: matchingJob._id.toString(),
        created_at: evaluationData.communication_evaluation?.created_at || new Date().toISOString(),
        processing_time: evaluationData.communication_evaluation?.processing_time || 0
      });

      await communicationEval.save();

      // Save Technical Evaluation
      const evaluation = new evaluationModel({
        technical_evaluation: {
          matched_skills: evaluationData.technical_evaluation?.matched_skills || [],
          project_evaluation: evaluationData.technical_evaluation?.project_evaluation?.map(proj => 
            `${proj.repo_name}: ${proj.details} (Complexity: ${proj.complexity}, Relevance: ${proj.relevance})`
          ) || [],
          technical_answers_score: evaluationData.technical_evaluation?.technical_answers_score || 'Low',
          overall_technical_fit: evaluationData.technical_evaluation?.overall_technical_fit || 'Low',
          coverage_percentage: evaluationData.technical_evaluation?.coverage_percentage || 0
        },
        communication_evaluation: {
          error: evaluationData.communication_evaluation?.error || ''
        },
        candidate_id: candidateID,
        job_id: matchingJob._id.toString(),
        created_at: evaluationData.created_at || new Date().toISOString(),
        processing_time: evaluationData.processing_time || 0
      });

      await evaluation.save();

      // Trigger cultural fit evaluation by making a POST request to /evaluate_cultural_fit
      console.log('Sending to Python endpoint /evaluate_cultural_fit:', {
        resume: resume.originalname,
        answers: parsedAnswers,
        github_url: github_url || '',
        job_description,
        candidateID,
        job_id: matchingJob._id
      });

      const culturalFitFormData = new FormData();
      culturalFitFormData.append('resume', resume.buffer, {
        filename: resume.originalname,
        contentType: resume.mimetype
      });
      culturalFitFormData.append('answers', JSON.stringify(parsedAnswers));
      culturalFitFormData.append('github_url', github_url || '');
      culturalFitFormData.append('job_description', job_description);
      culturalFitFormData.append('candidate_id', candidateID);
      culturalFitFormData.append('job_id', matchingJob._id.toString());

      const culturalFitResponse = await axios.post('http://localhost:5000/evaluate_cultural_fit', culturalFitFormData, {
        headers: {
          ...culturalFitFormData.getHeaders()
        }
      });

      const culturalFitData = culturalFitResponse.data;

      // Validate cultural fit response data
      if (
        !culturalFitData.behavioral_answers_assessment ||
        !culturalFitData.candidate_id ||
        !culturalFitData.coverage_percentage ||
        !culturalFitData.created_at ||
        !culturalFitData.cultural_fit_report ||
        !culturalFitData.cultural_fit_score ||
        !culturalFitData.github_indicators_assessment ||
        !culturalFitData.matched_cultural_attributes ||
        !culturalFitData.processing_time ||
        !culturalFitData.strengths ||
        !culturalFitData.weaknesses
      ) {
        throw new Error('Incomplete cultural fit evaluation data received');
      }

      // Validate matched_cultural_attributes format
      if (
        !Array.isArray(culturalFitData.matched_cultural_attributes) ||
        !culturalFitData.matched_cultural_attributes.every(
          item =>
            typeof item === 'object' &&
            item.attribute &&
            typeof item.attribute === 'string' &&
            item.jd_requirement &&
            typeof item.jd_requirement === 'string' &&
            item.evidence &&
            typeof item.evidence === 'string'
        )
      ) {
        throw new Error('Invalid matched_cultural_attributes format in response');
      }

      // Validate strengths and weaknesses format
      if (
        !Array.isArray(culturalFitData.strengths) ||
        !culturalFitData.strengths.every(item => typeof item === 'string') ||
        !Array.isArray(culturalFitData.weaknesses) ||
        !culturalFitData.weaknesses.every(item => typeof item === 'string')
      ) {
        throw new Error('Invalid strengths or weaknesses format in response');
      }

      // Save Cultural Fit Evaluation
      const cultureFit = new cultureFitModel({
        cultural_fit_score: culturalFitData.cultural_fit_score,
        matched_cultural_attributes: culturalFitData.matched_cultural_attributes,
        behavioral_answers_assessment: culturalFitData.behavioral_answers_assessment,
        github_indicators_assessment: culturalFitData.github_indicators_assessment,
        cultural_fit_report: culturalFitData.cultural_fit_report,
        strengths: culturalFitData.strengths,
        weaknesses: culturalFitData.weaknesses,
        coverage_percentage: culturalFitData.coverage_percentage,
        candidate_id: culturalFitData.candidate_id,
        job_id: matchingJob._id.toString(),
        created_at: culturalFitData.created_at,
        processing_time: culturalFitData.processing_time
      });

      await cultureFit.save();

      // Return the evaluation result along with database save confirmation
      res.status(200).json({ 
        evaluation: {
          technical_evaluation: evaluationData,
          cultural_fit_evaluation: culturalFitData
        },
        database_updates: {
          candidate_updated: true,
          communication_evaluation_saved: true,
          technical_evaluation_saved: true,
          cultural_fit_evaluation_saved: true,
          candidate_id: candidateID,
          job_id: matchingJob._id,
          job_title: matchingJob.title,
          communication_eval_id: communicationEval._id,
          technical_eval_id: evaluation._id,
          cultural_fit_eval_id: cultureFit._id,
          updated_candidate_data: {
            skills: extractedSkills,
            work_experience: extractedWorkExperience,
            education: extractedEducation,
            github_contributions: githubContributions
          }
        }
      });

    } catch (error) {
      console.error('Error in evaluateCandidate:', error);
      
      // Handle different types of errors
      if (error.name === 'ValidationError') {
        return res.status(400).json({ 
          message: 'Database validation error', 
          error: error.message 
        });
      }
      
      if (error.name === 'CastError') {
        return res.status(400).json({ 
          message: 'Invalid candidateID format', 
          error: error.message 
        });
      }
      
      if (error.code === 'ECONNREFUSED') {
        return res.status(503).json({ 
          message: 'Evaluation service is not available', 
          error: 'Connection refused to evaluation service' 
        });
      }
      
      res.status(500).json({ 
        message: 'Error evaluating candidate', 
        error: error.response?.data?.error || error.message 
      });
    }
  });
};

const getJobEvaluations = async (req, res) => {
  try {
    const { job_id } = req.body;

    // Validate job_id format
    if (!job_id.match(/^[0-9a-fA-F]{24}$/)) {
      return res.status(400).json({ message: 'Invalid job ID format' });
    }

    // Find all evaluations matching the job_id
    const communicationEvaluations = await communicationEvaluationModel.find({ job_id });
    const culturalFitEvaluations = await culturalFitEvaluationModel.find({ job_id });
    const technicalEvaluations = await technicalEvaluationModel.find({ job_id });

    // Combine all evaluations into a single response object
    const evaluations = {
      communication: communicationEvaluations,
      cultural_fit: culturalFitEvaluations,
      technical: technicalEvaluations
    };

    // Check if any evaluations were found
    if (
      evaluations.communication.length === 0 &&
      evaluations.cultural_fit.length === 0 &&
      evaluations.technical.length === 0
    ) {
      return res.status(404).json({ message: 'No evaluations found for this job ID' });
    }

    res.status(200).json({ job_id, evaluations });
  } catch (error) {
    res.status(500).json({ message: 'Error retrieving evaluations', error: error.message });
  }
};

module.exports = { Candidatesignup, CandidateLogin, getAllJobs, evaluateCandidate };