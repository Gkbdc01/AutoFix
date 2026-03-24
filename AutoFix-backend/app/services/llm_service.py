"""LLM service — sends code to OpenAI/Azure for error analysis."""

import json
import logging
import os
import difflib
from typing import Any, Dict

from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# System prompt that instructs the model how to analyse code
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """\
You are an expert code reviewer and debugger.
You will receive source code along with its programming language.

Your task:
1. Analyse the code carefully for bugs, syntax errors, type errors, \
logical mistakes, or any other issues.
2. Identify UP TO 5 most critical errors (if any).
3. Return your answer as a JSON object with exactly these fields:

   • "hasError"     (boolean) – true if you found any errors, false otherwise.
   • "errors"       (array)   – list of error objects. Each has:
     - "line"       (integer) – 1-based line number
     - "message"    (string)  – concise description
     - "errorType"  (string)  – one of: 'syntax', 'logic', 'performance', 'security', 'general'
     - "severity"   (string)  – one of: 'error', 'warning', 'info'

Rules:
- Only flag genuine errors — do NOT flag style preferences, missing comments, or minor naming conventions.
- Sort errors by line number (ascending).
- If the code is correct, return {"hasError": false, "errors": []}.
- Always return valid JSON and nothing else.
"""


def _build_user_message(language: str, code: str) -> str:
    """Build the user message containing the code to analyse."""
    return (
        f"Language: {language}\n"
        f"```{language}\n"
        f"{code}\n"
        f"```"
    )


async def analyze_code(language: str, code: str) -> Dict[str, any]:
    """Send code to Azure AI Foundry and return a structured error analysis with multiple errors."""
    api_key = os.getenv("OPENAI_API_KEY", "").strip().strip('"')
    if not api_key:
        logger.error("OPENAI_API_KEY is not set — returning no-error fallback.")
        return {"hasError": False, "errors": [], "source": "fallback"}

    model = os.getenv("OPENAI_MODEL", "gpt-5-nano").strip().strip('"')
    base_url = os.getenv("AZURE_BASE_URL", "").strip().strip('"')

    if not base_url:
        logger.error("AZURE_BASE_URL is not set — returning no-error fallback.")
        return {"hasError": False, "errors": [], "source": "fallback"}

    logger.info("Using AsyncOpenAI with base_url=%s, model=%s", base_url, model)

    client = AsyncOpenAI(
        base_url=base_url,
        api_key=api_key,
    )

    try:
        response = await client.chat.completions.create(
            model=model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": _build_user_message(language, code)},
            ],
        )

        content = response.choices[0].message.content
        logger.info("Raw LLM response: %s", content[:300])
        result = json.loads(content)

        has_error = bool(result.get("hasError", False))
        errors = result.get("errors", []) if has_error else []
        
        # Validate and normalize error objects
        normalized_errors = []
        for err in errors:
            if isinstance(err, dict) and "line" in err and "message" in err:
                normalized_errors.append({
                    "line": int(err["line"]),
                    "message": str(err["message"]),
                    "errorType": str(err.get("errorType", "general")),
                    "severity": str(err.get("severity", "error")),
                })
        
        return {
            "hasError": has_error,
            "errors": normalized_errors,
            "source": "llm",
        }

    except json.JSONDecodeError as exc:
        logger.exception("Failed to parse LLM JSON response: %s", exc)
        return {"hasError": False, "errors": [], "source": "error"}

    except Exception as exc:
        logger.exception("OpenAI API call failed: %s", exc)
        return {"hasError": False, "errors": [], "source": "error"}

FIX_SYSTEM_PROMPT = """\
You are an expert code fixer.
You will receive source code, the programming language, and a specific error \
(with line number and description).

Your task:
1. Fix ONLY the identified error — do not refactor or change anything else.
2. Return your answer as a JSON object with exactly these fields:

   • "fixed"       (boolean) – true if you were able to fix the error.
   • "fixedCode"   (string)  – the entire corrected source code.
   • "explanation"  (string)  – a brief explanation of what you changed.

Rules:
- Preserve all original formatting, comments, and structure.
- Only fix the specific error mentioned — nothing else.
- Return the COMPLETE file content in fixedCode, not just the changed line.
- Always return valid JSON and nothing else.
"""


def _build_fix_message(language: str, code: str, line: int, message: str) -> str:
    """Build the user message for a fix request."""
    return (
        f"Language: {language}\n"
        f"Error on line {line}: {message}\n"
        f"```{language}\n"
        f"{code}\n"
        f"```"
    )


async def fix_code(language: str, code: str, line: int, message: str) -> Dict[str, Any]:
    """Send code + error to LLM and return the fixed version."""
    api_key = os.getenv("OPENAI_API_KEY", "").strip().strip('"')
    if not api_key:
        return {"fixed": False, "source": "fallback", "explanation": "API key not configured."}

    model = os.getenv("OPENAI_MODEL", "gpt-5-nano").strip().strip('"')
    base_url = os.getenv("AZURE_BASE_URL", "").strip().strip('"')

    if not base_url:
        return {"fixed": False, "source": "fallback", "explanation": "AZURE_BASE_URL not configured."}

    client = AsyncOpenAI(base_url=base_url, api_key=api_key)

    try:
        response = await client.chat.completions.create(
            model=model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": FIX_SYSTEM_PROMPT},
                {"role": "user", "content": _build_fix_message(language, code, line, message)},
            ],
        )

        content = response.choices[0].message.content
        logger.info("Raw LLM fix response: %s", content[:200])
        result = json.loads(content)

        return {
            "fixed": bool(result.get("fixed", False)),
            "fixedCode": result.get("fixedCode"),
            "explanation": result.get("explanation"),
            "source": "llm",
        }

    except Exception as exc:
        logger.exception("Fix API call failed: %s", exc)
        return {"fixed": False, "source": "error", "explanation": f"LLM call failed: {exc}"}


def generate_diff(original_code: str, fixed_code: str) -> str:
    """Generate a unified diff between original and fixed code."""
    original_lines = original_code.splitlines(keepends=True)
    fixed_lines = fixed_code.splitlines(keepends=True)
    
    diff_lines = difflib.unified_diff(
        original_lines,
        fixed_lines,
        fromfile="original.txt",
        tofile="fixed.txt",
        lineterm="",
    )
    
    return "\n".join(diff_lines)