"""Backlog Copilot — Streamlit UI.

Workshop notes -> AI-drafted backlog (mock mode: cached output for fictional
samples) -> quality checks -> Product Owner edits and approves each story ->
export CSV / Markdown, optionally save approved stories to Supabase.
"""

from __future__ import annotations

import os

import pandas as pd
import streamlit as st

import export
import llm
import storage
from quality import blocking_findings, check_backlog, check_story
from schemas import AcceptanceCriterion
from scoring import IMPACT_VALUES, rice_for_story

st.set_page_config(page_title="Backlog Copilot", page_icon="🗂️", layout="wide")

MOSCOW = ["Must", "Should", "Could", "Won't"]
POINTS = [1, 2, 3, 5, 8]
ss = st.session_state
ss.setdefault("gen", 0)          # bumps on every generation -> fresh widget keys
ss.setdefault("result", None)
ss.setdefault("notes_used", "")
ss.setdefault("flash", [])       # (level, message) shown once
ss.setdefault("notes_input", "")


def flash(level: str, message: str) -> None:
    ss.flash.append((level, message))


def k(story_id: str, name: str) -> str:
    return f"g{ss.gen}_{story_id}_{name}"


def backlog():
    return ss.result.backlog if ss.result else None


def find_story(story_id: str):
    return next(s for s in backlog().stories if s.id == story_id)


def unapprove(story) -> None:
    story.approved = False
    ss[k(story.id, "approved")] = False


# ------------------------------------------------------------ callbacks ----

def on_load_sample() -> None:
    name = ss.get("sample_choice")
    if name:
        ss.notes_input = llm.load_sample(name)


def on_upload() -> None:
    upload = ss.get("upload")
    if upload is None:
        return
    try:
        ss.notes_input = llm.read_upload(upload.name, upload.getvalue())
    except llm.InputError as exc:
        flash("error", str(exc))


def on_generate() -> None:
    notes = ss.notes_input
    try:
        result = llm.generate_backlog(notes)
    except (llm.InputError, llm.GenerationError) as exc:
        flash("error", str(exc))
        return
    ss.gen += 1
    ss.result = result
    ss.notes_used = notes
    kept, dropped = len(result.backlog.stories), len(result.dropped)
    flash("success", f"Generated {kept} stories ({dropped} dropped by the evidence check). All start unapproved.")


def on_toggle_approval(story_id: str) -> None:
    story = find_story(story_id)
    wanted = ss[k(story_id, "approved")]
    if not wanted:
        story.approved = False
        return
    problems = blocking_findings(story, ss.notes_used)
    if problems:
        ss[k(story_id, "approved")] = False
        story.approved = False
        flash("error", f"{story_id} cannot be approved: " + "; ".join(p.message for p in problems))
    else:
        story.approved = True


def on_save_edits(story_id: str) -> None:
    story = find_story(story_id)
    criteria = []
    for i in range(1, 5):
        parts = [ss.get(k(story_id, f"ac{i}_{p}"), "").strip() for p in ("given", "when", "then")]
        if any(parts):
            criteria.append(AcceptanceCriterion.model_construct(given=parts[0], when=parts[1], then=parts[2]))
    new = {
        "title": ss[k(story_id, "title")].strip(),
        "role": ss[k(story_id, "role")].strip(),
        "want": ss[k(story_id, "want")].strip(),
        "so_that": ss[k(story_id, "so_that")].strip(),
        "evidence_quote": ss[k(story_id, "quote")].strip(),
        "moscow": ss[k(story_id, "moscow")],
        "points": ss[k(story_id, "points")],
    }
    old_criteria = [(a.given, a.when, a.then) for a in story.acceptance_criteria]
    new_criteria = [(a.given, a.when, a.then) for a in criteria]
    changed = any(getattr(story, f) != v for f, v in new.items()) or old_criteria != new_criteria
    if not changed:
        flash("info", f"No changes to {story_id}.")
        return
    for f, v in new.items():
        setattr(story, f, v)
    story.acceptance_criteria = criteria
    was_approved = story.approved
    unapprove(story)  # US-07 AC-03: editing a story un-approves that story only
    note = " It was un-approved and needs re-approval." if was_approved else ""
    problems = blocking_findings(story, ss.notes_used)
    if problems:
        flash("warning", f"{story_id} saved with issues to fix before approval: "
              + "; ".join(p.message for p in problems) + note)
    else:
        flash("success", f"{story_id} saved. Quality checks pass.{note}")


