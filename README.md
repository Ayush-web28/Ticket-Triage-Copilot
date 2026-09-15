# Ticket Triage Copilot

A support-ticket triage agent for the **NVIDIA x Nebius Global AI Hackathon** (Best Apps and Agents track).

Every incoming ticket flows through a **tiered NVIDIA Nemotron 3 pipeline** served on **Nebius Token Factory**:

```
Ticket  →  Nemotron 3 Nano  →  Nemotron 3 Super  →  RAG retrieval  →  Nemotron 3 Ultra
           (classify)          (route/prioritize)   (KB grounding)    (draft resolution)
```

- **Nano** does the cheap, high-volume work: category / urgency / sentiment classification on every ticket.
- **Super** makes the routing decision: priority (1-5), which team owns it, and whether it needs to be escalated to a human before any auto-reply goes out.
- A small retrieval step grounds the draft in your knowledge base (TF-IDF locally in mock mode, real embeddings via Nebius otherwise).
- **Ultra** is reserved for the one step that actually needs strong reasoning: writing a full, KB-grounded draft reply.

A human reviews and approves (or edits) every draft before anything is "sent" — this is a copilot, not an autonomous responder.

## Why this shape

Support triage is a textbook case for tiered model routing: most of the pipeline is simple classification that a small model nails in milliseconds, and only the final drafting step benefits from a large reasoning model. Routing the right ticket to the right model is also literally the product.

## Project structure

```
backend/            FastAPI service, SQLite storage, the 4-stage pipeline
  app/
    pipeline/        classify.py (Nano) / route.py (Super) / rag.py / draft.py (Ultra)
    routes/          REST endpoints
    seed_data/       synthetic tickets + a small support knowledge base
frontend/           React + Vite + Tailwind dashboard
```

## Quickstart

### 1. Backend

```bash
cd backend
python -m venv .venv
.venv/Scripts/activate   # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env
```

Edit `backend/.env` and set `NEBIUS_API_KEY` (get one at [tokenfactory.nebius.com](https://tokenfactory.nebius.com)).

> **Verify model slugs before a real run.** `MODEL_NANO`/`MODEL_SUPER`/`MODEL_ULTRA` in `.env.example` follow Nebius's `nvidia/nemotron-3-<size>-<total>b-a<active>b` naming (confirmed for Super: `nvidia/nemotron-3-super-120b-a12b`). Check the current exact slugs for Nano/Ultra against the [live model catalog](https://tokenfactory.nebius.com/models/catalog) since catalog names shift as new sizes roll out.

Load the knowledge base and 12 synthetic tickets, then start the API:

```bash
python -m app.seed
python -m uvicorn app.main:app --reload --port 8000
```

No `NEBIUS_API_KEY`? The app runs in **mock mode** automatically — deterministic rule-based classification, TF-IDF retrieval, and template drafts stand in for the three Nemotron calls, so the whole pipeline and UI are still fully demoable offline.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173). The dev server proxies `/api` to the backend on port 8000.

## What to look at

- **Dashboard** — live queue with category/urgency/priority/team/status, plus per-tier average latency so the model-routing story is visible at a glance.
- **Ticket detail** — the full pipeline trace (which model ran each stage, how long it took), which KB articles the draft was grounded on, and an editable draft reply with Approve & Send.
- **Submit a ticket** — type any support request and watch it move through Nano → Super → Ultra in real time.

## Nebius Token Factory / NVIDIA Nemotron usage

- All three tiers of **NVIDIA Nemotron 3** (Nano, Super, Ultra) are called through Nebius Token Factory's OpenAI-compatible API (`https://api.tokenfactory.nebius.com/v1/`), selected per-stage by task difficulty rather than using one model for everything.
- Retrieval embeddings use Nebius's embeddings endpoint (`BAAI/bge-en-icl` by default).
- `backend/app/nebius_client.py` is the single integration point — swap models or add a fourth tier there.

## Deploying a public demo

This repo has no infra dependency beyond SQLite, so it deploys as two small free-tier services.

### Backend on Render

1. Push this repo to GitHub (see below).
2. In Render: **New > Blueprint**, point it at the repo — it reads [`render.yaml`](render.yaml) and creates the web service automatically (root dir `backend`, build `pip install -r requirements.txt`, start `python -m app.seed && uvicorn app.main:app --host 0.0.0.0 --port $PORT`).
3. Set the `NEBIUS_API_KEY` env var in the Render dashboard (it's marked `sync: false` in the blueprint so it isn't committed to git). Leave `MOCK_MODE=false`.
4. Deploy, then note the service URL, e.g. `https://ticket-triage-backend.onrender.com`.

Render's free tier uses an ephemeral filesystem — SQLite resets on every redeploy/restart, but `python -m app.seed` re-runs automatically on boot, so the demo data is always there. Tickets created live between restarts will be lost on the free tier; upgrade to a paid instance with a persistent disk (or swap in Render's free Postgres) if that matters for judging.

### Frontend on Vercel

1. **New Project** in Vercel, import the same GitHub repo.
2. Set **Root Directory** to `frontend` (Vercel auto-detects the Vite framework preset from there — no other config needed).
3. Add an env var `VITE_API_BASE` = your Render backend URL from above (e.g. `https://ticket-triage-backend.onrender.com`).
4. Deploy. The backend already allows all CORS origins, so the frontend can call it directly cross-origin.

### GitHub repo (required for submission anyway)

1. Go to [github.com/new](https://github.com/new), create a **public** repo (e.g. `ticket-triage-copilot`). Don't initialize it with a README/License/.gitignore — this repo already has them.
2. Copy the repo's URL and give it to whoever is pushing the code (`git remote add origin <url> && git push -u origin main`).

## License

MIT — see [LICENSE](LICENSE).
