"""Pydantic models for request/response validation."""

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class CodeError(BaseModel):
    """A single error found in code."""
    line: int = Field(..., description="1-based line number of the error")
    message: str = Field(..., description="Human-readable error description")
    severity: str = Field(default="error", description="'error', 'warning', or 'info'")
    errorType: str = Field(default="general", description="Type: 'syntax', 'logic', 'performance', 'security'")


class AnalyzeRequest(BaseModel):
    """Schema for the code analysis request sent by the VS Code extension."""

    language: str = Field(
        ...,
        description="The VS Code languageId of the file (e.g. 'python', 'javascript').",
        examples=["python", "javascript", "typescript"],
    )
    code: str = Field(
        ...,
        description="The full source code content of the saved file.",
    )
    filePath: Optional[str] = Field(
        default=None,
        description="Optional file path for tracking/history purposes.",
    )


class AnalyzeResponse(BaseModel):
    """Schema for the code analysis response returned to the extension.
    
    Now supports multiple errors instead of just one.
    """

    hasError: bool = Field(
        ...,
        description="Whether the LLM detected any errors in the code.",
    )
    errors: List[CodeError] = Field(
        default_factory=list,
        description="List of all detected errors, sorted by line number.",
    )
    source: Optional[str] = Field(
        default=None,
        description="Where the result came from: 'llm', 'fallback', 'cache', 'error'.",
    )
    # Backward compatibility for old single-error clients
    line: Optional[int] = Field(default=None, description="DEPRECATED: use errors[0].line")
    message: Optional[str] = Field(default=None, description="DEPRECATED: use errors[0].message")

    
class FixRequest(BaseModel):
    language: str
    code: str
    line: int
    message: str
    filePath: Optional[str] = Field(default=None, description="Optional file path for tracking")


class FixResponse(BaseModel):
    fixed: bool
    fixedCode: Optional[str] = None
    explanation: Optional[str] = None
    source: Optional[str] = None
    diff: Optional[str] = Field(default=None, description="Unified diff format showing changes")


class ErrorHistoryEntry(BaseModel):
    """A record of an error detected in the error history."""
    timestamp: datetime
    filePath: str
    language: str
    line: int
    message: str
    errorType: str
    severity: str
    fixed: bool = Field(default=False, description="Whether the user applied a fix")


class ErrorStats(BaseModel):
    """Statistics about detected errors."""
    totalErrors: int = Field(default=0, description="Total errors detected in this session")
    errorsByType: dict = Field(default_factory=dict, description="Count by error type")
    errorsBySeverity: dict = Field(default_factory=dict, description="Count by severity")
    mostCommonFile: Optional[str] = Field(default=None, description="File with most errors")
    recentErrors: List[ErrorHistoryEntry] = Field(default_factory=list, description="Last 10 errors")
