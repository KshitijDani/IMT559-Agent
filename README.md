# Exercise Tracker

Exercise Tracker is a full-stack web app for logging workouts, storing one location per workout, and reviewing recent activity and weekly totals.

## Stack

- Frontend: React + Vite
- Backend: FastAPI
- Database: PostgreSQL
- Auth: Google Sign-In, with an optional dev-user bypass for local development

## Repo structure

- `frontend/`: React app
- `backend/`: FastAPI app and backend tests
- `docker-compose.yml`: local PostgreSQL service
- `.env.example`: shared environment variable template for the whole app

## Prerequisites

You need these tools installed before running the app locally:

- Git
- Python 3.11 or newer
- Node.js 20 or newer
- npm
- Docker Desktop

To verify your local setup, run:

```bash
python3 --version
node --version
npm --version
docker --version
docker compose version
```

## Installing prerequisites

### Docker Desktop

This project uses Docker to run PostgreSQL locally.

If you do not already have Docker Desktop:

1. Download Docker Desktop for your operating system from Docker's official website.
2. Install it.
3. Open Docker Desktop and wait until it shows that Docker is running.

After installation, confirm it works:

```bash
docker --version
docker compose version
```

### Python

If `python3 --version` does not work, install Python 3 from the official Python website or through your system package manager.

### Node.js

If `node --version` does not work, install Node.js 20 or newer from the official Node.js website.

## Local setup

### 1. Clone the repository

```bash
git clone https://github.com/KshitijDani/IMT559-Agent.git
cd IMT559-Agent
```

### 2. Create the root environment file

Copy the example env file:

```bash
cp .env.example .env
```

Important variables in `.env`:

- `DATABASE_URL`: PostgreSQL connection string used by the backend
- `JWT_SECRET`: secret used to sign auth cookies
- `ALLOW_DEV_AUTH`: when `true`, the frontend and backend both allow the shared dev-user login flow
- `GOOGLE_CLIENT_ID`: required only if you want real Google Sign-In
- `DEV_USER_EMAIL` and `DEV_USER_NAME`: used when dev auth is enabled

For local development, the easiest option is:

```env
ALLOW_DEV_AUTH=true
GOOGLE_CLIENT_ID=
```

Set a real JWT secret before sharing the app publicly.

### 3. Start PostgreSQL with Docker

From the repo root:

```bash
docker compose up -d
```

This starts PostgreSQL on `localhost:5432`.

To confirm the container is running:

```bash
docker compose ps
```

To stop the database later:

```bash
docker compose down
```

### 4. Set up the backend Python environment

From the repo root:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

This creates an isolated Python environment for the backend and installs FastAPI, SQLAlchemy, PostgreSQL drivers, and test dependencies.

### 5. Install frontend dependencies

In a new terminal, or after finishing backend setup:

```bash
cd frontend
npm install
```

### 6. Build the frontend

The backend serves the built frontend files from `frontend/dist`, so build the frontend before starting the app:

```bash
cd frontend
npm run build
```

You must rebuild the frontend after any frontend code changes.

### 7. Start the backend server

From the repo root:

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Once started, open:

- [http://localhost:8000](http://localhost:8000)

The backend serves both:

- the frontend UI at `http://localhost:8000`
- the API at `http://localhost:8000/api/*`

Examples:

- `http://localhost:8000/`
- `http://localhost:8000/dashboard`
- `http://localhost:8000/health`

## Auth modes

### Local development mode

If `.env` contains:

```env
ALLOW_DEV_AUTH=true
```

the app will let you enter as the configured dev user instead of requiring Google Sign-In.

The dev user details come from:

- `DEV_USER_EMAIL`
- `DEV_USER_NAME`

### Google Sign-In mode

If you want to use real Google auth:

1. Set `ALLOW_DEV_AUTH=false`
2. Set `GOOGLE_CLIENT_ID` in `.env`
3. Rebuild the frontend:

```bash
cd frontend
npm run build
```

4. Restart the backend

## Running tests

Backend tests:

```bash
cd backend
source .venv/bin/activate
pytest
```

The backend tests use an isolated in-memory SQLite database, so they do not require the Docker PostgreSQL instance.

## Common issues

### `docker: command not found`

Docker Desktop is not installed or not running yet.

### `Connection refused` on port `5432`

PostgreSQL is not running. Start it with:

```bash
docker compose up -d
```

### `ModuleNotFoundError` or missing Python packages

Make sure you created and activated the backend virtual environment:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Frontend changes are not showing up

Rebuild the frontend:

```bash
cd frontend
npm run build
```

Then restart the backend.

### Google login is not showing

Check:

- `ALLOW_DEV_AUTH=false`
- `GOOGLE_CLIENT_ID` is set in `.env`
- you rebuilt the frontend after changing `.env`

## Development workflow summary

From a fresh clone, the usual order is:

1. `cp .env.example .env`
2. `docker compose up -d`
3. `cd backend && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
4. `cd frontend && npm install && npm run build`
5. `cd backend && source .venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000`

Then open [http://localhost:8000](http://localhost:8000).
