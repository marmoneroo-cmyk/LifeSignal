# Deploy LifeSignal to a real URL

End-to-end deploy guide. **All steps free-tier eligible.** Total time: ~20 minutes.

---

## Stack

- **Frontend** → Vercel (Next.js, free hobby tier)
- **Backend** → Railway (Python, $5/mo trial credit; or Render/Fly free tier)
- **Database** → Railway-managed PostgreSQL (auto-provisioned), or stays SQLite for solo demos

---

## 1. Push to GitHub

```powershell
cd "C:\Users\shlom\Desktop\health insurances"
git init
git add .
git commit -m "Initial commit"
gh repo create lifesignal --private --source=. --push
```

---

## 2. Deploy the backend (Railway)

1. Go to **https://railway.app/new** and click **"Deploy from GitHub repo"**
2. Pick your `lifesignal` repo
3. **Root directory:** set to `backend`
4. Railway auto-detects Python and uses [`railway.json`](backend/railway.json) — start command:
   `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. **Add a PostgreSQL service:** "+ New" → "Database" → "PostgreSQL". Railway sets
   `DATABASE_URL` automatically as an env var.
6. **Set environment variables** under the backend service → Variables:
   ```
   CORS_ORIGINS=https://<your-frontend>.vercel.app
   JWT_SECRET=<run: openssl rand -hex 32>
   ANTHROPIC_API_KEY=sk-ant-...   # optional, enables Claude chat + narration
   ANTHROPIC_MODEL=claude-sonnet-4-6
   ```
7. Railway generates a public URL — copy it (e.g. `https://lifesignal-prod.up.railway.app`)
8. **Seed the production DB once.** Open Railway shell → Run:
   ```bash
   python -m app.data.seed
   ```

---

## 3. Deploy the frontend (Vercel)

1. Go to **https://vercel.com/new** and import the same `lifesignal` repo
2. **Root directory:** set to `frontend`
3. Framework: Next.js (auto-detected via [`vercel.json`](frontend/vercel.json))
4. **Environment Variables:**
   ```
   NEXT_PUBLIC_API_URL=https://lifesignal-prod.up.railway.app
   ```
   (use the Railway URL from step 2.7)
5. Click **Deploy**

---

## 4. Connect the two

After the frontend deploys, copy its URL (e.g. `https://lifesignal.vercel.app`)
and **update the Railway backend's `CORS_ORIGINS`** env var to that URL, then
restart the service. This closes the loop — the browser will now be allowed to
call the API.

---

## 5. Verify

Open `https://lifesignal.vercel.app` → log in with `demo@demo.com` / `demo1234`.
The dashboard, report, chat, and PDF/Excel upload should all work.

---

## Cost estimate

| Component | Free tier | If you grow |
|---|---|---|
| Vercel (frontend) | Unlimited hobby projects | Pro $20/mo |
| Railway (backend) | $5 trial credit; ~$3/mo at idle | Pay-as-you-go |
| Railway Postgres | Included | $5/mo at scale |
| Anthropic API | Pay per token (~$0.003 per chat) | — |

**Bottom line:** for a personal / small group, you're effectively free besides ~$3/mo
on Railway and whatever Claude tokens you use.

---

## Alternatives

- **Render** (free tier with cold starts) — drop-in replacement for Railway, uses [`Procfile`](backend/Procfile)
- **Fly.io** (generous free tier) — needs a `fly.toml`; can add on request
- **Single-host (cheaper):** deploy both on one Railway service — frontend builds inside backend
