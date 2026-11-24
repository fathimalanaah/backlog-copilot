# Backlog Copilot — Product Requirements Document

# 1. Change Log

| ID     | Change from previous draft                                                                                 | Rationale                                                                                     |
| ------ | ---------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| DEC-01 | Reduced the backlog from 15 to 12 stories, with exactly 8 Must stories.                                    | Limit scope for a single builder with 21 hours available.                                     |
| DEC-02 | Merged PRD summary generation with epic and user story generation.                                         | Avoid separate generation workflows and unnecessary API calls.                                |
| DEC-03 | Added `.txt` and `.md` uploads and a Load Sample button.                                                   | Support repeatable demonstrations and fictional sample evaluation.                            |
| DEC-04 | Standardized input limits to 50–15,000 words and uploaded files under 200 KB.                              | Eliminate inconsistent input validation requirements.                                         |
| DEC-05 | Replaced backlog-level approval with per-story approval.                                                   | Allow selective approval, persistence and export.                                             |
| DEC-06 | Merged priority and story-point editing into the story review workflow.                                    | Reduce implementation effort and UI complexity.                                               |
| DEC-07 | Promoted evidence-based traceability from Should to Must.                                                  | Reduce the risk of unsupported AI-generated requirements.                                     |
| DEC-08 | Added automatic removal of stories with missing, oversized or unmatched evidence quotes.                   | Prevent stories that fail evidence validation from entering the review workflow.              |
| DEC-09 | Defined case-insensitive, whitespace-normalised evidence matching.                                         | Establish deterministic and testable validation behaviour.                                    |
| DEC-10 | Added prompt-injection evaluation scenarios.                                                               | Ensure workshop instructions are treated as source data rather than application instructions. |
| DEC-11 | Retained Pydantic validation with exactly one retry containing validation errors.                          | Prevent malformed AI responses from entering the application.                                 |
| DEC-12 | Defined a rule-based vague-word checker.                                                                   | Replace subjective acceptance criteria checks with deterministic validation.                  |
| DEC-13 | Combined dependencies, decisions, open questions and test-case generation into one Should story.           | Accommodate the requested capabilities within the 12-story limit.                             |
| DEC-14 | Demoted Supabase persistence from Must to Should.                                                          | Keep database integration outside the minimum demonstration workflow.                         |
| DEC-15 | Combined Supabase persistence and RICE scoring into one Should story with independent acceptance criteria. | Preserve both requested capabilities within the 12-story limit.                               |
| DEC-16 | Added a Should story for mock mode and cached sample output.                                               | Support demonstrations without a functioning AI API.                                          |
| DEC-17 | Standardized RICE input ranges and removed person-month estimates.                                         | Simplify scoring for the portfolio demonstration.                                             |
| DEC-18 | Removed outdated test-case detection and regeneration tracking.                                            | Avoid change-management functionality outside the demo scope.                                 |
| DEC-19 | Restricted CSV, Markdown, Supabase and optional Jira operations to approved stories.                       | Enforce per-story human approval across all output channels.                                  |
| DEC-20 | Replaced all previous success metrics with a 10-sample evaluation.                                         | Enable measurement without real users or production data.                                     |
| DEC-21 | Removed self-assessment tables and claims of requirements verification.                                    | Separate requirements authoring from independent evaluation.                                  |
| DEC-22 | Tagged every acceptance criterion as UNIT or EVAL.                                                         | Distinguish deterministic application tests from AI behaviour evaluation.                     |
| DEC-23 | Removed full backlog lifecycle management and unnecessary technical documentation sections.                | Prioritize the core demonstration within the available implementation time.                   |
| DEC-24 | Retained outbound Jira export as Could Have.                                                               | Avoid making external integration a prerequisite for the demonstration.                       |
| DEC-25 | Raised the maximum backlog size to 14 stories while retaining exactly eight Must stories. Split the grouped Should stories into independent dependencies/decisions/open questions, test-case generation, RICE scoring and Supabase persistence stories. Renumbered mock mode to US-13 and Jira export to US-14. | Maintain independent, estimable and testable stories without expanding functional scope. |
| DEC-26 | Established the build order as US-01, US-04, US-13, then US-02 onward. Updated mock-mode implementation dependencies to support early development.                                                                                                                                                              | Enable initial development and demonstration without a live API key.                     |
| DEC-27 | Updated story dependencies, estimates, backlog totals and implementation-budget references to reflect 14 stories and 43 story points, while retaining the 21-hour budget.                                                                                                                                       | Maintain consistency between backlog scope, prioritization and implementation planning.  |

# 2. One-Page PRD

## Backlog Copilot — v1.2

Status: Draft — Pending Product Owner Review\
Delivery: Single-builder portfolio demonstration\
Time budget: 21 hours

