# 🤖 AI-Powered Resume & Job Matching Agent

A full-stack, production-style recruitment assistant that combines transformer-based semantic matching, LLM agentic workflows, and cloud-native infrastructure to help users interpret resume–job alignment — without ever making the final hiring decision.

This project implements Sentence-BERT semantic similarity, a controlled LLM agent (planning, tool calling, verification, human escalation), Redis-backed caching and rate limiting, Docker containerization, and AWS deployment — built with transparency, privacy, and human oversight as first-class concerns.

---

## 🧰 Tech Stack

![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white&style=for-the-badge)
![Flask](https://img.shields.io/badge/Flask-000000?logo=flask&logoColor=white&style=for-the-badge)
![React](https://img.shields.io/badge/React-61DAFB?logo=react&logoColor=black&style=for-the-badge)
![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?logo=pytorch&logoColor=white&style=for-the-badge)
![Hugging Face](https://img.shields.io/badge/Hugging%20Face-FFD21E?logo=huggingface&logoColor=black&style=for-the-badge)
![Anthropic](https://img.shields.io/badge/Anthropic%20Claude-D4A27F?logo=anthropic&logoColor=white&style=for-the-badge)
![Redis](https://img.shields.io/badge/Redis-DC382D?logo=redis&logoColor=white&style=for-the-badge)
![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white&style=for-the-badge)
![AWS](https://img.shields.io/badge/AWS-232F3E?logo=amazonaws&logoColor=white&style=for-the-badge)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white&style=for-the-badge)


---

## 🧩 System Design

This diagram represents the high-level architecture of the AI-powered resume and job matching platform, including the request flow, agentic workflow, semantic matching engine, caching layer, and cloud deployment.

<p align="center">
  <img src="./Readme-Photos/System-Design.png" alt="System Design Diagram" width="800"/>
</p>

### Overview

- Users upload resumes and job descriptions through the React frontend (PDF/DOCX)
- The Flask backend validates requests and coordinates application services
- Documents are parsed and normalized (skills, experience, education) using NLP (spaCy / NLTK)
- A Sentence-BERT model generates embeddings for semantic similarity scoring
- The agent orchestrator plans tasks, calls tools, maintains workflow state, and verifies outputs
- An LLM integration service (Anthropic Claude, provider-abstracted) generates structured explanations and skill-gap analyses
- Redis caches embeddings/matches and enforces rate limits on expensive endpoints
- A verification module checks schemas, required fields, evidence references, and unsupported claims
- Uncertain or high-impact cases are escalated to human review
- The application is containerized with Docker and deployed to AWS (ECS/Fargate)

This design mirrors production-grade AI systems that combine deterministic ML pipelines with controlled LLM agents and responsible AI safeguards.

---

## 🚀 Features

- Semantic matching with Sentence-BERT embeddings + similarity scoring
- LLM agentic workflow (task planning, tool calling, state management, verification)
- Structured, schema-validated LLM outputs with deterministic checks
- Human-review escalation path for uncertain or high-impact cases
- Explainable results: match scores, evidence, detected skill gaps, and limitations
- Provider-abstracted LLM interface (Claude primary; OpenAI/Gemini fallback)
- Redis caching for embeddings, document processing, and match results
- Redis-based API rate limiting and cost controls
- Secure environment-based API key handling (no user-supplied keys)
- Prompt injection defenses and input validation
- Flask backend + React frontend with a minimal-training-overhead UI
- Dockerized multi-service environment via Docker Compose
- AWS deployment (ECS/Fargate) for reproducible, remote access
- Mixed-methods evaluation: precision@k, MRR, workflow reliability, latency, cache hit ratio, usability

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
│   ├── api/
│   │   ├── routes.py
│   │   └── schemas.py
│   │
│   ├── services/
│   │   ├── document_parser.py
│   │   ├── nlp_preprocessor.py
│   │   ├── semantic_matcher.py
│   │   ├── agent_orchestrator.py
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

## ⚙️ Configuration

### Example `.env`

```env
FLASK_ENV=development
SECRET_KEY=change-me

# LLM Provider (never commit real keys)
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-xxxxxxxx
LLM_MODEL=claude-sonnet

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
ANTHROPIC_API_KEY=sk-ant-xxxxxxxx
DATABASE_URL=postgresql://user:pass@db:5432/resume_matcher
REDIS_URL=redis://redis:6379/0
SECRET_KEY=change-me
```

> API credentials are stored via environment variables or a secrets manager and are never hardcoded in source control. End users are **never** asked to supply their own LLM keys.

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
    image: postgres:16-alpine
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
# add your API key and database credentials
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

## 🧪 Testing

### Upload a resume and job description

```bash
curl -X POST http://localhost:5000/api/match \
  -F "resume=@sample_resume.pdf" \
  -F "job_description=@sample_job.docx"
```

### Check rate limiting (should return HTTP 429 after limit)

```bash
for i in $(seq 1 70); do
  curl -s -o /dev/null -w "%{http_code}\n" http://localhost:5000/api/match
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
| Semantic matching quality | Precision@k, Mean Reciprocal Rank (expert-reviewed sample) |
| Agent workflow reliability | % completed workflows, % schema-valid LLM outputs |
| System performance | End-to-end API latency, Redis cache hit ratio |
| Usability & interpretability | Post-task questionnaire, Likert ratings of clarity/trust |

Supporting metrics: recall/F1, rate-limit accuracy, error rates, LLM token/request usage, cache invalidation behavior.

---

## 🔁 Request Flow

```
User (React Frontend)
  ↓
Flask Backend (validated API endpoints)
  ↓
Agent Orchestrator
  (Plan → Tool Calls → Match → LLM Explanation → Verify → Escalate?)
  ↓
Semantic Matching Engine (Sentence-BERT)
  ↓
Redis (cache + rate limit)  |  Database (state + results)
  ↓
LLM Integration Service (Claude, provider-abstracted)
  ↓
Verification Module (schemas + deterministic checks)
  ↓
Results + Explanations + Limitations → Human Review
```

---

## 🧠 Key Concepts Implemented

- Sentence-BERT semantic similarity for resume–job alignment
- Controlled agentic workflow (planning, tool calling, state, verification)
- Human-in-the-loop escalation for uncertain/high-impact cases
- Structured output schemas + deterministic business-rule validation
- Redis caching strategy (content-hash keys, documented TTLs)
- Distributed rate limiting to protect the service and control LLM costs
- Prompt injection defenses (untrusted document input, restricted tools)
- Secure secrets management (environment-based, never hardcoded)
- Containerized reproducible environments (Docker + Compose)
- AWS container hosting (ECS/Fargate) for remote accessibility
- Responsible AI: no final hiring decisions, no bias-free claims, privacy-first data handling

---

## ⚡ Performance

- Semantic matching decoupled from LLM calls for repeatable, low-latency scoring
- Redis caching reduces repeated embedding and match computation
- Rate limiting prevents abuse and runaway LLM costs
- Graceful degradation when Redis, the database, or the LLM provider is unavailable

Target:
- Sub-second cached match responses
- Stable latency under concurrent uploads
- Clear HTTP 429 behavior under rate limiting

---

## 🔮 Future Improvements

- Kubernetes deployment (auto-scaling, health checks, config management)
- Retrieval-augmented generation for richer job-context grounding
- OpenTelemetry distributed tracing
- Grafana dashboards for cache/latency/LLM-cost monitoring
- Expanded fairness evaluation across job categories and resume styles
- Limited demonstration ATS integration (if approved)
- Persistent agent workflow state for long-running analyses
- Multi-provider LLM failover (Claude → OpenAI → Gemini)

---

## 📚 What This Project Demonstrates

- Applied NLP and transformer-based semantic matching
- Real-world LLM agent design with verification and guardrails
- Responsible AI practices (explainability, privacy, human oversight)
- Production-style backend and infrastructure engineering
- Mixed-methods evaluation linking model quality to system behavior
- End-to-end delivery: design → implementation → security → cloud deployment

---

## 🏁 Summary

This project delivers a deployable, containerized, AWS-hosted AI recruitment assistant that pairs deterministic semantic matching with a controlled LLM agent — emphasizing transparency, privacy, verification, and human control at every step.

Built to assist — designed to be questioned.