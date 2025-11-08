import { useState, useEffect } from 'react';
import { documentsAPI, queryAPI } from '../services/api';
import useStore from '../store/useStore';

function Dashboard() {
  const { user, fetchUser } = useStore();
  const [documents, setDocuments] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [messages, setMessages] = useState([]);
  const [query, setQuery] = useState('');
  const [querying, setQuerying] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchUser();
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      const response = await documentsAPI.list();
      setDocuments(response.data);
    } catch (error) {
      console.error('Failed to load documents:', error);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploading(true);
    setError('');

    try {
      await documentsAPI.upload(file, (progressEvent) => {
        const progress = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        );
        setUploadProgress(progress);
      });

      // Reload documents
      await loadDocuments();
      setUploadProgress(0);
      e.target.value = ''; // Clear input
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to upload document');
    } finally {
      setUploading(false);
    }
  };

  const handleDeleteDocument = async (docId) => {
    if (!confirm('Are you sure you want to delete this document?')) return;

    try {
      await documentsAPI.delete(docId);
      await loadDocuments();
    } catch (error) {
      setError('Failed to delete document');
    }
  };

  const handleQuery = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    // Check if user has configured LLM
    if (!user?.has_openai_key && !user?.has_anthropic_key && !user?.has_custom_endpoint) {
      setError('Please configure your LLM API key in Settings first');
      return;
    }

    setQuerying(true);
    setError('');

    // Add user message
    const userMessage = { role: 'user', content: query };
    setMessages((prev) => [...prev, userMessage]);

    try {
      const response = await queryAPI.query({
        query: query,
        top_k: 5,
      });

      // Add assistant message
      const assistantMessage = {
        role: 'assistant',
        content: response.data.answer,
        sources: response.data.sources,
      };
      setMessages((prev) => [...prev, assistantMessage]);
      setQuery('');
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to process query');
      // Remove user message on error
      setMessages((prev) => prev.slice(0, -1));
    } finally {
      setQuerying(false);
    }
  };

  const getStatusBadge = (processed) => {
    const statuses = {
      0: { label: 'Pending', class: 'status-pending' },
      1: { label: 'Processing', class: 'status-processing' },
      2: { label: 'Completed', class: 'status-completed' },
      '-1': { label: 'Failed', class: 'status-failed' },
    };
    const status = statuses[processed] || statuses[0];
    return <span className={`status-badge ${status.class}`}>{status.label}</span>;
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
  };

  return (
    <div className="container">
      <div className="dashboard">
        <h1>Dashboard</h1>

        {error && <div className="error-message">{error}</div>}

        <div className="dashboard-grid">
          <div>
            <div className="card">
              <h3>Documents ({documents.length})</h3>

              <div className="file-upload">
                <label className="btn btn-primary">
                  {uploading ? `Uploading ${uploadProgress}%` : 'Upload Document'}
                  <input
                    type="file"
                    accept=".pdf,.docx,.txt"
                    onChange={handleFileUpload}
                    disabled={uploading}
                    style={{ display: 'none' }}
                  />
                </label>
                <div style={{ fontSize: '0.85rem', color: '#666', marginTop: '0.5rem' }}>
                  Accepts: PDF, DOCX, TXT
                </div>
              </div>

              <div className="document-list">
                {documents.length === 0 ? (
                  <p style={{ color: '#666', textAlign: 'center' }}>
                    No documents uploaded yet
                  </p>
                ) : (
                  documents.map((doc) => (
                    <div key={doc.id} className="document-item">
                      <div className="document-info">
                        <div className="filename">{doc.filename}</div>
                        <div className="meta">
                          {formatFileSize(doc.file_size)} • {doc.chunk_count} chunks •{' '}
                          {getStatusBadge(doc.processed)}
                        </div>
                      </div>
                      <div className="document-actions">
                        <button
                          className="btn btn-danger"
                          onClick={() => handleDeleteDocument(doc.id)}
                        >
                          Delete
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>

          <div>
            <div className="card">
              <h3>Ask Questions</h3>

              <div className="chat-container">
                <div className="messages">
                  {messages.length === 0 ? (
                    <div style={{ textAlign: 'center', color: '#666', padding: '2rem' }}>
                      Upload documents and ask questions to get started!
                    </div>
                  ) : (
                    messages.map((msg, idx) => (
                      <div key={idx} className={`message ${msg.role}`}>
                        <div className="message-content">{msg.content}</div>
                        {msg.sources && msg.sources.length > 0 && (
                          <div className="sources">
                            <h4>Sources:</h4>
                            {msg.sources.map((source, sidx) => (
                              <div key={sidx} className="source-item">
                                [Source {source.source_number}] Document ID: {source.document_id}
                                {source.page_number && `, Page ${source.page_number}`}
                                (Similarity: {(source.similarity * 100).toFixed(1)}%)
                                <br />
                                <em>{source.text_snippet}</em>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    ))
                  )}
                </div>

                <form onSubmit={handleQuery} className="chat-input">
                  <textarea
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Ask a question about your documents..."
                    disabled={querying}
                  />
                  <button
                    type="submit"
                    className="btn btn-primary"
                    disabled={querying || !query.trim()}
                  >
                    {querying ? 'Thinking...' : 'Send'}
                  </button>
                </form>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