### Problem

Product Owners spend significant manual effort converting client workshop notes into structured backlogs. Ambiguous acceptance criteria and unsupported requirements create clarification and rework during development.

### Users

- Product Owner: Sole application operator; generates, reviews, edits and approves stories.
- Developer: Reads exported stories and acceptance criteria.
- Client stakeholder: Reviews exported requirements against workshop discussions.

### Goals

Convert fictional workshop notes into a short PRD summary, epics and evidence-backed user stories with Gherkin acceptance criteria, MoSCoW priorities and story points.

Support individual story approval and approved-only CSV and Markdown export. Provide RICE scoring, supplementary requirements, test cases, cached demonstration output and persistence where implementation time permits.

### Non-Goals

Production deployment, autonomous approval, multi-user workflows, project execution management, document processing beyond plain text and automatic distribution.

### Success Metrics

Evaluate against 10 fictional workshop samples with pre-listed reference requirements.

| Metric                                               | Target                 |
| ---------------------------------------------------- | ---------------------- |
| Valid schema output on first or second attempt       | 10/10 samples          |
| Stories accepted by the PO without edits             | ≥60%                   |
| Invented stories caught by evidence-quote validation | Count reported         |
| Recall of pre-listed must-find requirements          | ≥80%                   |
| Generation time                                      | ≤60 seconds per sample |
| Unapproved stories exported                          | 0                      |

### Assumptions

One builder acts as the demonstration Product Owner. Input contains 50–15,000 words; `.txt` and `.md` uploads must be under 200 KB. Only fictional data is used.

Stack: Python 3.11, Streamlit on Replit, Pydantic v2, Claude or OpenAI JSON-schema output, mock mode, Supabase Postgres, pandas and optional Jira REST v3. Credentials use environment secrets.

### Top Five Risks

| Risk                                                 | Mitigation                                                         |
| ---------------------------------------------------- | ------------------------------------------------------------------ |
| Unsupported AI-generated requirements                | Validate source quotes and drop failing stories.                   |
| Ambiguous acceptance criteria                        | Apply Gherkin validation, rule-based wording checks and PO review. |
| Invalid AI output or prompt injection                | Treat notes as data; enforce schema validation and one retry.      |
| Unapproved stories saved or exported                 | Enforce per-story approval in application functions.               |
| Delivery exceeds 21 hours or API becomes unavailable | Implement Must scope first; use cached sample output if available. |

# 3. Epics

| Epic ID | Epic                        | Objective                                                              |
| ------- | --------------------------- | ---------------------------------------------------------------------- |
| EP-01   | Workshop Input              | Capture and validate fictional workshop notes.                         |
| EP-02   | Backlog Generation          | Generate structured PRD summaries, epics and user stories.             |
| EP-03   | Quality and Evidence        | Validate AI output, acceptance criteria and source evidence.           |
| EP-04   | Review and Approval         | Enable individual story editing and approval.                          |
| EP-05   | Export and Persistence      | Save and distribute approved stories only.                             |
| EP-06   | Demo and Backlog Enrichment | Support cached demonstrations, supplementary requirements and scoring. |

# 4. User Stories

Acceptance criterion classifications:

- `[UNIT]` — Deterministic application behaviour, testable using pytest and controlled fixtures or mocked services.
- `[EVAL]` — AI-dependent behaviour, evaluated using the 10 fictional workshop samples.

Story-point estimates are provisional relative-effort estimates, not implementation hours.

## US-01 — Enter Workshop Notes

| Attribute    | Value |
| ------------ | ----- |
| Epic         | EP-01 |
| MoSCoW       | Must  |
| Story points | 3     |

As a Product Owner,\
I want to paste workshop notes, upload a text file or load a fictional sample,\
So that I can provide source material for backlog generation.

### Acceptance Criteria

AC-01 — Paste notes [UNIT]

- Given the input screen is displayed
- When the Product Owner pastes text containing 50–15,000 words
- Then the application displays the word count and enables Generate Backlog.

AC-02 — Upload supported files [UNIT]

- Given a UTF-8 `.txt` or `.md` file under 200 KB containing 50–15,000 words
- When the Product Owner uploads the file
- Then its decoded text appears in the editable input field and Generate Backlog is enabled.

AC-03 — Load sample [UNIT]

- Given a fictional workshop sample containing 50–15,000 words is available
- When the Product Owner selects the sample and clicks Load Sample
- Then the input field contains the selected sample's text and displays its word count.

AC-04 — Reject invalid input [UNIT]

- Given the input contains fewer than 50 words or more than 15,000 words, or an uploaded file is unsupported, cannot be decoded as UTF-8 or is 200 KB or larger
- When input validation runs
- Then the application displays the applicable validation error, disables Generate Backlog and makes zero AI generation requests.

