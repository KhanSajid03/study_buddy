# Study Buddy - Detailed Setup Guide

This guide will walk you through setting up Study Buddy step-by-step.

## Table of Contents
1. [Quick Start (Docker - Recommended)](#quick-start-docker)
2. [Manual Setup](#manual-setup)
3. [LLM Configuration](#llm-configuration)
4. [First Steps](#first-steps)
5. [Common Issues](#common-issues)

---

## Quick Start (Docker)

This is the easiest way to get started. Everything runs in containers.

### Step 1: Install Docker

**Windows:**
1. Download Docker Desktop from https://www.docker.com/products/docker-desktop
2. Install and restart your computer
3. Verify: Open terminal and run `docker --version`

**Mac:**
1. Download Docker Desktop from https://www.docker.com/products/docker-desktop
2. Install and start Docker Desktop
3. Verify: Open terminal and run `docker --version`

**Linux:**
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
# Log out and back in
```

### Step 2: Configure Environment

```bash
cd study_buddy
cp .env.example .env
```

Edit `.env` file:
```bash
# Change these to secure values
POSTGRES_USER=studybuddy
POSTGRES_PASSWORD=your-secure-password-here
POSTGRES_DB=study_buddy
SECRET_KEY=your-random-secret-key-here
```

**Generate a secure SECRET_KEY:**
```bash
# On Linux/Mac:
openssl rand -hex 32

# On Windows (PowerShell):
-join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | % {[char]$_})
```

### Step 3: Start the Application

```bash
docker-compose up -d
```

This will:
1. Download required Docker images
2. Build backend and frontend containers
3. Start PostgreSQL with pgvector
4. Start the backend API
5. Start the frontend web server

**First time setup takes 5-10 minutes** as it downloads models and builds images.

### Step 4: Verify Everything is Running

```bash
docker-compose ps
```

You should see 3 services running:
- `study_buddy-db-1`
- `study_buddy-backend-1`
- `study_buddy-frontend-1`

Check logs if something failed:
```bash
docker-compose logs backend
docker-compose logs frontend
```

### Step 5: Access the Application

Open your browser and go to: **http://localhost:3000**

---

## Manual Setup

If you prefer not to use Docker or want to develop locally.

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+

### Step 1: Install PostgreSQL with pgvector

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib build-essential git

# Install pgvector
git clone --branch v0.5.1 https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install
cd ..
```

**Mac (with Homebrew):**
```bash
brew install postgresql@14
brew services start postgresql@14

# Install pgvector
git clone --branch v0.5.1 https://github.com/pgvector/pgvector.git
cd pgvector
make
make install
cd ..
```

**Windows:**
1. Download PostgreSQL from https://www.postgresql.org/download/windows/
2. Install PostgreSQL
3. For pgvector, use Docker instead (easier on Windows)

### Step 2: Create Database

```bash
# Start PostgreSQL
sudo -u postgres psql

# In PostgreSQL shell:
CREATE DATABASE study_buddy;
CREATE USER studybuddy WITH PASSWORD 'changeme';
GRANT ALL PRIVILEGES ON DATABASE study_buddy TO studybuddy;
\q

# Connect to the database and enable pgvector
sudo -u postgres psql -d study_buddy
CREATE EXTENSION vector;
\q
```

### Step 3: Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate it
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database credentials
```

Edit `backend/.env`:
```
DATABASE_URL=postgresql://studybuddy:changeme@localhost:5432/study_buddy
SECRET_KEY=your-random-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
HOST=0.0.0.0
PORT=8000
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE_MB=100
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

**Start the backend:**
```bash
python -m app.main
```

Backend should be running at http://localhost:8000

### Step 4: Frontend Setup

Open a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
```

Edit `frontend/.env`:
```
VITE_API_URL=http://localhost:8000
```

**Start the frontend:**
```bash
npm run dev
```

Frontend should be running at http://localhost:3000

---

## LLM Configuration

You need to configure at least one LLM provider to use the question-answering feature.

### Option 1: OpenAI (Easiest, Paid)

**Cost:** ~$0.50-2 per 1M tokens (GPT-3.5-turbo)

1. Go to https://platform.openai.com/api-keys
2. Create an account or log in
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)
5. In Study Buddy:
   - Go to Settings
   - Paste key in "OpenAI API Key"
   - Set provider to "OpenAI"
   - Set model to "gpt-3.5-turbo" (or "gpt-4" for better quality)
   - Click "Save Settings"

### Option 2: Anthropic Claude (Best Quality, Paid)

**Cost:** ~$3 per 1M tokens (Claude Sonnet)

1. Go to https://console.anthropic.com/
2. Create an account or log in
3. Go to API Keys section
4. Create a new key
5. Copy the key (starts with `sk-ant-`)
6. In Study Buddy:
   - Go to Settings
   - Paste key in "Anthropic API Key"
   - Set provider to "Anthropic"
   - Set model to "claude-3-5-sonnet-20241022"
   - Click "Save Settings"

### Option 3: Ollama (Free, Self-Hosted)

**Cost:** $0 (runs locally, needs ~8GB RAM)

1. Install Ollama:
   - Mac: `brew install ollama`
   - Linux: `curl -fsSL https://ollama.ai/install.sh | sh`
   - Windows: Download from https://ollama.ai

2. Start Ollama:
```bash
ollama serve
```

3. Pull a model:
```bash
# Small model (4GB RAM)
ollama pull llama2

# Or larger model (8GB RAM)
ollama pull llama2:13b

# Or even larger (16GB RAM)
ollama pull llama2:70b
```

4. In Study Buddy:
   - Go to Settings
   - Set provider to "Custom"
   - Set endpoint to "http://localhost:11434"
   - Set model to "llama2" (or whichever you pulled)
   - Leave API key blank
   - Click "Save Settings"

### Option 4: LM Studio (Free, Self-Hosted with GUI)

1. Download LM Studio from https://lmstudio.ai/
2. Install and open LM Studio
3. Download a model (e.g., "TheBloke/Mistral-7B-Instruct")
4. Go to "Local Server" tab
5. Click "Start Server" (default port 1234)
6. In Study Buddy:
   - Go to Settings
   - Set provider to "Custom"
   - Set endpoint to "http://localhost:1234"
   - Set model to the model you loaded
   - Leave API key blank
   - Click "Save Settings"

---

## First Steps

### 1. Register an Account

1. Go to http://localhost:3000
2. Click "Register"
3. Enter username and password
4. Click "Register"
5. Go to login page and log in

### 2. Configure LLM

1. Click "Settings" in the navbar
2. Follow one of the LLM configuration options above
3. Save settings

### 3. Upload Your First Document

1. Go to Dashboard
2. Click "Upload Document"
3. Select a PDF, Word, or text file
4. Wait for processing to complete (status will show "Completed")

### 4. Ask Your First Question

1. In the chat interface, type a question about your document
2. Click "Send"
3. Wait for the AI to generate an answer
4. View the answer and citations

### Example Questions:
- "What is this document about?"
- "Summarize the main points"
- "What does it say about [topic]?"
- "List the key findings"

---

## Common Issues

### Issue: Docker containers won't start

**Error:** "port already in use"

**Solution:**
```bash
# Check what's using the ports
# On Linux/Mac:
lsof -i :8000
lsof -i :5432
lsof -i :3000

# On Windows:
netstat -ano | findstr :8000

# Either stop those services or change ports in docker-compose.yml
```

### Issue: Backend can't connect to database

**Error:** "could not connect to server"

**Solution:**
```bash
# Check if database is running
docker-compose ps

# Check database logs
docker-compose logs db

# Restart database
docker-compose restart db
```

### Issue: "No module named 'app'"

**Solution:**
```bash
# Make sure you're in the backend directory
cd backend

# Make sure virtual environment is activated
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: Frontend shows "Network Error"

**Solution:**
1. Check backend is running at http://localhost:8000
2. Visit http://localhost:8000/docs - should show API docs
3. Check VITE_API_URL in frontend/.env
4. Check browser console for CORS errors

### Issue: Document processing stuck at "Processing"

**Solution:**
```bash
# Check backend logs
docker-compose logs backend

# Common causes:
# 1. Corrupted PDF - try a different file
# 2. Out of memory - check Docker memory settings
# 3. Model download in progress - wait 5-10 minutes

# Restart backend
docker-compose restart backend
```

### Issue: Query fails with "API key not configured"

**Solution:**
1. Go to Settings
2. Configure at least one LLM provider
3. Make sure API key is valid
4. Save settings
5. Try query again

### Issue: Embedding model download is slow

This is normal on first startup. The `all-MiniLM-L6-v2` model is ~80MB.

**Solution:** Wait 5-10 minutes. Check logs:
```bash
docker-compose logs backend | grep -i "download"
```

### Issue: Out of memory

**Symptoms:** Backend crashes, containers restart

**Solution:**
1. Increase Docker memory (Docker Desktop → Settings → Resources)
2. Recommended: 4GB minimum, 8GB for better performance
3. Or use a smaller embedding model

---

## Next Steps

- Read the main README.md for architecture details
- Explore the API docs at http://localhost:8000/docs
- Check out the source code
- Try different document types
- Experiment with different LLM models

---

## Getting Help

If you're still stuck:

1. Check backend logs: `docker-compose logs backend`
2. Check frontend console (F12 in browser)
3. Verify all environment variables are set
4. Try with a simple text file first
5. Test API directly at http://localhost:8000/docs

## Performance Tips

- Use GPT-3.5-turbo for faster, cheaper responses
- Use Claude Sonnet for better accuracy
- Use Ollama with smaller models (llama2) for privacy
- Close other applications if using local models
- SSD recommended for database performance
