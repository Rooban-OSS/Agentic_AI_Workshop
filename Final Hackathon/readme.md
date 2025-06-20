
# AI-Powered Recruitment Platform

A full-stack platform that leverages AI to automate and enhance the recruitment process for both recruiters and candidates. It features a Node.js/Express backend, a React frontend, and Python-based AI agents for advanced candidate evaluation, resume parsing, and scoring.

---

Architecture : https://drive.google.com/file/d/1LYic_nN6VzZCjgFO8GGauJ5ItxwaiqdN/view?usp=sharing

Video : https://drive.google.com/file/d/1eVhIG4jbfsQACMsgqc6iP2bbyLlGb6dN/view?usp=sharing

## Folder Structure

```
.
├── backend/
│   ├── .env
│   ├── index.js
│   ├── controllers/
│   │   ├── candidateController.js
│   │   ├── dashboardController.js
│   │   └── recruiterController.js
│   ├── db/
│   │   └── configDB.js
│   ├── models/
│   │   ├── aggregateModel.js
│   │   ├── candidateModel.js
│   │   ├── communicationEvaluationModel.js
│   │   ├── cultureFitModel.js
│   │   ├── evaluationModel.js
│   │   ├── jobModel.js
│   │   └── recruiterModel.js
│   ├── middleware.js
│   └── package.json
├── frontend/
│   ├── .gitignore
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── README.md
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   ├── index.css
│   │   └── components/
│   │       ├── candidateLoginSign.jsx
│   │       ├── candidateRegister.jsx
│   │       ├── jobDetails.jsx
│   │       ├── jobManagement.jsx
│   │       ├── recruiterLoginSign.jsx
│   │       └── style.css
│   └── public/
├── python/
│   ├── .env
│   ├── agents.py
│   └── app.py
└── package.json
```

---

## Prerequisites

