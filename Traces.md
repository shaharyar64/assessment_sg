# TRACE Documents — Email Generation Assistant

Source spec: `Specs.md`

Each trace shows a real input example, what the system should return, and when it passes. No implementation details — only what you provide and what you get back.

---

## Quick Reference

| Trace | What You Provide | What the System Returns |
|---|---|---|
| 01 | Intent + Key Facts + Tone | Complete professional email |
| 02 | Intent + Key Facts (Tone missing) | Clear validation error — no email |
| 03 | Intent + empty Key Facts + Tone | Clear validation error — no email |
| 04 | Intent + Key Facts + Tone | Email using only provided facts |
| 05 | One scenario + structured prompting | Reliable email with all sections |
| 06 | 10 scenario file | 10 validated scenarios with reference emails |
| 07 | 10 scenarios × 2 strategies | 20 generated emails saved to file |
| 08 | Generated email + key facts | Fact Recall score |
| 09 | Generated email + requested tone | Tone and Format Accuracy score |
| 10 | Generated email | Conciseness and Fluency score |
| 11 | All generated emails + metrics | Evaluation results file with averages |
| 12 | Evaluation results | Recommended strategy with reason |
| 13 | All project outputs | Final PDF report |
| 14 | — | README with setup and run steps |

---

# TRACE 01 — Valid Email Generation

**Purpose:** Generate one complete professional email from valid structured input.

**Input**

Intent: Follow up after a product demo

Key Facts:
- The demo was held on Monday
- The client asked for pricing details
- The proposal should be shared by Friday
- The client is interested in the automation dashboard

Tone: Formal

**Output**

Subject: Follow-Up on Product Demo

Hi [Recipient Name],

Thank you for attending the product demo on Monday. I appreciate your interest in the automation dashboard and the questions you shared during the session.

As discussed, I will prepare the pricing details and share the proposal with you by Friday.

Please let me know if there is any additional information you would like included.

Best regards,
[Sender Name]

**Passes when:** Email has subject, greeting, body, and closing; all four key facts are included; tone is formal; no invented details.

---

# TRACE 02 — Missing Required Field

**Purpose:** Reject input when Tone is missing.

**Input**

Intent: Apologize for a delayed response

Key Facts:
- The response was delayed due to internal review
- The requested document is now attached

Tone: *(missing)*

**Output**

Status: Error

Message: The email scenario is missing a required field: tone.

Missing fields: tone

**Passes when:** No email is generated, no LLM call is made, and the error clearly names the missing field.

---

# TRACE 03 — Empty Key Facts Rejected

**Purpose:** Reject input when Key Facts list is empty.

**Input**

Intent: Confirm next steps after a call

Key Facts: *(empty)*

Tone: Professional

**Output**

Status: Error

Message: At least one key fact is required to generate an accurate email.

**Passes when:** No email is generated and the system does not ask the model to invent missing details.

---

# TRACE 04 — No Unsupported Information

**Purpose:** Generated emails must not invent names, prices, dates, attachments, or commitments.

**Input**

Intent: Request proposal details

Key Facts:
- The client requested more detail about implementation timeline
- The client wants a breakdown of support options
- The response should ask for availability for a follow-up call

Tone: Professional

**Bad output (must fail validation)**

Subject: Proposal Details for Acme Corp

Hi Sarah,

Thank you for your interest in our enterprise package. The implementation will cost $15,000 and can begin next Monday. I have attached the final proposal.

Best regards,
Alex

Unsupported items: Acme Corp, Sarah, enterprise package, $15,000, next Monday, attached proposal, Alex

**Correct output**

Subject: Request for Proposal Details

Hi [Recipient Name],

Thank you for your interest. Could you please share more detail about the implementation timeline you have in mind and the support options you would like us to cover? I would also be happy to schedule a follow-up call to discuss the proposal in more detail. Please let me know your availability.

Best regards,
[Sender Name]

**Passes when:** Bad output is flagged; correct output uses only the three provided facts.

---

# TRACE 05 — Structured Prompting Strategy

**Purpose:** Use a documented advanced prompting technique for reliable generation.

**Input**

Same as TRACE 01 — Intent, Key Facts, and Tone for one scenario.

**Prompt approach**

Structured prompting with role instruction: the prompt separates task, input fields, output requirements, and a no-hallucination rule. The model is told to return Subject, Greeting, Body, and Closing.

**Output**

Same quality as TRACE 01 — complete email with all key facts, correct tone, and no invented details.

**Passes when:** Structured prompting is used in generation and explained in the final report.

---

# TRACE 06 — Ten Evaluation Scenarios

**Purpose:** Load exactly 10 unique scenarios, each with a human reference email.

**Input**

Scenario file with 10 entries. Each entry includes Intent, Key Facts, Tone, and Human Reference Email.

Example scenario (SCN-001):

Intent: Follow up after a product demo
Key Facts: demo on Monday, pricing request, proposal by Friday, interest in automation dashboard
Tone: Formal
Human Reference Email: *(ideal email for this scenario)*

**Output**

10 scenarios loaded and validated. All have Intent, Key Facts, Tone, and Human Reference Email. Scenario IDs are unique.

**Passes when:** Count is exactly 10, all fields present, no duplicates.

---

# TRACE 07 — Strategy A and Strategy B Generation

**Purpose:** Generate emails for all 10 scenarios using two strategies on the same dataset.

**Input**

10 scenarios from `data/scenarios.json`
Strategy A: basic prompt
Strategy B: structured prompt

**Output**

