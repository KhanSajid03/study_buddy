import { Link } from 'react-router-dom';
import useStore from '../store/useStore';

function Home() {
  const { isAuthenticated } = useStore();

  return (
    <div className="container">
      <div style={{ textAlign: 'center', padding: '4rem 2rem' }}>
        <h1 style={{ fontSize: '3rem', marginBottom: '1rem', color: '#2c3e50' }}>
          Study Buddy
        </h1>
        <p style={{ fontSize: '1.5rem', color: '#666', marginBottom: '2rem' }}>
          Your Personal RAG-powered Document Assistant
        </p>

        <div style={{ maxWidth: '600px', margin: '0 auto', textAlign: 'left' }}>
          <div className="card">
            <h3>Features</h3>
            <ul style={{ lineHeight: '2' }}>
              <li>Upload and process PDF, Word, and text documents</li>
              <li>Ask questions and get AI-powered answers with citations</li>
              <li>Use your own API keys (OpenAI, Anthropic, or self-hosted)</li>
              <li>Secure user authentication and document isolation</li>
              <li>Multi-document querying support</li>
              <li>Up to 3GB storage per user</li>
            </ul>
          </div>

          <div style={{ textAlign: 'center', marginTop: '2rem' }}>
            {isAuthenticated ? (
              <Link to="/dashboard" className="btn btn-primary">
                Go to Dashboard
              </Link>
            ) : (
              <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
                <Link to="/login" className="btn btn-primary">
                  Login
                </Link>
                <Link to="/register" className="btn btn-secondary">
                  Register
                </Link>
              </div>
            )}
          </div>
        </div>

        <div style={{ marginTop: '3rem', fontSize: '0.9rem', color: '#999' }}>
          <p>Built with FastAPI, React, PostgreSQL, and pgvector</p>
        </div>
      </div>
    </div>
  );
}

export default Home;
