"""Unit tests for SourceEditor safe edit application."""

import pytest
from backend.app.correction.models import EditOperation, EditType
from backend.app.correction.editor import SourceEditor


def test_valid_insert_operation():
    source = "int a = 10\nreturn a;"
    # Insert ';' at offset 10 (after 10)
    op = EditOperation(
        operation=EditType.INSERT,
        start_offset=10,
        end_offset=10,
        replacement=";",
    )
    success, result, errors = SourceEditor.apply_edits(source, [op])
    assert success is True
    assert errors == []
    assert result == "int a = 10;\nreturn a;"
    # Ensure original source is not mutated
    assert source == "int a = 10\nreturn a;"


def test_valid_replace_operation():
    source = "integ a = 10;"
    op = EditOperation(
        operation=EditType.REPLACE,
        start_offset=0,
        end_offset=5,
        replacement="int",
        expected_text="integ",
    )
    success, result, errors = SourceEditor.apply_edits(source, [op])
    assert success is True
    assert result == "int a = 10;"


def test_valid_delete_operation():
    source = "int a = 10;;;"
    op = EditOperation(
        operation=EditType.DELETE,
        start_offset=11,
        end_offset=13,
        replacement="",
        expected_text=";;",
    )
    success, result, errors = SourceEditor.apply_edits(source, [op])
    assert success is True
    assert result == "int a = 10;"


def test_expected_text_mismatch():
    source = "int x = 42;"
    op = EditOperation(
        operation=EditType.REPLACE,
        start_offset=0,
        end_offset=3,
        replacement="float",
        expected_text="char",  # Mismatch: actual is "int"
    )
    success, result, errors = SourceEditor.apply_edits(source, [op])
    assert success is False
    assert len(errors) >= 1
    assert "Expected text 'char' did not match actual text 'int'" in errors[0]
    assert result == source


def test_out_of_bounds_offsets():
    source = "int x = 1;"
    op = EditOperation(
        operation=EditType.INSERT,
        start_offset=100,
        end_offset=100,
        replacement=";",
    )
    success, result, errors = SourceEditor.apply_edits(source, [op])
    assert success is False
    assert any("exceed source length" in err for err in errors)


def test_negative_offsets():
    source = "int x = 1;"
    op = EditOperation(
        operation=EditType.INSERT,
        start_offset=-1,
        end_offset=-1,
        replacement=";",
    )
    success, result, errors = SourceEditor.apply_edits(source, [op])
    assert success is False
    assert any("Negative offsets" in err for err in errors)


def test_overlapping_edits_rejected():
    source = "int x = 10 + 20;"
    op1 = EditOperation(operation=EditType.REPLACE, start_offset=4, end_offset=10, replacement="y")
    op2 = EditOperation(operation=EditType.REPLACE, start_offset=8, end_offset=15, replacement="z")
    success, result, errors = SourceEditor.apply_edits(source, [op1, op2])
    assert success is False
    assert any("Overlapping edits detected" in err for err in errors)


def test_multiple_non_overlapping_edits_applied_correctly():
    source = "int a = 10\nint b = 20"
    op1 = EditOperation(operation=EditType.INSERT, start_offset=10, end_offset=10, replacement=";")
    op2 = EditOperation(operation=EditType.INSERT, start_offset=21, end_offset=21, replacement=";")
    success, result, errors = SourceEditor.apply_edits(source, [op1, op2])
    assert success is True
    assert result == "int a = 10;\nint b = 20;"
