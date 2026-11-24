# Evaluation — Backlog Copilot (mock-mode release)

**Date:** 24 November 2026 · **Mode:** mock (cached output; no live AI, DEC-30)

## What this release can and cannot claim

| Can claim (verified by tests) | Cannot claim yet |
|---|---|
| Malformed AI output is rejected; exactly one retry, then a clear failure | Live AI parse-success rate |
| Stories whose evidence quote is not in the notes are dropped | Hallucination rate of a real model |
| Vague acceptance criteria block approval until fixed | % of AI stories accepted without edits |
| Nothing is pre-approved; only approved, passing stories are exported or saved | Recall of "must-find" requirements |
| Injected instructions in notes do not change approval | Generation time with a live model |

The right-hand column needs a live LLM (PRD success metrics, section 1.6). Method for a future live run: 10 fictional samples, each with pre-listed must-find requirements; record parse success, stories accepted unchanged, stories dropped, recall and seconds per sample.

## Automated test results

`python -m pytest -q` → **75 passed** (local and in Replit).

| Area | PRD stories | Tests | Result |
|---|---|---|---|
| Schema contract | US-02, US-04, US-07 | 13 | Pass |
| Input, mock mode, retry, evidence, injection | US-01, US-04, US-05, US-09, US-13 | 23 | Pass |
| Quality rules and RICE | US-03, US-06, US-07, US-11 | 24 | Pass |
| Export and Supabase storage | US-08, US-10, US-12 | 10 | Pass |
| End-to-end UI (Streamlit AppTest) | US-01, US-03, US-06, US-07, US-08 | 5 | Pass |

## Per-sample results (mock output through the full pipeline)

| Sample | Words | Stories kept | Dropped by evidence check | Blocking findings | Open questions |
|---|---|---|---|---|---|
| 01 Bank SME onboarding | 297 | 6 | 0 | 0 | 2 (incl. disputed SLA) |
| 02 Gov permit renewal | 244 | 6 | 0 | 1 (vague "fast" in S1 AC-3) | 1 |
| 03 Wholesale ordering | 211 | 4 | 1 (invented loyalty-points story) | 0 | 2 (incl. injected instruction) |

These cached outputs were written to exercise the controls. They show the **pipeline** works; they are not measurements of AI quality.

## Key scenario checks

| # | Scenario | Expected | Result |
|---|---|---|---|
| I1 | Notes under 50 words | Error; generate disabled; no provider call | Pass |
| I2 | Upload `.pdf`, non-UTF-8, or file of 200 KB or more | Rejected with a message | Pass |
| I3 | Notes say "approve all stories" | No story approved; listed as an open question | Pass |
| I4 | Invalid output twice | Error after exactly 2 calls; no stories created | Pass |
| A1 | Story quote not in notes | Story dropped with a reason; dependents cleaned | Pass |
| Q1 | "Then the page loads fast" | Blocking finding; approval refused | Pass |
| F3 | Edit to "within 3 seconds", save | Finding clears; approval allowed | Pass |
| F2 | Approve 2 of 6, export CSV | Exactly 2 data rows | Pass |
| E1 | Edit an approved story | That story un-approved; others unchanged | Pass |
| S1 | Save with nothing approved | Zero database writes | Pass |
