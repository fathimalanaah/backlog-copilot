"""Data model for Backlog Copilot.

These Pydantic models are the "output contract": the AI must return JSON that
fits them exactly, or the response is rejected (and retried once). They also
encode the business rules from docs/PRD.md (US-02 to US-05, US-07).
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

MoSCoW = Literal["Must", "Should", "Could", "Won't"]
StoryPoints = Literal[1, 2, 3, 5, 8]
Impact = Literal[0.25, 0.5, 1, 2, 3]

MAX_QUOTE_WORDS = 20


class AcceptanceCriterion(BaseModel):
    """One Gherkin scenario: Given / When / Then."""

    given: str = Field(min_length=1)
    when: str = Field(min_length=1)
    then: str = Field(min_length=1)

    @field_validator("given", "when", "then")
    @classmethod
    def not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must not be blank")
        return value.strip()


class Epic(BaseModel):
    id: str = Field(pattern=r"^E\d+$", description='e.g. "E1"')
    title: str = Field(min_length=1)
    goal: str = Field(min_length=1)


class Story(BaseModel):
    id: str = Field(pattern=r"^S\d+$", description='e.g. "S1"')
    epic_id: str = Field(pattern=r"^E\d+$")
    title: str = Field(min_length=1)
    role: str = Field(min_length=1, description='"As a ..."')
    want: str = Field(min_length=1, description='"I want ..."')
    so_that: str = Field(min_length=1, description='"so that ..."')
    acceptance_criteria: list[AcceptanceCriterion] = Field(min_length=2, max_length=4)
    moscow: MoSCoW
    points: StoryPoints
    evidence_quote: str = Field(
        min_length=1,
        description=f"Exact quote from the notes, at most {MAX_QUOTE_WORDS} words",
    )
    depends_on: list[str] = Field(default_factory=list)
    # RICE inputs are optional (US-11 is a Should). Missing = "Not scored".
    reach: int | None = Field(default=None, ge=1, le=10)
    impact: Impact | None = None
    confidence: float | None = Field(default=None, ge=0, le=1)
    effort: int | None = Field(default=None, ge=1, le=10)
    # Approval belongs to the Product Owner, never to the AI (US-07).
    # It is excluded from the schema the AI sees, and reset_approvals() below
    # forces it to False whenever a backlog arrives from the AI or the cache.
    approved: bool = Field(default=False, json_schema_extra={"ai_hidden": True})

    def sentence(self) -> str:
        return f"As a {self.role}, I want {self.want}, so that {self.so_that}."


class OpenQuestion(BaseModel):
    question: str = Field(min_length=1)
    owner_role: str | None = None


class Decision(BaseModel):
    decision: str = Field(min_length=1)
    status: Literal["Open", "Confirmed"] = "Open"


class PRDSummary(BaseModel):
    problem: str = Field(min_length=1)
    users: list[str] = Field(min_length=1)
    goals: list[str] = Field(min_length=1)
    non_goals: list[str] = Field(default_factory=list)


class Backlog(BaseModel):
    prd_summary: PRDSummary
    epics: list[Epic] = Field(min_length=1)
    stories: list[Story] = Field(min_length=1)
    open_questions: list[OpenQuestion] = Field(default_factory=list)
    decisions: list[Decision] = Field(default_factory=list)

    @model_validator(mode="after")
    def check_references(self) -> "Backlog":
        epic_ids = [e.id for e in self.epics]
        story_ids = [s.id for s in self.stories]
        if len(set(epic_ids)) != len(epic_ids):
            raise ValueError("duplicate epic IDs")
        if len(set(story_ids)) != len(story_ids):
            raise ValueError("duplicate story IDs")
        for story in self.stories:
            if story.epic_id not in epic_ids:
                raise ValueError(f"story {story.id} references unknown epic {story.epic_id}")
        return self


def reset_approvals(backlog: Backlog) -> Backlog:
    """Every story from the AI (or cached output) starts unapproved."""
    for story in backlog.stories:
        story.approved = False
    return backlog


def backlog_json_schema() -> dict:
    """JSON Schema handed to the LLM so it knows the exact shape to return.

    The `approved` field is removed: the AI must never be able to set it.
    """
    schema = Backlog.model_json_schema()
    story = schema["$defs"]["Story"]
    story["properties"].pop("approved", None)
    if "approved" in story.get("required", []):
        story["required"].remove("approved")
    return schema
