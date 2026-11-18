# 🤖 MatchPilot.ai — AI-Powered Resume & Job Matching Agent

A full-stack, cloud-hosted AI recruitment assistant that combines transformer-based semantic matching, hybrid ranking (Sentence-BERT + BM25 + structured requirement matching + Cross-Encoder reranking), LLM-generated explanations, and production-style infrastructure — built with transparency, evidence, and human oversight as first-class concerns.

This project implements Sentence-BERT semantic similarity, BM25 keyword relevance, structured requirement-level matching, Cross-Encoder reranking, a controlled LLM explanation layer (OpenAI structured outputs), Redis-backed caching and rate limiting, PostgreSQL + pgvector persistence, Docker containerization, and AWS (ECS/Fargate) deployment.

IT452 Project Capstone

---

## 🧰 Tech Stack

![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white&style=for-the-badge)
![Flask](https://img.shields.io/badge/Flask-000000?logo=flask&logoColor=white&style=for-the-badge)
![React](https://img.shields.io/badge/React-61DAFB?logo=react&logoColor=black&style=for-the-badge)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?logo=typescript&logoColor=white&style=for-the-badge)
![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?logo=pytorch&logoColor=white&style=for-the-badge)
![Hugging Face](https://img.shields.io/badge/Hugging%20Face-FFD21E?logo=huggingface&logoColor=black&style=for-the-badge)
![OpenAI](https://img.shields.io/badge/OpenAI-412991?logo=openai&logoColor=white&style=for-the-badge)
![Redis](https://img.shields.io/badge/Redis-DC382D?logo=redis&logoColor=white&style=for-the-badge)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white&style=for-the-badge)
![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white&style=for-the-badge)
![AWS](https://img.shields.io/badge/AWS-232F3E?logo=amazonaws&logoColor=white&style=for-the-badge)

---

## 🧩 System Design

MatchPilot.ai is organized as a React frontend backed by a Flask API, with a hybrid matching engine and an LLM explanation layer sitting on top of persistent storage.

### Overview

- Users upload resumes and job descriptions through the React frontend (TXT, DOCX, PDF)
- The Flask backend validates requests and coordinates the matching pipeline
- Documents are parsed and normalized (skills, experience, education) using NLP (spaCy / NLTK)
- A Sentence-BERT model generates 384-dimensional embeddings for semantic similarity scoring
- BM25 computes keyword relevance across the job collection
- A structured requirement matching service checks each job requirement against resume evidence
- A weighted hybrid score combines the three signals (Semantic 35%, BM25 25%, Structured 40%)
- A Cross-Encoder reranks the top candidates by evaluating each resume–job pair jointly
- An LLM explanation service (OpenAI, structured JSON outputs) generates match summaries, matching/missing skills, strengths, gaps, and recommendations
- PostgreSQL + pgvector persists resumes, jobs, embeddings, and match explanations
- Redis caches embeddings and match results and enforces rate limits
- Human-review and explainability are preserved throughout: the system assists, it never makes final hiring decisions
- The application is containerized with Docker and deployed to AWS (ECS/Fargate)

---

## 🚀 Features

- Semantic matching with Sentence-BERT embeddings + cosine similarity
- BM25 keyword relevance scoring across the job collection
- Structured requirement-level matching with per-requirement evidence status
- Cross-Encoder reranking of hybrid results
- Weighted hybrid scoring (Semantic 35% / BM25 25% / Structured 40%)
- LLM-generated explanations with structured, schema-validated JSON output
- Explainable results: match scores, evidence, detected skill gaps, and limitations
- Distinguishes skills listed vs. skills demonstrated in projects or employment
- Persistent storage of resumes, jobs, embeddings, and match explanations (PostgreSQL + pgvector)
- Redis caching for embeddings and repeated match results
- Redis-based API rate limiting and cost controls
- Secure environment-based API key handling (no user-supplied keys)
- Prompt injection defenses and input validation
- Flask backend + React (TypeScript) frontend
- Dynamic Resume and Job detail pages with individual and comparison views
- Dockerized multi-service environment via Docker Compose
- AWS deployment (ECS/Fargate) for reproducible, remote access
- Mixed-methods evaluation: matching quality, agent reliability, latency, cache hit ratio, usability

---

### 🏗 Folder Structure

```
ai-resume-matcher/
│
├── .env.example
├── .gitignore
├── docker-compose.yaml
├── LICENSE
├── README.md
├── AI_USE_LOG.md
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app.py
│   │
│   ├── routes/
│   │   ├── api/
│   │   │   ├── jobs/routes.py
│   │   │   ├── resumes/routes.py
│   │   │   └── matches/routes.py
│   │   └── schemas.py
│   │
│   ├── services/
│   │   ├── document_parser.py
│   │   ├── nlp_preprocessor.py
│   │   ├── embedding_service.py
│   │   ├── semantic_matcher.py
│   │   ├── skill_extraction.py
│   │   ├── resume_analyzer.py
│   │   ├── job_analyzer.py
│   │   ├── requirement_matching.py
│   │   ├── hybrid_matching.py
│   │   ├── cross_encoder.py
│   │   ├── llm_service.py
│   │   └── verification.py
│   │
│   ├── models/
│   │   ├── database.py
│   │   └── entities.py
│   │
│   └── infra/
│       ├── cache.py
│       └── rate_limiter.py
│
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   └── src/
│       ├── components/
│       ├── pages/
│       │   ├── Dashboard
│       │   ├── Resumes
│       │   ├── Jobs
│       │   └── Matching
│       └── api/
│
├── deployments/
│   ├── aws/
│   │   └── ecs-task-definition.json
│   └── docker-compose.prod.yaml
│
├── tests/
│   ├── test_matcher.py
│   ├── test_agent.py
│   ├── test_verification.py
│   └── test_rate_limit.py
│
├── Readme-Photos/
│   └── System-Design.png
│
└── docs/
    ├── architecture.md
    └── evaluation.md
```

---

## ⚙️ Configuration

### Example `.env`

```env
FLASK_ENV=development
SECRET_KEY=change-me

# LLM Provider (never commit real keys)
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-xxxxxxxx
LLM_MODEL=gpt-4o-mini

# Hugging Face (Cross-Encoder model access)
HUGGINGFACE_TOKEN=hf_xxxxxxxx

# Database
DATABASE_URL=postgresql://user:pass@db:5432/resume_matcher

# Redis
REDIS_URL=redis://redis:6379/0

# Rate limiting
RATE_LIMIT_REQUESTS=60
RATE_LIMIT_WINDOW_SECONDS=60
```

---

## 🔐 Environment Variables

Create a `.env` file (never commit it):

```env
OPENAI_API_KEY=sk-xxxxxxxx
HUGGINGFACE_TOKEN=hf_xxxxxxxx
DATABASE_URL=postgresql://user:pass@db:5432/resume_matcher
REDIS_URL=redis://redis:6379/0
SECRET_KEY=change-me
```

> API credentials are stored via environment variables or a secrets manager and are never hardcoded in source control. End users are **never** asked to supply their own LLM keys.

---

## 🗄 Database (PostgreSQL + pgvector)

Embeddings are stored as native `VECTOR(384)` columns with pgvector.

```sql
-- Enable UUID generation and vector support
CREATE EXTENSION IF NOT EXISTS vector;

-- 1. Embeddings
CREATE TABLE embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model VARCHAR(255) NOT NULL,
    dimensions INTEGER NOT NULL,
    embedding VECTOR(384) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT valid_embedding_dimensions CHECK (dimensions = 384)
);

-- 2. Resumes
CREATE TABLE resumes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    embedding_id UUID NOT NULL UNIQUE REFERENCES embeddings(id) ON DELETE RESTRICT,
    raw_text TEXT NOT NULL,
    analysis JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 3. Jobs
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    embedding_id UUID NOT NULL UNIQUE REFERENCES embeddings(id) ON DELETE RESTRICT,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    analysis JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 4. Matches
CREATE TABLE matches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    resume_id UUID NOT NULL REFERENCES resumes(id),
    job_id UUID NOT NULL REFERENCES jobs(id),
    text TEXT NOT NULL,
    analysis JSONB NOT NULL,
    scores JSONB NOT NULL,
    resume_updated_at TIMESTAMPTZ NOT NULL,
    job_updated_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_resumes_created_at ON resumes(created_at);
CREATE INDEX idx_jobs_created_at ON jobs(created_at);
CREATE INDEX idx_matches_resume_id ON matches(resume_id);
CREATE INDEX idx_matches_job_id ON matches(job_id);
```

---

## 🐳 Docker Setup

### docker-compose.yaml (Local Development)

```yaml
services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "5000:5000"
    env_file:
      - .env
    depends_on:
      - redis
      - db
    networks:
      - app-network

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    depends_on:
      - backend
    networks:
      - app-network

  redis:
    image: redis:7-alpine
    networks:
      - app-network

  db:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: resume_matcher
    volumes:
      - pgdata:/var/lib/postgresql/data
    networks:
      - app-network

networks:
  app-network:
    driver: bridge

volumes:
  pgdata:
```

---

## 🛠 Local Setup

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/ai-resume-matcher.git
cd ai-resume-matcher
```

### 2. Configure environment

```bash
cp .env.example .env
# add your API keys and database credentials
```

### 3. Start everything

```bash
docker-compose up --build
```

### 4. Access the application

```
Frontend: http://localhost:3000
Backend API: http://localhost:5000
```

---

## 🔌 API Endpoints

### Resumes

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/resumes/` | Upload and store a resume |
| GET | `/api/resumes/` | List all resumes |
| GET | `/api/resumes/<resume_id>` | Retrieve a single resume |

### Jobs

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/jobs` | Create and store a job |
| GET | `/api/jobs` | List all jobs |
| GET | `/api/jobs/<job_id>` | Retrieve a single job |

### Matching

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/jobs/match` | Basic Sentence-BERT ranking against all jobs |
| POST | `/api/jobs/match-requirements` | Requirement-level evidence for one resume vs. one job |
| POST | `/api/jobs/hybrid-match` | Hybrid ranking of all jobs for one resume (Semantic + BM25 + Structured + Cross-Encoder rerank) |
| POST | `/api/jobs/compare` | Detailed evaluation of one resume vs. one job |

### Matches (Persisted LLM Explanations)

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/matches/resumes/<resume_id>` | Top jobs for a resume |
| GET | `/api/matches/jobs/<job_id>` | Top applicants for a job |
| GET | `/api/matches/` | All saved match explanations |
| GET | `/api/matches/<matching_id>` | One saved explanation |

---

## 🧪 Testing

### Upload a resume and job, then run a hybrid match

```bash
# Upload a resume
curl -X POST http://localhost:5000/api/resumes/ \
  -F "file=@sample_resume.pdf"

# Upload a job
curl -X POST http://localhost:5000/api/jobs \
  -F "title=Backend Engineer" \
  -F "description=@sample_job.docx"

# Hybrid match
curl -X POST http://localhost:5000/api/jobs/hybrid-match \
  -H "Content-Type: application/json" \
  -d '{"resume_id": "YOUR_RESUME_ID"}'
```

### Check rate limiting (should return HTTP 429 after limit)

```bash
for i in $(seq 1 70); do
  curl -s -o /dev/null -w "%{http_code}\n" http://localhost:5000/api/jobs/hybrid-match
done
```

### Run the automated test suite

```bash
docker-compose exec backend pytest tests/ -v
```

---

## 📊 Evaluation

Primary evaluation metrics:

| Metric | Method |
|---|---|
| Semantic matching quality | Precision@k, Recall, F1, MRR (expert-reviewed sample) |
| Hybrid ranking improvement | Compare Semantic-only vs. Hybrid vs. Hybrid + Cross-Encoder |
| Requirement matching accuracy | Per-requirement evidence status reviewed against manual assessment |
| LLM output reliability | % schema-valid structured outputs, evidence-backed claims |
| System performance | End-to-end API latency, Redis cache hit ratio |
| Rate limiting | Correct enforcement under repeated/concurrent requests |
| Cost efficiency | LLM token/request usage, redundant request reduction |
| Usability & interpretability | Post-task questionnaire, Likert ratings of clarity/trust |

---

## 🔁 Matching Pipeline

```
User (React + TypeScript Frontend)
  ↓
Flask Backend (validated API endpoints)
  ↓
Document Parser → NLP Preprocessor → Analyzers (Resume / Job)
  ↓
Embedding Service (Sentence-BERT, 384-d)
  ↓
Hybrid Matching Engine
  ├── Semantic similarity   (35%)
  ├── BM25 keyword relevance (25%)
  └── Structured requirement matching (40%)
  ↓
Cross-Encoder Reranking
  ↓
Redis (cache + rate limit)  |  PostgreSQL + pgvector (state + results)
  ↓
LLM Explanation Service (OpenAI, structured JSON schema)
  ↓
Verification Module (schema + deterministic checks)
  ↓
Results + Explanations + Limitations → Human Review
```

---

## 🧠 Key Concepts Implemented

- Sentence-BERT semantic similarity for resume–job alignment
- BM25 keyword relevance to catch exact terminology and technical keywords
- Structured requirement-level matching with per-requirement evidence status
- Weighted hybrid scoring across three complementary signals
- Cross-Encoder reranking of top candidates for joint relevance evaluation
- LLM explanation layer with structured, schema-validated JSON output
- Explainability: evidence, strengths, gaps, uncertainty for every assessment
- Human-in-the-loop: no final hiring decisions, no automatic applications
- Redis caching strategy and distributed rate limiting for cost control
- Prompt injection defenses (untrusted document input, restricted tools)
- Secure secrets management (environment-based, never hardcoded)
- PostgreSQL + pgvector for native embedding storage and similarity queries
- Containerized reproducible environments (Docker + Compose)
- AWS container hosting (ECS/Fargate) for remote accessibility
- Responsible AI: no bias-free claims, privacy-first data handling

---

## ⚡ Performance

- Semantic matching decoupled from LLM calls for repeatable, low-latency scoring
- Redis caching reduces repeated embedding and match computation
- Hybrid scoring is deterministic; the LLM is used only for explanation
- Rate limiting prevents abuse and runaway LLM costs
- Graceful degradation when Redis, the database, or the LLM provider is unavailable

Target:
- Sub-second cached match responses
- Stable latency under concurrent uploads
- Clear HTTP 429 behavior under rate limiting

---

## 🔮 Future Improvements

- Transferable/related skill detection (e.g., Express.js as evidence for a Node.js requirement)
- Years-of-experience and education/certification matching
- Distinguishing mandatory vs. preferred qualifications when wording is ambiguous
- Partial status for related-but-incomplete evidence
- Kubernetes deployment (auto-scaling, health checks, config management)
- Retrieval-augmented generation for richer job-context grounding
- OpenTelemetry distributed tracing and Grafana dashboards
- Expanded fairness evaluation across job categories and resume styles
- Persistent agent workflow state for long-running analyses
- Multi-provider LLM failover (OpenAI → Anthropic → Gemini)

---

## 📚 What This Project Demonstrates

- Applied NLP and transformer-based semantic matching
- Hybrid retrieval and ranking systems (bi-encoder + lexical + structured + cross-encoder)
- LLM integration with structured outputs and verification
- Responsible AI practices (explainability, privacy, human oversight)
- Production-style backend, database, and infrastructure engineering
- Mixed-methods evaluation linking model quality to system behavior
- End-to-end delivery: design → implementation → security → cloud deployment

---

## 🏁 Summary

MatchPilot.ai delivers a deployable, containerized, AWS-hosted AI recruitment assistant that pairs a hybrid matching engine (Sentence-BERT + BM25 + structured requirement matching + Cross-Encoder reranking) with an LLM explanation layer — emphasizing transparency, evidence, privacy, verification, and human control at every step.

Built to assist — designed to be questioned.