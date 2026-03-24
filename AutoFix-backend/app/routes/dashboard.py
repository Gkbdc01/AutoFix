"""Routes for error history, statistics, and configuration."""

import logging
from fastapi import APIRouter
from app.models.schemas import ErrorStats
from app.services import error_history
from app.services import config_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/history")
async def get_history(limit: int = 50):
    """Get recent error history."""
    entries = error_history.get_history(limit)
    return {
        "count": len(entries),
        "errors": [
            {
                "timestamp": e.timestamp.isoformat(),
                "filePath": e.filePath,
                "language": e.language,
                "line": e.line,
                "message": e.message,
                "errorType": e.errorType,
                "severity": e.severity,
                "fixed": e.fixed,
            }
            for e in entries
        ],
    }


@router.get("/stats", response_model=ErrorStats)
async def get_stats():
    """Get error statistics."""
    return error_history.get_stats()


@router.post("/history/clear")
async def clear_history():
    """Clear all error history."""
    error_history.clear_history()
    return {"status": "cleared"}


@router.get("/config")
async def get_config():
    """Get the current configuration."""
    return config_service.get_config()


@router.post("/config/reload")
async def reload_config():
    """Reload configuration from disk."""
    config_service.reload_config()
    return {"status": "reloaded", "config": config_service.get_config()}
