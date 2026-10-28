"""CrewAI Agent integration for C syntax error correction."""

import json
import logging
import uuid
from typing import Optional
from backend.app.compiler.diagnostics import Diagnostic
from backend.app.correction.models import (
    CorrectionCandidate,
    EditOperation,
    ValidationStatus,
)
from backend.app.agents.base import BaseCorrectionAgent
from backend.app.agents.prompts import SYSTEM_CORRECTION_PROMPT, format_correction_user_prompt
from backend.app.config import settings

logger = logging.getLogger(__name__)


class CrewAICorrectionAgent(BaseCorrectionAgent):
    """
    CrewAI single-agent workflow for C syntax error correction.
    Uses CrewAI Agent + Task + LLM configuration.
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None) -> None:
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model_name = model or settings.GEMINI_MODEL

    def propose_corrections(
        self,
        source_code: str,
        diagnostics: list[Diagnostic],
    ) -> list[CorrectionCandidate]:
        if not self.api_key or not settings.AI_ENABLED:
            logger.info("CrewAI/Gemini is disabled or API key is not configured.")
            return []

        diag_lines = [
            f"- [{d.code}] Line {d.line}, Col {d.column}: {d.message} (Excerpt: {d.excerpt!r})"
            for d in diagnostics
        ]
        diag_summary = "\n".join(diag_lines)
        user_prompt = format_correction_user_prompt(source_code, diag_summary)

        try:
            from crewai import Agent, Task, Crew, LLM

            llm = LLM(
                model=f"gemini/{self.model_name}",
                api_key=self.api_key,
                temperature=0.1,
            )

            agent = Agent(
                role="C Syntax Correction Specialist",
                goal="Propose minimal, context-aware syntax corrections using the supplied source and compiler diagnostics.",
                backstory=(
                    "You are an expert compiler engineer and C syntax repair specialist. "
                    "You analyze deterministic compiler diagnostics, locate the exact syntax fault, "
                    "and propose the smallest necessary edit operations formatted strictly as JSON."
                ),
                llm=llm,
                verbose=False,
            )

            task = Task(
                description=f"{SYSTEM_CORRECTION_PROMPT}\n\n{user_prompt}",
                expected_output="Valid JSON matching the correction candidate schema.",
                agent=agent,
            )

            crew = Crew(
                agents=[agent],
                tasks=[task],
                verbose=False,
            )

            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(crew.kickoff)
                result = future.result()

            raw_text = str(result.raw) if hasattr(result, "raw") else str(result)
            parsed = self._parse_json_response(raw_text)
            if parsed:
                return parsed
            raise ValueError("CrewAI did not return any valid candidate JSON")

        except Exception as e:
            logger.warning(f"CrewAI execution failed ({e}). Falling back to direct GeminiCorrectionAgent...")
            try:
                from backend.app.agents.gemini_agent import GeminiCorrectionAgent
                direct_agent = GeminiCorrectionAgent(api_key=self.api_key, model=self.model_name)
                return direct_agent.propose_corrections(source_code, diagnostics)
            except Exception as e2:
                logger.error(f"Fallback GeminiCorrectionAgent also failed: {e2}")
                return []


    def _parse_json_response(self, text: str) -> list[CorrectionCandidate]:
        candidates: list[CorrectionCandidate] = []
        try:
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
                cand_id = f"cand_crew_{uuid.uuid4().hex[:8]}"
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
                        confidence=float(item.get("confidence", 0.85)),
                    )
                )

        except Exception as e:
            logger.error(f"Failed to parse CrewAI JSON output: {e}")

        return candidates
