import { useState, useEffect } from 'react';
import { usersAPI } from '../services/api';
import useStore from '../store/useStore';

function Settings() {
  const { user, fetchUser } = useStore();
  const [formData, setFormData] = useState({
    email: '',
    openai_api_key: '',
    anthropic_api_key: '',
    custom_llm_endpoint: '',
    custom_llm_api_key: '',
    preferred_llm_provider: 'openai',
    preferred_model: 'gpt-3.5-turbo',
  });

  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (user) {
      setFormData({
        email: user.email || '',
        openai_api_key: '',
        anthropic_api_key: '',
        custom_llm_endpoint: '',
        custom_llm_api_key: '',
        preferred_llm_provider: user.preferred_llm_provider,
        preferred_model: user.preferred_model,
      });
    }
  }, [user]);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      // Only send non-empty fields
      const updateData = {};
      Object.keys(formData).forEach((key) => {
        if (formData[key] !== '') {
          updateData[key] = formData[key];
        }
      });

      await usersAPI.updateSettings(updateData);
      await fetchUser();

      setSuccess('Settings updated successfully');

      // Clear API key fields after successful update
      setFormData({
        ...formData,
        openai_api_key: '',
        anthropic_api_key: '',
        custom_llm_api_key: '',
      });

      setTimeout(() => setSuccess(''), 3000);
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to update settings');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <div className="card" style={{ maxWidth: '800px', margin: '2rem auto' }}>
        <h2>Settings</h2>

        {success && <div className="success-message">{success}</div>}
        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="settings-section">
            <h4>Profile</h4>
            <div className="form-group">
              <label>Username</label>
              <input type="text" value={user?.username || ''} disabled />
            </div>

            <div className="form-group">
              <label>Email</label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="your@email.com"
              />
            </div>
          </div>

          <div className="settings-section">
            <h4>LLM Configuration</h4>

            <div className="form-group">
              <label>Preferred Provider</label>
              <select
                name="preferred_llm_provider"
                value={formData.preferred_llm_provider}
                onChange={handleChange}
              >
                <option value="openai">OpenAI</option>
                <option value="anthropic">Anthropic</option>
                <option value="custom">Custom Endpoint</option>
              </select>
            </div>

            <div className="form-group">
              <label>Preferred Model</label>
              <input
                type="text"
                name="preferred_model"
                value={formData.preferred_model}
                onChange={handleChange}
                placeholder="e.g., gpt-3.5-turbo, claude-3-sonnet-20240229"
              />
              <small style={{ color: '#666', fontSize: '0.85rem' }}>
                Examples: gpt-3.5-turbo, gpt-4, claude-3-sonnet-20240229, claude-3-5-sonnet-20241022
              </small>
            </div>
          </div>

          <div className="settings-section">
            <h4>API Keys</h4>
            <p style={{ color: '#666', fontSize: '0.9rem', marginBottom: '1rem' }}>
              Your API keys are stored securely. Leave blank to keep existing keys.
              {user?.has_openai_key && ' ✓ OpenAI key configured'}
              {user?.has_anthropic_key && ' ✓ Anthropic key configured'}
              {user?.has_custom_endpoint && ' ✓ Custom endpoint configured'}
            </p>

            <div className="form-group">
              <label>OpenAI API Key</label>
              <input
                type="password"
                name="openai_api_key"
                value={formData.openai_api_key}
                onChange={handleChange}
                placeholder={user?.has_openai_key ? '••••••••••••••••' : 'sk-...'}
              />
              <small style={{ color: '#666', fontSize: '0.85rem' }}>
                Get your key at: https://platform.openai.com/api-keys
              </small>
            </div>

            <div className="form-group">
              <label>Anthropic API Key</label>
              <input
                type="password"
                name="anthropic_api_key"
                value={formData.anthropic_api_key}
                onChange={handleChange}
                placeholder={user?.has_anthropic_key ? '••••••••••••••••' : 'sk-ant-...'}
              />
              <small style={{ color: '#666', fontSize: '0.85rem' }}>
                Get your key at: https://console.anthropic.com/
              </small>
            </div>
          </div>

          <div className="settings-section">
            <h4>Custom Endpoint (for self-hosted models)</h4>

            <div className="form-group">
              <label>Endpoint URL</label>
              <input
                type="text"
                name="custom_llm_endpoint"
                value={formData.custom_llm_endpoint}
                onChange={handleChange}
                placeholder="http://localhost:11434 (for Ollama)"
              />
              <small style={{ color: '#666', fontSize: '0.85rem' }}>
                OpenAI-compatible endpoint (e.g., Ollama, LM Studio, vLLM)
              </small>
            </div>

            <div className="form-group">
              <label>API Key (optional)</label>
              <input
                type="password"
                name="custom_llm_api_key"
                value={formData.custom_llm_api_key}
                onChange={handleChange}
                placeholder="Leave blank if no auth required"
              />
            </div>
          </div>

          <button type="submit" className="btn btn-primary btn-block" disabled={loading}>
            {loading ? 'Saving...' : 'Save Settings'}
          </button>
        </form>
      </div>
    </div>
  );
}

export default Settings;