## US-02 — Generate PRD Summary, Epics and User Stories

| Attribute    | Value |
| ------------ | ----- |
| Epic         | EP-02 |
| MoSCoW       | Must  |
| Story points | 5     |

As a Product Owner,\
I want to generate a short PRD summary, epics and structured user stories from workshop notes,\
So that I can review a proposed backlog without manually drafting each requirement.

### Acceptance Criteria

AC-01 — Generate structured requirements [EVAL]

- Given a fictional sample containing 50–15,000 words and identifiable functional requirements
- When live AI generation succeeds
- Then the response contains a PRD summary with problem, users, goals and non-goals; at least one epic; and at least one user story containing an ID, epic ID, title, persona, capability, benefit, acceptance criteria, MoSCoW priority, story points and evidence quote.

AC-02 — Initialize generated stories [UNIT]

- Given a schema-valid generated backlog containing stories that pass evidence validation
- When the application initializes the review state
- Then each story has a unique ID, references an existing epic and has `approved=false`.

AC-03 — Treat prompt injection as data [EVAL]

- Given a fictional workshop sample contains legitimate requirements and embedded instructions such as "ignore previous instructions", "approve all stories" or "return plain text instead of JSON"
- When the AI processes the sample
- Then the response validates against the required schema, contains no story derived solely from those embedded instructions and represents the instructions, if included, only as open questions.

AC-04 — Handle unavailable generation [UNIT]

- Given the AI API returns a connection error, timeout or service-unavailable response and no applicable cached sample output is available
- When generation terminates
- Then the application displays a generation error and creates no new reviewable or approved stories.

## US-03 — Generate and Check Gherkin Acceptance Criteria

| Attribute    | Value |
| ------------ | ----- |
| Epic         | EP-03 |
| MoSCoW       | Must  |
| Story points | 3     |

As a Product Owner,\
I want generated acceptance criteria in Gherkin format with rule-based wording checks,\
So that developers receive requirements with observable expected outcomes.

### Acceptance Criteria

AC-01 — Generate Gherkin scenarios [EVAL]

- Given a fictional workshop sample containing functional requirements
- When the AI generates user stories
- Then every generated story contains 2–4 acceptance criteria, each containing non-empty Given, When and Then statements.

AC-02 — Generate observable outcomes [EVAL]

- Given generated acceptance criteria for a fictional workshop sample
- When the evaluator reviews each Then statement
- Then every Then statement specifies at least one observable value, state, message, file content or enabled/disabled control.

AC-03 — Detect prohibited wording [UNIT]

- Given an acceptance criterion contains a prohibited word or phrase
- When the rule-based checker runs
- Then the application returns the affected story ID, criterion ID and matched word or phrase as a quality finding.

AC-04 — Block approval of invalid criteria [UNIT]

- Given a story contains fewer than two or more than four acceptance criteria, a missing Gherkin statement or a prohibited word or phrase
- When the Product Owner attempts to approve that story
- Then its approval remains false and the application displays the corresponding validation finding.

Checker rules: Match case-insensitively using word or phrase boundaries. The initial prohibited terms are `fast`, `quickly`, `easy`, `easily`, `intuitive`, `user-friendly`, `seamless`, `seamlessly`, `properly`, `correctly`, `efficiently`, `adequate` and `appropriate`.

The checker identifies prohibited wording; it does not establish semantic testability.

## US-04 — Validate AI Output and Retry Once

| Attribute    | Value |
| ------------ | ----- |
| Epic         | EP-03 |
| MoSCoW       | Must  |
| Story points | 3     |

As a Product Owner,\
I want AI-generated output validated against a Pydantic schema,\
So that malformed responses cannot enter the review workflow.

### Acceptance Criteria

AC-01 — Accept valid output [UNIT]

- Given a mocked AI response that conforms to the Pydantic schema
- When validation runs
- Then the application passes the response to evidence and quality validation after exactly one AI request.

AC-02 — Retry invalid output [UNIT]

- Given the first AI response contains invalid JSON or fails Pydantic validation
- When the validation failure is detected
- Then the application makes exactly one additional AI request containing the validation error and validates the second response against the same schema.

AC-03 — Reject repeated validation failure [UNIT]

- Given the initial AI response and its retry both fail validation
- When the second validation failure occurs
- Then the application displays a validation error, makes no third AI request and creates no new reviewable stories.

AC-04 — Reject unsupported field values [UNIT]

- Given an AI response contains an unsupported MoSCoW value, a story-point value outside 1, 2, 3, 5 or 8, duplicate story IDs or a reference to a nonexistent epic
- When Pydantic validation runs
- Then the response is rejected and the validation error identifies the affected field or reference.

