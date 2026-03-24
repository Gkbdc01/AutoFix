"""Error history tracking — stores recent errors in memory."""

import logging
from datetime import datetime
from typing import List, Dict
from collections import defaultdict

from app.models.schemas import ErrorHistoryEntry, ErrorStats, CodeError

logger = logging.getLogger(__name__)

# In-memory store: max 100 most recent errors
MAX_HISTORY_SIZE = 100
_error_history: List[ErrorHistoryEntry] = []


def add_error(
    file_path: str,
    language: str,
    error: CodeError,
    fixed: bool = False,
) -> None:
    """Add an error to the history."""
    entry = ErrorHistoryEntry(
        timestamp=datetime.now(),
        filePath=file_path or "unknown",
        language=language,
        line=error.line,
        message=error.message,
        errorType=error.errorType,
        severity=error.severity,
        fixed=fixed,
    )
    _error_history.append(entry)
    
    # Keep only the last 100 errors
    if len(_error_history) > MAX_HISTORY_SIZE:
        _error_history.pop(0)
    
    logger.info("Error recorded: %s:%d - %s", file_path, error.line, error.message)


def get_history(limit: int = 50) -> List[ErrorHistoryEntry]:
    """Get the most recent errors (in reverse chronological order)."""
    return list(reversed(_error_history[-limit:]))


def get_stats() -> ErrorStats:
    """Generate statistics about recorded errors."""
    if not _error_history:
        return ErrorStats()
    
    error_by_type: Dict[str, int] = defaultdict(int)
    error_by_severity: Dict[str, int] = defaultdict(int)
    file_counts: Dict[str, int] = defaultdict(int)
    
    for entry in _error_history:
        error_by_type[entry.errorType] += 1
        error_by_severity[entry.severity] += 1
        file_counts[entry.filePath] += 1
    
    most_common_file = max(file_counts, key=file_counts.get) if file_counts else None
    
    return ErrorStats(
        totalErrors=len(_error_history),
        errorsByType=dict(error_by_type),
        errorsBySeverity=dict(error_by_severity),
        mostCommonFile=most_common_file,
        recentErrors=list(reversed(_error_history[-10:])),
    )


def clear_history() -> None:
    """Clear all stored history."""
    global _error_history
    _error_history = []
    logger.info("Error history cleared")
