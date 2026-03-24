"""POST /fix — asks the LLM to fix the identified error."""

import logging
from fastapi import APIRouter
from app.models.schemas import FixRequest, FixResponse
from app.services import llm_service
from app.services import error_history

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/fix", response_model=FixResponse)
async def fix_code(req: FixRequest):
    """Accept code + error info and return the corrected code with diff."""
    logger.info("Received /fix request — language=%s, line=%s", req.language, req.line)
    result = await llm_service.fix_code(
        language=req.language,
        code=req.code,
        line=req.line,
        message=req.message,
    )
    
    # Generate diff if fix was successful
    if result.get("fixed") and result.get("fixedCode"):
        diff = llm_service.generate_diff(req.code, result["fixedCode"])
        result["diff"] = diff
        
        # Mark error as fixed in history
        error_history.add_error(
            file_path=req.filePath or "unknown",
            language=req.language,
            error={
                "line": req.line,
                "message": req.message,
                "errorType": "general",
                "severity": "error",
            },
            fixed=True,
        )
    
    return result