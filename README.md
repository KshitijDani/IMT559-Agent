# Exercise Tracker

Exercise Tracker is a simple full-stack web app for logging workouts, storing a single location per workout, and seeing your recent exercise history and weekly totals.

## Stack

- Frontend: React + Vite
- Backend: FastAPI
- Database: Postgres
- Auth: demo-mode no-auth locally, with Google Sign-In support available for future use

## Features

- Google account sign-in
- Log workouts with preset or custom activity types
- Manual duration entry
- Browser geolocation with manual location fallback
- Dashboard with totals and recent workouts
- Workout history list for the signed-in user
- Single-origin local runtime through `http://localhost:8000`

## Project structure

- `frontend/`: React single-page app
- `backend/`: FastAPI API and tests
- `docker-compose.yml`: local Postgres service

## Local setup

### 1. Start Postgres

```bash
docker compose up -d
```

### 2. Configure the backend

```bash
cp .env.example .env
cd backend
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
```

Update the root `.env` with your `JWT_SECRET`, `BASE_URL`, and any ngrok/CORS settings you need.

For a public ngrok app running through the backend on port `8000`, set:

- `CORS_ORIGINS` to a comma-separated list including `http://localhost:8000` and any public app URLs
- `SECURE_COOKIES=true`
- `COOKIE_SAMESITE=none`

### 3. Configure the frontend

```bash
cd frontend
npm install
npm run build
```

### 4. Run the full app through the backend

```bash
cd ../backend
./.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The backend serves both:

- frontend UI at `http://localhost:8000`
- backend API at `http://localhost:8000/api/*`

Examples:

- `http://localhost:8000/`
- `http://localhost:8000/dashboard`
- `http://localhost:8000/api/health` is still `http://localhost:8000/health`

## Notes

- The current demo flow does not require login.
- Both frontend and backend read configuration from the single root `.env` file.
- Rebuild the frontend with `npm run build` in `frontend/` whenever you change frontend code.
- FastAPI serves the compiled files from `frontend/dist`, so the app runs behind a single base URL.
- Change `BASE_URL` in the root `.env` when you want the app to point at a different public or local host.
- `backend/app/config.py` reads `BASE_URL` from the root `.env` at runtime.
- `frontend/src/api.js` reads the same root `BASE_URL` at build time through Vite, so rebuild `frontend/` after changing it.

## Backend test suite

```bash
cd backend
pytest
```

The tests use an isolated in-memory SQLite database so they can run quickly without requiring Postgres.