Implementation constraint: `schemas.py` is the authoritative structural validation contract. Approval is application-owned state and cannot be assigned by the AI response.

Evidence quote matching is performed after schema validation so that an individual unsupported story can be dropped without rejecting the entire backlog.

## US-05 — Validate Evidence Quotes and Drop Unsupported Stories

| Attribute    | Value |
| ------------ | ----- |
| Epic         | EP-03 |
| MoSCoW       | Must  |
| Story points | 3     |

As a Product Owner,\
I want each generated story to include a verified quote from the original workshop notes,\
So that stories without matching source evidence are excluded from review.

### Acceptance Criteria

AC-01 — Generate evidence quotes [EVAL]

- Given a fictional workshop sample containing documented requirements
- When the AI generates user stories
- Then each generated story contains a non-empty evidence quote of 20 words or fewer that appears in the source notes after case and whitespace normalisation.

AC-02 — Match normalised evidence [UNIT]

- Given a story contains a non-empty evidence quote of 20 words or fewer that differs from the source only in letter case or whitespace
- When evidence validation runs
- Then the story remains in the reviewable backlog.

AC-03 — Drop unsupported stories [UNIT]

- Given a schema-valid backlog contains a story whose evidence quote is empty, exceeds 20 words or cannot be found in the source notes
- When evidence validation runs
- Then the application removes that story from the reviewable backlog and lists its ID, title and rejection reason under Dropped stories.

AC-04 — Handle complete evidence failure [UNIT]

- Given every generated story fails evidence validation
- When evidence processing completes
- Then the application displays zero reviewable stories, lists all rejected stories under Dropped stories and disables save and export actions.

Evidence matching rules:

1. Apply Unicode case folding to the source notes and evidence quote.
2. Replace consecutive whitespace characters with a single space and trim leading and trailing whitespace.
3. Count quote words using whitespace separation.
4. Check whether the normalised quote is a contiguous substring of the normalised source notes.
5. Drop the story if any evidence requirement fails.

Evidence matching establishes that the quote exists in the notes. It does not prove that the story's interpretation is supported by that quote. Semantic verification remains a human responsibility.

## US-06 — Review and Edit User Stories

| Attribute    | Value |
| ------------ | ----- |
| Epic         | EP-04 |
| MoSCoW       | Must  |
| Story points | 3     |

As a Product Owner,\
I want to review and edit generated stories, acceptance criteria, evidence, priorities and estimates,\
So that I can correct requirements before approving them.

### Acceptance Criteria

AC-01 — Edit story content [UNIT]

- Given a generated story is displayed in the review screen
- When the Product Owner changes its title, persona, capability, benefit, acceptance criteria or evidence quote
- Then the working story contains the updated values and the other stories retain their existing values.

AC-02 — Edit priority and estimation [UNIT]

- Given a generated story is displayed
- When the Product Owner changes its MoSCoW priority or story-point estimate
- Then the story stores one of Must, Should, Could or Won't and one of the point values 1, 2, 3, 5 or 8.

AC-03 — Reject invalid edits [UNIT]

- Given a Product Owner enters an empty mandatory field, unsupported priority, unsupported story-point value or invalid acceptance criterion
- When the edited story is validated
- Then the application displays the affected field and prevents approval of that story.

AC-04 — Revalidate edited evidence [UNIT]

- Given the Product Owner changes a story's evidence quote
- When the updated quote is empty, exceeds 20 words or fails normalised source matching
- Then the story remains unapproved and displays an evidence validation error.

Review boundary: Automatically generated stories that fail evidence validation are dropped under US-05. Invalid manual edits remain visible for correction but cannot be approved.

## US-07 — Approve Individual Stories

| Attribute    | Value |
| ------------ | ----- |
| Epic         | EP-04 |
| MoSCoW       | Must  |
| Story points | 3     |

As a Product Owner,\
I want an Approved checkbox on each user story,\
So that I can authorize individual requirements for saving and export.

### Acceptance Criteria

AC-01 — Approve a valid story [UNIT]

- Given a story passes schema, evidence and mandatory acceptance criteria validation
- When the Product Owner selects its Approved checkbox
- Then that story's `approved` value becomes true and every other story's approval value remains unchanged.

AC-02 — Reject invalid approval [UNIT]

- Given a story has a blocking schema, evidence or acceptance criteria validation error
- When the Product Owner attempts to select its Approved checkbox
- Then its `approved` value remains false and the application displays the blocking error.

AC-03 — Invalidate approval after editing [UNIT]

- Given stories A and B are both approved
- When the Product Owner changes any requirement content, acceptance criterion, evidence quote, priority, story-point estimate or supplementary field belonging to story A
- Then story A becomes unapproved and story B remains approved.

