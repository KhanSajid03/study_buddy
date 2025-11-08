import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import useStore from '../store/useStore';

function Register() {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
  });

  const [localError, setLocalError] = useState('');
  const [success, setSuccess] = useState(false);

  const { register, error, loading, clearError } = useStore();
  const navigate = useNavigate();

  useEffect(() => {
    return () => clearError();
  }, [clearError]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLocalError('');

    if (formData.password !== formData.confirmPassword) {
      setLocalError('Passwords do not match');
      return;
    }

    if (formData.password.length < 6) {
      setLocalError('Password must be at least 6 characters');
      return;
    }

    const { confirmPassword, ...registerData } = formData;
    const success = await register(registerData);

    if (success) {
      setSuccess(true);
      setTimeout(() => {
        navigate('/login');
      }, 2000);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  return (
    <div className="auth-container">
      <h2>Register for Study Buddy</h2>

      {(error || localError) && (
        <div className="error-message">{error || localError}</div>
      )}

      {success && (
        <div className="success-message">
          Registration successful! Redirecting to login...
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Username</label>
          <input
            type="text"
            name="username"
            value={formData.username}
            onChange={handleChange}
            required
            minLength={3}
          />
        </div>

        <div className="form-group">
          <label>Email (optional)</label>
          <input
            type="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
          />
        </div>

        <div className="form-group">
          <label>Password</label>
          <input
            type="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            required
            minLength={6}
          />
        </div>

        <div className="form-group">
          <label>Confirm Password</label>
          <input
            type="password"
            name="confirmPassword"
            value={formData.confirmPassword}
            onChange={handleChange}
            required
          />
        </div>

        <button type="submit" className="btn btn-primary btn-block" disabled={loading}>
          {loading ? 'Registering...' : 'Register'}
        </button>
      </form>

      <div className="auth-switch">
        Already have an account? <Link to="/login">Login here</Link>
      </div>
    </div>
  );
}

export default Register;
