const express = require('express');
const connectDB = require('./db/configDB');
const { signup, login, createJob, getMyJobs, getJobEvaluations, getAggregateScore } = require('./controllers/recruiterController');
const cors = require('cors');
const { Candidatesignup, CandidateLogin, getAllJobs, evaluateCandidate } = require('./controllers/candidateController');
const bodyParser = require('body-parser');
const multer = require('multer');

const app = express();


// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true })); // For application/x-www-form-urlencoded 

app.use(cors({
  origin: 'http://localhost:5173',
  methods: ['GET', 'POST'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));

// Connect to MongoDB
connectDB();

// Routes
app.post('/api/recruiter/signup', signup);
app.post('/api/recruiter/login', login);
app.post('/api/job/create',  createJob);
app.post('/api/job/my-jobs', getMyJobs);
app.post('/api/candidate/signup' , Candidatesignup);
app.post('/api/candidate/login', CandidateLogin);
app.get('/api/candidate/jobs', getAllJobs);
app.post('/api/candidate/apply', evaluateCandidate);
app.post('/api/candidate/evaluate', getJobEvaluations);
app.use(bodyParser.json());
app.post('/api/recruiter/aggregate-score', getAggregateScore);

// Start server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});