"""Route: POST /analyze — receives code from the VS Code extension."""

import logging

from fastapi import APIRouter, HTTPException

from app.models.schemas import AnalyzeRequest, AnalyzeResponse
from app.services import llm_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(payload: AnalyzeRequest) -> AnalyzeResponse:
    """Analyse source code for errors using an LLM.

    Receives the full file content + language from the VS Code extension,
    forwards it to the OpenAI-backed LLM service, and returns a structured
    error report.
    """
    logger.info(
        "Received /analyze request — language=%s, code_length=%d",
        payload.language,
        len(payload.code),
    )

    if not payload.code.strip():
        return AnalyzeResponse(hasError=False)

    try:
        result = await llm_service.analyze_code(
            language=payload.language,
            code=payload.code,
        )
        return AnalyzeResponse(**result)

    except Exception as exc:  # noqa: BLE001
        logger.exception("Unexpected error in /analyze: %s", exc)
        raise HTTPException(status_code=500, detail="Internal analysis error.") from exc
