"""End-to-end UI tests with Streamlit's AppTest (no browser needed).

Covers the demo flow: load sample -> generate -> blocked approval of a vague
story -> fix it -> approve -> export only approved stories.
"""

from pathlib import Path

import pytest

streamlit_testing = pytest.importorskip("streamlit.testing.v1")
AppTest = streamlit_testing.AppTest


@pytest.fixture
def app(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "mock")
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_ANON_KEY", raising=False)
    at = AppTest.from_file(str(Path(__file__).resolve().parent.parent / "app.py"), default_timeout=30)
    at.run()
    assert not at.exception
    return at


def load_and_generate(at, sample):
    at.selectbox(key="sample_choice").set_value(sample).run()
    next(b for b in at.button if b.label == "Load sample").click().run()
    assert "FICTIONAL SAMPLE" in at.text_area(key="notes_input").value
    next(b for b in at.button if b.label == "Generate backlog").click().run()
    assert not at.exception
    return at


def approve_box(at, story_id):
    return next(c for c in at.checkbox if c.key.endswith(f"_{story_id}_approved"))


def test_generate_button_disabled_for_short_notes(app):
    app.text_area(key="notes_input").set_value("too short").run()
    gen = next(b for b in app.button if b.label == "Generate backlog")
    assert gen.disabled


def test_full_flow_bank_sample(app):
    at = load_and_generate(app, "01_bank_sme_onboarding")
    assert any("Generated 6 stories" in s.value for s in at.success)
    assert at.session_state["result"].source == "cached"
    # nothing approved yet -> export shows info, no download buttons
    assert not any(c.value for c in at.checkbox)
    approve_box(at, "S1").check().run()
    approve_box(at, "S3").check().run()
    b = at.session_state["result"].backlog
    assert [s.id for s in b.stories if s.approved] == ["S1", "S3"]
    import export
    csv_text = export.to_csv(b, at.session_state["notes_used"]).decode()
    assert csv_text.count("\nS") == 2


def test_vague_story_cannot_be_approved_until_fixed(app):
    at = load_and_generate(app, "02_gov_permit_renewal")
    approve_box(at, "S1").check().run()
    assert any("cannot be approved" in e.value for e in at.error)
    assert approve_box(at, "S1").value is False
    # fix the vague criterion through the edit form, then approve
    then3 = next(t for t in at.text_input if t.key.endswith("_S1_ac3_then"))
    then3.set_value("the request details are shown within 3 seconds")
    save = next(b for b in at.button if b.label == "Save changes" and "_S1_" in (b.form_id or ""))
    save.click().run()
    assert any("S1 saved. Quality checks pass" in s.value for s in at.success)
    approve_box(at, "S1").check().run()
    assert approve_box(at, "S1").value is True


def test_editing_an_approved_story_unapproves_only_that_story(app):
    at = load_and_generate(app, "01_bank_sme_onboarding")
    approve_box(at, "S1").check().run()
    approve_box(at, "S3").check().run()
    title = next(t for t in at.text_input if t.key.endswith("_S1_title"))
    title.set_value("Document checklist for each SME application")
    save = next(b for b in at.button if b.label == "Save changes" and "_S1_" in (b.form_id or ""))
    save.click().run()
    assert approve_box(at, "S1").value is False
    assert approve_box(at, "S3").value is True


def test_injection_sample_drops_invented_story(app):
    at = load_and_generate(app, "03_wholesale_ordering")
    result = at.session_state["result"]
    assert [d.id for d in result.dropped] == ["S5"]
    assert all(not s.approved for s in result.backlog.stories)
