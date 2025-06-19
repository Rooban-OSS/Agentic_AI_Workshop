Setup Instructions 
<!-- ------------------------------------------------------- -->
To run the Interview Panel Optimizer, follow these steps:

Clone the Repository:

git clone <repository-url>

Install Dependencies: Ensure Python 3.8+ is installed, then run:

pip install streamlit fastapi pymongo langchain langchain-google-genai langchain-community faiss-cpu sentence-transformers uvicorn python-dotenv pandas plotly requests

Set Environment Variables: Create a .env file in the project root:

<!-- gemini key -->
GEMINI_API_KEY=AIzaSyDm1hEuwB40_ER9gM-PpKnKhMl_flboPQs


Start MongoDB: Ensure MongoDB is running at the URI specified in database.py:
mongodb+srv://roobanrihub:thisisthepassword@cluster0.yeygogo.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0

Update the URI if using a different MongoDB instance.

<!-- Run backend command -->
Run the Backend: Start the FastAPI server:

uvicorn app.main:app --reload


<!-- Run frontend command -->
Run the Frontend: Start the Streamlit app:
streamlit run streamlit_app.py

Don't redirect to app folder !!!!!!!!!


Access the Application:
Backend: http://localhost:8000
Frontend: http://localhost:8501





Project Overview

Describes the project’s goals and technical architecture

The Interview Panel Optimizer addresses the challenge of inefficient and biased interview panel formation in companies. Many organizations struggle with panels that are overqualified, mismatched to the candidate’s role, or prone to bias due to prior associations. This project provides a solution that:





Optimizes panel composition for job role relevance using skill matching.



Ensures diversity in gender, ethnicity, and experience levels.



Prevents conflicts of interest by analyzing past collaborations and reporting structures.



Leverages industry best practices through RAG to design balanced panels.

The application is built with a Streamlit frontend for user interaction, a FastAPI backend for API services, and a MongoDB database for data storage. It uses LangChain and FAISS for RAG, with Google Gemini as the LLM for AI-driven decision-making. Four autonomous AI agents work together to deliver recommendations, coordinated by an orchestrator.

Features

Details the key functionalities of the application

The Interview Panel Optimizer includes the following features:

Job Management

Allows creation and listing of job postings





Create Jobs: Add new job postings with details like job role, description, required skills, experience level, department, and needed interviewer types.



List Jobs: View existing jobs with filtering options (skip, limit) and visualize job distribution by department using Plotly bar charts.



How It Works: Users input job details via a Streamlit form, which are sent to the FastAPI backend (/job/create). The data is stored in MongoDB, and the list endpoint (/jobs) retrieves paginated results.

Interviewer Management

Manages interviewer data and visualization





Add Interviewers: Register interviewers with name, email, department, skills, availability (JSON format), feedback score, experience level, interviewer type, gender, and ethnicity.



List Interviewers: Filter interviewers by department or type, with pagination. Visualize interviewer type distribution using Plotly pie charts.



How It Works: Interviewer data is submitted via a Streamlit form to the /interviewer/add endpoint, stored in MongoDB. The /interviewers endpoint supports filtering and pagination.

Candidate Management

Handles candidate registration and listing





Register Candidates: Add candidates with name, email, job role, skills, and experience level.



List Candidates: Filter candidates by job role with pagination. Visualize experience level distribution using Plotly bar charts.



How It Works: Candidate data is sent to /candidate/register and stored in MongoDB. The /candidates endpoint retrieves filtered, paginated results.

Panel Recommendations

Generates optimized interview panel recommendations





Generate Recommendations: Create optimized interview panels for a job or candidate, considering skill alignment, DEI compliance, and conflict avoidance.



Detailed Analysis: Display panel member details (name, ID, role, match score, conflict status, DEI compliance), skill coverage, quality metrics, conflict summary, DEI summary, and alternative interviewers.



Visualizations: Plotly charts for skill coverage (bar) and quality score distribution (pie).



How It Works: Users select a job or candidate via Streamlit, triggering API calls (/job/{job_id}/recommend_panel or /candidate/{candidate_id}/suggest_panel). The backend orchestrates AI agents to generate recommendations, displayed with badges for conflict and DEI status.

Health Check

Monitors system and database status





System Status: Check the API and database health via the /health endpoint, displaying status, database connection, version, and active features.