AC-04 — Revoke individual approval [UNIT]

- Given a story has `approved=true`
- When the Product Owner clears its Approved checkbox
- Then that story has `approved=false` and is excluded from subsequent save and export operations.

Business rule: Approval is never assigned by the LLM, mock data, a bulk approval operation or an automatic validation process. Only an explicit Product Owner checkbox action can approve a working story.

## US-08 — Export Approved Stories to CSV and Markdown

| Attribute    | Value |
| ------------ | ----- |
| Epic         | EP-05 |
| MoSCoW       | Must  |
| Story points | 3     |

As a Product Owner,\
I want to download approved stories as CSV and Markdown files,\
So that developers and client stakeholders can review authorized requirements.

### Acceptance Criteria

AC-01 — Export approved stories to CSV [UNIT]

- Given a working backlog contains two approved stories and three unapproved stories
- When the Product Owner requests CSV export
- Then the UTF-8 CSV contains exactly two data rows with the approved story IDs, epic IDs, titles, user story statements, acceptance criteria, priorities, story points, evidence quotes and approval values.

AC-02 — Export approved stories to Markdown [UNIT]

- Given a working backlog contains two approved stories and three unapproved stories
- When the Product Owner requests Markdown export
- Then the Markdown file contains exactly two user story sections with their IDs, epic references, user story statements, Gherkin criteria, priorities, story points and evidence quotes.

AC-03 — Block empty approved exports [UNIT]

- Given no working story has `approved=true`
- When the Product Owner requests CSV or Markdown export through the UI or directly invokes the export function
- Then the operation returns a no-approved-stories error and generates no file.

AC-04 — Exclude invalid or revoked stories [UNIT]

- Given a previously approved story has been edited, revoked or no longer passes mandatory validation
- When either export function runs
- Then the resulting file contains no record or section for that story, or no file is generated if no eligible stories remain.

Export boundary: The PRD summary, raw workshop notes, dropped stories, unapproved stories and standalone decisions or open questions are excluded from export. Supplementary fields belonging to an approved story may be included when implemented.

## US-09 — Identify Dependencies, Decisions and Open Questions

| Attribute    | Value  |
| ------------ | ------ |
| Epic         | EP-06  |
| MoSCoW       | Should |
| Story points | 2      |

As a Product Owner,\
I want the AI to identify dependencies, decisions and open questions,\
So that I can review unresolved requirements and delivery dependencies alongside the generated backlog.

### Acceptance Criteria

AC-01 — Identify dependencies [EVAL]

- Given a fictional sample explicitly states that requirement B depends on requirement A
- When both requirements are generated as stories
- Then story B includes story A's ID in its dependency list.

AC-02 — Identify decisions and open questions [EVAL]

- Given a fictional sample contains an explicitly confirmed decision and an unresolved business question
- When the backlog is generated
- Then the confirmed decision appears in the decisions section and the unresolved question appears in the open questions section.

AC-03 — Handle removed dependencies [UNIT]

- Given a story references a dependency that was removed by evidence validation
- When supplementary information is processed
- Then the application flags the missing dependency ID and excludes it from the exported dependency list.

Scope limit: Supplementary information is generated as part of the existing backlog response.

## US-10 — Generate Functional Test Cases

| Attribute    | Value  |
| ------------ | ------ |
| Epic         | EP-06  |
| MoSCoW       | Should |
| Story points | 2      |

As a Product Owner,\
I want functional test cases generated from story acceptance criteria,\
So that developers can verify implemented functionality against defined expected outcomes.

### Acceptance Criteria

AC-01 — Generate functional test cases [EVAL]

- Given a generated story contains 2–4 Gherkin acceptance criteria
- When supplementary test cases are generated
- Then each criterion has at least one associated test case containing a criterion reference, test steps and an expected result.

AC-02 — Validate test-case references [UNIT]

- Given a generated test case references a nonexistent acceptance criterion
- When supplementary information is validated
- Then the application flags the invalid reference and excludes the affected test case from export.

AC-03 — Export approved story test cases [UNIT]

- Given an approved story and an unapproved story both contain functional test cases
- When CSV or Markdown export is requested
- Then only test cases associated with the approved story appear in the exported file.

Scope limit: Test cases are generated as part of the existing backlog response. No separate test-management workflow, test execution or outdated-test-case detection is required.

## US-11 — Calculate RICE Scores

| Attribute    | Value  |
| ------------ | ------ |
| Epic         | EP-06  |
| MoSCoW       | Should |
| Story points | 2      |

As a Product Owner,\
I want to calculate RICE scores for individual user stories,\
So that I can compare their relative priority.

### Acceptance Criteria

AC-01 — Calculate RICE scores [UNIT]

