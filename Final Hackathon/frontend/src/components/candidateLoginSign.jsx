import { useState } from 'react';
import { useNavigate } from 'react-router-dom'; // Added import

function CandidateAuth() {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [message, setMessage] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const navigate = useNavigate(); // Replaced mock navigate

  const handleInputChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage(null);
    setIsLoading(true);

    const url = isLogin
      ? 'http://localhost:3000/api/candidate/login'
      : 'http://localhost:3000/api/candidate/signup';
    const payload = isLogin
      ? { email: formData.email, password: formData.password }
      : {
          email: formData.email,
          password: formData.password,
        };

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await response.json();

      if (response.ok) {
        if (data.candidateId) {
          sessionStorage.setItem('candidateId', data.candidateId);
        }
        setMessage({ type: 'success', text: isLogin ? 'Login successful!' : 'Signup successful!' });
        setFormData({ email: '', password: ''});
        
        setTimeout(() => {
          navigate('/candidate/jobs');
        }, 1500);
      } else {
        setMessage({ type: 'danger', text: data.message || 'Error occurred' });
      }
    } catch (error) {
      setMessage({ type: 'danger', text: 'Network error occurred' });
    } finally {
      setIsLoading(false);
    }
  };

  const toggleMode = () => {
    setIsLogin(!isLogin);
    setMessage(null);
    setFormData({ email: '', password: '' });
  };

  return (
    <div style={{
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '2rem 1rem',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
    }}>
      <style>
        {`
          .auth-container {
            width: 100%;
            max-width: 450px;
            margin: 0 auto;
          }

          .auth-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            border: none;
            border-radius: 24px;
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
            padding: 3rem 2.5rem;
            transition: all 0.4s ease;
            position: relative;
            overflow: hidden;
          }

          .auth-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            border-radius: 24px 24px 0 0;
          }

          .auth-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 35px 70px rgba(0, 0, 0, 0.2);
          }

          .auth-title {
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: 800;
            font-size: 2rem;
            text-align: center;
            margin-bottom: 0.5rem;
            letter-spacing: -0.5px;
          }

          .auth-subtitle {
            text-align: center;
            color: #6c757d;
            margin-bottom: 2.5rem;
            font-weight: 500;
          }

          .form-row {
            display: flex;
            gap: 1rem;
            margin-bottom: 1.5rem;
          }

          .form-group {
            margin-bottom: 1.5rem;
            position: relative;
          }

          .form-group.half {
            flex: 1;
          }

          .form-label {
            font-weight: 600;
            color: #495057;
            margin-bottom: 0.6rem;
            display: block;
            font-size: 0.9rem;
            letter-spacing: 0.5px;
          }

          .form-control {
            width: 100%;
            border: 2px solid #e9ecef;
            border-radius: 16px;
            padding: 1rem 1.2rem;
            transition: all 0.3s ease;
            background: #fafbfc;
            font-size: 1rem;
            font-family: inherit;
            box-sizing: border-box;
          }

          .form-control:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 0.3rem rgba(102, 126, 234, 0.15);
            background: white;
            transform: translateY(-1px);
          }

          .form-control::placeholder {
            color: #adb5bd;
          }

          .btn-primary {
            width: 100%;
            background: linear-gradient(135deg, #667eea, #764ba2);
            border: none;
            border-radius: 16px;
            padding: 1rem 2rem;
            font-weight: 600;
            font-size: 1.1rem;
            color: white;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
            position: relative;
            overflow: hidden;
            margin-bottom: 1.5rem;
          }

          .btn-primary:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 12px 35px rgba(102, 126, 234, 0.4);
          }

          .btn-primary:active {
            transform: translateY(0);
          }

          .btn-primary:disabled {
            opacity: 0.7;
            cursor: not-allowed;
            transform: none;
          }

          .btn-link {
            background: none;
            border: none;
            color: #667eea;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            font-size: 0.95rem;
            padding: 0.5rem;
            border-radius: 8px;
            width: 100%;
          }

          .btn-link:hover {
            color: #5a67d8;
            background: rgba(102, 126, 234, 0.1);
            transform: translateY(-1px);
          }

          .alert {
            border: none;
            border-radius: 12px;
            padding: 1rem 1.5rem;
            font-weight: 500;
            margin-bottom: 2rem;
            animation: slideIn 0.3s ease-out;
          }

          .alert-success {
            background: linear-gradient(135deg, #d1f2eb, #a7f3d0);
            color: #065f46;
            border-left: 4px solid #10b981;
          }

          .alert-danger {
            background: linear-gradient(135deg, #fecaca, #fca5a5);
            color: #991b1b;
            border-left: 4px solid #ef4444;
          }

          .loading-spinner {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            border-top-color: white;
            animation: spin 0.8s ease-in-out infinite;
            margin-right: 0.5rem;
          }

          .mode-indicator {
            display: flex;
            justify-content: center;
            margin-bottom: 2rem;
          }

          .mode-tab {
            padding: 0.5rem 1.5rem;
            border-radius: 20px;
            margin: 0 0.25rem;
            font-weight: 600;
            font-size: 0.9rem;
            transition: all 0.3s ease;
            cursor: pointer;
            border: 2px solid transparent;
          }

          .mode-tab.active {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
          }

          .mode-tab.inactive {
            color: #6c757d;
            background: #f8f9fa;
          }

          .form-animation {
            animation: fadeInUp 0.5s ease-out;
          }

          @keyframes slideIn {
            from {
              opacity: 0;
              transform: translateY(-20px);
            }
            to {
              opacity: 1;
              transform: translateY(0);
            }
          }

          @keyframes fadeInUp {
            from {
              opacity: 0;
              transform: translateY(30px);
            }
            to {
              opacity: 1;
              transform: translateY(0);
            }
          }

          @keyframes spin {
            to {
              transform: rotate(360deg);
            }
          }

          @media (max-width: 768px) {
            .auth-card {
              padding: 2rem 1.5rem;
              margin: 1rem;
            }
            
            .auth-title {
              font-size: 1.75rem;
            }
            
            .form-row {
              flex-direction: column;
              gap: 0;
            }
          }

          .icon-wrapper {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            border-radius: 50%;
            margin: 0 auto 1.5rem;
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
          }

          .icon-wrapper svg {
            width: 28px;
            height: 28px;
            color: white;
          }
        `}
      </style>

      <div className="auth-container">
        <div className="auth-card">
          <div className="icon-wrapper">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2C13.1 2 14 2.9 14 4C14 5.1 13.1 6 12 6C10.9 6 10 5.1 10 4C10 2.9 10.9 2 12 2ZM21 9V7L15 4V6C15 7.1 14.1 8 13 8S11 7.1 11 6V4L5 7V9C5 10.1 5.9 11 7 11S9 10.1 9 9V13C9 14.1 9.9 15 11 15H13C14.1 15 15 14.1 15 13V9C15 10.1 15.9 11 17 11S19 10.1 19 9M7.5 12C6.7 12 6 12.7 6 13.5S6.7 15 7.5 15 9 14.3 9 13.5 8.3 12 7.5 12M16.5 12C15.7 12 15 12.7 15 13.5S15.7 15 16.5 15 18 14.3 18 13.5 17.3 12 16.5 12Z"/>
            </svg>
          </div>

          <h1 className="auth-title">
            {isLogin ? 'Welcome Back' : 'Join Our Platform'}
          </h1>
          <p className="auth-subtitle">
            {isLogin ? 'Sign in to manage your job postings' : 'Create your recruiter account today'}
          </p>

          <div className="mode-indicator">
            <div 
              className={`mode-tab ${isLogin ? 'active' : 'inactive'}`}
              onClick={() => !isLogin && toggleMode()}
            >
              Login
            </div>
            <div 
              className={`mode-tab ${!isLogin ? 'active' : 'inactive'}`}
              onClick={() => isLogin && toggleMode()}
            >
              Sign Up
            </div>
          </div>

          {message && (
            <div className={`alert alert-${message.type}`}>
              {message.text}
            </div>
          )}

          <form onSubmit={handleSubmit} className="form-animation" key={isLogin ? 'login' : 'signup'}> {/* Changed div to form */}
            {/* {!isLogin && (
                
            )} */}
            
            <div className="form-group">
              <label className="form-label" htmlFor="email">Email Address</label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                className="form-control"
                placeholder="john@company.com"
                required
              />
            </div>
            
            <div className="form-group">
              <label className="form-label" htmlFor="password">Password</label>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                className="form-control"
                placeholder="••••••••"
                required
              />
            </div>
            
            <button 
              type="submit" // Changed to submit
              className="btn-primary"
              disabled={isLoading}
            >
              {isLoading && <span className="loading-spinner"></span>}
              {isLoading 
                ? (isLogin ? 'Signing In...' : 'Creating Account...') 
                : (isLogin ? 'Sign In' : 'Create Account')
              }
            </button>
            
            <button
              type="button"
              className="btn-link"
              onClick={toggleMode}
              disabled={isLoading}
            >
              {isLogin ? "Don't have an account? Sign up" : 'Already have an account? Sign in'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

export default CandidateAuth;