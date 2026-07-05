# Deploying AlphaQuantPro to Vercel

AlphaQuantPro is a **two-part app**: a Next.js **frontend** and a FastAPI **backend**. Vercel is an excellent host for the Next.js frontend. The backend needs some thought because two of its features do not fit Vercel's stateless serverless model:

- The **paper/simulation engine** runs **background threads** with **in-memory run state**. Serverless functions stop after each request, so long-running paper runs cannot continue in the background.
- Storage defaults to a **SQLite file**, but the serverless filesystem is **ephemeral/read-only** (only `/tmp` is writable and it is wiped often).

Because of this, there are two supported deployment shapes:

| Option | Frontend | Backend | Best for |
| --- | --- | --- | --- |
| **A. Recommended** | Vercel | A long-running host (Render / Railway / Fly.io) + Postgres or a volume | Full functionality, including paper runs and durable data |
| **B. Vercel-only** | Vercel | Vercel Python serverless (`backend/api/index.py`) + external Postgres | Quick demos; backtests and read APIs work, **paper runs are unreliable** |

Both options use the same frontend deployment. Pick your backend based on whether you need reliable paper runs and persistent storage.

---

## Prerequisites

- A [Vercel](https://vercel.com) account and the repo connected (GitHub import or `vercel` CLI).
- Optional API keys (the app works without them via labeled mock fallbacks):
  - `DEEPSEEK_API_KEY` — enables real DeepSeek analysis.
  - `QVERIS_API_KEY` — enables real QVeris.ai market data.
- For durable storage: a Postgres URL (e.g. **Vercel Postgres**, **Neon**, or **Supabase**). To use Postgres, add `psycopg[binary]` (or `psycopg2-binary`) to `backend/requirements.txt` and set `DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/DB`.

---

## Part 1 — Deploy the frontend to Vercel (both options)

1. In Vercel, **Add New → Project** and import this repository.
2. Set **Root Directory** to `frontend`. Vercel auto-detects Next.js (config is also pinned in `frontend/vercel.json`).
3. Add an **Environment Variable**:
   - `NEXT_PUBLIC_API_BASE_URL` = the public URL of your backend (from Part 2).
     - Example (Option A): `https://alphaquantpro-api.onrender.com`
     - Example (Option B): `https://<your-backend-project>.vercel.app`
4. **Deploy**. Your frontend will be live at `https://<project>.vercel.app`.

> `NEXT_PUBLIC_API_BASE_URL` is read at build time (see `frontend/lib/api.ts`). If you change it later, **redeploy** the frontend.

---

## Part 2, Option A — Backend on a long-running host (recommended)

This keeps paper-run background threads and persistent storage working. Example using **Render** (Railway/Fly.io are analogous):

1. **New → Web Service**, connect the repo, set **Root Directory** to `backend`.
2. **Build command**: `pip install -r requirements.txt`
3. **Start command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. **Environment variables**:
   - `DEEPSEEK_API_KEY`, `QVERIS_API_KEY` (optional)
   - `DATABASE_URL` — a Postgres URL for durability, **or** attach a persistent disk and use `sqlite:////data/alphaquantpro.db`.
5. Deploy, then copy the service URL into the frontend's `NEXT_PUBLIC_API_BASE_URL` and redeploy the frontend.

The backend already sends permissive CORS headers, so the Vercel frontend can call it cross-origin.

---

## Part 2, Option B — Backend on Vercel serverless (with caveats)

The repo includes `backend/vercel.json` and `backend/api/index.py` (an ASGI entry that exports the FastAPI `app`).

1. In Vercel, **Add New → Project**, import the repo **again** as a second project.
2. Set **Root Directory** to `backend`.
3. Vercel detects the Python runtime from `backend/vercel.json`; `backend/requirements.txt` is installed automatically.
4. **Environment variables**:
   - `DEEPSEEK_API_KEY`, `QVERIS_API_KEY` (optional)
   - `DATABASE_URL` — **strongly recommended**: point to external Postgres. Without it, storage falls back to `/tmp` and is reset frequently (the app auto-detects Vercel and uses `/tmp` so it won't crash on the read-only filesystem).
5. Deploy, then set the frontend's `NEXT_PUBLIC_API_BASE_URL` to this backend's URL and redeploy the frontend.

**Known limitations on Vercel serverless:**

- **Paper/simulation runs are unreliable.** They rely on background threads and in-memory state that a serverless function cannot keep alive after responding. Strategy CRUD, market-data fetch, backtests, and analysis endpoints work fine.
- **Cold starts / size.** `pandas` + `numpy` are large; keep an eye on the function size limit (`maxLambdaSize` is set to `250mb`). If you hit limits, prefer Option A.
- **No local file persistence.** Always use an external `DATABASE_URL` for anything you want to keep.

---

## Environment variables reference

| Variable | Where | Required | Purpose |
| --- | --- | --- | --- |
| `NEXT_PUBLIC_API_BASE_URL` | Frontend (Vercel) | Yes | Backend URL the browser calls |
| `DEEPSEEK_API_KEY` | Backend | No | Enables real DeepSeek LLM (else MOCK LLM OUTPUT) |
| `DEEPSEEK_BASE_URL` | Backend | No | Defaults to `https://api.deepseek.com` |
| `DEEPSEEK_MODEL` | Backend | No | Defaults to `deepseek-chat` (must be a DeepSeek model) |
| `QVERIS_API_KEY` | Backend | No | Enables real QVeris.ai data (else labeled MOCK DATA) |
| `QVERIS_BASE_URL` | Backend | No | Defaults to `https://qveris.ai/api/v1` |
| `QVERIS_SESSION_ID` | Backend | No | Defaults to `alphaquantpro-local` |
| `DATABASE_URL` | Backend | Recommended in prod | External DB for durable storage |

> API keys are backend-only. Never put `DEEPSEEK_API_KEY` or `QVERIS_API_KEY` in frontend/`NEXT_PUBLIC_*` variables — those are exposed to the browser.

---

## CLI quick path (optional)

```bash
# Frontend
cd frontend
vercel --prod            # set Root Directory / env in the dashboard or vercel.json

# Backend (Option B)
cd backend
vercel --prod
```

---

## Verify after deploy

1. Open `https://<backend-url>/health` → `{"status":"ok"}` and `https://<backend-url>/docs` → OpenAPI UI.
2. Open the frontend URL → the dashboard loads and the **Market Data** status card shows the active source (QVeris or MOCK DATA).
3. Create a strategy → run a backtest → confirm metrics, charts, trades, and logs render.
4. (Option A only) Start a paper run and confirm it updates and can be stopped.

> Reminder: AlphaQuantPro is **simulation-only** and is **not financial advice**. Live trading is disabled in the MVP regardless of where it is deployed.