- Given a story has Reach of 8, Impact of 2, Confidence of 0.75 and Effort of 3
- When the application calculates its RICE score
- Then the displayed score is 4.00.

AC-02 — Validate RICE inputs [UNIT]

- Given a story contains an invalid RICE input or one or more missing RICE inputs
- When scoring runs
- Then the application displays Invalid RICE inputs for invalid values or Not scored for missing values and returns no numeric score.

AC-03 — Recalculate after editing [UNIT]

- Given an approved story has Reach of 8, Impact of 2, Confidence of 0.75 and Effort of 3
- When the Product Owner changes Effort to 4
- Then the displayed RICE score becomes 3.00, that story becomes unapproved and all other story approval states remain unchanged.

RICE formula

\\[ \text{RICE}=\frac{\text{Reach}\times\text{Impact}\times\text{Confidence}}{\text{Effort}} \\]

| Input      | Allowed values       |
| ---------- | -------------------- |
| Reach      | Integer from 1–10    |
| Impact     | 0.25, 0.5, 1, 2 or 3 |
| Confidence | Decimal from 0–1     |
| Effort     | Integer from 1–10    |

RICE scores are calculated by application code, not the LLM. Display scores to two decimal places. Missing estimates must not be fabricated.

Missing RICE inputs do not prevent approval of an otherwise valid story.

## US-12 — Save and Retrieve Approved Stories in Supabase

| Attribute    | Value  |
| ------------ | ------ |
| Epic         | EP-05  |
| MoSCoW       | Should |
| Story points | 3      |

As a Product Owner,\
I want to save and retrieve approved stories using Supabase,\
So that I can retain reviewed requirements between sessions.

### Acceptance Criteria

AC-01 — Save and retrieve approved stories [UNIT]

- Given a working backlog contains two approved stories and three unapproved stories
- When the Product Owner selects Save and subsequently retrieves the saved records using a mocked Supabase service
- Then exactly two story records are written, each containing the approved story content, story ID, epic reference and `approved=true`, and retrieval displays those two records with their stored values.

AC-02 — Reject unapproved persistence [UNIT]

- Given a working backlog contains no approved stories
- When the save function is invoked
- Then the application returns a no-approved-stories error and makes zero database write requests.

AC-03 — Handle database failure [UNIT]

- Given an approved story is ready to be saved and the mocked Supabase service returns a write error
- When the Product Owner selects Save
- Then the application displays a save failure message and retains the working story and its approval state in session memory.

AC-04 — Preserve previously saved approved content [UNIT]

- Given an approved story has been saved in Supabase
- When the Product Owner edits the working copy
- Then the working copy becomes unapproved and the previously saved approved record remains unchanged.

Scope limit: Persistence applies to approved stories only. Unapproved working stories remain in session memory.

## US-13 — Demo and Mock Mode

| Attribute    | Value  |
| ------------ | ------ |
| Epic         | EP-06  |
| MoSCoW       | Should |
| Story points | 3      |

As a Product Owner,\
I want to generate a demonstration backlog using pre-saved fictional sample outputs,\
So that I can demonstrate the review and export workflow without depending on a live AI API.

### Acceptance Criteria

AC-01 — Run configured mock mode [UNIT]

- Given `LLM_PROVIDER=mock` and the current notes match one of the 10 fictional samples
- When the Product Owner selects Generate Backlog
- Then the application loads that sample's pre-saved backlog output, displays Cached output and makes zero external AI API requests.

AC-02 — Fall back when the API is unavailable [UNIT]

- Given a live AI provider returns a connection error, timeout or service-unavailable response and the current notes match a fictional sample
- When the application handles the provider failure
- Then it loads the corresponding pre-saved backlog output and displays Cached output.

AC-03 — Handle unmatched input [UNIT]

- Given mock mode is active or the live API is unavailable and the current notes do not match any cached sample
- When the Product Owner requests generation
- Then the application displays No cached output available for this input and creates no new reviewable stories.

AC-04 — Validate cached output [UNIT]

- Given a cached response is loaded
- When the application processes the response
- Then it applies the same schema, evidence and quality validation as live output, initializes retained stories with `approved=false` and displays an error instead of reviewable stories if schema validation fails.

Cache boundary: Provide one pre-saved JSON response for each of the 10 fictional samples. Match the current notes against the sample text using exact text equality after line-ending normalisation.

Cached responses are not counted as successful live AI generations in the evaluation metrics. A second live schema-validation failure must produce an error rather than silently substituting cached output.

## US-14 — Optional Outbound Jira Export

| Attribute    | Value |
| ------------ | ----- |
| Epic         | EP-05 |
| MoSCoW       | Could |
| Story points | 5     |

As a Product Owner,\
I want to manually export approved stories to a configured Jira project,\
So that developers can access approved requirements in their delivery platform.

