"""Tests for schemas.py — each test maps to a rule in docs/PRD.md."""

import copy
import json
import re
from pathlib import Path

import pytest
from pydantic import ValidationError

from schemas import Backlog, backlog_json_schema, reset_approvals

ROOT = Path(__file__).resolve().parent.parent
SAMPLE_NOTES = ROOT / "samples" / "01_bank_sme_onboarding.md"
CACHED = ROOT / "samples" / "cached" / "01_bank_sme_onboarding.json"


def load_cached() -> dict:
    return json.loads(CACHED.read_text(encoding="utf-8"))


def normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().casefold()


# ---------- valid data ----------

def test_cached_sample_is_valid():
    backlog = Backlog.model_validate(load_cached())
    assert len(backlog.stories) == 6
    assert len(backlog.epics) == 3


def test_every_cached_quote_appears_in_notes():
    """US-05: evidence quotes must exist in the notes (case/space-insensitive)."""
    notes = normalise(SAMPLE_NOTES.read_text(encoding="utf-8"))
    for story in Backlog.model_validate(load_cached()).stories:
        assert normalise(story.evidence_quote) in notes, story.id
        assert len(story.evidence_quote.split()) <= 20, story.id


def test_stories_start_unapproved():
    """US-07: nothing from the AI or cache is pre-approved."""
    data = load_cached()
    data["stories"][0]["approved"] = True  # pretend the AI tried to approve
    backlog = reset_approvals(Backlog.model_validate(data))
    assert all(not s.approved for s in backlog.stories)


def test_ai_schema_hides_approved_field():
    story_props = backlog_json_schema()["$defs"]["Story"]["properties"]
    assert "approved" not in story_props


# ---------- invalid data must be rejected (US-04) ----------

@pytest.mark.parametrize(
    "field, bad_value",
    [
        ("moscow", "Critical"),       # not a MoSCoW value
        ("points", 4),                # not 1, 2, 3, 5 or 8
        ("acceptance_criteria", []),  # fewer than 2 criteria
        ("evidence_quote", ""),       # empty quote
    ],
)
def test_bad_story_values_are_rejected(field, bad_value):
    data = load_cached()
    data["stories"][0][field] = bad_value
    with pytest.raises(ValidationError):
        Backlog.model_validate(data)


def test_too_many_criteria_rejected():
    data = load_cached()
    ac = data["stories"][0]["acceptance_criteria"][0]
    data["stories"][0]["acceptance_criteria"] = [ac] * 5
    with pytest.raises(ValidationError):
        Backlog.model_validate(data)


def test_blank_then_rejected():
    data = load_cached()
    data["stories"][0]["acceptance_criteria"][0]["then"] = "   "
    with pytest.raises(ValidationError):
        Backlog.model_validate(data)


def test_unknown_epic_rejected():
    data = load_cached()
    data["stories"][0]["epic_id"] = "E99"
    with pytest.raises(ValidationError, match="unknown epic"):
        Backlog.model_validate(data)


def test_duplicate_story_ids_rejected():
    data = load_cached()
    data["stories"].append(copy.deepcopy(data["stories"][0]))
    with pytest.raises(ValidationError, match="duplicate story"):
        Backlog.model_validate(data)


def test_rice_inputs_optional():
    """US-11: missing RICE inputs are allowed (shown as Not scored later)."""
    data = load_cached()
    for key in ("reach", "impact", "confidence", "effort"):
        data["stories"][0].pop(key)
    Backlog.model_validate(data)