def on_rice_edit() -> None:
    edits = ss["rice_editor"].get("edited_rows", {})
    stories = backlog().stories
    for row, change in edits.items():
        story = stories[int(row)]
        changed = False
        for col, field in (("Reach", "reach"), ("Impact", "impact"), ("Confidence", "confidence"), ("Effort", "effort")):
            if col in change:
                value = change[col]
                value = None if value is None or (isinstance(value, float) and pd.isna(value)) else value
                if field in ("reach", "effort") and value is not None:
                    value = int(value)
                if getattr(story, field) != value:
                    setattr(story, field, value)
                    changed = True
        if changed and story.approved:
            unapprove(story)
            flash("info", f"{story.id} RICE inputs changed; it needs re-approval.")


def on_save_db() -> None:
    try:
        n = storage.save_approved(backlog(), ss.get("project_name") or "Untitled", ss.notes_used)
        flash("success", f"Saved {n} approved stories to Supabase.")
    except export.NoApprovedStoriesError as exc:
        flash("error", str(exc))
    except storage.StorageError as exc:
        flash("error", f"{exc} Your working backlog is still here.")


# ------------------------------------------------------------ layout -------

st.title("🗂️ Backlog Copilot")
st.caption("Workshop notes → evidence-backed user stories → human review → export. "
           "AI drafts; rules check; the Product Owner approves.")

mode = os.getenv("LLM_PROVIDER", "mock")
with st.sidebar:
    st.subheader("Mode")
    if mode == "mock":
        st.info("**Mock mode.** Generation returns pre-saved output for the built-in "
                "fictional samples. No AI API is called.")
    else:
        st.warning(f"LLM_PROVIDER='{mode}' is not supported in this version.")
    st.subheader("How it works")
    st.markdown(
        "1. Load a sample or paste notes\n"
        "2. Generate a draft backlog\n"
        "3. Fix anything the quality checker flags\n"
        "4. Approve stories one by one\n"
        "5. Export CSV / Markdown"
    )
    st.caption("All samples are fictional. Do not paste real client data.")

for level, message in ss.flash:
    getattr(st, level)(message)
ss.flash = []

tab_input, tab_backlog, tab_quality, tab_prior, tab_export, tab_saved = st.tabs(
    ["1 · Input", "2 · Backlog", "3 · Quality", "4 · Prioritise", "5 · Export", "6 · Saved"]
)

# ---- 1 · Input -------------------------------------------------------------
with tab_input:
    samples = list(llm.list_samples())
    c1, c2 = st.columns([3, 1])
    c1.selectbox("Fictional sample", samples, key="sample_choice",
                 format_func=lambda s: s.split("_", 1)[1].replace("_", " ").title())
    c2.write("")
    c2.button("Load sample", on_click=on_load_sample, width="stretch")
    st.file_uploader("…or upload notes (.txt or .md, under 200 KB)", type=["txt", "md"],
                     key="upload", on_change=on_upload)
    st.text_area("Workshop notes", key="notes_input", height=320,
                 placeholder="Paste workshop notes here (50–15,000 words).")
    words = llm.word_count(ss.notes_input)
    valid = llm.MIN_WORDS <= words <= llm.MAX_WORDS
    st.caption(f"{words:,} words" + ("" if valid or words == 0 else
               f" — must be between {llm.MIN_WORDS} and {llm.MAX_WORDS:,}"))
    st.button("Generate backlog", type="primary", disabled=not valid, on_click=on_generate)

