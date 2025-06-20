import { useState, useEffect } from 'react';

function JobBrowser() {
  const [jobs, setJobs] = useState([]);
  const [message, setMessage] = useState(null);
  const [showApplyForm, setShowApplyForm] = useState(false);
  const [selectedJobId, setSelectedJobId] = useState(null);
  const [formData, setFormData] = useState({
    aboutYourself: '',
    strengthsWeaknesses: '',
    github_url: '',
    resume: null
  });

  const fetchJobs = async () => {
    const candidateId = sessionStorage.getItem('candidateId');
    if (!candidateId) {
      setMessage({ type: 'danger', text: 'Please log in to view jobs' });
      setJobs([]);
      return;
    }

    try {
      const response = await fetch('http://localhost:3000/api/candidate/jobs', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
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

  const handleApplyClick = (jobId) => {
    const candidateId = sessionStorage.getItem('candidateId');
    if (!candidateId) {
      setMessage({ type: 'danger', text: 'Please log in to apply for jobs' });
      return;
    }
    setSelectedJobId(jobId);
    setShowApplyForm(true);
  };

  const handleFormChange = (e) => {
    if (e.target.name === 'resume') {
      setFormData({ ...formData, resume: e.target.files[0] });
    } else {
      setFormData({ ...formData, [e.target.name]: e.target.value });
    }
  };

  const handleApplySubmit = async (e) => {
    e.preventDefault();
    const candidateId = sessionStorage.getItem('candidateId');
    if (!candidateId) {
      setMessage({ type: 'danger', text: 'Please log in to apply for jobs' });
      return;
    }

    const selectedJob = jobs.find(job => job._id === selectedJobId);
    if (!selectedJob) {
      setMessage({ type: 'danger', text: 'Selected job not found' });
      return;
    }

    const answers = [
      { text: formData.aboutYourself, type: 'about_yourself' },
      { text: formData.strengthsWeaknesses, type: 'strengths_weaknesses' }
    ];

    try {
      const formPayload = new FormData();
      formPayload.append('candidateID', candidateId);
      formPayload.append('jobId', selectedJobId);
      formPayload.append('answers', JSON.stringify(answers));
      formPayload.append('github_url', formData.github_url || '');
      formPayload.append('job_description', selectedJob.description);
      if (formData.resume) {
        formPayload.append('resume', formData.resume, formData.resume.name);
      } else {
        setMessage({ type: 'danger', text: 'Resume is required' });
        return;
      }

      const response = await fetch('http://localhost:3000/api/candidate/apply', {
        method: 'POST',
        body: formPayload
      });
      const data = await response.json();

      if (response.ok) {
        setMessage({ type: 'success', text: 'Application submitted successfully!' });
        setShowApplyForm(false);
        setFormData({ aboutYourself: '', strengthsWeaknesses: '', github_url: '', resume: null });
        setSelectedJobId(null);
      } else {
        setMessage({ type: 'danger', text: data.message || 'Error applying for job' });
      }
    } catch (error) {
      setMessage({ type: 'danger', text: 'Network error occurred' });
    }
  };

  const handleCancelApply = () => {
    setShowApplyForm(false);
    setFormData({ aboutYourself: '', strengthsWeaknesses: '', github_url: '', resume: null });
    setSelectedJobId(null);
  };

  useEffect(() => {
    fetchJobs(); // Fetch jobs on component mount
  }, []);

  return (
    <div style={{
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      minHeight: '100vh',
      padding: '2rem 1rem',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
    }}>
      <style>
        {`
          .job-browser-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border: none;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem;
          }

          .job-browser-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
          }

          .job-item {
            background: linear-gradient(135deg, #f8f9fa, #e9ecef);
            border: none;
            border-radius: 15px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
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
            margin-bottom: 0.5rem;
            font-size: 1.25rem;
          }

          .job-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
            flex-wrap: wrap;
            gap: 0.5rem;
          }

          .job-company {
            color: #636e72;
            font-weight: 600;
          }

          .job-location {
            color: #667eea;
            font-weight: 500;
            font-size: 0.9rem;
          }

          .job-description {
            color: #495057;
            line-height: 1.6;
            margin-bottom: 1rem;
          }

          .section-title {
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: 700;
            text-align: center;
            margin-bottom: 2rem;
          }

          .empty-state {
            text-align: center;
            color: #6c757d;
            padding: 3rem 1rem;
            background: #f8f9fa;
            border-radius: 15px;
            border: 2px dashed #dee2e6;
          }

          .empty-state h3 {
            margin-bottom: 1rem;
            color: #495057;
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

          .btn-apply {
            background: linear-gradient(135deg, #28a745, #218838);
            border: none;
            border-radius: 12px;
            padding: 0.75rem 1.5rem;
            font-weight: 600;
            font-size: 1rem;
            color: white;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(40, 167, 69, 0.4);
          }

          .btn-apply:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(40, 167, 69, 0.6);
          }

          .jobs-list {
            list-style: none;
            padding: 0;
            margin: 0;
          }

          .apply-form {
            background: #fff;
            border-radius: 15px;
            padding: 1.5rem;
            margin-top: 1rem;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
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

          .form-control::placeholder {
            color: #adb5bd;
          }

          .btn-cancel {
            background: linear-gradient(135deg, #dc3545, #c82333);
            border: none;
            border-radius: 12px;
            padding: 0.75rem 1.5rem;
            font-weight: 600;
            font-size: 1rem;
            color: white;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(220, 53, 69, 0.4);
            margin-left: 1rem;
          }

          .btn-cancel:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(220, 53, 69, 0.6);
          }

          .form-actions {
            display: flex;
            justify-content: flex-end;
            gap: 1rem;
          }

          .file-input-label {
            display: inline-block;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 0.75rem 1.5rem;
            border-radius: 12px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
          }

          .file-input-label:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
          }

          .file-input {
            display: none;
          }

          .file-name {
            margin-top: 0.5rem;
            color: #495057;
            font-size: 0.9rem;
          }

          @media (max-width: 768px) {
            .job-browser-card {
              margin: 1rem;
              padding: 1.5rem;
            }

            .job-meta {
              flex-direction: column;
              align-items: flex-start;
            }

            .form-actions {
              flex-direction: column;
              gap: 0.5rem;
            }
          }
        `}
      </style>

      <div className="job-browser-card">
        <h2 className="section-title">
          Job Browser
          {jobs.length > 0 && (
            <span className="job-count-badge">{jobs.length} Jobs</span>
          )}
        </h2>

        {message && (
          <div className={`alert alert-${message.type} fade-in`}>
            {message.text}
          </div>
        )}

        <div className="fade-in">
          {jobs.length === 0 ? (
            <div className="empty-state">
              <h3>No Jobs Available</h3>
              <p>There are no job listings available at the moment.</p>
            </div>
          ) : (
            <ul className="jobs-list">
              {jobs.map((job, index) => (
                <li key={job._id} className="job-item" style={{ animationDelay: `${index * 0.1}s` }}>
                  <h4 className="job-title">{job.title}</h4>
                  <div className="job-meta">
                    <span className="job-company">{job.company}</span>
                    <span className="job-location">📍 {job.location}</span>
                  </div>
                  <p className="job-description">{job.description}</p>
                  <button
                    className="btn-apply"
                    onClick={() => handleApplyClick(job._id)}
                  >
                    Apply Now
                  </button>

                  {showApplyForm && selectedJobId === job._id && (
                    <div className="apply-form fade-in">
                      <h3 className="section-title">Apply for {job.title}</h3>
                      <form onSubmit={handleApplySubmit}>
                        <div className="form-group">
                          <label className="form-label" htmlFor={`aboutYourself-${job._id}`}>
                            Tell me about yourself
                          </label>
                          <textarea
                            id={`aboutYourself-${job._id}`}
                            name="aboutYourself"
                            rows={4}
                            value={formData.aboutYourself}
                            onChange={handleFormChange}
                            className="form-control"
                            placeholder="Provide a brief introduction about yourself"
                            required
                          />
                        </div>
                        <div className="form-group">
                          <label className="form-label" htmlFor={`strengthsWeaknesses-${job._id}`}>
                            What are your strengths and weaknesses?
                          </label>
                          <textarea
                            id={`strengthsWeaknesses-${job._id}`}
                            name="strengthsWeaknesses"
                            rows={4}
                            value={formData.strengthsWeaknesses}
                            onChange={handleFormChange}
                            className="form-control"
                            placeholder="Describe your key strengths and weaknesses"
                            required
                          />
                        </div>
                        <div className="form-group">
                          <label className="form-label" htmlFor={`github_url-${job._id}`}>
                            GitHub Profile Link
                          </label>
                          <input
                            type="url"
                            id={`github_url-${job._id}`}
                            name="github_url"
                            value={formData.github_url}
                            onChange={handleFormChange}
                            className="form-control"
                            placeholder="Enter your GitHub profile URL"
                          />
                        </div>
                        <div className="form-group">
                          <label className="form-label" htmlFor={`resume-${job._id}`}>
                            Upload Resume
                          </label>
                          <label className="file-input-label">
                            Choose File
                            <input
                              type="file"
                              id={`resume-${job._id}`}
                              name="resume"
                              accept=".pdf,.doc,.docx"
                              onChange={handleFormChange}
                              className="file-input"
                              required
                            />
                          </label>
                          {formData.resume && (
                            <span className="file-name">{formData.resume.name}</span>
                          )}
                        </div>
                        <div className="form-actions">
                          <button type="submit" className="btn-apply">
                            Submit Application
                          </button>
                          <button
                            type="button"
                            className="btn-cancel"
                            onClick={handleCancelApply}
                          >
                            Cancel
                          </button>
                        </div>
                      </form>
                    </div>
                  )}
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}

export default JobBrowser;