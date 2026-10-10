"""Safe source code editing and candidate generation engine."""

from typing import Optional
from backend.app.correction.models import EditOperation, EditType


class EditApplicationError(Exception):
    """Raised when an edit operation cannot be safely applied."""
    pass


class SourceEditor:
    """Safely applies structured edit operations to source text."""

    @staticmethod
    def validate_edit(source: str, edit: EditOperation) -> tuple[bool, Optional[str]]:
        source_len = len(source)

        if edit.start_offset < 0 or edit.end_offset < 0:
            return False, f"Negative offsets ({edit.start_offset}, {edit.end_offset}) are invalid."

        if edit.start_offset > source_len or edit.end_offset > source_len:
            return False, f"Offsets ({edit.start_offset}, {edit.end_offset}) exceed source length ({source_len})."

        if edit.start_offset > edit.end_offset:
            return False, f"start_offset ({edit.start_offset}) cannot be greater than end_offset ({edit.end_offset})."

        if edit.operation == EditType.INSERT and edit.start_offset != edit.end_offset:
            return False, f"Insert operation requires start_offset == end_offset, got ({edit.start_offset}, {edit.end_offset})."

        if edit.expected_text is not None:
            actual_text = source[edit.start_offset : edit.end_offset]
            if actual_text != edit.expected_text:
                return False, f"Expected text {edit.expected_text!r} did not match actual text {actual_text!r} at offsets ({edit.start_offset}, {edit.end_offset})."

        return True, None

    @classmethod
    def apply_edits(cls, source: str, edits: list[EditOperation]) -> tuple[bool, str, list[str]]:
        """
        Applies a list of non-overlapping edits to the source code.
        Returns: (success, corrected_source, error_messages)
        """
        if not edits:
            return True, source, []

        # Validate all edits individually
        errors: list[str] = []
        for i, edit in enumerate(edits):
            is_valid, err = cls.validate_edit(source, edit)
            if not is_valid and err:
                errors.append(f"Edit #{i + 1}: {err}")

        if errors:
            return False, source, errors

        # Check for overlapping edits
        sorted_edits = sorted(edits, key=lambda e: (e.start_offset, e.end_offset))
        for i in range(len(sorted_edits) - 1):
            cur = sorted_edits[i]
            nxt = sorted_edits[i + 1]
            if cur.end_offset > nxt.start_offset:
                errors.append(
                    f"Overlapping edits detected: [{cur.start_offset}, {cur.end_offset}] overlaps with [{nxt.start_offset}, {nxt.end_offset}]."
                )

        if errors:
            return False, source, errors

        # Apply edits from end to beginning to preserve earlier offsets
        reversed_edits = sorted(edits, key=lambda e: (e.start_offset, e.end_offset), reverse=True)
        result = source

        for edit in reversed_edits:
            before = result[: edit.start_offset]
            after = result[edit.end_offset :]
            result = before + edit.replacement + after

        return True, result, []