# ---- 2 · Backlog -----------------------------------------------------------
with tab_backlog:
    if not backlog():
        st.info("Generate a backlog on the Input tab first.")
    else:
        r = ss.result
        b = r.backlog
        approved = sum(s.approved for s in b.stories)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Stories for review", len(b.stories))
        m2.metric("Approved", approved)
        m3.metric("Dropped (no evidence)", len(r.dropped))
        m4.metric("Source", "Cached output" if r.source == "cached" else "Live AI")

        with st.expander("PRD summary, open questions and decisions", expanded=False):
            p = b.prd_summary
            st.markdown(f"**Problem:** {p.problem}")
            st.markdown("**Users:** " + ", ".join(p.users))
            st.markdown("**Goals:**\n" + "\n".join(f"- {g}" for g in p.goals))
            if p.non_goals:
                st.markdown("**Non-goals:**\n" + "\n".join(f"- {g}" for g in p.non_goals))
            st.markdown("**Epics:**\n" + "\n".join(f"- **{e.id}** {e.title}: {e.goal}" for e in b.epics))
            if b.open_questions:
                st.markdown("**Open questions:**\n" + "\n".join(
                    f"- {q.question}" + (f" _(owner: {q.owner_role})_" if q.owner_role else "")
                    for q in b.open_questions))
            if b.decisions:
                st.markdown("**Decisions:**\n" + "\n".join(f"- [{d.status}] {d.decision}" for d in b.decisions))

        if not b.stories:
            st.warning("Every generated story failed the evidence check. Nothing can be approved or exported.")

        for s in b.stories:
            findings = check_story(s, ss.notes_used)
            blocking = [f for f in findings if f.blocking]
            badge = "✅ Approved" if s.approved else ("⚠️ Needs fixes" if blocking else "⬜ Not approved")
            with st.expander(f"**{s.id} · {s.title}** — {s.moscow} · {s.points} pts · {badge}"):
                st.markdown(f"_{s.sentence()}_")
                for i, ac in enumerate(s.acceptance_criteria, start=1):
                    st.markdown(f"- **AC-{i}** Given {ac.given} · When {ac.when} · Then {ac.then}")
                st.caption(f'Evidence: "{s.evidence_quote}"'
                           + (f" · Depends on: {', '.join(s.depends_on)}" if s.depends_on else ""))
                for f in blocking:
                    st.error(f.message)
                if k(s.id, "approved") not in ss:
                    ss[k(s.id, "approved")] = s.approved
                st.checkbox("Approved", key=k(s.id, "approved"),
                            on_change=on_toggle_approval, args=(s.id,))
                with st.form(k(s.id, "form")):
                    st.markdown("**Edit story**")
                    st.text_input("Title", s.title, key=k(s.id, "title"))
                    a, b2, c = st.columns(3)
                    a.text_input("As a", s.role, key=k(s.id, "role"))
                    b2.text_input("I want", s.want, key=k(s.id, "want"))
                    c.text_input("So that", s.so_that, key=k(s.id, "so_that"))
                    rows = len(s.acceptance_criteria) + (1 if len(s.acceptance_criteria) < 4 else 0)
                    for i in range(1, rows + 1):
                        ac = s.acceptance_criteria[i - 1] if i <= len(s.acceptance_criteria) else None
                        g, w, t = st.columns(3)
                        g.text_input(f"AC-{i} Given", ac.given if ac else "", key=k(s.id, f"ac{i}_given"))
                        w.text_input(f"AC-{i} When", ac.when if ac else "", key=k(s.id, f"ac{i}_when"))
                        t.text_input(f"AC-{i} Then", ac.then if ac else "", key=k(s.id, f"ac{i}_then"))
                    st.caption("Clear all three fields of a criterion to remove it. 2–4 criteria required.")
                    q1, q2, q3 = st.columns([1, 1, 4])
                    q1.selectbox("MoSCoW", MOSCOW, index=MOSCOW.index(s.moscow), key=k(s.id, "moscow"))
                    q2.selectbox("Points", POINTS, index=POINTS.index(s.points), key=k(s.id, "points"))
                    q3.text_input("Evidence quote (must appear in the notes)", s.evidence_quote, key=k(s.id, "quote"))
                    st.form_submit_button("Save changes", on_click=on_save_edits, args=(s.id,))

        if r.dropped:
            st.subheader("Dropped stories")
            st.caption("Removed automatically because their evidence quote was not found in the notes.")
            st.dataframe(pd.DataFrame([{"ID": d.id, "Title": d.title, "Reason": d.reason} for d in r.dropped]),
                         hide_index=True, width="stretch")

# ---- 3 · Quality -----------------------------------------------------------
with tab_quality:
    if not backlog():
        st.info("Generate a backlog first.")
    else:
        findings = check_backlog(backlog(), ss.notes_used, ss.result.removed_dependencies)
        st.button("Re-check")  # checks run on every rerun; the button just triggers one
        if not findings:
            st.success("No quality findings. Every story passes the rule-based checks.")
        else:
            st.dataframe(pd.DataFrame([{
                "Story": f.story_id, "Criterion": f"AC-{f.criterion}" if f.criterion else "",
                "Rule": f.rule, "Blocks approval": "Yes" if f.blocking else "No", "Message": f.message,
            } for f in findings]), hide_index=True, width="stretch")
        st.caption("Rules: 2–4 Given/When/Then criteria, no empty parts, no vague words "
                   "(fast, easy, intuitive, user-friendly, seamless, properly…), evidence quote "
                   "found in the notes. Rules flag wording; the Product Owner still judges meaning.")

