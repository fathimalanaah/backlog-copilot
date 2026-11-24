"""Evidence-quote check (PRD US-05).

Every story must quote the workshop notes. After schema validation, stories
whose quote is empty, longer than 20 words, or not found in the notes are
removed from the reviewable backlog and listed as "dropped" with a reason.

Matching rules (US-05):
1. Case-fold the notes and the quote.
2. Collapse runs of whitespace to one space; trim.
3. The normalised quote must be a contiguous substring of the normalised notes.

A match proves the quote exists; it does not prove the story interprets it
correctly. That judgement stays with the Product Owner (PRD OQ-08).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from schemas import MAX_QUOTE_WORDS, Backlog, Story


@dataclass
class DroppedStory:
    id: str
    title: str
    reason: str


def normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().casefold()


def quote_problem(quote: str, notes: str) -> str | None:
    """Return a reason if the quote is invalid, or None if it is fine."""
    if not quote or not quote.strip():
        return "Evidence quote is empty"
    if len(quote.split()) > MAX_QUOTE_WORDS:
        return f"Evidence quote is longer than {MAX_QUOTE_WORDS} words"
    if normalise(quote) not in normalise(notes):
        return "Evidence quote not found in the workshop notes"
    return None


@dataclass
class EvidenceResult:
    backlog: Backlog
    dropped: list[DroppedStory]
    # (story_id, removed_dependency_id) pairs — PRD US-09 AC-03
    removed_dependencies: list[tuple[str, str]]


def verify_quotes(backlog: Backlog, notes: str) -> EvidenceResult:
    """Drop unsupported stories; clean dependencies that pointed at them."""
    kept: list[Story] = []
    dropped: list[DroppedStory] = []
    for story in backlog.stories:
        problem = quote_problem(story.evidence_quote, notes)
        if problem:
            dropped.append(DroppedStory(story.id, story.title, problem))
        else:
            kept.append(story)

    kept_ids = {s.id for s in kept}
    removed: list[tuple[str, str]] = []
    for story in kept:
        for dep in story.depends_on:
            if dep not in kept_ids:
                removed.append((story.id, dep))
        story.depends_on = [d for d in story.depends_on if d in kept_ids]

    # model_copy skips validation on purpose: zero kept stories is a valid
    # outcome here (US-05 AC-04), even though the AI must return at least one.
    cleaned = backlog.model_copy(update={"stories": kept})
    return EvidenceResult(cleaned, dropped, removed)
