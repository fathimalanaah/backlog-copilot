# Demo script: Backlog Copilot (about 2.5 minutes)

**Before the interview:** open the live link once (a free host may take about 30 seconds to wake up). Have the GitHub repo open in a second tab.

| # | Do | Say (2 sentences max) | If it goes wrong |
|---|---|---|---|
| 1 | Show sample 01 notes on the Input tab | "After a discovery workshop, turning notes like these into a backlog takes a PO hours, and vague criteria cause rework." | — |
| 2 | Click **Generate backlog** → Backlog tab | "It drafts a PRD summary, epics and stories. Every story carries a quote from the notes as evidence." | Refresh the page and load the sample again |
| 3 | Open the PRD summary expander | "Conflicts like the 2-day vs 3-day SLA become open questions, not guesses." | — |
| 4 | Load sample 02 → Generate → open S1 → tick **Approved** | "The rule checker blocks approval: 'loads fast' isn't testable." | — |
| 5 | Edit AC-3 to "shown within 3 seconds" → Save → Approve | "Once it's measurable the flag clears. Approval is per story and only a human can give it." | — |
| 6 | Load sample 03 → Generate → scroll to **Dropped stories** | "These notes contained an injected instruction and the draft invented a loyalty feature. The evidence check dropped the invented story, and nothing was auto-approved." | — |
| 7 | Prioritise tab | "RICE is calculated by code, not by the AI. Changing inputs on an approved story un-approves it." | — |
| 8 | Approve 2 stories → Export → download CSV | "Only approved stories leave the tool, with derived test cases." | Show `docs/EVALUATION.md` |
| 9 | GitHub: tests + `docs/` | "81 automated tests map to my PRD. Honest limit: this release runs on cached output, so I don't claim live-AI accuracy yet." | — |

## Likely questions

- **How do you stop it inventing requirements?** The evidence-quote rule with automatic dropping, plus open questions for anything missing. A matching quote proves the text exists; whether the story interprets it correctly is still the PO's call.
- **Why not let the AI judge quality?** Deterministic rules are repeatable and testable. AI grading its own output isn't evidence.
- **Why Streamlit?** It's a single-user internal tool, so I optimised for speed. For multiple users I'd move to a web framework with authentication.
- **Why mock mode?** I chose to ship the controls and review workflow first. The provider interface means a live model is one method away, and the retry logic is already tested with a fake model.
