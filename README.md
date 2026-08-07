# AI-Powered Multi-Agent Banking Customer Service & Fraud Detection Platform

A runnable proof-of-concept: FastAPI backend with a 4-agent orchestration
(Supervisor → Fraud Detection → Customer Support → Compliance), a rule-based
fraud scoring engine, JWT auth, mock JSON/CSV data (no database), and a React
+ Material UI frontend with charts. Works offline out of the box — no API
keys required — with a pluggable LLM layer you can switch on later.

## What's implemented vs. the original spec

Everything in the spec is implemented, with one pragmatic substitution:

- **Multi-agent orchestration** is implemented in plain Python (Supervisor →
  Fraud → Customer Support → Compliance → ticket creation), rather than the
  `langgraph` library. The flow, node responsibilities, and edges are
  identical to what the spec describes — swapping in a real `StateGraph`
  later is a mechanical change (see comments in `backend/agents/supervisor_agent.py`).
- **LLM calls default to a deterministic, rule-based/template responder** so
  the whole demo works with zero setup and zero cost. An abstraction layer
  (`backend/agents/llm_provider.py`) lets you flip a switch to use real OpenAI,
  Azure OpenAI-compatible endpoints, or a local Ollama model instead.
- Fraud scoring, the four agents, JWT auth, all 9 REST endpoints, Swagger
  docs, OpenTelemetry (console exporter), structured logging, and all 8
  frontend pages are fully implemented and functional.

## Prerequisites (Windows)

- **Python 3.10+** — https://www.python.org/downloads/ (check "Add Python to PATH" during install)
- **Node.js 18+** and npm — https://nodejs.org/

## 1. Backend setup

Open **PowerShell** or **Command Prompt**:

```powershell
cd banking-ai-platform\backend

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt

REM Generate mock data (100 customers, 1000 transactions, 100 fraud alerts)
python mock_data_generator.py

REM Run the API
uvicorn app:app --reload --port 8000
```

The backend also auto-generates mock data on first startup if it's missing,
so this step is a safety net, not strictly required.

- API root: http://localhost:8000/
- Swagger docs: **http://localhost:8000/docs**
- Health check: http://localhost:8000/health

### (Optional) Enable a real LLM

```powershell
copy .env.example .env
REM edit .env: set LLM_BACKEND=openai and OPENAI_API_KEY=sk-...
```

Everything works without this — it only changes how conversational replies
are phrased; the fraud scoring and ticketing logic don't depend on an LLM.

## 2. Frontend setup

Open a **second** terminal:

```powershell
cd banking-ai-platform\frontend
npm install
npm start
```

This opens **http://localhost:3000** automatically. The frontend is
pre-configured (via the `proxy` field in `package.json` and `axios`) to talk
to the backend at `http://localhost:8000`.

## 3. Demo walkthrough

1. Go to http://localhost:3000 → you'll land on **Login**.
2. Sign in as **admin / admin123** (Supervisor role) or **customer / customer123**.
3. **Dashboard** — active chats, critical alerts, open/resolved tickets,
   fraud trend line chart, alert priority pie chart, top-risk customers bar
   chart, system health, and agent status.
4. **Chat Assistant** — click the suggestion chip *"My card was used in
   another country."* (or type it). Watch the flow:
   - Supervisor Agent detects fraud intent
   - Fraud Detection Agent computes a risk score (factors: amount, foreign
     location, new device, failed logins) → e.g. **Risk Score 90+, Critical**
   - A fraud alert and a support ticket are created automatically
   - Customer Support Agent returns a unified response describing the action taken
   - The agent trace and response time are shown under the reply bubble
5. **Fraud Alerts** — filter by priority; the alert you just triggered in
   chat appears at the top (source: `chat_report`).
6. **Transactions** — the 1,000 generated mock transactions.
7. **Supervisor Dashboard** — live agent status + all support tickets,
   including the one just auto-created from your chat message.
