"""Tests for llm.py + evidence.py (PRD US-01, US-02, US-04, US-05, US-13)."""

import json

import pytest

import llm
from evidence import quote_problem
from llm import GenerationError, InputError, generate_backlog, load_sample, read_upload


class FakeProvider:
    """Returns queued raw outputs; records how often it was called."""

    name = "fake"

    def __init__(self, outputs):
        self.outputs = list(outputs)
        self.calls = 0
        self.feedback = []

    def generate(self, notes, system_prompt, feedback=None):
        self.calls += 1
        self.feedback.append(feedback)
        return self.outputs.pop(0)


def cached(name):
    return (llm.CACHED_DIR / f"{name}.json").read_text(encoding="utf-8")


# ---------- input (US-01) ----------

def test_short_notes_rejected_without_calling_ai():
    fake = FakeProvider([])
    with pytest.raises(InputError, match="too short"):
        generate_backlog("Need CRM.", provider=fake)
    assert fake.calls == 0


def test_too_long_notes_rejected():
    with pytest.raises(InputError, match="too long"):
        llm.validate_notes("word " * 15_001)


@pytest.mark.parametrize(
    "name, data, message",
    [
        ("notes.pdf", b"hello", "Unsupported file type"),
        ("notes.txt", b"\xff\xfe\xfa", "not valid UTF-8"),
        ("notes.md", b"a" * 200_000, "200 KB"),
    ],
)
def test_bad_uploads_rejected(name, data, message):
    with pytest.raises(InputError, match=message):
        read_upload(name, data)


def test_good_upload_accepted():
    assert read_upload("notes.md", "Hello – world".encode("utf-8")) == "Hello – world"


# ---------- mock mode (US-13) ----------

def test_every_sample_generates_in_mock_mode():
    for name in llm.list_samples():
        result = generate_backlog(load_sample(name), provider=llm.MockProvider())
        assert result.source == "cached"
        assert result.backlog.stories, name
        assert all(not s.approved for s in result.backlog.stories)


def test_mock_mode_unknown_notes_gives_clear_error():
    with pytest.raises(GenerationError, match="No cached output"):
        generate_backlog("word " * 60, provider=llm.MockProvider())


def test_mock_match_ignores_windows_line_endings():
    notes = load_sample("01_bank_sme_onboarding").replace("\n", "\r\n")
    assert generate_backlog(notes, provider=llm.MockProvider()).backlog.stories


def test_unsupported_provider_setting(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    with pytest.raises(GenerationError, match="not supported"):
        llm.get_provider()


# ---------- validation + retry (US-04) ----------


def bank_notes():
    return load_sample("01_bank_sme_onboarding")


def test_valid_output_needs_one_call():
    fake = FakeProvider([cached("01_bank_sme_onboarding")])
    result = generate_backlog(bank_notes(), provider=fake)
    assert fake.calls == 1 and result.attempts == 1


def test_invalid_then_valid_retries_once_with_error_feedback():
    fake = FakeProvider(['{"epics": "oops"}', cached("01_bank_sme_onboarding")])
    result = generate_backlog(bank_notes(), provider=fake)
    assert fake.calls == 2 and result.attempts == 2
    assert fake.feedback[0] is None and "invalid" in fake.feedback[1]


def test_two_invalid_outputs_raise_and_never_call_a_third_time():
    fake = FakeProvider(['{"epics": "oops"}', "not json at all", "unused"])
    with pytest.raises(GenerationError, match="failed validation twice"):
        generate_backlog(bank_notes(), provider=fake)
    assert fake.calls == 2


def test_markdown_fenced_json_is_accepted():
    fake = FakeProvider(["```json\n" + cached("01_bank_sme_onboarding") + "\n```"])
    assert generate_backlog(bank_notes(), provider=fake).attempts == 1


def test_ai_cannot_preapprove():
    data = json.loads(cached("01_bank_sme_onboarding"))
    for s in data["stories"]:
        s["approved"] = True
    result = generate_backlog(bank_notes(), provider=FakeProvider([json.dumps(data)]))
    assert all(not s.approved for s in result.backlog.stories)


# ---------- evidence (US-05, US-09 AC-03) ----------

def test_invented_story_is_dropped_and_dependency_cleaned():
    result = generate_backlog(load_sample("03_wholesale_ordering"), provider=llm.MockProvider())
    ids = [s.id for s in result.backlog.stories]
    assert "S5" not in ids  # loyalty-points story: quote not in notes
    assert [d.id for d in result.dropped] == ["S5"]
    assert "not found" in result.dropped[0].reason


def test_removed_dependency_is_reported():
    data = json.loads(cached("01_bank_sme_onboarding"))
    data["stories"][0]["evidence_quote"] = "this sentence is not in the notes"  # S1 dropped
    result = generate_backlog(bank_notes(), provider=FakeProvider([json.dumps(data)]))
    assert ("S2", "S1") in result.removed_dependencies
    s2 = next(s for s in result.backlog.stories if s.id == "S2")
    assert s2.depends_on == []


def test_all_stories_dropped_gives_empty_backlog():
    data = json.loads(cached("01_bank_sme_onboarding"))
    for s in data["stories"]:
        s["evidence_quote"] = "invented"
    result = generate_backlog(bank_notes(), provider=FakeProvider([json.dumps(data)]))
    assert result.backlog.stories == [] and len(result.dropped) == 6


@pytest.mark.parametrize(
    "quote, expected",
    [
        ("RMs KEEP   asking customers twice", None),  # case + spacing ignored
        ("", "empty"),
        ("word " * 21, "longer than 20"),
        ("customers love the new app", "not found"),
    ],
)
def test_quote_rules(quote, expected):
    problem = quote_problem(quote, bank_notes())
    if expected is None:
        assert problem is None
    else:
        assert expected in problem


def test_injection_sample_is_not_obeyed():
    result = generate_backlog(load_sample("03_wholesale_ordering"), provider=llm.MockProvider())
    assert all(not s.approved for s in result.backlog.stories)
    assert any("approve all stories" in q.question for q in result.backlog.open_questions)


@pytest.mark.parametrize("raw", [" mock", "mock ", "'mock'", '"mock"', "MOCK", ""])
def test_provider_mode_tolerates_stray_spaces_and_quotes(monkeypatch, raw):
    monkeypatch.setenv("LLM_PROVIDER", raw)
    assert llm.provider_mode() == "mock"
    assert isinstance(llm.get_provider(), llm.MockProvider)
