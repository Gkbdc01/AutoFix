"""POST /fix — asks the LLM to fix the identified error."""

import logging
from fastapi import APIRouter
from app.models.schemas import FixRequest, FixResponse
from app.services import llm_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/fix", response_model=FixResponse)
async def fix_code(req: FixRequest):
    """Accept code + error info and return the corrected code."""
    logger.info("Received /fix request — language=%s, line=%s", req.language, req.line)
    result = await llm_service.fix_code(
        language=req.language,
        code=req.code,
        line=req.line,
        message=req.message,
    )
    return result