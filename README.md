# Study Buddy - RAG Application

A cost-optimized RAG (Retrieval-Augmented Generation) application with user authentication, document upload, and intelligent question-answering with citations.

## Features

- **User Authentication**: Secure JWT-based authentication system
- **Document Upload**: Support for PDF, DOCX, and TXT files (max 100MB per file)
- **Document Processing**: Automatic text extraction and intelligent chunking
- **Vector Search**: pgvector-powered semantic search for relevant context
- **RAG Query Engine**: Ask questions and get AI-powered answers with source citations
- **Multi-Document Queries**: Query across all your uploaded documents
- **Flexible LLM Support**:
  - OpenAI (GPT-3.5, GPT-4)
  - Anthropic (Claude)
  - Self-hosted models (Ollama, LM Studio, vLLM)
- **User Isolation**: Each user's documents are completely isolated
- **Storage Limits**: 3GB per user
- **Free Embeddings**: Local sentence-transformers model (no API costs)

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **PostgreSQL + pgvector**: Vector database for semantic search
- **SQLAlchemy**: ORM for database operations
- **sentence-transformers**: Local embedding generation (all-MiniLM-L6-v2)
- **PyPDF2/python-docx**: Document processing
- **LangChain**: Text splitting and chunking

### Frontend
- **React 18**: Modern UI framework
- **Vite**: Fast build tool
- **Zustand**: Lightweight state management
- **Axios**: HTTP client
- **React Router**: Client-side routing

### Deployment
- **Docker & Docker Compose**: Containerized deployment
- **Nginx**: Frontend web server

## Quick Start with Docker

### Prerequisites
- Docker and Docker Compose installed
- At least 4GB of RAM available

### Setup

1. **Clone the repository**
```bash
cd study_buddy
```

2. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env and set secure passwords
```

3. **Start the application**
```bash
docker-compose up -d
```

This will start:
- PostgreSQL with pgvector on port 5432
- Backend API on http://localhost:8000
- Frontend on http://localhost:3000

4. **Access the application**
- Open http://localhost:3000 in your browser
- Register a new account
- Configure your LLM API key in Settings
- Upload documents and start asking questions!

### Stopping the application
```bash
docker-compose down
```

To also remove volumes (database and uploads):
```bash
docker-compose down -v
```

## Manual Setup (Without Docker)

### Backend Setup

1. **Install Python 3.11+**

2. **Install PostgreSQL with pgvector**
```bash
# On Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib
# Install pgvector extension
git clone https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install
```

3. **Create database**
```bash
sudo -u postgres psql
CREATE DATABASE study_buddy;
CREATE USER studybuddy WITH PASSWORD 'changeme';
GRANT ALL PRIVILEGES ON DATABASE study_buddy TO studybuddy;
\q
```

4. **Enable pgvector extension**
```bash
sudo -u postgres psql -d study_buddy
CREATE EXTENSION vector;
\q
```

5. **Install backend dependencies**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

6. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your database credentials
```

7. **Run the backend**
```bash
python -m app.main
# Or with uvicorn:
uvicorn app.main:app --reload
```

Backend will be available at http://localhost:8000

### Frontend Setup

1. **Install Node.js 18+**

2. **Install dependencies**
```bash
cd frontend
npm install
```

3. **Configure environment**
```bash
cp .env.example .env
# Edit .env if needed (default API URL is http://localhost:8000)
```

4. **Run the frontend**
```bash
npm run dev
```

Frontend will be available at http://localhost:3000

## Configuration

### LLM Setup

After registering, go to Settings to configure your LLM:

#### Option 1: OpenAI
1. Get API key from https://platform.openai.com/api-keys
2. Enter key in Settings
3. Set provider to "OpenAI"
4. Set model (e.g., "gpt-3.5-turbo", "gpt-4")

#### Option 2: Anthropic
1. Get API key from https://console.anthropic.com/
2. Enter key in Settings
3. Set provider to "Anthropic"
4. Set model (e.g., "claude-3-sonnet-20240229", "claude-3-5-sonnet-20241022")

#### Option 3: Self-Hosted (Ollama)
1. Install Ollama from https://ollama.ai
2. Pull a model: `ollama pull llama2`
3. In Settings:
   - Set provider to "Custom"
   - Set endpoint to "http://localhost:11434"
   - Set model to "llama2"
   - Leave API key blank

## Usage

### Uploading Documents

1. Navigate to Dashboard
2. Click "Upload Document"
3. Select PDF, DOCX, or TXT file (max 100MB)
4. Wait for processing to complete
5. Document will appear in your document list

### Asking Questions

1. Type your question in the chat interface
2. Click "Send"
3. View the AI-generated answer with citations
4. Click on sources to see the specific text snippets used

