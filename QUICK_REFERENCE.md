# Study Buddy - Quick Reference

## Common Commands

### Docker Commands

```bash
# Start application
docker-compose up -d

# Stop application
docker-compose down

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db

# Restart a service
docker-compose restart backend

# Rebuild after code changes
docker-compose up -d --build

# Stop and remove volumes (deletes data!)
docker-compose down -v

# Check service status
docker-compose ps
```

### Manual Development

```bash
# Backend
cd backend
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
python -m app.main

# Frontend
cd frontend
npm run dev
```

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get JWT token
- `GET /auth/me` - Get current user info

### Users
- `PUT /users/me` - Update user settings

### Documents
- `POST /documents/upload` - Upload document
- `GET /documents/` - List user's documents
- `GET /documents/{id}` - Get document details
- `DELETE /documents/{id}` - Delete document

### Query
- `POST /query/` - Query documents with RAG

## Environment Variables

### Backend (.env or docker-compose.yml)
```bash
DATABASE_URL=postgresql://user:pass@host:5432/dbname
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE_MB=100
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

### Frontend (.env)
```bash
VITE_API_URL=http://localhost:8000
```

## Database

### Connect to PostgreSQL

```bash
# With Docker
docker-compose exec db psql -U studybuddy -d study_buddy

# Without Docker
psql -U studybuddy -d study_buddy
```

### Useful SQL Commands

```sql
-- List all tables
\dt

-- View users
SELECT id, username, email, created_at FROM users;

-- View documents
SELECT id, filename, user_id, file_size, processed FROM documents;

-- View chunks count
SELECT COUNT(*) FROM document_chunks;

-- Check vector embeddings
SELECT id, chunk_index, embedding IS NOT NULL as has_embedding
FROM document_chunks LIMIT 10;

-- Delete user's documents
DELETE FROM documents WHERE user_id = 1;

-- View storage usage by user
SELECT user_id, COUNT(*) as doc_count, SUM(file_size) as total_bytes
FROM documents GROUP BY user_id;
```

## File Structure

```
study_buddy/
├── backend/
│   ├── app/
│   │   ├── models/         # Database models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── routers/        # API endpoints
│   │   ├── services/       # Business logic
│   │   ├── utils/          # Utilities (auth, etc.)
│   │   └── main.py         # FastAPI app
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API client
│   │   ├── store/          # State management
│   │   ├── styles/         # CSS
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   ├── Dockerfile
│   └── .env
├── docker-compose.yml
├── README.md
├── SETUP_GUIDE.md
└── .env
```

## Default Ports

- Frontend: 3000
- Backend: 8000
- PostgreSQL: 5432

## LLM Model Names

### OpenAI
- `gpt-3.5-turbo` - Fast, cheap
- `gpt-4` - Best quality, expensive
- `gpt-4-turbo` - Faster GPT-4

### Anthropic
- `claude-3-5-sonnet-20241022` - Best overall
- `claude-3-sonnet-20240229` - Good balance
- `claude-3-haiku-20240307` - Fast, cheap

### Ollama (Local)
- `llama2` - 7B model
- `llama2:13b` - Larger model
- `mistral` - Good alternative
- `codellama` - For code tasks

## Troubleshooting Quick Fixes

### Backend won't start
```bash
docker-compose restart backend
docker-compose logs backend
```

### Frontend won't start
```bash
docker-compose restart frontend
docker-compose logs frontend
```

### Database connection issues
```bash
docker-compose restart db
docker-compose exec db psql -U studybuddy -d study_buddy -c "SELECT 1"
```

### Reset everything
```bash
docker-compose down -v
docker-compose up -d --build
```

### Clear browser cache
- Chrome/Edge: Ctrl+Shift+Delete
- Firefox: Ctrl+Shift+Delete
- Clear site data for localhost:3000

## Testing

### Test Backend API

```bash
# Health check
curl http://localhost:8000/health

# Register user
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test123"}'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test123"}'
```

### Test Frontend

Visit http://localhost:3000 and:
1. Register → Should redirect to login
2. Login → Should redirect to dashboard
3. Upload document → Should show in list
4. Ask question → Should get answer with sources

## Performance Tips

1. **Use SSD** for database
2. **Allocate 4-8GB RAM** to Docker
3. **Use GPT-3.5** for faster responses
4. **Limit chunk count** (top_k=3-5) for faster queries
5. **Use smaller documents** (<50 pages) for faster processing

## Security Checklist

- [ ] Change SECRET_KEY in production
- [ ] Use strong passwords
- [ ] Enable HTTPS in production
- [ ] Set specific CORS origins
- [ ] Implement rate limiting
- [ ] Regular database backups
- [ ] Keep dependencies updated
- [ ] Use secrets manager for API keys

## Backup and Restore

### Backup
```bash
# Database
docker-compose exec db pg_dump -U studybuddy study_buddy > backup.sql

# Documents
docker cp study_buddy-backend-1:/app/uploads ./uploads_backup
```

### Restore
```bash
# Database
docker-compose exec -T db psql -U studybuddy study_buddy < backup.sql

# Documents
docker cp ./uploads_backup study_buddy-backend-1:/app/uploads
```

## Monitoring

### Check Resource Usage
```bash
docker stats
```

### Check Disk Usage
```bash
docker system df
```

### View Specific Container Stats
```bash
docker stats study_buddy-backend-1
```

## Useful Links

- FastAPI Docs: http://localhost:8000/docs
- PostgreSQL Docs: https://www.postgresql.org/docs/
- pgvector GitHub: https://github.com/pgvector/pgvector
- React Docs: https://react.dev
- OpenAI API: https://platform.openai.com/docs
- Anthropic API: https://docs.anthropic.com
- Ollama: https://ollama.ai
