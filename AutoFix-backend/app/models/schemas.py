"""Pydantic models for request/response validation."""

from typing import Optional
from pydantic import BaseModel, Field


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


class AnalyzeResponse(BaseModel):
    """Schema for the code analysis response returned to the extension.

    When hasError is False, `line` and `message` may be omitted.
    When hasError is True, both `line` and `message` must be present.
    """

    hasError: bool = Field(
        ...,
        description="Whether the LLM detected an error in the code.",
    )
    line: Optional[int] = Field(
        default=None,
        description="1-based line number where the error was found.",
    )
    message: Optional[str] = Field(
        default=None,
        description="Human-readable description of the error.",
    )
    source: Optional[str] = Field(
        default=None,
        description="Where the result came from: 'llm' = real analysis, 'fallback' = config issue, 'error' = LLM call failed.",
    )

    
class FixRequest(BaseModel):
    language: str
    code: str
    line: int
    message: str


class FixResponse(BaseModel):
    fixed: bool
    fixedCode: Optional[str] = None
    explanation: Optional[str] = None
    source: Optional[str] = None
