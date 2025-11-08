# Study Buddy - Architecture Documentation

## System Overview

Study Buddy is a three-tier application with a React frontend, FastAPI backend, and PostgreSQL database with pgvector extension.

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Browser                             │
│                     (http://localhost:3000)                      │
└──────────────────────────────┬──────────────────────────────────┘
                               │ HTTP/HTTPS
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Frontend (React + Vite)                     │
│  ┌────────────┬──────────────┬───────────────┬────────────────┐ │
│  │   Pages    │  Components  │    Store      │   Services     │ │
│  │  Home      │  Navbar      │   Zustand     │   API Client   │ │
│  │  Login     │  Protected   │   Auth State  │   Axios        │ │
│  │  Dashboard │  Route       │   User Data   │                │ │
│  │  Settings  │              │               │                │ │
│  └────────────┴──────────────┴───────────────┴────────────────┘ │
└──────────────────────────────┬──────────────────────────────────┘
                               │ REST API (JSON)
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Backend (FastAPI)                            │
│  ┌────────────┬──────────────┬───────────────┬────────────────┐ │
│  │  Routers   │   Services   │    Models     │     Utils      │ │
│  │  /auth     │  Document    │   User        │   JWT Auth     │ │
│  │  /users    │  Processor   │   Document    │   Password     │ │
│  │  /documents│  Embedding   │   Chunk       │   Hash         │ │
│  │  /query    │  RAG Service │               │                │ │
│  └────────────┴──────────────┴───────────────┴────────────────┘ │
└─────┬───────────────────────┬────────────────────┬──────────────┘
      │                       │                    │
      │ SQLAlchemy           │ HTTP               │ File I/O
      ▼                       ▼                    ▼
┌──────────────┐    ┌──────────────────┐   ┌─────────────┐
│ PostgreSQL   │    │  LLM APIs        │   │  Filesystem │
│ + pgvector   │    │  - OpenAI        │   │  /uploads   │
│              │    │  - Anthropic     │   │             │
│ Tables:      │    │  - Custom        │   │  Documents  │
│ - users      │    │                  │   │  Storage    │
│ - documents  │    └──────────────────┘   └─────────────┘
│ - chunks     │
│              │
│ Extensions:  │
│ - vector     │
└──────────────┘
```

## Data Flow

### 1. User Registration Flow

```
User → Frontend → Backend → Database
                    │
                    ├─ Hash password (bcrypt)
                    ├─ Create user record
                    └─ Return user data
```

### 2. Authentication Flow

```
Login Request
    │
    ▼
Backend validates credentials
    │
    ├─ Check username exists
    ├─ Verify password hash
    ├─ Generate JWT token
    │   └─ Payload: {sub: user_id, exp: timestamp}
    └─ Return token
         │
         ▼
Frontend stores in localStorage
         │
         ▼
All subsequent requests include:
Authorization: Bearer <token>
```

### 3. Document Upload & Processing Flow

```
User selects file
    │
    ▼
Frontend uploads with FormData
    │
    ▼
Backend receives file
    │
    ├─ Validate file type & size
    ├─ Check user storage quota
    ├─ Save to filesystem
    ├─ Create document record (status: Processing)
    │
    ▼
Document Processing Pipeline
    │
    ├─ Extract text
    │   ├─ PDF: PyPDF2
    │   ├─ DOCX: python-docx
    │   └─ TXT: direct read
    │
    ├─ Chunk text
    │   └─ LangChain RecursiveCharacterTextSplitter
    │       ├─ Chunk size: 512 tokens
    │       ├─ Overlap: 50 tokens
    │       └─ Preserve paragraphs/sentences
    │
    ├─ Generate embeddings
    │   └─ sentence-transformers (all-MiniLM-L6-v2)
    │       └─ Output: 384-dimensional vectors
    │
    ├─ Store chunks in database
    │   └─ Each chunk:
    │       ├─ text content
    │       ├─ page number
    │       ├─ chunk index
    │       ├─ embedding vector
    │       └─ user_id (for isolation)
    │
    └─ Update document status (Completed)
```

### 4. RAG Query Flow

```
User types question
    │
    ▼
Frontend sends query request
    │
    ▼
Backend RAG Service
    │
    ├─ 1. Embed query
    │   └─ sentence-transformers → 384-dim vector
    │
    ├─ 2. Vector similarity search
    │   └─ pgvector cosine distance
    │       SELECT *, embedding <=> query_vector AS distance
    │       FROM document_chunks
    │       WHERE user_id = current_user
    │       ORDER BY distance
    │       LIMIT top_k (default: 5)
    │
    ├─ 3. Build context
    │   └─ Format retrieved chunks:
    │       [Source 1], Page X:
    │       <chunk text>
    │
    │       [Source 2], Page Y:
    │       <chunk text>
    │
    ├─ 4. Build prompt
    │   └─ System: "You are a helpful assistant..."
    │       Context: <retrieved chunks>
    │       Question: <user query>
    │       Instructions: Answer with citations
    │
    ├─ 5. Call LLM
    │   ├─ OpenAI: POST https://api.openai.com/v1/chat/completions
    │   ├─ Anthropic: POST https://api.anthropic.com/v1/messages
    │   └─ Custom: POST {endpoint}/v1/chat/completions
    │
    ├─ 6. Format response
    │   └─ {
    │       answer: "...[Source 1]...[Source 2]...",
    │       sources: [
    │         {
    │           source_number: 1,
    │           document_id: 123,
    │           page_number: 5,
    │           text_snippet: "...",
    │           similarity: 0.85
    │         }
    │       ]
    │     }
    │
    └─ Return to frontend
         │
         ▼
Frontend displays answer with citations
```

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- LLM Configuration
    openai_api_key VARCHAR(255),
    anthropic_api_key VARCHAR(255),
    custom_llm_endpoint VARCHAR(255),
    custom_llm_api_key VARCHAR(255),
    preferred_llm_provider VARCHAR(50) DEFAULT 'openai',
    preferred_model VARCHAR(100) DEFAULT 'gpt-3.5-turbo'
);

CREATE INDEX idx_users_username ON users(username);
```

### Documents Table
```sql
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(512) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    file_size BIGINT NOT NULL,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed INTEGER DEFAULT 0,  -- 0: pending, 1: processing, 2: completed, -1: failed

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_documents_user_id ON documents(user_id);
```

### Document Chunks Table
```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE document_chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id) NOT NULL,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    chunk_index INTEGER NOT NULL,
    chunk_text TEXT NOT NULL,
    page_number INTEGER,
    embedding vector(384),  -- pgvector type
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_chunks_document_id ON document_chunks(document_id);
CREATE INDEX idx_chunks_user_id ON document_chunks(user_id);
CREATE INDEX idx_chunks_embedding ON document_chunks USING ivfflat (embedding vector_cosine_ops);
```

## API Endpoints

### Authentication
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/register` | Register new user | No |
| POST | `/auth/login` | Login and get JWT | No |
| GET | `/auth/me` | Get current user | Yes |

### Users
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| PUT | `/users/me` | Update user settings | Yes |

### Documents
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/documents/upload` | Upload document | Yes |
| GET | `/documents/` | List user's documents | Yes |
| GET | `/documents/{id}` | Get document details | Yes |
| DELETE | `/documents/{id}` | Delete document | Yes |

### Query
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/query/` | Query with RAG | Yes |

## Security Architecture

### Authentication & Authorization
```
Request → JWT Validation → Extract user_id → Filter by user_id
          │
          ├─ Validate token signature
          ├─ Check expiration
          ├─ Extract user_id from payload
          └─ Verify user exists
```

### Data Isolation
- All database queries filtered by `user_id`
- Documents: `WHERE user_id = current_user_id`
- Chunks: `WHERE user_id = current_user_id`
- No cross-user data access possible

### Password Security
- Passwords hashed with bcrypt (cost factor: 12)
- Never stored in plain text
- Rainbow table attacks prevented

### API Key Storage
- Stored in database (encrypted in production)
- Never exposed to frontend
- Used only server-side for LLM calls

## Component Interactions

### Frontend Components
```
App.jsx
  ├─ Navbar
  ├─ Router
  │   ├─ Home
  │   ├─ Login
  │   ├─ Register
  │   ├─ Dashboard (Protected)
  │   │   ├─ Document Upload
  │   │   ├─ Document List
  │   │   └─ Chat Interface
  │   └─ Settings (Protected)
  │       ├─ Profile Settings
  │       └─ LLM Configuration
  └─ Store (Zustand)
      ├─ user
      ├─ token
      ├─ isAuthenticated
      └─ actions
```

### Backend Services
```
FastAPI App
  ├─ Routers
  │   ├─ Auth Router
  │   ├─ Users Router
  │   ├─ Documents Router
  │   └─ Query Router
  │
  ├─ Services
  │   ├─ Document Processor
  │   │   ├─ PDF Parser
  │   │   ├─ DOCX Parser
  │   │   ├─ TXT Parser
  │   │   └─ Text Chunker
  │   │
  │   ├─ Embedding Service
  │   │   └─ sentence-transformers
  │   │
  │   └─ RAG Service
  │       ├─ Retrieval
  │       ├─ Context Building
  │       └─ LLM Integration
  │
  └─ Models
      ├─ User
      ├─ Document
      └─ DocumentChunk
```

## Deployment Architecture

### Docker Compose Setup
```
Docker Host
  │
  ├─ Network: study_buddy_default
  │
  ├─ Container: db (PostgreSQL + pgvector)
  │   ├─ Image: ankane/pgvector:latest
  │   ├─ Port: 5432
  │   └─ Volume: postgres_data
  │
  ├─ Container: backend (FastAPI)
  │   ├─ Build: ./backend/Dockerfile
  │   ├─ Port: 8000
  │   ├─ Volume: backend_uploads
  │   └─ Depends: db
  │
  └─ Container: frontend (React + Nginx)
      ├─ Build: ./frontend/Dockerfile (multi-stage)
      ├─ Port: 3000 (mapped to 80 in container)
      └─ Depends: backend
```

## Performance Considerations

### Embedding Generation
- Model loaded once on startup
- Cached in memory
- ~100ms per chunk
- Batched for efficiency

### Vector Search
- pgvector IVFFlat index
- Approximate nearest neighbor search
- Sub-second query times
- Scales to millions of vectors

### Document Processing
- Synchronous in current implementation
- Future: Async with Celery/RQ
- Progress tracking via database status

### Caching Opportunities
- Embedding cache (future)
- Query result cache (future)
- LLM response cache (future)

## Scalability

### Current Capacity
- Single server: 100-1000 users
- Storage: Limited by disk space
- Concurrent users: 10-50

### Scaling Options
1. **Vertical Scaling**
   - Increase server resources
   - More RAM for model caching
   - Faster CPU for processing

2. **Horizontal Scaling**
   - Multiple backend instances (load balanced)
   - Shared database
   - Shared file storage (S3/MinIO)

3. **Database Scaling**
   - Read replicas for queries
   - Separate vector search instance
   - Partitioning by user_id

4. **Queue-Based Processing**
   - Celery for async tasks
   - Redis for task queue
   - Separate worker processes

## Monitoring & Logging

### Application Logs
- Backend: uvicorn logs
- Frontend: browser console
- Database: PostgreSQL logs

### Metrics to Monitor
- Request rate
- Response time
- Error rate
- Document processing time
- Vector search latency
- LLM API costs
- Storage usage

### Health Checks
- `/health` endpoint
- Database connectivity
- Filesystem access
- LLM API availability

## Future Architecture Improvements

1. **Microservices**
   - Separate document processing service
   - Separate embedding service
   - API gateway

2. **Caching Layer**
   - Redis for session management
   - Embedding cache
   - Query result cache

3. **Object Storage**
   - S3/MinIO for documents
   - Better scalability
   - Backup & recovery

4. **Message Queue**
   - RabbitMQ/Redis for async tasks
   - Document processing queue
   - Notification queue

5. **Observability**
   - Prometheus for metrics
   - Grafana for dashboards
   - Sentry for error tracking
   - ELK stack for logs