20 generated emails saved — 10 per strategy, same scenarios for both.

Example pair for SCN-001:
- Basic prompt: email with subject, greeting, body, closing
- Structured prompt: email with subject, greeting, body, closing (typically more complete)

**Passes when:** Both strategies produce 10 outputs each from the same 10 scenarios.

---

# TRACE 08 — Fact Recall Metric

**Purpose:** Score whether the generated email includes all required key facts.

**Input**

Key Facts:
- The demo was held on Monday
- The client asked for pricing details
- The proposal should be shared by Friday
- The client is interested in the automation dashboard

Generated email: "Thank you for attending the product demo on Monday. I appreciate your interest in the automation dashboard. I will prepare the pricing details and share the proposal with you by Friday."

**Output**

Fact Recall: 4 of 4 key facts included — score 1.0

**Partial failure example**

If the email omits the automation dashboard fact:

Fact Recall: 3 of 4 — score 0.75
Missing: The client is interested in the automation dashboard

**Passes when:** Score equals included facts divided by total facts; missing facts are listed.

---

# TRACE 09 — Tone and Format Accuracy Metric

**Purpose:** Score tone alignment and email structure.

**Input**

Requested tone: Empathetic

Generated email:

Subject: Apology for the Delay
Greeting: Hi [Recipient Name],
Body: I apologize for the delay and understand this may have caused inconvenience. The review is now complete, and the updated document is ready.
Closing: Best regards, [Sender Name]

**Output**

Tone and Format Accuracy: 1.0 — empathetic tone matched, all four sections present.

**Failure example**

Subject missing, closing missing, tone too blunt → score 0.25

**Passes when:** Both tone and format (subject, greeting, body, closing) are checked.

---

# TRACE 10 — Conciseness and Fluency Metric

**Purpose:** Score readability, polish, and conciseness.

**Input**

Generated email:

Subject: Next Steps

Hi [Recipient Name],

Thank you for the call today. I will send the updated timeline by Wednesday and confirm the implementation owner after the internal review.

Best regards,
[Sender Name]

**Output**

Conciseness and Fluency: 1.0 — clear, polished, no unnecessary wordiness.

**Failure example**

Awkward phrasing, grammar issues, or excessive repetition → score 0.25

**Passes when:** Readability and conciseness are scored on a 0.0–1.0 rubric.

---

# TRACE 11 — Evaluation Results File

**Purpose:** Output structured evaluation results with metric definitions, raw scores, and averages.

**Input**

20 generated emails (10 scenarios × 2 strategies) scored with all three metrics.

**Output**

Evaluation results file containing:
- Metric definitions: Fact Recall, Tone and Format Accuracy, Conciseness and Fluency
- Raw score per scenario per strategy
- Overall averages per strategy

Example averages:
- Basic prompt overall average: 0.78
- Structured prompt overall average: 0.91

**Passes when:** File is CSV or JSON with definitions, all raw scores, and averages.

---

# TRACE 12 — Strategy Comparison and Recommendation

**Purpose:** Compare both strategies and recommend the better one using metric data.

**Input**

Evaluation results from TRACE 11.

**Output**

Recommended strategy: Structured prompt

Reason: Highest overall average (0.91 vs 0.78) and better scores across all three metrics.

Biggest failure mode of basic prompt: missed key facts and inconsistent formatting.

Production recommendation: Use structured prompt — more complete, tone-accurate, and polished emails across the same 10 scenarios.

**Passes when:** Winner is chosen from data, failure mode is explained, and recommendation is written in plain language.

---

# TRACE 13 — Final Report

**Purpose:** Produce a PDF report with all required analysis sections.

**Input**

Prompt template, evaluation results, and comparison summary.

**Output**

Final report PDF including:
1. Project summary
2. Prompting approach and template
3. Evaluation dataset summary
4. Custom metric definitions and logic
5. Raw evaluation results
6. Strategy comparison
7. Failure mode analysis
8. Final recommendation

**Passes when:** PDF exists with all sections and recommendation is supported by metric data.

---

# TRACE 14 — README and Setup

**Purpose:** A new user can set up and run the project from the README alone.

**Output**

README covering: overview, requirements, setup, commands for generation / evaluation / comparison, output file locations, and final report location.

**Passes when:** README exists and a new user can run the full project from it.

---

# End-to-End Flow

**What you run:** Full pipeline on 10 scenarios.

**What happens:**
1. Load and validate 10 scenarios
2. Generate emails with Strategy A and Strategy B
3. Evaluate both with three custom metrics
4. Save raw scores and calculate averages
5. Compare strategies and select a winner
6. Generate final report

**Final output:**
- Generated emails file
- Evaluation results file
- Comparison summary
- Final report PDF
- Recommended strategy: structured prompt (0.91 vs 0.78)

**Passes when:** All 14 traces above pass end to end.

---

# Requirement Coverage

| Requirement | Traces |
|---|---|
| REQ-001 Structured inputs | 01, 02, 03 |
| REQ-002 One email per scenario | 01 |
| REQ-003 Complete email structure | 01, 09 |
| REQ-004 No invented information | 03, 04, 08 |
| REQ-005 Advanced prompting | 05, 13 |
| REQ-006 Ten scenarios | 06 |
| REQ-007 Human reference email | 06 |
| REQ-008 Three custom metrics | 08, 09, 10 |
| REQ-009 Structured evaluation output | 11 |
| REQ-010 Two-strategy comparison | 07, 12 |
| REQ-011 Data-driven recommendation | 12, 13 |
| REQ-012 README | 14 |