### Document Management

- View all your documents in the sidebar
- See processing status (Pending, Processing, Completed, Failed)
- Delete documents you no longer need
- View chunk count and file size

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Architecture

### Document Processing Pipeline

```
Upload → Parse → Chunk → Embed → Store in pgvector
```

1. **Upload**: File saved to filesystem
2. **Parse**: Extract text (PyPDF2 for PDF, python-docx for Word)
3. **Chunk**: Split into 512-token chunks with 50-token overlap
4. **Embed**: Generate vectors using sentence-transformers
5. **Store**: Save chunks and embeddings in PostgreSQL

### Query Pipeline

```
Query → Embed → Vector Search → Build Context → LLM → Response
```

1. **Embed**: Convert query to vector
2. **Search**: Find top-k similar chunks using cosine similarity
3. **Filter**: Only retrieve user's own documents
4. **Context**: Build prompt with relevant chunks
5. **LLM**: Generate answer using user's configured LLM
6. **Citations**: Return answer with source references

## Cost Breakdown

### Self-Hosted Option (Cheapest)
- VPS: $5-10/month (e.g., DigitalOcean, Hetzner)
- LLM: $0 (using Ollama)
- Embeddings: $0 (local model)
- **Total: ~$5-10/month**

### Cloud Option with API Keys
- VPS: $5-10/month
- LLM: Pay-as-you-go
  - OpenAI GPT-3.5: ~$0.50-2 per 1M tokens
  - Claude Sonnet: ~$3 per 1M tokens
- Embeddings: $0 (local model)
- **Total: $5-10/month + usage**

## Storage

- **Documents**: Filesystem (in Docker volume or local disk)
- **Metadata**: PostgreSQL
- **Vectors**: pgvector (384 dimensions)
- **Limit**: 3GB per user

## Security

- JWT-based authentication
- Bcrypt password hashing
- Row-level security via user_id filtering
- API keys stored in database (encrypted in production)
- CORS protection
- File upload validation

## Troubleshooting

### Backend won't start
- Check PostgreSQL is running
- Verify pgvector extension is installed
- Check database credentials in .env
- Ensure Python 3.11+ is installed

### Frontend can't connect to backend
- Verify backend is running on port 8000
- Check VITE_API_URL in frontend/.env
- Check CORS settings in backend

### Document processing fails
- Check file format is supported (PDF, DOCX, TXT)
- Verify file isn't corrupted
- Check backend logs for errors
- Ensure sufficient disk space

### Query returns no results
- Upload documents first
- Wait for processing to complete (status: Completed)
- Configure LLM API key in Settings
- Check backend logs for errors

## Development

### Backend Development
```bash
cd backend
source venv/bin/activate
# Make changes to code
# Backend auto-reloads with uvicorn --reload
```

### Frontend Development
```bash
cd frontend
npm run dev
# Frontend hot-reloads automatically
```

### Database Migrations

Currently using SQLAlchemy's `create_all()`. For production, consider Alembic:

```bash
pip install alembic
alembic init migrations
# Create migrations as needed
```

## Production Deployment

### Environment Variables

Set these securely in production:

```bash
SECRET_KEY=<random-64-char-string>
POSTGRES_PASSWORD=<secure-password>
DATABASE_URL=postgresql://user:pass@host:5432/db
```

### Security Checklist

- [ ] Change default SECRET_KEY
- [ ] Use strong database passwords
- [ ] Configure CORS with specific origins
- [ ] Enable HTTPS (use reverse proxy like Nginx)
- [ ] Set up database backups
- [ ] Configure rate limiting
- [ ] Enable API key encryption
- [ ] Set up monitoring and logging
- [ ] Use secrets manager for API keys
- [ ] Configure firewall rules

### Scaling Considerations

- Use Redis for caching embeddings
- Implement async document processing (Celery)
- Add CDN for frontend static assets
- Use connection pooling for database
- Consider Kubernetes for orchestration
- Add load balancer for multiple backend instances

## License

MIT License - feel free to use for personal or commercial projects

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review backend logs: `docker-compose logs backend`
3. Review frontend console for errors
4. Check API documentation at /docs

## Contributing

Contributions welcome! Areas for improvement:

- Add support for more document types (Excel, PowerPoint)
- Implement document versioning
- Add collaborative features
- Implement streaming responses
- Add support for images in PDFs
- Create admin dashboard
- Add analytics and usage tracking
- Implement document sharing

## Roadmap

- [ ] Streaming responses for real-time answers
- [ ] Support for image extraction from PDFs
- [ ] Document versioning and history
- [ ] Collaborative workspaces
- [ ] Advanced search filters
- [ ] Export conversations
- [ ] Mobile app
- [ ] Chrome extension for web page RAG
