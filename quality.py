"""Rule-based quality checker (PRD US-03, US-06, US-07).

Deterministic rules, not the AI grading itself. A "blocking" finding prevents
approval of that story; a "warning" is shown but does not block.

The checker finds prohibited wording; it does not prove a criterion is
testable. Semantic review stays with the Product Owner (PRD OQ-18).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from difflib import SequenceMatcher

from evidence import normalise, quote_problem
from schemas import Backlog, Story

PROHIBITED_TERMS = [
    "fast", "quickly", "easy", "easily", "intuitive", "user-friendly",
    "seamless", "seamlessly", "properly", "correctly", "efficiently",
    "adequate", "appropriate",
]
_PROHIBITED_RE = re.compile(
    r"(?<![\w-])(" + "|".join(re.escape(t) for t in PROHIBITED_TERMS) + r")(?![\w-])",
    re.IGNORECASE,
)
DUPLICATE_TITLE_SIMILARITY = 0.9


@dataclass
class Finding:
    story_id: str
    rule: str
    message: str
    blocking: bool
    criterion: int | None = None  # 1-based acceptance-criterion number


def prohibited_words(text: str) -> list[str]:
    return sorted({m.group(1).lower() for m in _PROHIBITED_RE.finditer(text)})


def check_story(story: Story, notes: str | None = None) -> list[Finding]:
    found: list[Finding] = []
    sid = story.id

    for field_name in ("title", "role", "want", "so_that"):
        if not str(getattr(story, field_name, "")).strip():
            found.append(Finding(sid, "missing_field", f"'{field_name}' is empty", True))

    count = len(story.acceptance_criteria)
    if not 2 <= count <= 4:
        found.append(Finding(sid, "criteria_count", f"Has {count} acceptance criteria; needs 2 to 4", True))

    for i, ac in enumerate(story.acceptance_criteria, start=1):
        for part in ("given", "when", "then"):
            if not getattr(ac, part).strip():
                found.append(Finding(sid, "missing_gherkin", f"AC-{i}: '{part}' is empty", True, i))
        words = prohibited_words(f"{ac.given} {ac.when} {ac.then}")
        if words:
            found.append(Finding(
                sid, "vague_wording",
                f"AC-{i} uses vague wording: {', '.join(words)}. Replace with a measurable outcome.",
                True, i,
            ))

    if notes is not None:
        problem = quote_problem(story.evidence_quote, notes)
        if problem:
            found.append(Finding(sid, "evidence", problem, True))

    return found


def check_backlog(
    backlog: Backlog,
    notes: str | None = None,
    removed_dependencies: list[tuple[str, str]] | None = None,
) -> list[Finding]:
    found: list[Finding] = []
    for story in backlog.stories:
        found.extend(check_story(story, notes))

    # Duplicate titles (warning)
    stories = backlog.stories
    for i, a in enumerate(stories):
        for b in stories[i + 1:]:
            ratio = SequenceMatcher(None, normalise(a.title), normalise(b.title)).ratio()
            if ratio >= DUPLICATE_TITLE_SIMILARITY:
                found.append(Finding(b.id, "duplicate", f"Title is a near-duplicate of {a.id}", False))

    # Dependencies that point to stories not in the backlog (warning)
    ids = {s.id for s in stories}
    for s in stories:
        for dep in s.depends_on:
            if dep not in ids:
                found.append(Finding(s.id, "dependency", f"Depends on {dep}, which is not in the backlog", False))
    for sid, dep in removed_dependencies or []:
        if sid in ids:
            found.append(Finding(sid, "dependency", f"Dependency on {dep} removed: {dep} was dropped (no evidence)", False))

    return found


def blocking_findings(story: Story, notes: str | None = None) -> list[Finding]:
    return [f for f in check_story(story, notes) if f.blocking]


def can_approve(story: Story, notes: str | None = None) -> bool:
    """US-07 AC-01/AC-02: approval only when no blocking findings remain."""
    return not blocking_findings(story, notes)
