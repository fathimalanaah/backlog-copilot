"""RICE scoring (PRD US-11). Calculated by code, never by the AI.

RICE = (Reach x Impact x Confidence) / Effort
Reach 1-10, Impact one of {0.25, 0.5, 1, 2, 3}, Confidence 0-1, Effort 1-10.
Missing inputs -> "Not scored"; out-of-range inputs -> "Invalid RICE inputs".
"""

from __future__ import annotations

from dataclasses import dataclass

IMPACT_VALUES = (0.25, 0.5, 1, 2, 3)
NOT_SCORED = "Not scored"
INVALID = "Invalid RICE inputs"


@dataclass
class RiceResult:
    score: float | None
    status: str  # "Scored", NOT_SCORED or INVALID

    def label(self) -> str:
        return f"{self.score:.2f}" if self.score is not None else self.status


def rice(reach, impact, confidence, effort) -> RiceResult:
    values = (reach, impact, confidence, effort)
    if any(v is None or v == "" for v in values):
        return RiceResult(None, NOT_SCORED)
    try:
        reach, impact, confidence, effort = float(reach), float(impact), float(confidence), float(effort)
    except (TypeError, ValueError):
        return RiceResult(None, INVALID)
    valid = (
        1 <= reach <= 10 and reach.is_integer()
        and impact in IMPACT_VALUES
        and 0 <= confidence <= 1
        and 1 <= effort <= 10 and effort.is_integer()
    )
    if not valid:
        return RiceResult(None, INVALID)
    return RiceResult(round(reach * impact * confidence / effort, 2), "Scored")


def rice_for_story(story) -> RiceResult:
    return rice(story.reach, story.impact, story.confidence, story.effort)
