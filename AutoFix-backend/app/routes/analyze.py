"""Route: POST /analyze — receives code from the VS Code extension."""

import logging

from fastapi import APIRouter, HTTPException

from app.models.schemas import AnalyzeRequest, AnalyzeResponse, CodeError
from app.services import llm_service
from app.services import error_history
from app.services import config_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(payload: AnalyzeRequest) -> AnalyzeResponse:
    """Analyse source code for multiple errors using an LLM.

    Receives the full file content + language from the VS Code extension,
    forwards it to the OpenAI-backed LLM service, and returns a structured
    error report containing up to 5 errors.
    """
    logger.info(
        "Received /analyze request — language=%s, code_length=%d",
        payload.language,
        len(payload.code),
    )

    if not payload.code.strip():
        return AnalyzeResponse(hasError=False, errors=[])

    try:
        result = await llm_service.analyze_code(
            language=payload.language,
            code=payload.code,
        )
        
        has_error = result.get("hasError", False)
        errors_data = result.get("errors", [])
        
        # Convert to CodeError objects and apply configuration
        code_errors = []
        for err_data in errors_data:
            error_obj = CodeError(
                line=err_data.get("line", 0),
                message=err_data.get("message", ""),
                errorType=err_data.get("errorType", "general"),
                severity=err_data.get("severity", "error"),
            )
            
            # Apply severity override from config
            config_severity = config_service.get_severity(error_obj.errorType)
            error_obj.severity = config_severity
            
            # Check if this error type is ignored
            if not config_service.is_rule_ignored(error_obj.errorType):
                code_errors.append(error_obj)
                # Track in history
                error_history.add_error(
                    file_path=payload.filePath or "unknown",
                    language=payload.language,
                    error=error_obj,
                )
        
        # Respect max errors config
        max_errors = config_service.get_max_errors()
        code_errors = code_errors[:max_errors]
        
        response = AnalyzeResponse(
            hasError=len(code_errors) > 0,
            errors=code_errors,
            source=result.get("source", "llm"),
        )
        
        # For backward compatibility, set line/message to first error
        if code_errors:
            response.line = code_errors[0].line
            response.message = code_errors[0].message
        
        return response

    except Exception as exc:  # noqa: BLE001
        logger.exception("Unexpected error in /analyze: %s", exc)
        raise HTTPException(status_code=500, detail="Internal analysis error.") from exc