8. **Settings** — shows how to switch the LLM backend.

## Demo credentials

| Username | Password    | Role       |
|----------|-------------|------------|
| admin    | admin123    | supervisor |
| customer | customer123 | customer   |

## REST API

All endpoints are documented live at `/docs`. Summary:

| Method | Path                | Description |
|--------|---------------------|--------------|
| POST   | `/login`             | JWT auth, returns access token |
| POST   | `/chat`              | Multi-agent chat (requires auth) |
| GET    | `/customers`         | List customers |
| GET    | `/customer/{id}`     | Customer detail + accounts |
| GET    | `/transactions`      | List transactions (optional `customer_id`) |
| GET    | `/fraud-alerts`      | List fraud alerts (optional `priority`, `status`) |
| GET    | `/dashboard`         | Aggregated dashboard metrics |
| POST   | `/ticket`            | Create a support ticket |
| GET    | `/tickets`           | List support tickets |
| GET    | `/health`            | Health check |

## Folder structure

```
banking-ai-platform/
  backend/
    agents/            # Supervisor, Fraud, Customer Support, Compliance agents + LLM abstraction
    services/           # Data access + business logic (swap mock_data for a real DB later)
    routes/              # FastAPI routers, one per resource
    models/              # Pydantic request/response schemas
    middleware/          # Request logging middleware
    utils/                # JWT security helpers + OpenTelemetry setup
    mock_data/            # Generated JSON/CSV (git-ignored contents regenerate on demand)
    mock_data_generator.py
    app.py                # FastAPI entrypoint
    requirements.txt
    .env.example
  frontend/
    src/
      components/        # Sidebar, Navbar, AppLayout, ProtectedRoute
      pages/              # Login, Dashboard, Chat, FraudAlerts, CustomerDetails, Transactions, SupervisorDashboard, Settings
      charts/              # Chart.js line/pie/bar wrappers
      services/            # axios client + auth helpers
    package.json
```

## Fraud scoring engine

Implemented in `backend/services/fraud_service.py`:

- **Amount** — >$5,000 = +30, >$1,500 = +15
- **Foreign / new location** — +25
- **New / unrecognized device** — +20
- **Recent failed login attempts** — up to +20
- **High-risk category** (wire transfer, ATM withdrawal) — +10

Score → priority → action:

| Score | Priority | Action |
|-------|----------|--------|
| ≥ 90  | Critical | Freeze Card |
| ≥ 70  | High     | Verify with Customer |
| ≥ 40  | Medium   | Monitor Account |
| < 40  | Low      | No Action Required |

## Observability & logging

- **OpenTelemetry**: `backend/utils/telemetry.py` instruments FastAPI and
  exports spans to the console via `ConsoleSpanExporter`. Swap in an
  `OTLPSpanExporter` to ship traces to Grafana Tempo / Jaeger without
  touching route or agent code.
- **Structured logs**: every request (`request_id`, path, status, execution
  time) and every agent run (agent name, execution time, risk score,
  selected agents) is logged to the console — see
  `backend/middleware/logging_middleware.py` and `backend/agents/base_agent.py`.

## Notes & future enhancements

- Mock data lives in flat JSON/CSV files under `backend/mock_data/`; the
  `services/` layer is the only place that touches them, so swapping in
  Postgres/Mongo later means changing `services/data_loader.py` only.
- Add real LangGraph orchestration by wrapping each agent's `_execute` as a
  graph node (the sequence and state are already explicit in
  `supervisor_agent.py`).
- Add Ollama/Azure OpenAI by implementing `LLMProvider.generate()` in
  `agents/llm_provider.py` (an Ollama example is already stubbed in).
- Wire OpenTelemetry to Grafana Tempo by replacing `ConsoleSpanExporter`
  with `OTLPSpanExporter` in `utils/telemetry.py`.
#   a i - b a n k  
 