"""
Banking AI Platform — FastAPI entrypoint.

Run:
    uvicorn app:app --reload --port 8000

Swagger UI:
    http://localhost:8000/docs
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import auth, chat, customers, transactions, fraud, dashboard, tickets, health
from middleware.logging_middleware import RequestLoggingMiddleware
from utils.telemetry import setup_telemetry, logger

app = FastAPI(
    title="AI-Powered Multi-Agent Banking Customer Service & Fraud Detection Platform",
    description="Proof of concept — multi-agent banking assistant with fraud detection.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # demo only — restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(customers.router)
app.include_router(transactions.router)
app.include_router(fraud.router)
app.include_router(dashboard.router)
app.include_router(tickets.router)

try:
    setup_telemetry(app)
except Exception as e:
    logger.warning(f"OpenTelemetry setup skipped: {e}")


@app.on_event("startup")
def on_startup():
    import os
    mock_dir = os.path.join(os.path.dirname(__file__), "mock_data")
    if not os.path.exists(os.path.join(mock_dir, "customers.json")):
        logger.info("No mock data found — generating it now...")
        import mock_data_generator  # runs generation as a side effect of import
    logger.info("Banking AI Platform backend started.")


@app.get("/")
def root():
    return {
        "message": "Banking AI Platform API is running.",
        "docs": "/docs",
        "health": "/health",
    }
