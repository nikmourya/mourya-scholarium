# Mourya Scholarium

> **Your Portal to Advanced Research, Learning, and Academic Excellence.**

A premium scholar-first academic intelligence and writing platform built on a multi-agent architecture.

## Architecture

```
┌─ Frontend (Next.js 14) ────────────────────────────────────┐
│  Landing · Auth · Onboarding · Dashboard · Writing Studio  │
└───────────────────────┬────────────────────────────────────┘
                        │ REST API
┌───────────────────────▼────────────────────────────────────┐
│  Backend (FastAPI)                                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Lead Orchestrator Agent                             │   │
│  │  ├── Writing Pedagogy Agent (English level → config) │   │
│  │  ├── Style Learning Agent (user voice extraction)    │   │
│  │  ├── Academic Retrieval Agent (3 scholarly APIs)     │   │
│  │  ├── ML Systems Agent (XGBoost-style ranking)       │   │
│  │  ├── Literature Review Agent (narrative reviews)     │   │
│  │  ├── Writing Engine (Claude LLM generation)         │   │
│  │  ├── Citation Agent (APA 7th, bibliography)         │   │
│  │  ├── Integrity Agent (claim verification)           │   │
│  │  └── Evaluation Agent (metrics logging)             │   │
│  └─────────────────────────────────────────────────────┘   │
└────┬──────────┬──────────┬──────────┬──────────────────────┘
     │          │          │          │
 PostgreSQL   Qdrant     Redis    Anthropic API
```

---

## Quick Start (Local Development)

### Prerequisites
- Python 3.11+
- Node.js 20+
- (Optional) Docker & Docker Compose

### 1. Clone and configure

```bash
git clone https://github.com/YOUR_USERNAME/mourya-scholarium.git
cd mourya-scholarium
cp .env.example .env
# Edit .env if needed — defaults work for local development
```

### 2. Start the backend

```bash
cd apps/api
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn main:app --reload --port 8000
```

The backend runs at **http://localhost:8000**. Check the health endpoint at http://localhost:8000/ and API docs at http://localhost:8000/docs.

### 3. Start the frontend

```bash
cd apps/web
npm install
npm run dev
```

The frontend runs at **http://localhost:3000**.

### 4. Test the app

1. Open http://localhost:3000
2. Click **Start Writing** → goes to registration
3. Fill in name, email, password → click **Create Account**
4. You'll be redirected to the onboarding flow
5. Complete onboarding → arrives at dashboard

---

## Docker Compose (Full Stack)

```bash
cd mourya-scholarium
cp .env.example .env
docker-compose up -d
```

This starts PostgreSQL, Redis, Qdrant, FastAPI backend (port 8000), and Next.js frontend (port 3000).

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/auth/register` | Create account |
| POST | `/api/v1/auth/login` | Login |
| POST | `/api/v1/profile` | Save user profile |
| POST | `/api/v1/profile/style-sample` | Upload writing sample |
| GET | `/api/v1/profile/style-signature` | Get style signature |
| POST | `/api/v1/projects` | Create project |
| GET | `/api/v1/projects` | List projects |
| POST | `/api/v1/write` | Submit writing request (full pipeline) |
| GET | `/api/v1/write/{id}` | Get session |
| POST | `/api/v1/write/{id}/feedback` | Submit feedback |
| POST | `/api/v1/retrieve` | Search scholarly sources |
| POST | `/api/v1/cite/format` | Format bibliography |
| GET | `/api/v1/evidence/{id}` | Get evidence traces |

---

## MVP Writing Modes

- ✅ **Write from Prompt** — Generate academic text from a simple prompt
- ✅ **Rewrite / Polish** — Improve existing text while preserving meaning
- ✅ **Narrative Literature Review** — Source-grounded thematic synthesis
- 🔜 Methodology, Results to Prose, Abstract, Research Proposal

---

## Deployment Guide

### Deploy Frontend on Vercel

1. Push to GitHub (see below)
2. Go to [vercel.com](https://vercel.com) → **New Project**
3. Import your GitHub repo
4. Set **Root Directory** to `apps/web`
5. Set **Framework Preset** to `Next.js`
6. Add environment variable:
   - `NEXT_PUBLIC_API_URL` = your deployed backend URL (e.g., `https://mourya-scholarium-api.onrender.com`)
7. Click **Deploy**

### Deploy Backend on Render

1. Push to GitHub (see below)
2. Go to [render.com](https://render.com) → **New Web Service**
3. Connect your GitHub repo
4. Set **Root Directory** to `apps/api`
5. Set **Build Command** to:
   ```
   pip install -r requirements.txt && python -m spacy download en_core_web_sm
   ```
6. Set **Start Command** to:
   ```
   uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
7. Add environment variables:
   | Variable | Value |
   |----------|-------|
   | `APP_ENV` | `production` |
   | `APP_DEBUG` | `false` |
   | `USE_SQLITE` | `true` |
   | `CORS_ORIGINS` | Your Vercel frontend URL |
   | `APP_SECRET_KEY` | Random 64-char string |
   | `JWT_SECRET_KEY` | Random string |
   | `JWT_ALGORITHM` | `HS256` |
   | `JWT_EXPIRATION_MINUTES` | `1440` |
8. Click **Create Web Service**

### After Both Are Deployed

1. Copy your Render backend URL (e.g., `https://mourya-scholarium-api.onrender.com`)
2. In Vercel dashboard → Settings → Environment Variables → set `NEXT_PUBLIC_API_URL` to that URL
3. In Render dashboard → Environment → set `CORS_ORIGINS` to your Vercel URL (e.g., `https://mourya-scholarium.vercel.app`)
4. Redeploy both services

---

## Push to GitHub

```bash
cd mourya-scholarium

# Initialize git
git init
git add .
git commit -m "Initial commit: Mourya Scholarium MVP"

# Create repo on GitHub (via github.com or CLI)
# Then push:
git remote add origin https://github.com/YOUR_USERNAME/mourya-scholarium.git
git branch -M main
git push -u origin main
```

---

## Environment Variables Reference

### Backend (`apps/api`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `APP_ENV` | No | `development` | Environment mode |
| `APP_SECRET_KEY` | Yes | `change-me` | Application secret |
| `APP_DEBUG` | No | `true` | Enable debug mode |
| `CORS_ORIGINS` | Yes | `http://localhost:3000` | Allowed origins (comma-separated) |
| `USE_SQLITE` | No | `true` | Use SQLite instead of PostgreSQL |
| `JWT_SECRET_KEY` | Yes | `change-me` | JWT signing secret |
| `JWT_ALGORITHM` | No | `HS256` | JWT algorithm |
| `ANTHROPIC_API_KEY` | No | _(empty)_ | Anthropic API key for writing features |

### Frontend (`apps/web`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | No | _(empty)_ | Backend URL. Empty = use proxy rewrite |

---

## Tech Stack

- **Frontend:** Next.js 14, TypeScript, Zustand, Tiptap (editor)
- **Backend:** FastAPI, SQLAlchemy (async), Pydantic v2
- **Database:** SQLite (dev) / PostgreSQL 16 (prod), Qdrant (vectors), Redis (cache)
- **AI:** Anthropic Claude API, spaCy NLP, XGBoost-style ranking
- **Infra:** Docker, Vercel (frontend), Render (backend)

## License

Proprietary — © 2026 Mourya Scholarium
