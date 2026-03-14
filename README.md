# NyayaSetu — Public Grievance Intelligence Platform

A full-stack AI-powered platform for transparent public grievance management in India, with automatic complaint clustering, SLA monitoring, fake-closure detection, and undertrial rights (Section 436A) tracking.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18 + Vite + Tailwind CSS |
| Backend | Python FastAPI + Uvicorn |
| Database | Supabase (PostgreSQL) |
| AI (LLM) | Groq API (Llama 3.1 8B) |
| AI (Embeddings) | Google Gemini (text-embedding-004) |
| SMS | Twilio |
| Maps | Leaflet.js / react-leaflet |
| Charts | Recharts |

## Setup Instructions

### 1. Prerequisites
- Python 3.11+ (`py --version`)
- Node.js 18+ (`node --version`)
- npm 9+ (`npm --version`)

### 2. Get API Keys

| Service | URL | What you need |
|---------|-----|--------------|
| Supabase | https://supabase.com | Project URL + Anon Key |
| Groq | https://console.groq.com | API Key (free tier) |
| Gemini | https://aistudio.google.com/apikey | API Key (free tier) |
| Twilio | https://twilio.com | Account SID + Auth Token + Phone Number |

### 3. Set Up Supabase
1. Create a new Supabase project
2. Go to **SQL Editor**
3. Paste the contents of `backend/schema.sql` and run it
4. Copy your **Project URL** and **Anon Key** from Settings > API

### 4. Backend Setup
```bash
cd backend
cp .env.template .env
# Edit .env and paste your API keys

py -m pip install -r requirements.txt
py -m uvicorn main:app --reload --port 8000
```

### 5. Seed Test Data (optional)
```bash
cd backend
py seed_data.py
```

### 6. Frontend Setup
```bash
cd frontend
cp .env.template .env
# Default: VITE_API_URL=http://localhost:8000

npm install
npm run dev
```

Open http://localhost:5173

## Pages

| Route | Page | Purpose |
|-------|------|---------|
| `/` | Citizen Portal | Submit complaints via voice/text |
| `/officer` | Officer Dashboard | Stats, map, complaints, clusters, briefs |
| `/justice` | Justice-Link | Undertrial prisoner rights (436A) |
| `/track/:id` | Track Complaint | Citizen tracks complaint status |

## Key Features
- **Voice Input**: Web Speech API for complaint dictation
- **AI Analysis**: Auto-categorize, score urgency, detect credibility
- **Tamper-Proof Receipts**: SHA-256 hashed complaint records
- **Smart Clustering**: AI groups similar complaints by ward/category
- **SLA Monitoring**: Auto-detect breached complaints (>48hrs open)
- **Fake Closure Detection**: Auto-reopen if citizen doesn't confirm within 2 min (demo)
- **Governance Briefs**: AI-generated intelligence reports for officers
- **436A Rights**: Track undertrial prisoners eligible for bail

## Deployment

### Frontend (Vercel)
```bash
cd frontend
npm run build
# Deploy dist/ folder to Vercel
```

### Backend (Railway)
1. Push backend/ to a GitHub repo
2. Connect to Railway
3. Set environment variables from .env
4. Deploy with: `uvicorn main:app --host 0.0.0.0 --port $PORT`
