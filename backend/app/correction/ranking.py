"""Candidate ranking engine for sorting and selecting best correction proposals."""

from backend.app.correction.models import CorrectionCandidate, ValidationStatus


class CandidateRanker:
    """Ranks correction candidates using deterministic heuristic criteria."""

    @staticmethod
    def calculate_score(candidate: CorrectionCandidate, original_error_count: int) -> float:
        score = 0.0

        # 1. Validation status weight (0 - 50 points)
        if candidate.validation_status == ValidationStatus.SYNTAX_VALIDATED:
            score += 50.0
            if candidate.remaining_error_count == 0:
                score += 20.0  # Perfect complete fix bonus
        elif candidate.validation_status == ValidationStatus.PROPOSED:
            score += 10.0
        elif candidate.validation_status == ValidationStatus.UNVERIFIED:
            score += 5.0
        else:
            # Rejected statuses
            score -= 100.0

        # 2. Error reduction weight (0 - 20 points)
        if candidate.remaining_error_count is not None:
            resolved = original_error_count - candidate.remaining_error_count
            if resolved > 0:
                score += min(resolved * 10.0, 20.0)

        # 3. Minimal change footprint penalty (fewer chars edited = higher score)
        char_change_count = 0
        for op in candidate.edit_operations:
            deleted_len = op.end_offset - op.start_offset
            inserted_len = len(op.replacement)
            char_change_count += deleted_len + inserted_len

        # Small penalty for large change footprints
        score -= min(char_change_count * 0.1, 10.0)

        # 4. Penalty for warnings
        score -= len(candidate.warnings) * 5.0

        return score

    @classmethod
    def rank_candidates(
        cls,
        candidates: list[CorrectionCandidate],
        original_error_count: int,
    ) -> list[CorrectionCandidate]:
        """Calculates ranking scores and returns candidates sorted in descending order of score."""
        for cand in candidates:
            cand.ranking_score = cls.calculate_score(cand, original_error_count)

        # Sort: highest score first
        return sorted(candidates, key=lambda c: c.ranking_score or -999.0, reverse=True)
