"""Backlog generation pipeline (PRD US-01, US-02, US-04, US-05, US-13).

    notes -> validate input -> provider returns raw JSON text
          -> Pydantic validation (retry once with the error) -> reset approvals
          -> evidence-quote check (drop unsupported stories) -> result

This version runs in MOCK mode only (project decision DEC-30): the provider
returns a pre-saved backlog for each fictional sample in samples/. A live LLM
provider can be added later by implementing `Provider.generate()`; nothing
else in the pipeline needs to change.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

from pydantic import ValidationError

from evidence import DroppedStory, verify_quotes
from schemas import Backlog, reset_approvals

ROOT = Path(__file__).resolve().parent
SAMPLES_DIR = ROOT / "samples"
CACHED_DIR = SAMPLES_DIR / "cached"
PROMPT_PATH = ROOT / "prompts" / "system_backlog.md"

MIN_WORDS = 50
MAX_WORDS = 15_000
MAX_UPLOAD_BYTES = 200_000  # PRD OQ-03: "under 200 KB" = fewer than 200,000 bytes
ALLOWED_EXTENSIONS = (".txt", ".md")


class InputError(ValueError):
    """Notes or upload failed validation; no generation request is made."""


class GenerationError(RuntimeError):
    """Generation failed; no reviewable stories are created."""


# ---------------------------------------------------------------- input ----

def word_count(text: str) -> int:
    return len(text.split())  # PRD OQ-04: whitespace-separated tokens


def validate_notes(notes: str) -> str:
    words = word_count(notes)
    if words < MIN_WORDS:
        raise InputError(f"Notes too short: {words} words. Minimum is {MIN_WORDS}.")
    if words > MAX_WORDS:
        raise InputError(f"Notes too long: {words:,} words. Maximum is {MAX_WORDS:,}.")
    return notes


def read_upload(filename: str, data: bytes) -> str:
    """US-01 AC-02/AC-04: .txt or .md, UTF-8, under 200 KB."""
    if not filename.lower().endswith(ALLOWED_EXTENSIONS):
        raise InputError("Unsupported file type. Upload a .txt or .md file.")
    if len(data) >= MAX_UPLOAD_BYTES:
        raise InputError("File is 200 KB or larger. Upload a smaller file.")
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise InputError("File is not valid UTF-8 text.") from exc


# ---------------------------------------------------------------- samples --

def _normalise_newlines(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n").strip()


def list_samples() -> dict[str, Path]:
    """Sample name -> notes file. Every sample has a cached backlog."""
    return {p.stem: p for p in sorted(SAMPLES_DIR.glob("*.md")) if (CACHED_DIR / f"{p.stem}.json").exists()}


def load_sample(name: str) -> str:
    return list_samples()[name].read_text(encoding="utf-8")


# ---------------------------------------------------------------- providers -

class Provider(Protocol):
    name: str

    def generate(self, notes: str, system_prompt: str, feedback: str | None = None) -> str:
        """Return raw JSON text for a Backlog."""


class MockProvider:
    """Returns the pre-saved backlog when the notes match a fictional sample
    exactly (after line-ending normalisation) — PRD US-13 cache boundary."""

    name = "mock"

    def generate(self, notes: str, system_prompt: str, feedback: str | None = None) -> str:
        target = _normalise_newlines(notes)
        for stem, path in list_samples().items():
            if _normalise_newlines(path.read_text(encoding="utf-8")) == target:
                return (CACHED_DIR / f"{stem}.json").read_text(encoding="utf-8")
        raise GenerationError(
            "No cached output available for this input. Mock mode only works with "
            "the built-in fictional samples (choose one under 'Load sample')."
        )


def provider_mode() -> str:
    """LLM_PROVIDER, tolerant of stray spaces/quotes pasted into secret managers."""
    raw = os.getenv("LLM_PROVIDER") or "mock"
    return raw.strip().strip("'\"").strip().lower() or "mock"


def get_provider() -> Provider:
    mode = provider_mode()
    if mode != "mock":
        # DEC-30: live AI is out of scope for this release.
        raise GenerationError(
            f"LLM_PROVIDER='{mode}' is not supported in this version. Set LLM_PROVIDER=mock."
        )
    return MockProvider()


# ---------------------------------------------------------------- pipeline -

@dataclass
class GenerationResult:
    backlog: Backlog
    dropped: list[DroppedStory]
    removed_dependencies: list[tuple[str, str]]
    source: str  # "cached" for mock mode
    attempts: int
    seconds: float
    log: list[str] = field(default_factory=list)


def _parse(raw: str) -> Backlog:
    text = raw.strip()
    if text.startswith("```"):  # tolerate markdown fences around JSON
        text = text.strip("`")
        text = text[text.find("{"):]
    return Backlog.model_validate(json.loads(text))


def generate_backlog(notes: str, provider: Provider | None = None) -> GenerationResult:
    validate_notes(notes)  # raises InputError before any provider call
    provider = provider or get_provider()
    system_prompt = PROMPT_PATH.read_text(encoding="utf-8")
    started = time.perf_counter()
    log: list[str] = []

    feedback: str | None = None
    backlog: Backlog | None = None
    attempts = 0
    for attempts in (1, 2):  # US-04: first try + exactly one retry
        raw = provider.generate(notes, system_prompt, feedback)
        try:
            backlog = _parse(raw)
            break
        except (json.JSONDecodeError, ValidationError) as exc:
            feedback = f"Your previous output was invalid. Fix these errors and return JSON only:\n{exc}"
            log.append(f"Attempt {attempts} failed validation: {str(exc).splitlines()[0]}")
    if backlog is None:
        raise GenerationError(
            "The AI output failed validation twice. No stories were created. "
            + (log[-1] if log else "")
        )

    reset_approvals(backlog)  # US-07: nothing arrives pre-approved
    checked = verify_quotes(backlog, notes)
    return GenerationResult(
        backlog=checked.backlog,
        dropped=checked.dropped,
        removed_dependencies=checked.removed_dependencies,
        source="cached" if provider.name == "mock" else "live",
        attempts=attempts,
        seconds=round(time.perf_counter() - started, 2),
        log=log,
    )