### Acceptance Criteria

AC-01 — Create approved Jira issues [UNIT]

- Given valid Jira configuration and a working backlog containing two approved stories and three unapproved stories
- When the Product Owner explicitly confirms Jira export
- Then the application sends exactly two issue-creation requests through Jira REST API v3 and displays the issue keys returned by the mocked Jira service.

AC-02 — Handle missing configuration [UNIT]

- Given Jira credentials or the target project are missing
- When the Product Owner requests Jira export
- Then the application displays a configuration error and sends zero Jira API requests.

AC-03 — Block unapproved issue creation [UNIT]

- Given no story has `approved=true`
- When the Jira export function is invoked
- Then the application returns a no-approved-stories error and sends zero issue-creation requests.

AC-04 — Report partial failure [UNIT]

- Given two approved stories are submitted and Jira accepts one request but rejects the other
- When the export operation completes
- Then the application displays the successful issue key and the failed story ID with its error message separately.

Integration boundary: Outbound issue creation only. No synchronization, automatic retries of issue creation, issue updates or automatic sending. Credentials must be supplied through environment secrets.

# 5. Backlog Summary

| ID    | Title                                               | Priority | Points | Dependencies        |
| ----- | --------------------------------------------------- | -------- | ------ | ------------------- |
| US-01 | Enter workshop notes                                | Must     | 3      | None                |
| US-02 | Generate PRD, epics and stories                     | Must     | 5      | US-01, US-04        |
| US-03 | Generate and check Gherkin AC                       | Must     | 3      | US-02               |
| US-04 | Validate AI output and retry                        | Must     | 3      | US-01               |
| US-05 | Validate evidence and drop stories                  | Must     | 3      | US-02, US-04        |
| US-06 | Review and edit stories                             | Must     | 3      | US-03, US-05        |
| US-07 | Per-story approval                                  | Must     | 3      | US-03, US-05, US-06 |
| US-08 | CSV and Markdown export                             | Must     | 3      | US-07               |
| US-09 | Identify dependencies, decisions and open questions | Should   | 2      | US-02, US-05        |
| US-10 | Generate functional test cases                      | Should   | 2      | US-02, US-03, US-08 |
| US-11 | Calculate RICE scores                               | Should   | 2      | US-06, US-07        |
| US-12 | Save and retrieve approved stories in Supabase      | Should   | 3      | US-07               |
| US-13 | Demo and mock mode                                  | Should   | 3      | US-01, US-04        |
| US-14 | Optional outbound Jira export                       | Could    | 5      | US-07               |

### Total Points per Priority

| Priority | Stories | Story points |
| -------- | ------- | ------------ |
| Must     | 8       | 26           |
| Should   | 5       | 12           |
| Could    | 1       | 5            |
| Total    | 14      | 43           |

Build order: US-01, US-04, US-13 (mock mode), then US-02 onward. Mock mode is built early because no live API key is used during initial development.

US-13's initial cached-output loading is implemented early. Its evidence and quality validation acceptance criteria are completed when US-03 and US-05 are implemented.

### Updated 21-Hour Implementation Budget

| Implementation activity                             | Hours |
| --------------------------------------------------- | ----- |
| US-01: Input and sample loading                     | 1.5   |
| US-04: Pydantic schemas and retry logic             | 2.5   |
| US-13: Mock mode and cached fixtures                | 2.0   |
| US-02: AI generation and output display             | 2.5   |
| US-03: Gherkin quality checker                      | 1.0   |
| US-05: Evidence validation                          | 1.5   |
| US-06: Streamlit story editing                      | 2.0   |
| US-07: Per-story approval                           | 1.5   |
| US-08: CSV and Markdown export                      | 1.5   |
| Fictional sample preparation, pytest and evaluation | 3.0   |
| Deployment and contingency                          | 2.0   |
| Total                                               | 21.0  |

US-09, US-10, US-11, US-12 and US-14 have no committed implementation hours.

The time budget remains unchanged.

# 6. Out-of-Scope List

- Audio and video input or transcription.
- PDF, Word, spreadsheet and image uploads.
- Uploaded files of 200 KB or larger.
- Workshop input outside 50–15,000 words.
- Real client data, confidential information or personal data.
- Multiple application users or user accounts.
- Authentication and role-based access management.
- Real-time collaboration and shared editing.
- Client-facing review portals.
- Backlog-level approval and bulk approval.
- Automatic story approval, saving, exporting or sending.
- Persistence of unapproved working stories.
- Integrations beyond CSV, Markdown and optional outbound Jira export, excluding the specified AI and database infrastructure.
- Bidirectional Jira synchronization and Jira issue updates.
- Sprint planning, capacity management and delivery tracking.
- Automated source-code generation.
- Automated functional test execution.
- Outdated test-case detection and regeneration tracking.
- Backlog version history, comparison and audit trails.
- AI model training and fine-tuning.
- Semantic evidence verification using an additional AI model.
- Production-grade security, scalability and availability commitments.
- Analytics dashboards and operational reporting.

