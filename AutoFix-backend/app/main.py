"""AutoFix Backend — FastAPI application entry point."""

import logging

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.analyze import router as analyze_router
from app.routes.fix import router as fix_router

# Load environment variables from .env file (OPENAI_API_KEY, etc.)
# override=True ensures .env values always take precedence over stale env vars
load_dotenv(override=True)

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)

# FastAPI app
app = FastAPI(
    title="AutoFix Backend",
    description="AI-powered code error analysis service for the AutoFix VS Code extension.",
    version="0.1.0",
)

# CORS — the VS Code extension (Electron) makes requests from localhost.
# Allow all origins during development; tighten for production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(analyze_router)
app.include_router(fix_router)

# Health check
@app.get("/health")
async def health():
    """Simple health-check endpoint."""
    return {"status": "ok"}
