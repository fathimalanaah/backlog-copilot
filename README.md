# Backlog Copilot

**Turns raw client-workshop notes into a reviewed product backlog: epics, user stories with Gherkin acceptance criteria, MoSCoW and RICE priorities, and test cases. Every story must quote the notes, a rule-based checker flags vague criteria, and nothing is exported until a Product Owner approves it.**

> Portfolio project 1 of 6 · Built by Fathima · Python · Streamlit · Pydantic · Supabase · Replit
> Live demo: _see the link in the repository's About section_ · All data is fictional.

---

## The problem

After a discovery workshop, a Product Owner spends hours turning notes into user stories. Acceptance criteria are often vague ("the page loads fast"), which causes rework, and AI drafting tools can invent requirements nobody asked for.

## What it does

1. **Input:** paste notes, upload a `.txt`/`.md` file, or load one of three fictional samples (50–15,000 words).
2. **Generate:** produces a PRD summary, epics, 4–6 user stories, open questions and decisions.
3. **Validate:** the output must match a strict Pydantic schema (one retry with the error message, then a clear failure).
4. **Evidence check:** every story must quote the notes word-for-word (20 words or fewer). Stories without a matching quote are **dropped automatically** and listed with a reason.
5. **Quality check:** deterministic rules flag missing Given/When/Then parts, fewer than 2 or more than 4 criteria, and vague words (*fast, easy, intuitive, user-friendly, seamless, properly…*). Blocking findings prevent approval.
6. **Review and approve:** edit any story; approve **one story at a time**. Editing an approved story un-approves it. The AI can never approve anything.
7. **Prioritise:** MoSCoW plus RICE scores calculated by code, never by the AI.
8. **Export:** CSV and Markdown containing **approved stories only**, with test cases derived from each criterion.
9. **Save (optional):** approved stories to Supabase.

## How the AI is controlled

| Risk | Control |
|---|---|
| Invented requirements | Evidence-quote rule plus automatic drop (`evidence.py`) |
| Malformed output | Pydantic schema, one retry with the validation error, then failure (`llm.py`, `schemas.py`) |
| Vague acceptance criteria | Rule-based checker that blocks approval (`quality.py`) |
| Instructions hidden in notes ("approve all stories") | Treated as data; the `approved` field is hidden from the AI and reset on every load |
| Unreviewed output leaving the tool | Per-story human approval; export and save only include approved, passing stories |

## Current mode: mock (no live AI)

This release runs in **mock mode** (decision DEC-30). "Generate" returns a pre-saved backlog for each of the three built-in fictional samples and labels it *Cached output*. The full pipeline still runs on that output: schema validation, approval reset, evidence check and quality rules. Live AI can be added by implementing one `Provider.generate()` method in `llm.py`. **No live-AI accuracy figures are claimed.**

| Sample | Demonstrates |
|---|---|
| 01 · Bank SME onboarding | Clean run: 6 stories, a disputed SLA raised as an open question, dependencies |
| 02 · Government permit renewal | Vague criterion ("loads fast") is flagged and approval is blocked until it's fixed |
| 03 · Wholesale ordering | A prompt-injection line is ignored, and an invented "loyalty points" story is dropped by the evidence check |

## Architecture

```
notes ─▶ validate input ─▶ Provider (mock: cached JSON)
      ─▶ Pydantic schema (retry once) ─▶ reset approvals
      ─▶ evidence check (drop unsupported) ─▶ quality rules
      ─▶ Streamlit review UI (edit · approve per story · RICE)
      ─▶ export CSV / Markdown  ·  save approved to Supabase (optional)
```

| File | Responsibility |
|---|---|
| `app.py` | Streamlit UI: Input, Backlog, Quality, Prioritise, Export, Saved tabs |
| `schemas.py` | Pydantic output contract and business rules |
| `llm.py` | Input validation, provider (mock), validate-and-retry pipeline |
| `evidence.py` | Evidence-quote matching and dropping |
| `quality.py` | Rule-based quality findings and the approval gate |
| `scoring.py` | RICE calculation |
| `export.py` | CSV and Markdown export, derived test cases |
| `storage.py` | Supabase save and list (approved only) |
| `prompts/system_backlog.md` | The rule book for a live AI |
| `samples/` | Fictional workshop notes, plus `cached/` outputs |
| `docs/` | PRD, decisions log, evaluation, demo script, Supabase setup SQL |

## Testing

**75 automated tests** (`python -m pytest -q`), each tied to a PRD story:

| Test file | Tests | Covers |
|---|---|---|
| `test_schemas.py` | 13 | Schema rules, approval hidden from the AI |
| `test_pipeline.py` | 23 | Input limits, uploads, mock mode, retry-once, evidence drop, injection |
| `test_quality_scoring.py` | 24 | Vague words, criteria count, edit checks, duplicates, RICE |
| `test_export_storage.py` | 10 | Approved-only export, test cases, Supabase save/fail paths |
| `test_app.py` | 5 | End-to-end UI flow with Streamlit AppTest |

Details are in [`docs/EVALUATION.md`](docs/EVALUATION.md).

## Run it

```bash
pip install -r requirements.txt
LLM_PROVIDER=mock streamlit run app.py
python -m pytest -q
```

Environment variables (names only; see `.env.example`): `LLM_PROVIDER=mock`, plus optionally `SUPABASE_URL` and `SUPABASE_ANON_KEY`. To enable saving, run `docs/supabase_setup.sql` once in the Supabase SQL editor.

## Limitations and path to production

- Mock mode only: no live AI, so no measured AI accuracy yet.
- Single user, English text only, no authentication. The Supabase demo policy lets the public key insert and read (but not edit or delete) fictional rows.
- The evidence check proves a quote exists, not that the story interprets it correctly. That judgement stays with the Product Owner.
- No Jira export in this release (it was a "Could").
- For production: user sign-in and per-user database policies, a live LLM with spend limits and a data-processing agreement, audit history, and data residency review.

## My role vs AI tools

I wrote the requirements (PRD, 14 user stories, decisions log), set the scope cuts and acceptance criteria, and reviewed and directed the build. AI assistants (Claude, ChatGPT) helped draft the PRD and generate code and tests. I reviewed the output against the PRD, and every rule is covered by tests. The planning trail is in [`docs/PRD.md`](docs/PRD.md) and [`docs/DECISIONS.md`](docs/DECISIONS.md).