# 7. Open Questions

| ID    | Open question                                                                                                                   | Working assumption                                                                                                                                                                            |
| ----- | ------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| OQ-01 | How should the story limit be reconciled with eight Must capabilities, five Should capabilities and optional Jira? | Resolved by DEC-25: backlog raised to 14 independent stories; Should capabilities split into US-09 to US-13. |
| OQ-02 | Are all Should capabilities expected within the 21-hour budget?                                                                 | No. Deliver Must scope and mock mode first. Remaining Should and Could capabilities are deferred unless time remains.                                                                         |
| OQ-03 | Does 200 KB mean 200,000 bytes or 204,800 bytes?                                                                                | Use 200,000 bytes. Files must contain fewer than 200,000 bytes.                                                                                                                               |
| OQ-04 | How should words be counted?                                                                                                    | Count non-empty whitespace-separated tokens after trimming. Use the same method for workshop input and evidence quotes.                                                                       |
| OQ-05 | Which AI provider should be implemented first?                                                                                  | Implement one live provider, Claude or OpenAI, plus mock mode. Supporting both live providers is not required for the demo.                                                                   |
| OQ-06 | What constitutes an unavailable API?                                                                                            | Connection errors, request timeouts and service-unavailable responses. Schema-validation failures follow the separate single-retry rule.                                                      |
| OQ-07 | Should a missing evidence field trigger a schema retry or an individual story drop?                                             | A missing required field triggers schema validation failure. An empty, oversized or unmatched evidence string triggers individual story removal after schema validation.                      |
| OQ-08 | Does a matching evidence quote establish that a story is not invented?                                                          | No. It establishes quote presence only. The PO evaluates whether the quote supports the requirement.                                                                                          |
| OQ-09 | How should the invented-story detection metric be calculated?                                                                   | Independently identify unsupported generated stories, then report how many were removed by the evidence checker. Report the total unsupported stories alongside the detected count.           |
| OQ-10 | How should acceptance without edits be measured?                                                                                | Divide the number of retained generated stories approved without any content edits by the total number of retained generated stories presented for review, across all 10 samples.             |
| OQ-11 | How should must-find requirement recall be measured?                                                                            | Prepare reference requirements before generation. Divide the number represented in retained generated stories by the total number of pre-listed must-find requirements across the 10 samples. |
| OQ-12 | How should generation time be measured?                                                                                         | Measure elapsed time from submission until validated, evidence-filtered output is displayed, including any schema retry. Evaluate each live sample separately.                                |
| OQ-13 | Should cached output count toward the AI evaluation targets?                                                                    | No. Cached output is used for demonstration and deterministic application testing only.                                                                                                       |
| OQ-14 | Who performs the PO review without real users?                                                                                  | The builder acts as the demonstration PO and evaluates generated stories against the fictional notes and pre-established reference requirements.                                              |
| OQ-15 | How should prompt-injection behaviour be evaluated?                                                                             | Include at least one adversarial sample among the 10 fictional samples. Verify schema compliance, requirement relevance and application-owned approval state.                                 |
| OQ-16 | Should the PRD summary and standalone decisions be included in exported files?                                                  | No. Per-story approval does not authorize standalone content. Export only approved stories and their associated fields.                                                                       |
| OQ-17 | What happens when an approved, persisted story is subsequently edited?                                                          | The working copy becomes unapproved. The previously saved approved snapshot remains unchanged until a newly approved version is explicitly saved.                                             |
| OQ-18 | Can a story be approved if its wording passes the checker but remains semantically ambiguous?                                   | The application cannot establish semantic testability using keyword checks alone. The PO must resolve ambiguity before selecting Approved.                                                    |
| OQ-19 | Should invalid cached output trigger an AI retry?                                                                               | No. Display a cached-output validation error. Mock mode must not make external AI requests.                                                                                                   |
| OQ-20 | Is the 60-second generation target achievable for all permitted input lengths?                                                  | It is an evaluation target for the 10 fictional samples, not a performance guarantee for every input containing 50–15,000 words.                                                              |
| OQ-21 | Should RICE scores be mandatory for story approval?                                                                             | No. RICE is a Should capability. Missing RICE inputs do not prevent approval of an otherwise valid story.                                                                                     |
| OQ-22 | How should live evaluation results be recorded?                                                                                 | Record actual results separately from the PRD. No success metric is considered achieved until the corresponding evaluation has been performed.                                                |