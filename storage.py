"""Save and retrieve approved stories in Supabase (PRD US-12, Should).

Only approved, quality-passing stories are written. Unapproved work stays in
the browser session. If Supabase is not configured, saving is disabled and
the rest of the app keeps working.

Table (created once with docs/supabase_setup.sql):
    saved_stories(id bigserial, project text, story_id text,
                  payload jsonb, saved_at timestamptz default now())
"""

from __future__ import annotations

import os

from export import NoApprovedStoriesError, exportable_stories
from schemas import Backlog, Story

TABLE = "saved_stories"


class StorageError(RuntimeError):
    pass


def is_configured() -> bool:
    return bool(os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_ANON_KEY"))


def get_client():
    from supabase import create_client  # imported lazily so tests need no network

    return create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_ANON_KEY"])


def save_approved(backlog: Backlog, project: str, notes: str | None = None, client=None) -> int:
    stories = exportable_stories(backlog, notes)
    if not stories:
        raise NoApprovedStoriesError("No approved stories to save. Approve at least one story first.")  # US-12 AC-02
    rows = [
        {"project": project, "story_id": s.id, "payload": s.model_dump(mode="json")}
        for s in stories
    ]
    try:
        client = client or get_client()
        client.table(TABLE).insert(rows).execute()
    except Exception as exc:  # US-12 AC-03: report, keep session state untouched
        raise StorageError(f"Save failed: {exc}") from exc
    return len(rows)


def list_saved(client=None, limit: int = 200) -> list[dict]:
    try:
        client = client or get_client()
        response = (
            client.table(TABLE)
            .select("project, story_id, payload, saved_at")
            .order("saved_at", desc=True)
            .limit(limit)
            .execute()
        )
    except Exception as exc:
        raise StorageError(f"Could not load saved stories: {exc}") from exc
    return response.data or []


def story_from_row(row: dict) -> Story:
    return Story.model_validate(row["payload"])
