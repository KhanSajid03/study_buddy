# Changelog

All notable changes to Study Buddy will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-11-07

### Initial Release

#### Added
- **Authentication System**
  - User registration with username and password
  - JWT-based authentication
  - Secure password hashing with bcrypt
  - Protected API routes

- **Document Management**
  - Upload PDF, DOCX, and TXT files (up to 100MB)
  - Automatic text extraction and processing
  - Document list with status tracking
  - Delete documents functionality
  - Storage limit: 3GB per user

- **RAG Query System**
  - Vector similarity search using pgvector
  - Local embeddings with sentence-transformers (all-MiniLM-L6-v2)
  - Support for multiple LLM providers:
    - OpenAI (GPT-3.5, GPT-4)
    - Anthropic (Claude)
    - Custom endpoints (Ollama, LM Studio, etc.)
  - Answer generation with source citations
  - Multi-document querying

- **User Settings**
  - Configure LLM provider and model
  - Manage API keys securely
  - Set custom endpoints for self-hosted models

- **Backend Features**
  - FastAPI web framework
  - PostgreSQL with pgvector for vector storage
  - SQLAlchemy ORM
  - Intelligent text chunking (512 tokens, 50 overlap)
  - Page number tracking for citations
  - Automatic embedding generation

- **Frontend Features**
  - React 18 with Vite
  - Responsive, mobile-friendly design
  - Real-time upload progress
  - Chat interface for Q&A
  - Document status badges
  - Source citations with text snippets

- **DevOps**
  - Docker and Docker Compose configuration
  - Multi-stage frontend build
  - Nginx for production serving
  - Volume management for persistence
  - Startup scripts for easy development

- **Documentation**
  - Comprehensive README
  - Detailed setup guide
  - Quick reference guide
  - API documentation
  - Contributing guidelines
  - Project summary

#### Technical Details
- Backend: Python 3.11, FastAPI 0.109.0
- Frontend: React 18, Vite 5
- Database: PostgreSQL 14+ with pgvector
- Embeddings: sentence-transformers (all-MiniLM-L6-v2, 384 dimensions)
- Authentication: JWT with HS256
- Document Processing: PyPDF2, python-docx, LangChain
- State Management: Zustand
- API Client: Axios

#### Security
- JWT token-based authentication
- Bcrypt password hashing (cost factor: 12)
- User data isolation via user_id filtering
- CORS protection
- File upload validation
- Maximum file size limits

#### Performance
- Local embedding generation (no API costs)
- pgvector for fast similarity search
- Optimized chunking strategy
- Support for up to 3GB per user

---

## [Unreleased]

### Planned Features
- Streaming LLM responses
- Async document processing with Celery
- Support for Excel and PowerPoint files
- Image extraction from PDFs
- Document versioning
- Usage analytics dashboard
- Mobile app
- Browser extension

### Under Consideration
- Multi-language support
- Collaborative workspaces
- Document comparison
- Export conversations
- Advanced search filters
- Dark mode

---

## Version History

- **1.0.0** (2024-11-07) - Initial release with core RAG functionality

---

## Migration Guides

### Migrating to 1.0.0
This is the initial release, no migration needed.

---

## Breaking Changes

None yet.

---

## Deprecations

None yet.

---

## Notes

- For detailed API changes, see API documentation at `/docs`
- For setup instructions, see SETUP_GUIDE.md
- For contribution guidelines, see CONTRIBUTING.md
