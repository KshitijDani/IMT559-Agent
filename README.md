# Exercise Tracker

Exercise Tracker is a simple full-stack web app for logging workouts, storing a single location per workout, and seeing your recent exercise history and weekly totals.

## Stack

- Frontend: React + Vite
- Backend: FastAPI
- Database: Postgres
- Auth: Google Sign-In with backend token verification and an HTTP-only session cookie

## Features

- Google account sign-in
- Log workouts with preset or custom activity types
- Manual duration entry
- Browser geolocation with manual location fallback
- Dashboard with totals and recent workouts
- Workout history list for the signed-in user

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
cd backend
cp .env.example .env
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Update `backend/.env` with your Google OAuth client ID and a strong `JWT_SECRET`.

For a public ngrok frontend calling a public ngrok backend, set:

- `CORS_ORIGINS` to a comma-separated list including your local frontend and public frontend URLs
- `SECURE_COOKIES=true`
- `COOKIE_SAMESITE=none`

### 3. Configure the frontend

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

Update `frontend/.env` with the same Google client ID and the backend URL if needed.

If you expose the Vite dev server through ngrok, start it with host binding enabled and use the ngrok hostname in Vite's allowed host list. This repo already allows:

- `headgear-grinch-credit.ngrok-free.dev`

## Google sign-in setup

1. Create a Google OAuth web application credential in Google Cloud.
2. Add `http://localhost:5173` as an authorized JavaScript origin.
3. Put that client ID in both:
   - `backend/.env` as `GOOGLE_CLIENT_ID`
   - `frontend/.env` as `VITE_GOOGLE_CLIENT_ID`

## Backend test suite

```bash
cd backend
pytest
```

The tests use an isolated in-memory SQLite database so they can run quickly without requiring Postgres.
