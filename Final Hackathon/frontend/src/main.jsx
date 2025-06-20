import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import App from './App.jsx';
import RecruiterAuth from './components/recruiterLoginSign.jsx';
import JobManagement from './components/jobManagement.jsx';
import CandidateAuth from './components/candidateLoginSign.jsx';
import JobBrowser from './components/candidateRegister.jsx';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<App />} />
        <Route path="/recruiter" element={<RecruiterAuth />} />
        <Route path="/candidate" element={<CandidateAuth />} />
        <Route path="/candidate/jobs" element={<JobBrowser />} />
        <Route path="/jobs" element={<JobManagement />} />
      </Routes>
    </BrowserRouter>
  </React.StrictMode>
);