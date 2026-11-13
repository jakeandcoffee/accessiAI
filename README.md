# AccessiAI

AI-Powered Accessibility Audit Platform. Scan websites for accessibility issues and get AI-driven remediation suggestions.

## Tech Stack

- **Frontend:** React 19, TypeScript, Vite, Tailwind CSS, React Query
- **Backend:** FastAPI, SQLAlchemy (async), Strawberry GraphQL, Playwright
- **Database:** PostgreSQL 16
- **AI:** Anthropic Claude API

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose
- (Optional) An [Anthropic API key](https://console.anthropic.com/) for AI-powered features

## Quick Start (Docker Compose)

```bash
# Clone the repo
git clone <repo-url> && cd AccessiAI

# Set your Anthropic API key (optional)
export ANTHROPIC_API_KEY=your-key-here

# Start all services
docker compose up --build
```

## install docker if you have it
brew install --cask docker
```

## once you installed the docker, open the docker desktop with
open -a Docker
```

Once running:

| Service  | URL                      |
|----------|--------------------------|
| Frontend | http://localhost:5173     |
| Backend  | http://localhost:8000     |
| API Docs | http://localhost:8000/docs|
| GraphQL  | http://localhost:8000/graphql |
| Postgres | localhost:5432            |

To stop everything:

```bash
docker compose down
```

To stop and remove stored data:

```bash
docker compose down -v
```

## Manual Setup

If you prefer running each service individually:

### 1. Database

Start only Postgres via Docker:

```bash
docker compose up db
```

Or use a local PostgreSQL instance and create a database named `accessiai`.

### 2. Backend

```bash
cd backend

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browser for scanning
playwright install chromium

# Set environment variables
export DATABASE_URL=postgresql+asyncpg://accessiai:accessiai_dev@localhost:5432/accessiai
export JWT_SECRET_KEY=dev-secret-key-change-in-production
export ANTHROPIC_API_KEY=your-key-here  # optional
export FRONTEND_URL=http://localhost:5173

# Run database migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start the dev server
npm run dev
```

The frontend will be available at http://localhost:5173.

## Environment Variables

| Variable            | Description                          | Default                     |
|---------------------|--------------------------------------|-----------------------------|
| `DATABASE_URL`      | PostgreSQL connection string         | (set by Docker Compose)     |
| `JWT_SECRET_KEY`    | Secret for JWT token signing         | (set by Docker Compose)     |
| `ANTHROPIC_API_KEY` | Anthropic API key for AI features    | —                           |
| `FRONTEND_URL`      | Frontend origin for CORS             | `http://localhost:5173`     |
| `ENVIRONMENT`       | `development` or `production`        | `development`               |
| `VITE_API_URL`      | Backend URL used by the frontend     | `http://localhost:8000`     |

## Sharing for External Testing

You can share the app with testers via a public URL tunnel — no deployment needed. The app runs on your machine and the tunnel forwards traffic.

### Option 1: Cloudflare Tunnel (Recommended)

No account required. Fast and reliable.

```bash
# Install cloudflared
brew install cloudflared

# Build the frontend for production (served from the backend on one port)
docker compose exec -e VITE_API_URL= frontend npm run build

# Copy the build into the backend container
docker cp frontend/dist/. $(docker compose ps -q backend):/app/frontend_dist/

# Start the tunnel
cloudflared tunnel --url http://localhost:8000
```

Cloudflare prints a public URL like `https://random-words.trycloudflare.com` — send that to your tester. They can register an account and use the full app.

To stop: `pkill cloudflared`

### Option 2: ngrok

Requires a free account at [ngrok.com](https://dashboard.ngrok.com/signup).

```bash
# Install ngrok
brew install ngrok

# Authenticate (one-time — get your token from https://dashboard.ngrok.com/get-started/your-authtoken)
ngrok config add-authtoken YOUR_TOKEN

# Build and copy frontend (same as above)
docker compose exec -e VITE_API_URL= frontend npm run build
docker cp frontend/dist/. $(docker compose ps -q backend):/app/frontend_dist/

# Start the tunnel
ngrok http 8000
```

ngrok prints a public URL like `https://xxxx.ngrok-free.app` — send that to your tester.

To stop: `Ctrl+C` or `pkill ngrok`

### Notes

- Your machine must stay on and Docker running while testers use the link
- The tunnel URL changes each time you restart it (free tier)
- Testers register their own account on the login page
- Scans run on your local machine so performance depends on your connection

## Project Structure

```
AccessiAI/
├── backend/
│   ├── app/
│   │   ├── api/          # REST API routes
│   │   ├── core/         # Config, security
│   │   ├── database/     # DB connection, base model
│   │   ├── graphql/      # GraphQL schema & queries
│   │   ├── models/       # SQLAlchemy models
│   │   ├── scanner/      # Accessibility scanning logic
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic
│   │   └── main.py       # FastAPI app entry point
│   ├── migrations/       # Alembic migrations
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   ├── package.json
│   └── vite.config.ts
├── docker-compose.yml
└── README.md
```
