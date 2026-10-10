"""Gemini API Correction Agent using structured prompting."""

import json
import logging
import uuid
from typing import Optional
from backend.app.compiler.diagnostics import Diagnostic
from backend.app.correction.models import (
    CorrectionCandidate,
    EditOperation,
    EditType,
    ValidationStatus,
)
from backend.app.agents.base import BaseCorrectionAgent
from backend.app.agents.prompts import SYSTEM_CORRECTION_PROMPT, format_correction_user_prompt
from backend.app.config import settings

logger = logging.getLogger(__name__)


class GeminiCorrectionAgent(BaseCorrectionAgent):
    """
    Direct Gemini integration for C syntax error corrections.
    Sends compiler diagnostics + source context and parses structured JSON proposals.
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None) -> None:
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model_name = model or settings.GEMINI_MODEL

    def propose_corrections(
        self,
        source_code: str,
        diagnostics: list[Diagnostic],
    ) -> list[CorrectionCandidate]:
        if not self.api_key:
            logger.warning("Gemini API key is not configured.")
            return []

        # Summarize diagnostics for context
        diag_lines = [
            f"- [{d.code}] Line {d.line}, Col {d.column}: {d.message} (Excerpt: {d.excerpt!r})"
            for d in diagnostics
        ]
        diag_summary = "\n".join(diag_lines)
        user_prompt = format_correction_user_prompt(source_code, diag_summary)

        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=self.api_key)
            response = client.models.generate_content(
                model=self.model_name,
                contents=[
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_text(text=SYSTEM_CORRECTION_PROMPT),
                            types.Part.from_text(text=user_prompt),
                        ],
                    )
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.1,
                ),
            )

            raw_text = response.text or ""
            return self._parse_json_response(raw_text)

        except Exception as e:
            logger.error(f"Gemini API request failed: {e}")
            return []

    def _parse_json_response(self, text: str) -> list[CorrectionCandidate]:
        candidates: list[CorrectionCandidate] = []
        try:
            # Clean possible markdown wrapping if any
            clean_text = text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.startswith("```"):
                clean_text = clean_text[3:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]
            clean_text = clean_text.strip()

            data = json.loads(clean_text)
            cands_list = data.get("candidates", [])

            for item in cands_list:
                cand_id = f"cand_gemini_{uuid.uuid4().hex[:8]}"
                edit_ops: list[EditOperation] = []

                for op_data in item.get("edit_operations", []):
                    edit_ops.append(EditOperation.from_dict(op_data))

                candidates.append(
                    CorrectionCandidate(
                        candidate_id=cand_id,
                        summary=item.get("summary", "Syntax error correction"),
                        explanation=item.get("explanation", ""),
                        edit_operations=edit_ops,
                        validation_status=ValidationStatus.PROPOSED,
                        related_diagnostics=item.get("related_diagnostics", []),
                        confidence=float(item.get("confidence", 0.8)),
                    )
                )

        except Exception as e:
            logger.error(f"Failed to parse model JSON output: {e}")

        return candidates