# ---- 4 · Prioritise --------------------------------------------------------
with tab_prior:
    if not backlog():
        st.info("Generate a backlog first.")
    else:
        stories = backlog().stories
        df = pd.DataFrame([{
            "ID": s.id, "Title": s.title, "MoSCoW": s.moscow,
            "Reach": s.reach, "Impact": s.impact, "Confidence": s.confidence, "Effort": s.effort,
            "RICE": rice_for_story(s).label(),
        } for s in stories])
        st.caption("Edit RICE inputs: Reach 1–10, Impact 0.25/0.5/1/2/3, Confidence 0–1, Effort 1–10. "
                   "Changing an approved story's inputs un-approves it.")
        st.data_editor(
            df, key="rice_editor", on_change=on_rice_edit, hide_index=True, width="stretch",
            disabled=["ID", "Title", "MoSCoW", "RICE"],
            column_config={
                "Reach": st.column_config.NumberColumn(min_value=1, max_value=10, step=1),
                "Impact": st.column_config.SelectboxColumn(options=list(IMPACT_VALUES)),
                "Confidence": st.column_config.NumberColumn(min_value=0.0, max_value=1.0, step=0.05),
                "Effort": st.column_config.NumberColumn(min_value=1, max_value=10, step=1),
            },
        )
        st.markdown("**Ranked by RICE** (RICE = Reach × Impact × Confidence ÷ Effort)")
        ranked = sorted(stories, key=lambda s: (rice_for_story(s).score is None, -(rice_for_story(s).score or 0)))
        st.dataframe(pd.DataFrame([{"Rank": i, "ID": s.id, "Title": s.title, "MoSCoW": s.moscow,
                                    "RICE": rice_for_story(s).label()} for i, s in enumerate(ranked, 1)]),
                     hide_index=True, width="stretch")

# ---- 5 · Export ------------------------------------------------------------
with tab_export:
    if not backlog():
        st.info("Generate a backlog first.")
    else:
        b = backlog()
        ready = export.exportable_stories(b, ss.notes_used)
        approved_but_blocked = [s.id for s in b.stories if s.approved and s not in ready]
        st.metric("Stories ready to export", f"{len(ready)} of {len(b.stories)}")
        if approved_but_blocked:
            st.warning("Approved but failing checks, so excluded: " + ", ".join(approved_but_blocked))
        if not ready:
            st.info("No approved stories yet. Approve stories on the Backlog tab. Nothing is exported until you do.")
        else:
            c1, c2 = st.columns(2)
            c1.download_button("⬇️ Download CSV", export.to_csv(b, ss.notes_used),
                               file_name="approved_backlog.csv", mime="text/csv", width="stretch")
            c2.download_button("⬇️ Download Markdown", export.to_markdown(b, ss.notes_used),
                               file_name="approved_backlog.md", mime="text/markdown", width="stretch")
            st.caption("Exports contain approved stories only, with acceptance criteria, priorities, "
                       "evidence and derived test cases. Jira export is not part of this release.")

# ---- 6 · Saved -------------------------------------------------------------
with tab_saved:
    if not storage.is_configured():
        st.info("Supabase is not configured (SUPABASE_URL / SUPABASE_ANON_KEY). Saving is disabled; "
                "everything else works.")
    else:
        if backlog():
            st.text_input("Project name", value="Demo workshop", key="project_name")
            st.button("Save approved stories", on_click=on_save_db)
        if st.button("Show saved stories"):
            try:
                rows = storage.list_saved()
                if rows:
                    st.dataframe(pd.DataFrame([{
                        "Saved at": r["saved_at"][:19].replace("T", " "), "Project": r["project"],
                        "ID": r["story_id"], "Title": r["payload"].get("title", ""),
                        "MoSCoW": r["payload"].get("moscow", ""),
                    } for r in rows]), hide_index=True, width="stretch")
                else:
                    st.info("Nothing saved yet.")
            except storage.StorageError as exc:
                st.error(str(exc))