How It Works: Streamlit queries the /health endpoint, showing metrics like system status and active features (skill matching, DEI compliance, conflict checking, panel optimization).

DEI Compliance

Ensures diversity in panel composition





Diversity Analysis: Ensures panels meet diversity standards for gender, ethnicity, and experience levels, flagging non-compliant compositions.



How It Works: The DEI Compliance Agent analyzes panel composition against RAG-retrieved DEI policies, assigning compliance statuses and identifying issues.

Conflict Avoidance

Detects and mitigates conflicts of interest





Conflict Detection: Identifies potential or confirmed conflicts (e.g., past collaborations, reporting relationships, departmental overlap).



How It Works: The Conflict Checker Agent uses RAG and LLM reasoning to detect conflicts, providing detailed summaries for each panel member.

AI Agents

Describes the four autonomous AI agents and their roles

The core of the Interview Panel Optimizer lies in its four autonomous AI agents, each designed to handle a specific aspect of panel formation. These agents are implemented as classes in agents.py, using LangChain for AI-driven decision-making and RAG for context-aware recommendations.

Skill Match Agent

Matches interviewers to job requirements





Purpose: Recommends panelists based on alignment with the job’s required skills and past interview feedback.



Functionality:





Calculates a skill match score combining exact skill matches (40%) and semantic similarity (60%) using Google Gemini.



Scores interviewer quality based on past feedback (60%) and years of experience (40%).



Returns a sorted list of interviewers with overall scores, matching skills, and skill gaps.



RAG Integration: Uses semantic similarity for skill matching, primarily relying on LLM reasoning.



Implementation: SkillMatchAgent class with a LangChain LLMChain and a custom prompt for skill analysis.

DEI Compliance Agent

Ensures panel diversity





Purpose: Ensures panels reflect diversity in gender, ethnicity, and experience levels, adhering to DEI policies.



Functionality:





Analyzes panel composition (gender, ethnicity, department, experience level) against DEI policies retrieved via RAG.



Assigns a compliance score (0.0–1.0) and status (compliant/non-compliant) for the panel and each member.



Identifies issues (e.g., underrepresentation of genders or ethnicities).



RAG Integration: Retrieves DEI policies from the FAISS vector store (e.g., “at least 30% representation of underrepresented groups”).



Implementation: DEIComplianceAgent class with a LangChain LLMChain and a prompt for DEI analysis.

Conflict Checker Agent

Identifies conflicts of interest





Purpose: Detects conflicts of interest (e.g., past collaborations, reporting relationships, departmental overlap).



Functionality:





Analyzes relationships between interviewers and the candidate using MongoDB data and LLM reasoning.



Assigns conflict status (none, potential, confirmed) and provides details for each panel member.



Determines an overall conflict level for the panel.



RAG Integration: Uses RAG to retrieve conflict-related best practices, enhancing LLM-based conflict detection.



Implementation: ConflictCheckerAgent class with a LangChain LLMChain and a prompt for conflict analysis.

Panel Design Optimizer Agent

Designs optimal panel compositions





Purpose: Designs balanced panel compositions based on industry best practices.



Functionality:





Generates a panel strategy (size, interviewer types, experience mix, required skills) using RAG-retrieved best practices.



Selects interviewers from the scored list provided by the Skill Match Agent, ensuring alignment with the strategy.



RAG Integration: Retrieves best practices (e.g., “3–5 member panel with technical and behavioral interviewers”) from the FAISS vector store.



Implementation: PanelDesignOptimizerAgent class with a LangChain LLMChain and a prompt for panel composition.

RAG Implementation

Explains how Retrieval-Augmented Generation is used

Retrieval-Augmented Generation (RAG) is a key component, enabling agents to make informed decisions based on industry best practices and DEI policies.





Vector Store: Uses FAISS to store and retrieve best practices and DEI policies. The vector store is initialized in database.py and agents.py with documents like:





“Optimal panel size is 3–5 members, balancing technical, behavioral, and managerial perspectives.”



“DEI policies require at least 30% representation of underrepresented genders and ethnicities.”



Embeddings: Documents are embedded using HuggingFace’s all-MiniLM-L6-v2 model, converting text into vectors for similarity search.



Retrieval Process:





Agents (DEI Compliance, Conflict Checker, Panel Design Optimizer) construct a query based on job, candidate, or panel data.



The query is passed to vector_store.similarity_search, retrieving the top-k relevant documents (e.g., k=2 for DEI, k=3 for panel design).



Retrieved documents are fed as context to the LLM (Google Gemini) via LangChain prompts.



Generation: The LLM combines the retrieved context with job/candidate data to generate structured JSON outputs (e.g., panel strategy, conflict status, DEI compliance).



Benefits:





Ensures context-aware decisions aligned with industry standards.



Allows scalability by adding new best practices to the vector store.

The FAISS vector store is initialized at startup, ensuring all agents access the same knowledge base.

Agent Communication

Details how agents collaborate to produce recommendations

The four AI agents operate autonomously but collaborate through the AgentOrchestrator class in agents.py to produce a cohesive panel recommendation.

AgentOrchestrator Workflow

Describes the orchestration process





Input: Receives a job ID or candidate ID and a flag (is_final) indicating whether it’s a job-based or candidate-based recommendation.



Steps:





Fetch Data: Retrieves job and candidate data from MongoDB. For candidate-based recommendations, finds the corresponding job by job role.



Panel Design Optimizer: Generates a panel composition strategy (size, types, experience mix).



Skill Match Agent: Scores all interviewers based on skill alignment and quality.



Panel Design Optimizer: Selects interviewers to match the strategy.



Conflict Checker Agent: Analyzes the selected panel for conflicts.



DEI Compliance Agent: Evaluates the panel for DEI compliance.



Aggregation: Combines results into a PanelRecommendation object.



Output: Returns a structured JSON response to the FastAPI endpoint.

Data Flow

Explains how data moves between agents





Skill Match Agent: Provides scored interviewers to the Panel Design Optimizer.



Panel Design Optimizer: Generates strategy and selects the panel, passing it to Conflict Checker and DEI Compliance agents.



Conflict Checker & DEI Compliance: Analyze the panel independently, returning results to the orchestrator.



Orchestrator: Aggregates results, calculates skill coverage and quality metrics, and compiles alternatives.

Autonomy

Highlights agent independence





Each agent encapsulates its own LLM chain and prompt, making decisions independently.



The orchestrator ensures loose coupling, allowing agents to focus on their tasks.

Structured Outputs

Describes output format for interoperability





Agents return JSON objects with consistent schemas (e.g., conflict status, DEI compliance score).



The PanelRecommendation Pydantic model ensures data integrity and type safety.

Project Structure

Outlines the organization of the codebase

interview-panel-optimizer/
├── app/
│   ├── __init__.py          # Package initialization
│   ├── main.py              # FastAPI backend with API endpoints
│   ├── database.py          # MongoDB and FAISS vector store setup
│   ├── models.py            # Pydantic models for data validation
│   ├── crud.py              # CRUD operations for MongoDB
│   ├── agents.py            # Autonomous AI agents and orchestrator
│   ├── utils.py             # Empty, as agent logic moved to agents.py
├── streamlit_app.py         # Streamlit frontend for user interaction
├── .env                    # Environment variables
├── README.md               # This file
├── requirements.txt         # Python dependencies

Technologies Used

Lists the technologies powering the project





Python 3.8+: Core programming language.



Streamlit: Web frontend for user interface.



FastAPI: API backend with CORS support.



MongoDB: NoSQL database for data storage.



LangChain: Framework for LLM chains and RAG.



Google Gemini: LLM for AI-driven decision-making.



FAISS: Vector store for RAG with HuggingFace embeddings.



Pydantic: Data validation and type safety.



Plotly: Interactive visualizations.



HuggingFace Embeddings: all-MiniLM-L6-v2 for vectorizing best practices.



Uvicorn: ASGI server for FastAPI.



Python-dotenv: Environment variable management.

Contributing

Guides contributors on how to contribute

Contributions are welcome. To contribute:





Fork the repository.



Create a feature branch (git checkout -b feature/awesome-feature).



Commit changes (git commit -m "Add awesome feature").



Push to the branch (git push origin feature/awesome-feature).



Open a pull request.

Ensure code follows PEP 8 standards and includes tests. For bug reports or feature requests, open an issue on GitHub.

License

Specifies the project’s licensing terms

This project is licensed under the MIT License. See the LICENSE file for details.