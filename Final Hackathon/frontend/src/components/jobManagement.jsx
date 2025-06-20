import { useState, useEffect } from 'react';

function JobManagement() {
  const [formData, setFormData] = useState({
    title: '',
    company: '',
    location: '',
    description: '',
    weight: [{
      key: 'weights',
      value: { technical: 0.4, communication: 0.25, cultural: 0.25, optional: 0.1 },
      description: '',
      type: 'default',
      enabled: true
    }]
  });
  const [jobs, setJobs] = useState([]);
  const [message, setMessage] = useState(null);
  const [activeTab, setActiveTab] = useState('create');
  const [selectedJobId, setSelectedJobId] = useState(null);
  const [evaluations, setEvaluations] = useState([]);
  const [expandedSections, setExpandedSections] = useState({});

  const handleInputChange = (e) => {
    if (e.target.name === 'weight') {
      const selectedWeight = JSON.parse(e.target.value);
      setFormData({
        ...formData,
        weight: [{
          key: 'weights',
          value: selectedWeight,
          description: '',
          type: 'default',
          enabled: true
        }]
      });
    } else {
      setFormData({ ...formData, [e.target.name]: e.target.value });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage(null);

    const recruiterId = sessionStorage.getItem('recruiterId');
    if (!recruiterId) {
      setMessage({ type: 'danger', text: 'Please log in to create a job' });
      return;
    }

    const payload = { ...formData, recruiterId };

    try {
      const response = await fetch('http://localhost:3000/api/job/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await response.json();

      if (response.ok) {
        setMessage({ type: 'success', text: 'Job created successfully!' });
        setFormData({
          title: '',
          company: '',
          location: '',
          description: '',
          weight: [{
            key: 'weights',
            value: { technical: 0.4, communication: 0.25, cultural: 0.25, optional: 0.1 },
            description: '',
            type: 'default',
            enabled: true
          }]
        });
        fetchJobs();
        setTimeout(() => setActiveTab('view'), 1500);
      } else {
        setMessage({ type: 'danger', text: data.message || 'Error creating job' });
      }
    } catch (error) {
      setMessage({ type: 'danger', text: 'Network error occurred' });
    }
  };

  const fetchJobs = async () => {
    const recruiterId = sessionStorage.getItem('recruiterId');
    if (!recruiterId) {
      setMessage({ type: 'danger', text: 'Please log in to view jobs' });
      setJobs([]);
      return;
    }

    try {
      const response = await fetch('http://localhost:3000/api/job/my-jobs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ recruiterId })
      });
      const data = await response.json();

      if (response.ok) {
        setJobs(data.jobs || []);
      } else {
        setMessage({ type: 'danger', text: data.message || 'No jobs found' });
        setJobs([]);
      }
    } catch (error) {
      setMessage({ type: 'danger', text: 'Network error occurred' });
      setJobs([]);
    }
  };

  const fetchEvaluations = async (id) => {
    try {
      const response = await fetch('http://localhost:3000/api/candidate/evaluate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ job_id: id })
      });
      const data = await response.json();

      if (response.ok) {
        setEvaluations(data.evaluations || []);
        setActiveTab('evaluations');
      } else {
        setMessage({ type: 'danger', text: data.message || 'No evaluations found' });
        setEvaluations([]);
      }
    } catch (error) {
      setMessage({ type: 'danger', text: 'Network error occurred' });
      setEvaluations([]);
    }
  };

  const downloadCSV = () => {
    const headers = [
      'Candidate ID',
      'Communication Score',
      'Clarity',
      'Structure',
      'Tone',
      'Technical Fit',
      'Technical Score',
      'Coverage %',
      'Cultural Fit Score',
      'Cultural Coverage %',
      'Created At'
    ];

    const rows = evaluations.map(candidate => {
      const comm = candidate.communication[0] || {};
      const tech = candidate.technical[0] || {};
      const culture = candidate.cultural_fit[0] || {};
      return [
        candidate.candidate_id,
        comm.communication_score || '',
        comm.clarity_assessment || '',
        comm.structure_assessment || '',
        comm.tone_assessment || '',
        tech.technical_evaluation?.overall_technical_fit || '',
        tech.technical_evaluation?.technical_answers_score || '',
        tech.technical_evaluation?.coverage_percentage || '',
        culture.cultural_fit_score || '',
        culture.coverage_percentage || '',
        new Date(comm.created_at || tech.created_at || culture.created_at).toLocaleString()
      ].map(field => `"${field}"`).join(',');
    });

    const csvContent = [headers.join(','), ...rows].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `evaluations_job_${selectedJobId}.csv`;
    link.click();
  };

  const downloadCandidateCSV = (candidate) => {
    const headers = [
      'Candidate ID',
      'Communication Score',
      'Clarity',
      'Structure',
      'Tone',
      'Communication Strengths',
      'Communication Weaknesses',
      'Technical Fit',
      'Technical Score',
      'Coverage %',
      'Technical Skills',
      'Technical Projects',
      'Cultural Fit Score',
      'Cultural Coverage %',
      'Cultural Report',
      'Cultural Attributes',
      'Cultural Strengths',
      'Cultural Weaknesses',
      'Created At'
    ];

    const comm = candidate.communication[0] || {};
    const tech = candidate.technical[0] || {};
    const culture = candidate.cultural_fit[0] || {};

    const row = [
      candidate.candidate_id,
      comm.communication_score || '',
      comm.clarity_assessment || '',
      comm.structure_assessment || '',
      comm.tone_assessment || '',
      (comm.strengths || []).join('; ') || '',
      (comm.weaknesses || []).join('; ') || '',
      tech.technical_evaluation?.overall_technical_fit || '',
      tech.technical_evaluation?.technical_answers_score || '',
      tech.technical_evaluation?.coverage_percentage || '',
      (tech.technical_evaluation?.matched_skills || []).map(s => `${s.skill} (${s.proficiency}) - ${s.jd_requirement}`).join('; ') || '',
      (tech.technical_evaluation?.project_evaluation || []).join('; ') || '',
      culture.cultural_fit_score || '',
      culture.coverage_percentage || '',
      culture.cultural_fit_report || '',
      (culture.matched_cultural_attributes || []).map(a => `${a.attribute} - ${a.jd_requirement}`).join('; ') || '',
      (culture.strengths || []).join('; ') || '',
      (culture.weaknesses || []).join('; ') || '',
      new Date(comm.created_at || tech.created_at || culture.created_at).toLocaleString()
    ].map(field => `"${String(field).replace(/"/g, '""')}"`).join(',');

    const csvContent = [headers.join(','), row].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `candidate_${candidate.candidate_id}_evaluation.csv`;
    link.click();
  };

  useEffect(() => {
    fetchJobs();
  }, []);

  const handleTabChange = (tab) => {
    setActiveTab(tab);
    setMessage(null);
    if (tab !== 'evaluations') {
      setSelectedJobId(null);
      setEvaluations([]);
    }
  };

  const handleJobClick = (id) => {
    setSelectedJobId(id);
    fetchEvaluations(id);
  };

  const toggleSection = (candidateId, section) => {
    setExpandedSections(prev => ({
      ...prev,
      [`${candidateId}-${section}`]: !prev[`${candidateId}-${section}`]
    }));
  };

  return (
    <div style={{
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      minHeight: '100vh',
      padding: '2rem 1rem',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
    }}>
      <style>
        {`
          .job-management-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
            max-width: 1000px;
            margin: 0 auto;
            padding: 2.5rem;
          }

          .job-management-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
          }

          .custom-nav {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 0.75rem;
            margin-bottom: 2rem;
            box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.06);
            display: flex;
            gap: 1rem;
            justify-content: center;
          }

          .nav-btn {
            flex: 0 1 auto;
            border-radius: 10px;
            font-weight: 600;
            color: #6c757d;
            transition: all 0.3s ease;
            padding: 0.75rem 2rem;
            border: none;
            background: transparent;
            cursor: pointer;
            font-size: 1.1rem;
            position: relative;
            overflow: hidden;
          }

          .nav-btn:hover {
            color: #ffffff;
            background: linear-gradient(135deg, #667eea, #764ba2);
          }

          .nav-btn.active {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
          }

          .nav-btn::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 3px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            transform: scaleX(0);
            transition: transform 0.3s ease;
          }

          .nav-btn:hover::after {
            transform: scaleX(1);
          }

          .nav-btn.active::after {
            transform: scaleX(1);
          }

          .form-group {
            margin-bottom: 1.5rem;
          }

          .form-label {
            font-weight: 600;
            color: #495057;
            margin-bottom: 0.5rem;
            display: block;
          }

          .form-control {
            width: 100%;
            border: 2px solid #e9ecef;
            border-radius: 12px;
            padding: 0.75rem 1rem;
            transition: all 0.3s ease;
            background: #fafbfc;
            font-size: 1rem;
            font-family: inherit;
          }

          .form-control:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
            background: white;
          }

          .btn-create, .btn-download {
            width: auto;
            background: linear-gradient(135deg, #667eea, #764ba2);
            border: none;
            border-radius: 12px;
            padding: 0.75rem 2rem;
            font-weight: 600;
            font-size: 1.1rem;
            color: white;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
            margin: 0.5rem;
          }

          .btn-create:hover, .btn-download:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
          }

          .btn-download.candidate {
            padding: 0.5rem 1.5rem;
            font-size: 0.9rem;
          }

          .job-item {
            background: linear-gradient(135deg, #f8f9fa, #e9ecef);
            border-radius: 15px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            transition: all 0.3s ease;
            border-left: 4px solid #667eea;
          }

          .job-item:hover {
            transform: translateX(5px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
          }

          .job-title {
            color: #2d3436;
            font-weight: 700;
            font-size: 1.25rem;
            margin: 0 0 0.5rem 0;
          }

          .job-id {
            color: #667eea;
            cursor: pointer;
            font-weight: 500;
            text-decoration: underline;
          }

          .job-id:hover {
            color: #764ba2;
          }

          .job-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
            flex-wrap: wrap;
            gap: 0.5rem;
          }

          .section-title {
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 700;
            text-align: center;
            margin-bottom: 2rem;
            font-size: 2rem;
          }

          .empty-state {
            text-align: center;
            color: #6c757d;
            padding: 3rem 1rem;
            background: #f8f9fa;
            border-radius: 15px;
            border: 2px dashed #dee2e6;
          }

          .alert {
            border: none;
            border-radius: 12px;
            padding: 1rem 1.5rem;
            font-weight: 500;
            margin-bottom: 1.5rem;
          }

          .alert-success {
            background: #d1f2eb;
            color: #0d5d3f;
            border-left: 4px solid #28a745;
          }

          .alert-danger {
            background: #f8d7da;
            color: #721c24;
            border-left: 4px solid #dc3545;
          }

          .fade-in {
            animation: fadeIn 0.5s ease-in;
          }

          @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
          }

          .job-count-badge {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            margin-left: 0.5rem;
          }

          .evaluation-item {
            background: #ffffff;
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
            transition: all 0.3s ease;
          }

          .evaluation-item:hover {
            box-shadow: 0 6px 15px rgba(0, 0, 0, 0.1);
          }

          .evaluation-header {
            font-weight: 600;
            color: #2d3436;
            margin-bottom: 1rem;
            font-size: 1.2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
          }

          .evaluation-section {
            margin-bottom: 1.5rem;
            border-left: 3px solid #667eea;
            padding-left: 1rem;
          }

          .evaluation-section-header {
            cursor: pointer;
            padding: 0.75rem;
            background: #f8f9fa;
            border-radius: 8px;
            margin-bottom: 0.5rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: background 0.3s ease;
          }

          .evaluation-section-header:hover {
            background: #e9ecef;
          }

          .evaluation-label {
            font-weight: 600;
            color: #2d3436;
            font-size: 1.1rem;
            margin: 0;
          }

          .evaluation-text {
            color: #495057;
            line-height: 1.6;
            margin: 0.5rem 0;
          }

          .skills-list {
            list-style: none;
            padding: 0;
            margin: 0;
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
          }

          .skill-item {
            background: #e9ecef;
            padding: 0.25rem 0.75rem;
            border-radius: 8px;
            font-size: 0.9rem;
            color: #495057;
          }

          .toggle-icon {
            font-size: 1.2rem;
            transition: transform 0.3s ease;
          }

          .toggle-icon.expanded {
            transform: rotate(180deg);
          }

          .button-group {
            display: flex;
            justify-content: flex-end;
            margin-bottom: 1.5rem;
            gap: 1rem;
          }

          @media (max-width: 768px) {
            .job-management-card {
              margin: 1rem;
              padding: 1.5rem;
            }
            
            .custom-nav {
              flex-direction: column;
              gap: 0.5rem;
            }
            
            .nav-btn {
              text-align: center;
              padding: 0.75rem 1rem;
            }
            
            .job-meta {
              flex-direction: column;
              align-items: flex-start;
            }
            
            .button-group {
              flex-direction: column;
              align-items: stretch;
            }
            
            .evaluation-header {
              flex-direction: column;
              align-items: flex-start;
              gap: 0.5rem;
            }
          }
        `}
      </style>

      <div className="job-management-card">
        <h2 className="section-title">Job Management Portal</h2>
        
        <div className="custom-nav">
          <button
            className={`nav-btn ${activeTab === 'create' ? 'active' : ''}`}
            onClick={() => handleTabChange('create')}
          >
            Create Job
          </button>
          <button
            className={`nav-btn ${activeTab === 'view' ? 'active' : ''}`}
            onClick={() => handleTabChange('view')}
          >
            My Jobs
            {jobs.length > 0 && (
              <span className="job-count-badge">{jobs.length}</span>
            )}
          </button>
          {selectedJobId && (
            <button
              className={`nav-btn ${activeTab === 'evaluations' ? 'active' : ''}`}
              onClick={() => handleTabChange('evaluations')}
            >
              Candidate Evaluations
              {evaluations.length > 0 && (
                <span className="job-count-badge">{evaluations.length}</span>
              )}
            </button>
          )}
        </div>

        {message && (
          <div className={`alert alert-${message.type} fade-in`}>
            {message.text}
          </div>
        )}

        {activeTab === 'create' && (
          <div className="fade-in">
            <h3 className="section-title">Create New Job</h3>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label className="form-label" htmlFor="title">Job Title</label>
                <input
                  type="text"
                  id="title"
                  name="title"
                  value={formData.title}
                  onChange={handleInputChange}
                  className="form-control"
                  placeholder="Enter job title"
                  required
                />
              </div>
              
              <div className="form-group">
                <label className="form-label" htmlFor="company">Company</label>
                <input
                  type="text"
                  id="company"
                  name="company"
                  value={formData.company}
                  onChange={handleInputChange}
                  className="form-control"
                  placeholder="Enter company name"
                  required
                />
              </div>
              
              <div className="form-group">
                <label className="form-label" htmlFor="location">Location</label>
                <input
                  type="text"
                  id="location"
                  name="location"
                  value={formData.location}
                  onChange={handleInputChange}
                  className="form-control"
                  placeholder="Enter job location"
                  required
                />
              </div>
              
              <div className="form-group">
                <label className="form-label" htmlFor="description">Job Description</label>
                <textarea
                  id="description"
                  name="description"
                  rows={4}
                  value={formData.description}
                  onChange={handleInputChange}
                  className="form-control"
                  placeholder="Enter detailed job description"
                  required
                />
              </div>
              
              <div className="form-group">
                <label className="form-label" htmlFor="weight">Evaluation Weights</label>
                <select
                  id="weight"
                  name="weight"
                  onChange={handleInputChange}
                  className="form-control"
                  required
                >
                  <option value={JSON.stringify({ technical: 0.4, communication: 0.25, cultural: 0.25, optional: 0.1 })}>
                    Balanced (Tech: 40%, Comm: 25%, Culture: 25%, Optional: 10%)
                  </option>
                  <option value={JSON.stringify({ technical: 0.5, communication: 0.2, cultural: 0.2, optional: 0.1 })}>
                    Tech Heavy (Tech: 50%, Comm: 20%, Culture: 20%, Optional: 10%)
                  </option>
                  <option value={JSON.stringify({ technical: 0.3, communication: 0.35, cultural: 0.25, optional: 0.1 })}>
                    Communication Focus (Tech: 30%, Comm: 35%, Culture: 25%, Optional: 10%)
                  </option>
                  <option value={JSON.stringify({ technical: 0.3, communication: 0.25, cultural: 0.35, optional: 0.1 })}>
                    Culture Focus (Tech: 30%, Comm: 25%, Culture: 35%, Optional: 10%)
                  </option>
                </select>
              </div>
              
              <button 
                type="submit" 
                className="btn-create"
              >
                Create Job
              </button>
            </form>
          </div>
        )}

        {activeTab === 'view' && (
          <div className="fade-in">
            <h3 className="section-title">
              My Job Listings
              {jobs.length > 0 && (
                <span className="job-count-badge">{jobs.length} Jobs</span>
              )}
            </h3>
            
            {jobs.length === 0 ? (
              <div className="empty-state">
                <h3>No Jobs Found</h3>
                <p>You haven't created any job listings yet.</p>
                <button 
                  className="nav-btn active"
                  onClick={() => setActiveTab('create')}
                >
                  Create Your First Job
                </button>
              </div>
            ) : (
              <ul className="jobs-list">
                {jobs.map((job, index) => (
                  <li key={job._id} className="job-item" style={{animationDelay: `${index * 0.1}s`}}>
                    <h4 className="job-title">{job.title}</h4>
                    <div className="job-meta">
                      <span className="job-company">{job.company}</span>
                      <span className="job-location">📍 {job.location}</span>
                    </div>
                    <p className="job-description">{job.description}</p>
                    <p>
                      <span className="job-id" onClick={() => handleJobClick(job._id)}>
                        Job ID: {job._id}
                      </span>
                    </p>
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}

        {activeTab === 'evaluations' && (
          <div className="fade-in">
            <div className="button-group">
              <button 
                className="btn-download"
                // onClick={downloadCSV}
                disabled={evaluations.length === 0}
              >
                Download All Evaluations (CSV)
              </button>
            </div>
            <h3 className="section-title">
              Candidate Evaluations for Job ID: {selectedJobId}
              {evaluations.length > 0 && (
                <span className="job-count-badge">{evaluations.length} Candidates</span>
              )}
            </h3>
            
            {evaluations.length === 0 ? (
              <div className="empty-state">
                <h3>No Evaluations Found</h3>
                <p>No candidate evaluations available for this job.</p>
                <button 
                  className="nav-btn active"
                  onClick={() => setActiveTab('view')}
                >
                  Back to Jobs
                </button>
              </div>
            ) : (
              <ul className="jobs-list">
                {evaluations.map((candidate, index) => (
                  <li key={candidate.candidate_id} className="evaluation-item" style={{animationDelay: `${index * 0.1}s`}}>
                    <div className="evaluation-header">
                      <span>Candidate ID: {candidate.candidate_id}</span>
                      <button 
                        className="btn-download candidate"
                        onClick={() => downloadCandidateCSV(candidate)}
                      >
                        Download Evaluation
                      </button>
                    </div>
                    
                    {candidate.communication.length > 0 && (
                      <div className="evaluation-section">
                        <div 
                          className="evaluation-section-header"
                          onClick={() => toggleSection(candidate.candidate_id, 'communication')}
                        >
                          <h5 className="evaluation-label">Communication Evaluations</h5>
                          <span className={`toggle-icon ${expandedSections[`${candidate.candidate_id}-communication`] ? 'expanded' : ''}`}>
                            ▼
                          </span>
                        </div>
                        {expandedSections[`${candidate.candidate_id}-communication`] && (
                          <div>
                            {candidate.communication.map((comm, idx) => (
                              <div key={comm._id} style={{ marginBottom: '1rem' }}>
                                <p className="evaluation-text"><strong>Score:</strong> {comm.communication_score}</p>
                                <p className="evaluation-text"><strong>Clarity:</strong> {comm.clarity_assessment}</p>
                                <p className="evaluation-text"><strong>Structure:</strong> {comm.structure_assessment}</p>
                                <p className="evaluation-text"><strong>Tone:</strong> {comm.tone_assessment}</p>
                                <p className="evaluation-text"><strong>Strengths:</strong></p>
                                <ul>
                                  {comm.strengths.map((strength, i) => (
                                    <li key={i} className="evaluation-text">{strength}</li>
                                  ))}
                                </ul>
                                <p className="evaluation-text"><strong>Weaknesses:</strong></p>
                                <ul>
                                  {comm.weaknesses.map((weakness, i) => (
                                    <li key={i} className="evaluation-text">{weakness}</li>
                                  ))}
                                </ul>
                                <p className="evaluation-text"><strong>Created At:</strong> {new Date(comm.created_at).toLocaleString()}</p>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    )}

                    {candidate.technical.length > 0 && (
                      <div className="evaluation-section">
                        <div 
                          className="evaluation-section-header"
                          onClick={() => toggleSection(candidate.candidate_id, 'technical')}
                        >
                          <h5 className="evaluation-label">Technical Evaluations</h5>
                          <span className={`toggle-icon ${expandedSections[`${candidate.candidate_id}-technical`] ? 'expanded' : ''}`}>
                            ▼
                          </span>
                        </div>
                        {expandedSections[`${candidate.candidate_id}-technical`] && (
                          <div>
                            {candidate.technical.map((tech, idx) => (
                              <div key={tech._id} style={{ marginBottom: '1rem' }}>
                                <p className="evaluation-text"><strong>Technical Fit:</strong> {tech.technical_evaluation.overall_technical_fit}</p>
                                <p className="evaluation-text"><strong>Technical Score:</strong> {tech.technical_evaluation.technical_answers_score}</p>
                                <p className="evaluation-text"><strong>Coverage:</strong> {tech.technical_evaluation.coverage_percentage}%</p>
                                <p className="evaluation-text"><strong>Matched Skills:</strong></p>
                                <ul className="skills-list">
                                  {tech.technical_evaluation.matched_skills.map((skill, i) => (
                                    <li key={i} className="skill-item">
                                      {skill.skill} ({skill.proficiency}) - {skill.jd_requirement}
                                    </li>
                                  ))}
                                </ul>
                                <p className="evaluation-text"><strong>Projects:</strong></p>
                                <ul>
                                  {tech.technical_evaluation.project_evaluation.map((project, i) => (
                                    <li key={i} className="evaluation-text">{project}</li>
                                  ))}
                                </ul>
                                <p className="evaluation-text"><strong>Created At:</strong> {new Date(tech.created_at).toLocaleString()}</p>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    )}

                    {candidate.cultural_fit.length > 0 && (
                      <div className="evaluation-section">
                        <div 
                          className="evaluation-section-header"
                          onClick={() => toggleSection(candidate.candidate_id, 'cultural')}
                        >
                          <h5 className="evaluation-label">Cultural Fit Evaluations</h5>
                          <span className={`toggle-icon ${expandedSections[`${candidate.candidate_id}-cultural`] ? 'expanded' : ''}`}>
                            ▼
                          </span>
                        </div>
                        {expandedSections[`${candidate.candidate_id}-cultural`] && (
                          <div>
                            {candidate.cultural_fit.map((culture, idx) => (
                              <div key={culture._id} style={{ marginBottom: '1rem' }}>
                                <p className="evaluation-text"><strong>Score:</strong> {culture.cultural_fit_score}</p>
                                <p className="evaluation-text"><strong>Coverage:</strong> {culture.coverage_percentage}%</p>
                                <p className="evaluation-text"><strong>Report:</strong> {culture.cultural_fit_report}</p>
                                <p className="evaluation-text"><strong>Matched Attributes:</strong></p>
                                <ul className="skills-list">
                                  {culture.matched_cultural_attributes.map((attr, i) => (
                                    <li key={i} className="skill-item">
                                      {attr.attribute} - {attr.jd_requirement}
                                    </li>
                                  ))}
                                </ul>
                                <p className="evaluation-text"><strong>Strengths:</strong></p>
                                <ul>
                                  {culture.strengths.map((strength, i) => (
                                    <li key={i} className="evaluation-text">{strength}</li>
                                  ))}
                                </ul>
                                <p className="evaluation-text"><strong>Weaknesses:</strong></p>
                                <ul>
                                  {culture.weaknesses.map((weakness, i) => (
                                    <li key={i} className="evaluation-text">{weakness}</li>
                                  ))}
                                </ul>
                                <p className="evaluation-text"><strong>Created At:</strong> {new Date(culture.created_at).toLocaleString()}</p>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default JobManagement;