- Node.js (v16+ recommended)
- npm
- Python 3.10+
- pip
- MongoDB Atlas account (or use provided connection strings)
- [OpenAI API Key](https://platform.openai.com/)

---

## Environment Variables

### `backend/.env`

```
MONGODB_URI=mongodb+srv://roobanrihub:hgJbcw6g2pXciAzh@interviewsm.yy0o8wc.mongodb.net/recruiter?retryWrites=true&w=majority&appName=InterviewSM
JWT_SECRET=your_jwt_secret_key
```

### `python/.env`

```
```

---

## Setup Instructions

### 1. Clone the Repository

```sh
git clone <your-repo-url>
cd <repo-folder>
```

---

### 2. Backend Setup

```sh
cd backend
npm install
```

- Create a `.env` file in `backend/` with the values above.

#### Start the Backend Server

```sh
npm start
```

The backend runs on [http://localhost:3000](http://localhost:3000).

---

### 3. Frontend Setup

```sh
cd ../frontend
npm install
```

#### Start the Frontend

```sh
npm run dev
```

The frontend runs on [http://localhost:5173](http://localhost:5173).

---

### 4. Python AI Agent Setup

```sh
cd ../python
pip install -r requirements.txt
```

- Create a `.env` file in `python/` with the values above.

#### Start the Python Service

```sh
python app.py
```

The Python service runs on [http://localhost:5000](http://localhost:5000).

---

## System Overview

- **Frontend**: React SPA for candidate and recruiter flows, job browsing, application, and management.
- **Backend**: Express API for authentication, job CRUD, candidate/job management, and proxying to Python AI endpoints.
- **Python AI Agents**: Flask API for resume parsing, technical/communication/cultural evaluation, and scoring using OpenAI and LangChain.

---

## Key Features

- **Recruiter Portal**: Signup/login, create jobs, view jobs, see candidate evaluations, download CSV reports.
- **Candidate Portal**: Signup/login, browse jobs, apply with resume/answers/GitHub, track applications.
- **AI Resume Parsing**: Extracts structured data from PDF/DOCX resumes.
- **Technical/Communication/Cultural Evaluation**: Uses LLMs and RAG for deep candidate assessment.
- **Scoring & Aggregation**: Weighted scoring of candidates, customizable by job.
- **CSV Export**: Download candidate evaluation reports.

---

## API Endpoints

### Backend (Node.js)

#### Recruiter

- `POST /api/recruiter/signup` — Recruiter registration
- `POST /api/recruiter/login` — Recruiter login
- `POST /api/job/create` — Create a job posting
- `POST /api/job/my-jobs` — List jobs by recruiter
- `POST /api/recruiter/aggregate-score` — Get aggregate candidate scores

#### Candidate

- `POST /api/candidate/signup` — Candidate registration
- `POST /api/candidate/login` — Candidate login
- `GET /api/candidate/jobs` — List all jobs
- `POST /api/candidate/apply` — Apply for a job (uploads resume, answers, GitHub)
- `POST /api/candidate/evaluate` — Get evaluations for a job

### Python AI Service (Flask)

- `POST /parse_candidate` — Parse resume, answers, GitHub; returns structured candidate data
- `POST /evaluate_candidate` — Evaluate technical/communication fit for a job
- `POST /evaluate_cultural_fit` — Evaluate cultural fit for a job
- `POST /aggregate_score` — Aggregate scores with custom weights

---

## Data Models

- **Candidate**: Name, email, password, skills, work experience, education, certifications, answers, GitHub contributions, created_at.
- **Job**: jobId, title, company, location, recruiterId, description, postedDate, weight (scoring weights).
- **Evaluation**: Technical, communication, and cultural fit evaluations, with detailed breakdowns and scores.
- **AggregateScore**: Final weighted score and breakdown for each candidate/job.

---

## Usage Flow

1. **Recruiter** creates an account and posts jobs with custom evaluation weights.
2. **Candidate** registers, browses jobs, and applies by uploading a resume, answering questions, and providing a GitHub link.
3. **AI Agents** parse the resume, analyze answers, fetch GitHub data, and evaluate the candidate for the job.
4. **Recruiter** views all applicants and their AI-generated evaluations and can export results as CSV.

---

## Notes

- MongoDB Atlas must be accessible from your machine.
- The backend and Python services must be running for full functionality.
- The OpenAI API key is required for all AI-powered features.
- Resume parsing supports PDF and DOCX formats.

---

## License

This project is licensed under the ISC License.

---

## Contact

For questions or support, please open an issue or contact the maintainer.

Candidate Evaluation System README

Overview

This system comprises four specialized agents designed to evaluate job candidates based on their resumes, answers, GitHub contributions, and alignment with job requirements. Each agent focuses on a specific aspect of evaluation, leveraging AI (OpenAI GPT-4o mini), MongoDB for data storage, and LangChain for structured processing.

Agents

1. CandidateDataParserAgent

Purpose: Extracts structured information from candidate resumes (PDF or DOCX) and integrates GitHub contributions.

Functionality:





Parses resumes to extract name, email, skills, work experience, education, and certifications.



Fetches GitHub contributions (repos, stars, forks) using the GitHub API.



Saves parsed data to MongoDB (candidate_db.candidates and answers collections).



Handles errors for unsupported file formats or failed extractions.

Key Features:





Uses PyMuPDF for PDF text extraction and python-docx for DOCX files.



Employs a LangChain pipeline with a prompt template for structured JSON output.



Converts non-serializable objects (e.g., MongoDB ObjectId, datetime) for JSON compatibility.

2. CommunicationSkillsEvaluatorAgent

Purpose: Assesses the candidate’s communication skills based on written answers.

Functionality:





Evaluates clarity, structure, and professional tone of candidate answers.



Assigns a communication score (0-100) based on clarity (40%), structure (30%), and tone (30%).



Identifies inappropriate language and provides qualitative feedback.



Saves evaluations to MongoDB (candidate_db.communication_evaluations).

Key Features:





Uses a LangChain pipeline with a tailored prompt for JSON output.



Focuses on at least 80% of provided answers for comprehensive evaluation.

3. TechnicalDepthEvaluatorAgent

Purpose: Evaluates technical skills, project complexity, and technical question responses against a job description (JD).

Functionality:





Matches candidate skills (from resume, GitHub, answers) to JD requirements using semantic/fuzzy matching.



Assigns proficiency levels (Beginner, Intermediate, Advanced) based on experience and certifications.



Evaluates GitHub project complexity (stars, forks, descriptions) and technical answer depth.



Uses Retrieval-Augmented Generation (RAG) with FAISS vector store for context-enhanced evaluation.



Saves results to MongoDB (candidate_db.evaluations).

Key Features:





Integrates with CandidateDataParserAgent and CommunicationSkillsEvaluatorAgent.



Ensures at least 70% coverage of JD technical requirements.



Combines technical and communication evaluation results.

4. CulturalFitEvaluatorAgent

Purpose: Assesses alignment with company values based on soft skills, culture-fit answers, and GitHub contributions.

Functionality:





Evaluates soft skills and behavioral answers (type: culture-fit) for cultural attributes (e.g., collaboration, adaptability).



Analyzes GitHub contributions for teamwork and open-source involvement.



Assigns a cultural fit score (0-100) based on soft skills (30%), behavioral answers (40%), and GitHub indicators (30%).



Uses RAG with FAISS for semantic matching of cultural attributes.



Saves results to MongoDB (candidate_db.cultural_evaluations).

Key Features:





Ensures fairness by avoiding bias in evaluations.



Provides a human-readable cultural fit report.

5. ScoringAndAggregationAgent

Purpose: Aggregates scores from technical, communication, cultural, and optional factors to produce a final candidate score.

Functionality:





Validates input evaluations and weights (default: 40% technical, 25% communication, 25% cultural, 10% optional).



Extracts scores and evaluates optional factors (GitHub project impact, certifications) using LLM.



Aggregates scores using weighted sum and saves to MongoDB (candidate_db.aggregate_scores).



Uses LangGraph for a structured workflow (validate → extract → score optional → aggregate → save).

Key Features:





Ensures weights sum to 1.0 for accurate scoring.



Provides a detailed score breakdown with contributions from each component.

Dependencies





Python libraries: PyPDF2, python-docx, requests, langchain, langchain_openai, pymongo, python-dotenv, faiss-cpu, PyMuPDF.



MongoDB for data storage.



OpenAI API key for LLM access.



Environment variables in .env file (OPENAI_API_KEY, MONGO_URL).

Usage





Setup: Configure .env with API keys and MongoDB URL.



Input: Provide resume (PDF/DOCX), answers (array of text/type), GitHub URL, and job description.



Processing:





CandidateDataParserAgent parses resume and GitHub data.



TechnicalDepthEvaluatorAgent evaluates technical fit.



CommunicationSkillsEvaluatorAgent assesses communication skills.



CulturalFitEvaluatorAgent evaluates cultural alignment.



ScoringAndAggregationAgent combines scores into a final evaluation.



Output: Structured JSON with candidate data, evaluations, and final score, stored in MongoDB.

Notes





All agents return JSON-serializable outputs using convert_to_json_serializable.



Error handling ensures robust processing with detailed logging.



The system uses GPT-4o mini for cost-effective, high-quality evaluations.



RAG enhances technical and cultural evaluations with contextual knowledge.