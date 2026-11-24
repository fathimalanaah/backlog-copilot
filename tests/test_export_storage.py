"""Tests for export.py and storage.py (PRD US-08, US-10, US-12)."""

import csv
import io

import pytest

import llm
import storage
from export import NoApprovedStoriesError, test_cases as make_test_cases, to_csv, to_markdown


def fresh(name="01_bank_sme_onboarding"):
    notes = llm.load_sample(name)
    return llm.generate_backlog(notes, provider=llm.MockProvider()).backlog, notes


def approve(backlog, *ids):
    for s in backlog.stories:
        if s.id in ids:
            s.approved = True


# ---------- export (US-08) ----------

def test_csv_contains_only_approved_rows():
    backlog, notes = fresh()
    approve(backlog, "S1", "S3")  # 2 approved, 4 unapproved
    rows = list(csv.reader(io.StringIO(to_csv(backlog, notes).decode("utf-8"))))
    assert rows[0][0] == "ID"
    assert [r[0] for r in rows[1:]] == ["S1", "S3"]
    assert "Given" in rows[1][4] and "Then" in rows[1][4]


def test_markdown_contains_only_approved_sections_and_test_cases():
    backlog, notes = fresh()
    approve(backlog, "S1", "S3")
    md = to_markdown(backlog, notes).decode("utf-8")
    assert md.count("\n## ") == 2
    assert "## S1" in md and "## S3" in md and "## S2" not in md
    assert "TC-S1-1" in md
    assert "SME" not in md.split("## S1")[0]  # PRD summary is not exported


@pytest.mark.parametrize("func", [to_csv, to_markdown])
def test_no_approved_stories_produces_no_file(func):
    backlog, notes = fresh()
    with pytest.raises(NoApprovedStoriesError):
        func(backlog, notes)


def test_story_that_no_longer_passes_checks_is_excluded():
    """US-08 AC-04: approved but now invalid -> not exported."""
    backlog, notes = fresh()
    approve(backlog, "S1", "S3")
    backlog.stories[0].acceptance_criteria[0].then = "it works properly"
    rows = list(csv.reader(io.StringIO(to_csv(backlog, notes).decode("utf-8"))))
    assert [r[0] for r in rows[1:]] == ["S3"]


def test_test_cases_one_per_criterion():
    backlog, _ = fresh()
    story = backlog.stories[0]
    cases = make_test_cases(story)
    assert len(cases) == len(story.acceptance_criteria)
    assert cases[0]["expected"] == story.acceptance_criteria[0].then


# ---------- storage (US-12) with a fake Supabase client ----------

class FakeTable:
    def __init__(self, store, fail=False):
        self.store, self.fail = store, fail

    def insert(self, rows):
        if self.fail:
            raise ConnectionError("network down")
        self.store.extend(rows)
        return self

    def select(self, *_):
        return self

    def order(self, *_, **__):
        return self

    def limit(self, *_):
        return self

    def execute(self):
        return type("Resp", (), {"data": list(self.store)})()


class FakeClient:
    def __init__(self, fail=False):
        self.rows, self.fail, self.calls = [], fail, 0

    def table(self, _name):
        self.calls += 1
        return FakeTable(self.rows, self.fail)


def test_save_writes_only_approved_and_retrieves_them():
    backlog, notes = fresh()
    approve(backlog, "S1", "S3")
    client = FakeClient()
    assert storage.save_approved(backlog, "Demo", notes, client=client) == 2
    rows = storage.list_saved(client=client)
    assert [r["story_id"] for r in rows] == ["S1", "S3"]
    assert storage.story_from_row(rows[0]).approved is True


def test_save_with_nothing_approved_makes_zero_writes():
    backlog, notes = fresh()
    client = FakeClient()
    with pytest.raises(NoApprovedStoriesError):
        storage.save_approved(backlog, "Demo", notes, client=client)
    assert client.calls == 0


def test_save_failure_is_reported_and_session_kept():
    backlog, notes = fresh()
    approve(backlog, "S1")
    with pytest.raises(storage.StorageError, match="Save failed"):
        storage.save_approved(backlog, "Demo", notes, client=FakeClient(fail=True))
    assert backlog.stories[0].approved is True  # working copy untouched


def test_is_configured(monkeypatch):
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    assert storage.is_configured() is False
    monkeypatch.setenv("SUPABASE_URL", "https://x.supabase.co")
    monkeypatch.setenv("SUPABASE_ANON_KEY", "k")
    assert storage.is_configured() is True
