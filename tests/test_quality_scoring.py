"""Tests for quality.py and scoring.py (PRD US-03, US-06, US-07, US-11)."""

import pytest

import llm
from quality import can_approve, check_backlog, check_story, prohibited_words
from schemas import AcceptanceCriterion
from scoring import INVALID, NOT_SCORED, rice


def backlog(name="01_bank_sme_onboarding"):
    notes = llm.load_sample(name)
    return llm.generate_backlog(notes, provider=llm.MockProvider()), notes


# ---------- vague wording (US-03 AC-03) ----------

@pytest.mark.parametrize(
    "text, expected",
    [
        ("Then the page loads fast", ["fast"]),
        ("results appear within 3 seconds", []),
        ("is User-Friendly and SEAMLESS", ["seamless", "user-friendly"]),
        ("breakfast is served", []),          # 'fast' inside a word is fine
        ("appropriately", []),                # whole words only
    ],
)
def test_prohibited_words(text, expected):
    assert prohibited_words(text) == expected


def test_sample_two_has_vague_criterion_that_blocks_approval():
    result, notes = backlog("02_gov_permit_renewal")
    s1 = result.backlog.stories[0]
    findings = check_story(s1, notes)
    assert any(f.rule == "vague_wording" and f.criterion == 3 for f in findings)
    assert not can_approve(s1, notes)


def test_fixing_the_wording_clears_the_flag():
    """US-03 F3: edit 'loads fast' to a measurable outcome, re-check, flag clears."""
    result, notes = backlog("02_gov_permit_renewal")
    s1 = result.backlog.stories[0]
    s1.acceptance_criteria[2].then = "the request details are shown within 3 seconds"
    assert check_story(s1, notes) == []
    assert can_approve(s1, notes)


def test_clean_sample_has_no_blocking_findings():
    result, notes = backlog()
    assert [f for f in check_backlog(result.backlog, notes) if f.blocking] == []


# ---------- structural problems after editing (US-06 AC-03/AC-04) ----------

def test_too_few_criteria_after_edit_blocks():
    result, notes = backlog()
    story = result.backlog.stories[0]
    story.acceptance_criteria = story.acceptance_criteria[:1]
    assert any(f.rule == "criteria_count" for f in check_story(story, notes))
    assert not can_approve(story, notes)


def test_blank_then_after_edit_blocks():
    result, notes = backlog()
    story = result.backlog.stories[0]
    story.acceptance_criteria[0] = AcceptanceCriterion.model_construct(given="a", when="b", then=" ")
    assert any(f.rule == "missing_gherkin" for f in check_story(story, notes))


def test_edited_quote_not_in_notes_blocks():
    result, notes = backlog()
    story = result.backlog.stories[0]
    story.evidence_quote = "a sentence nobody said"
    assert any(f.rule == "evidence" for f in check_story(story, notes))


def test_empty_role_blocks():
    result, notes = backlog()
    story = result.backlog.stories[0]
    story.role = "  "
    assert any(f.rule == "missing_field" for f in check_story(story, notes))


# ---------- backlog-level warnings ----------

def test_duplicate_title_warning():
    result, notes = backlog()
    stories = result.backlog.stories
    stories[1].title = stories[0].title.upper() + " "
    dup = [f for f in check_backlog(result.backlog, notes) if f.rule == "duplicate"]
    assert dup and dup[0].story_id == stories[1].id and not dup[0].blocking


def test_removed_dependency_warning():
    result, notes = backlog()
    findings = check_backlog(result.backlog, notes, removed_dependencies=[("S2", "S9")])
    assert any(f.rule == "dependency" and "S9" in f.message for f in findings)


# ---------- RICE (US-11) ----------

def test_rice_example_from_prd():
    assert rice(8, 2, 0.75, 3).label() == "4.00"


def test_rice_recalculates_after_effort_change():
    assert rice(8, 2, 0.75, 4).label() == "3.00"


@pytest.mark.parametrize("args", [(None, 2, 0.5, 3), (5, 2, None, 3), (5, 2, 0.5, "")])
def test_rice_missing_is_not_scored(args):
    result = rice(*args)
    assert result.score is None and result.status == NOT_SCORED


@pytest.mark.parametrize("args", [(0, 2, 0.5, 3), (5, 4, 0.5, 3), (5, 2, 1.5, 3), (5, 2, 0.5, 0), (5.5, 2, 0.5, 3)])
def test_rice_invalid_inputs(args):
    result = rice(*args)
    assert result.score is None and result.status == INVALID
