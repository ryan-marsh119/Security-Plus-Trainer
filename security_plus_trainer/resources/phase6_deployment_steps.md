# Phase 6 — Deployment Steps (Part B, user-run)

These are the steps **only you** can do to take the app live on Railway. All the
code/config (Part A) is already done and verified locally — see the Phase 6 entry
in `CLAUDE.md` and the plan at `.claude/plans/ticklish-chasing-marble.md`.

**Topology recap:** one Railway **web service** (gunicorn → Django serves the API,
admin, *and* the React SPA from the same origin) + one Railway **PostgreSQL**.
Deploys are driven by GitHub Actions: push to `main` → `test` job → `deploy` job
(`railway up`) only if tests pass.

---

## 0. Prerequisites (one time)

- A GitHub account with this repo pushed to it (the `deploy` job triggers on push to `main`).
- A Railway account: go to https://railway.app and **Sign in with GitHub**.
- (Optional, for the superuser step) the Railway CLI locally:
  `npm install -g @railway/cli` then `railway login`.

---

## 1. Create the Railway project + database

1. Railway dashboard → **New Project**.
2. In the project, click **+ New** → **Database** → **Add PostgreSQL**.
   - This creates a managed Postgres and exposes a `DATABASE_URL` variable.

---

## 2. Create the web service from this repo

1. In the same project, click **+ New** → **GitHub Repo** → select this repository.
   - Railway detects `railway.json` and builds with the root **`Dockerfile`**
     (combined image). No build config needed.
2. Open the new service → **Settings** → confirm:
   - **Builder:** Dockerfile (from `railway.json`).
   - **Healthcheck Path:** `/api/v1/healthz` (from `railway.json`).

---

## 3. Set the web service environment variables

Service → **Variables** → add:

| Variable | Value |
|----------|-------|
| `SECRET_KEY` | a freshly generated secret (see below) |
| `DEBUG` | `False` |
| `DATABASE_URL` | reference the Postgres service's `DATABASE_URL` (use Railway's **Add Reference** → Postgres → `DATABASE_URL`) |

Notes:
- **Do NOT set** `SESSION_COOKIE_SECURE` / `CSRF_COOKIE_SECURE` — they default to
  `True` in prod (because `DEBUG=False`), which is what you want over HTTPS.
- `RAILWAY_PUBLIC_DOMAIN` is injected by Railway automatically; `settings.py`
  already adds it to `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS`.

Generate a `SECRET_KEY` (any one of these):

```bash
# Python (works anywhere Django is installed)
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# or OpenSSL
openssl rand -base64 48
```

---

## 4. Create the Railway API token for CI

1. Railway → **Account Settings** → **Tokens** → **Create Token** (name it e.g. `github-actions`).
   - A **project token** scoped to this project/environment is preferred.
2. Copy the token value.
3. GitHub → this repo → **Settings** → **Secrets and variables** → **Actions**:
   - **New repository secret:** name `RAILWAY_TOKEN`, value = the token.
4. **Only if** your Railway service is **not** named `web`:
   - Add a repository **Variable** (not secret): name `RAILWAY_SERVICE`, value = your
     service's exact name. (The CI deploy step runs `railway up --service <that>`.)

---

## 5. Approve the commit + push (triggers the first deploy)

Per the project rule, Claude has **not** committed/pushed. When you're ready:

1. Tell Claude to commit the Phase 6 changes and push to `main`
   (or do it yourself: `git add -A && git commit && git push origin main`).
2. Watch **GitHub → Actions**:
   - `test` job: Postgres service → migrate → `manage.py test` → `npm run build`.
   - `deploy` job (only after `test` passes): `railway up`.
3. Watch **Railway → your service → Deployments** for the build + release. The
   container entrypoint runs migrate → collectstatic → seed_domains →
   import_questions → gunicorn automatically (all idempotent).

> If `test` fails, **no deploy happens** — fix the failure and push again.

---

## 6. First-deploy admin user + live smoke test

1. Create a superuser against the live DB:
   ```bash
   railway run python manage.py createsuperuser
   ```
   (Or use the service's **Shell** in the Railway dashboard.)
2. Open your public URL (Railway → service → **Settings** → **Domains**, or click the
   generated `*.up.railway.app` URL). Verify:
   - `https://<your-domain>/api/v1/healthz` → `{"status": "ok"}`
   - `https://<your-domain>/` → the app loads (register/login works)
   - `https://<your-domain>/admin/` → admin login works
   - Take a short study session: question loads → submit answer → hint/explanation +
     green correct-answer reveal behave correctly.

---

## Ops cheatsheet (after go-live)

- **Logs:** `railway logs` (CLI) or Railway dashboard → service → **Logs**.
- **Restart:** Railway dashboard → service → **Restart**.
- **Redeploy / rollback:** service → **Deployments** → redeploy a previous build,
  or `git revert <bad commit>` + push (CI redeploys the reverted state).
- **Config change:** edit **Variables** → Railway re-releases automatically.
- **Run a one-off command:** `railway run <command>` (e.g. another `createsuperuser`,
  or `python manage.py shell`).

---

## Troubleshooting

| Symptom | Likely cause / fix |
|---------|--------------------|
| Deploy job fails: `Unauthorized` / `Project Token not found` | `RAILWAY_TOKEN` secret missing or wrong; regenerate + re-add. |
| Deploy job fails: `Multiple services found` / wrong service | Set the `RAILWAY_SERVICE` repo **variable** to your service name. |
| App returns `400 Bad Request` (DisallowedHost) | `RAILWAY_PUBLIC_DOMAIN` not present — confirm it's a Railway-managed service (it's auto-injected); a custom domain must also be added in Railway's Domains tab. |
| Login works but session/CSRF fails over HTTPS | Confirm `DEBUG=False` and that you did **not** override the secure-cookie vars; Railway terminates TLS and `SECURE_PROXY_SSL_HEADER` is already set. |
| Boot crashes on DB connect | `DATABASE_URL` not referenced from the Postgres plugin; re-add the reference. |
| Static/SPA assets 404 | Build issue — check the Deployments build log; `collectstatic` runs on boot and the SPA is baked into the image at `/app/frontend_build`. |
