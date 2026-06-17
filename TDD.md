# Test Design Document (TDD)
## Email Generation Assistant

| Field | Value |
|-------|-------|
| **Project** | Email Generation Assistant |
| **Version** | 2.1 |
| **Date** | June 2026 |
| **Purpose** | Input → expected output test cases (TC-01 to TC-30) |
| **Run tests** | `python -m pytest tests/ -v` (53 tests) |
| **Related docs** | `Traces.md`, `README.md` |

Each test case below defines **Input**, **Expected Output**, and **Pass Criteria**.  
Outputs marked *(actual)* come from a successful project run with Groq (`llama-3.3-70b-versatile`).

---

## How to Read These Test Cases

| Column | Meaning |
|--------|---------|
| **Input** | What you provide to the system |
| **Expected Output** | What the system must return |
| **Pass Criteria** | Conditions that must be true |

For LLM-generated emails, exact wording may vary between runs. Pass criteria focus on **structure**, **fact inclusion**, and **tone** — not word-for-word match.

---

## TC-01 — Valid Email Generation

**Command:** `python -m src.run_one` or `generate_email()`

### Input

```json
{
  "intent": "Follow up after a product demo",
  "key_facts": [
    "The demo was held on Monday",
    "The client asked for pricing details",
    "The proposal should be shared by Friday",
    "The client is interested in the automation dashboard"
  ],
  "tone": "Formal"
}
```

### Expected Output *(actual — Groq, structured strategy)*

```
Subject: Follow-up on Monday's Product Demo

Dear [Recipient Name],

I am writing to follow up on the product demo that we held on Monday. We appreciated
the opportunity to showcase our product's features and capabilities, and we were pleased
to learn about your interest in the automation dashboard. During the demo, you requested
pricing details, which we are currently compiling.

We understand that having this information is crucial for your decision-making process.
As discussed, we will share a proposal with you by Friday, which will include the pricing
details you requested.

If you have any further questions or need any additional information before receiving
the proposal, please do not hesitate to contact us.

Best regards,
[Sender Name]
```

**Saved to:** `outputs/my_email.json` → `"email"` field

### Pass Criteria

- Output contains `Subject:`, greeting, body, and closing
- All 4 key facts appear in the email
- Tone is formal (professional language)
- No invented names, prices, or dates beyond key facts
- HTTP 0 / exit code 0

---

## TC-02 — Missing Tone Rejected

**Command:** `validate_scenario()` / `run_all` validation trace

### Input

```json
{
  "intent": "Apologize for a delayed response",
  "key_facts": [
    "The response was delayed due to internal review",
    "The requested document is now attached"
  ]
}
```

*(tone field missing)*

### Expected Output *(actual)*

```json
{
  "status": "error",
  "message": "The email scenario is missing a required field: tone.",
  "missing": ["tone"]
}
```

### Pass Criteria

- No email is generated
- No LLM API call is made
- Error message names `tone` as missing field
- Trace log: `traces/validation/trace_missing_tone_001.json` → `"passed": true`

---

## TC-03 — Empty Key Facts Rejected

**Command:** `validate_scenario()` / `run_all` validation trace

### Input

```json
{
  "intent": "Confirm next steps after a call",
  "key_facts": [],
  "tone": "Professional"
}
```

### Expected Output *(actual)*

```json
{
  "status": "error",
  "message": "At least one key fact is required to generate an accurate email."
}
```

### Pass Criteria

- No email is generated
- No LLM API call is made
- Error message mentions key facts
- Trace log: `traces/validation/trace_empty_facts_001.json` → `"passed": true`

---

## TC-04 — No Unsupported Information

**Command:** `generate_email()` with structured strategy

### Input

```json
{
  "intent": "Request proposal details",
  "key_facts": [
    "The client requested more detail about implementation timeline",
    "The client wants a breakdown of support options",
    "The response should ask for availability for a follow-up call"
  ],
  "tone": "Professional"
}
```

### Expected Output

Email that:

- Includes all 3 key facts
- Uses `[Recipient Name]` / `[Sender Name]` placeholders instead of invented names
- Does **not** invent attachments, dollar amounts, or specific dates not in key facts

### Pass Criteria

- All key facts present (Fact Recall > 0)
- No fabricated pricing, file names, or calendar dates beyond input
- Structured prompt rules enforced via `prompt_builder.py` `## Rules` section

---

## TC-05 — Structured Prompting Produces Complete Email

**Command:** `generate_email(strategy="structured")`

### Input

Same as TC-01.

### Expected Output

Email with exactly these sections:

1. `Subject: ...`
2. Greeting line (Hi / Dear / Hello)
3. Body paragraphs covering intent + all facts
4. Closing (Best regards / Sincerely / Thanks)

Prompt sent to model must contain `## Task`, `## Output Requirements`, and `## Rules`.

### Pass Criteria

- `tone_and_format_accuracy` ≥ 0.875 (all 4 sections present)
- `fact_recall` = 1.0 for SCN-001 *(actual Groq run)*

---

## TC-06 — Load Ten Evaluation Scenarios

**Command:** `load_scenarios("data/scenarios.json")`

### Input

File: `data/scenarios.json`

### Expected Output

```json
{
  "count": 10,
  "ids": ["SCN-001", "SCN-002", "SCN-003", "SCN-004", "SCN-005",
          "SCN-006", "SCN-007", "SCN-008", "SCN-009", "SCN-010"]
}
```

Each scenario contains: `id`, `intent`, `key_facts`, `tone`, `reference_email`.

### Pass Criteria

- Exactly 10 scenarios loaded
- All IDs unique
- All required fields present
- Trace log: `traces/batch/trace_scenarios_load_001.json` → `"passed": true`

---

## TC-07 — Batch Generation (10 × 2 = 20 Emails)

**Command:** `python -m src.run_all`

### Input

- 10 scenarios from `data/scenarios.json`
- Strategies: `basic` and `structured`
- Model: Groq `llama-3.3-70b-versatile`

### Expected Output

File: `outputs/generated_emails.json`

```json
{
  "generated_emails": [
    { "scenario_id": "SCN-001", "strategy": "basic", "email": "..." },
    { "scenario_id": "SCN-001", "strategy": "structured", "email": "..." },
    "... 18 more entries ..."
  ]
}
```

**Total:** 20 email objects (10 scenarios × 2 strategies)

### Example — SCN-001 basic *(actual excerpt)*

**Input facts:** demo on Monday, pricing details, proposal by Friday, automation dashboard

**Output email (start):**
```
Subject: Follow-up on Product Demo and Pricing Details

Dear [Client's Name],

I hope this email finds you well. I wanted to follow up on the product demo
we held on Monday...
```

### Pass Criteria

- `len(generated_emails)` = 20
- Each entry has `scenario_id`, `strategy`, `prompt`, `email`
- Both strategies present for every scenario ID
- Trace log: `traces/batch/trace_batch_generation_001.json` → `"passed": true`

---

## TC-08 — Fact Recall Metric

**Command:** `score_fact_recall(key_facts, email_text)`

### Input

```json
{
  "key_facts": [
    "The demo was held on Monday",
    "The client asked for pricing details",
    "The proposal should be shared by Friday",
    "The client is interested in the automation dashboard"
  ],
  "email": "<SCN-001 basic email from generated_emails.json>"
}
```

### Expected Output *(actual)*

```json
{
  "fact_recall": 1.0,
  "details": {
    "included_count": 4,
    "total_count": 4,
    "included": ["The demo was held on Monday", "..."],
    "missing": [],
    "summary": "4 of 4 key facts included"
  }
}
```

### Input (negative case)

```json
{
  "key_facts": ["The contract expires next year"],
  "email": "Subject: Hello\n\nHi there,\n\nGeneric message.\n\nThanks"
}
```

### Expected Output (negative)

```json
{
  "fact_recall": 0.0,
  "details": {
    "included_count": 0,
    "total_count": 1,
    "missing": ["The contract expires next year"]
  }
}
```

### Pass Criteria

- Score = included / total
- Missing facts listed in `details.missing`

---

## TC-09 — Tone and Format Accuracy Metric

**Command:** `score_tone_and_format(tone, email_text)`

### Input

```json
{
  "tone": "Formal",
  "email": "Subject: Follow-Up\n\nHi [Name],\n\nBody text here.\n\nBest regards,\n[Sender]"
}
```

### Expected Output

```json
{
  "tone_and_format_accuracy": ">= 0.875",
  "details": {
    "sections_present": {
      "subject": true,
      "greeting": true,
      "body": true,
      "closing": true
    },
    "format_score": 0.5,
    "tone_score": "> 0"
  }
}
```

### Pass Criteria

- 0.125 per present section (max 0.5 format score)
- Tone score from keyword match against Formal indicators
- SCN-001 basic *(actual)*: `tone_and_format_accuracy` = 1.0

---

## TC-10 — Conciseness and Fluency Metric

**Command:** `score_conciseness_and_fluency(email_text)`

### Input (good email)

Normal-length email (~50–150 words), no double spaces, ends with punctuation.

### Expected Output

```json
{
  "conciseness_and_fluency": 1.0,
  "details": {
    "penalties": []
  }
}
```

### Input (too long)

Email body with 200+ words.

### Expected Output

```json
{
  "conciseness_and_fluency": 0.75,
  "details": {
    "penalties": ["excessive length"]
  }
}
```

### Pass Criteria

- Starts at 1.0, penalties applied for length, repetition, wordiness, grammar
- SCN-001 structured *(actual)*: score = 0.9 (minor penalty applied)

---

## TC-11 — Full Evaluation Output

**Command:** `python -m src.run_all` → step 4

### Input

20 generated emails from TC-07

### Expected Output

File: `outputs/evaluation_results.json`

```json
{
  "metric_definitions": { "... 3 metrics ..." },
  "scenario_scores": [ "... 20 score objects ..." ],
  "strategy_averages": {
    "basic": {
      "metric_averages": {
        "fact_recall": 1.0,
        "tone_and_format_accuracy": 0.9787,
        "conciseness_and_fluency": 0.965
      },
      "overall_average": 0.9812,
      "scenario_count": 10
    },
    "structured": {
      "metric_averages": {
        "fact_recall": 1.0,
        "tone_and_format_accuracy": 0.9236,
        "conciseness_and_fluency": 0.955
      },
      "overall_average": 0.9595,
      "scenario_count": 10
    }
  }
}
```

*(values from actual Groq run)*

### Pass Criteria

- 20 entries in `scenario_scores`
- Each has `scores` for all 3 metrics + `overall_average`
- Strategy averages computed for both `basic` and `structured`
- Trace log: `traces/evaluation/trace_full_evaluation_001.json` → `"passed": true`

---

## TC-12 — Strategy Comparison

**Command:** `compare_strategies(evaluation_results)`

### Input

Strategy averages from TC-11:

| Strategy | Overall Average |
|----------|-----------------|
| basic | 0.9812 |
| structured | 0.9595 |

### Expected Output *(actual)*

File: `outputs/comparison_summary.json`

```json
{
  "recommended_strategy": "basic",
  "winner": "basic",
  "loser": "structured",
  "reason": "Highest overall average (0.98 vs 0.96) and better scores across the three custom metrics.",
  "biggest_failure_mode": "Lowest average on Tone and Format Accuracy (0.92): inconsistent formatting and tone misalignment.",
  "production_recommendation": "Use basic — more complete, tone-accurate, and polished emails across the same 10 scenarios.",
  "overall_averages": {
    "basic": 0.9812,
    "structured": 0.9595
  },
  "metric_comparison": {
    "Fact Recall": { "basic": 1.0, "structured": 1.0 },
    "Tone and Format Accuracy": { "basic": 0.9787, "structured": 0.9236 },
    "Conciseness and Fluency": { "basic": 0.965, "structured": 0.955 }
  }
}
```

### Pass Criteria

- Winner = strategy with higher `overall_average`
- `biggest_failure_mode` identifies loser's weakest metric
- Trace log: `traces/comparison/trace_strategy_comparison_001.json` → `"passed": true`

---

## TC-13 — Final PDF Report

**Command:** `python -m src.run_all` → step 6

### Input

- `outputs/evaluation_results.json`
- `outputs/comparison_summary.json`

### Expected Output

File: `reports/final_report.pdf`

PDF contains:

1. Project summary
2. Prompt template documentation
3. Three metric definitions
4. Strategy comparison table
5. Production recommendation

### Pass Criteria

- File exists at `reports/final_report.pdf`
- Trace log: `traces/report/trace_final_analysis_generation_001.json` → `"passed": true`

---

## TC-14 — CLI Single Email (`run_one`)

**Command:**

```powershell
python -m src.run_one `
  --intent "Follow up after a product demo" `
  --fact "The demo was held on Monday" `
  --fact "The client asked for pricing details" `
  --tone "Formal" `
  --output "outputs/my_email.json"
```

### Input

CLI flags above (same intent/facts/tone as TC-01)

### Expected Output

1. Email printed to terminal
2. JSON file saved:

```json
{
  "scenario_id": "CUSTOM",
  "strategy": "structured",
  "intent": "Follow up after a product demo",
  "tone": "Formal",
  "key_facts": ["The demo was held on Monday", "The client asked for pricing details"],
  "prompt": "[SYSTEM]\nYou are a professional business email writer...",
  "email": "Subject: ...\n\nDear [Recipient Name],\n\n..."
}
```

### Pass Criteria

- Exit code 0
- `"email"` field non-empty
- `"strategy"` = `structured` (default)

---

## TC-15 — End-to-End Pipeline

**Command:** `python -m src.run_all`

### Input

- `data/scenarios.json` (10 scenarios)
- `GROQ_API_KEY` in `.env`
- No `--mock` flag

### Expected Output

| Artifact | Expected |
|----------|----------|
| `outputs/generated_emails.json` | 20 emails |
| `outputs/evaluation_results.json` | Scores + averages |
| `outputs/comparison_summary.json` | Winner + recommendation |
| `reports/final_report.pdf` | PDF report |
| `traces/e2e/trace_end_to_end_project_run_001.json` | `"passed": true` |

Console output includes:

```
Generating emails (Strategy A + B) using LangChain + Groq (llama-3.3-70b-versatile)...
  basic: overall average = 0.98
  structured: overall average = 0.96
  Recommended: basic
Pipeline complete.
```

### Pass Criteria

- Exit code 0
- All output files created
- E2E trace passed

---

## TC-16 — Mock Mode (Offline)

**Command:** `python -m src.run_all --mock`

### Input

Same as TC-15 but with `--mock` (no API key needed)

### Expected Output

- 20 emails in `outputs/generated_emails.json` (template-style, deterministic)
- Console: `Generating emails (Strategy A + B) using mock...`
- Comparison and evaluation still complete

### Pass Criteria

- No Groq API calls
- Pipeline completes without `.env` key
- Structured strategy includes more facts than basic in mock mode

---

## TC-17 — Missing Intent Rejected

**Command:** `validate_scenario()`

### Input

```json
{
  "key_facts": ["Some fact"],
  "tone": "Formal"
}
```

### Expected Output

```json
{
  "status": "error",
  "message": "The email scenario is missing a required field: intent.",
  "missing": ["intent"]
}
```

### Pass Criteria

- No email generated
- `intent` listed in `missing_fields`

---

## TC-18 — Whitespace-Only Fields Rejected

**Command:** `validate_scenario()`

### Input

```json
{
  "intent": "Follow up",
  "key_facts": ["Valid fact"],
  "tone": "   "
}
```

### Expected Output

```json
{
  "status": "error",
  "message": "The email scenario is missing a required field: tone.",
  "missing": ["tone"]
}
```

### Pass Criteria

- Blank/whitespace tone treated as missing
- Same behavior for whitespace-only `intent`

---

## TC-19 — Parse Subject Line Variant

**Command:** `parse_email()`

### Input

```
Subject Line: Quarterly Review

Dear Team,

Body here.

Regards,
Sender
```

### Expected Output

```json
{
  "subject": "Quarterly Review",
  "greeting": "Dear Team,",
  "body": "Body here.",
  "closing": "Regards,\nSender"
}
```

### Pass Criteria

- Recognises both `Subject:` and `Subject Line:` prefixes

---

## TC-20 — Parse Email Without Closing

**Command:** `parse_email()`

### Input

```
Subject: Update

Hello,

Only a body with no sign-off.
```

### Expected Output

```json
{
  "subject": "Update",
  "greeting": "Hello,",
  "body": "Only a body with no sign-off.",
  "closing": ""
}
```

### Pass Criteria

- Subject and greeting extracted
- Empty closing does not crash parser
- Tone & Format metric reflects missing closing section

---

## TC-21 — Partial Fact Recall

**Command:** `score_fact_recall()`

### Input

```json
{
  "key_facts": [
    "The demo was held on Monday",
    "The client asked for pricing details",
    "The client is interested in the automation dashboard"
  ],
  "email": "<email with Monday and pricing but NO automation dashboard>"
}
```

### Expected Output

```json
{
  "fact_recall": 0.6667,
  "details": {
    "included_count": 2,
    "total_count": 3,
    "missing": ["The client is interested in the automation dashboard"]
  }
}
```

### Pass Criteria

- Score = included / total (2/3)
- Missing facts listed explicitly

---

## TC-22 — Invalid Scenario File Rejected

**Command:** `load_scenarios(path)`

### Input

JSON file with fewer than 10 scenarios.

### Expected Output

```
ValueError: Scenario validation failed:
Expected exactly 10 scenarios, found 1.
```

### Pass Criteria

- Pipeline does not proceed with invalid scenario file
- Clear error message

---

## TC-23 — Urgent Tone Scoring

**Command:** `score_tone_and_format("Urgent", email)`

### Input

```json
{
  "tone": "Urgent",
  "email": "Subject: Deadline\n\nHi,\n\nThis is urgent. Deadline is tomorrow. Please respond ASAP.\n\nBest regards,\nSender"
}
```

### Expected Output

```json
{
  "tone_and_format_accuracy": "> 0.5",
  "details": {
    "tone_indicator_hits": ">= 1",
    "tone_requested": "Urgent"
  }
}
```

### Pass Criteria

- Urgent keywords (`urgent`, `ASAP`, `deadline`) increase tone score

---

## TC-24 — Conciseness Penalties

**Command:** `score_conciseness_and_fluency()`

### Input A — too long (200+ words)

### Expected Output A

```json
{ "conciseness_and_fluency": 0.75, "details": { "penalties": ["excessive length"] } }
```

### Input B — double spaces in body

### Expected Output B

```json
{ "details": { "penalties": ["double spaces"] } }
```

### Pass Criteria

- Score starts at 1.0, penalties subtract
- Multiple penalty types supported

---

## TC-25 — Structured Strategy Wins Comparison

**Command:** `compare_strategies()`

### Input

```json
{
  "strategy_averages": {
    "basic": { "overall_average": 0.72 },
    "structured": { "overall_average": 0.94 }
  }
}
```

### Expected Output

```json
{
  "winner": "structured",
  "recommended_strategy": "structured",
  "loser": "basic"
}
```

### Pass Criteria

- Higher overall average always wins
- Recommendation text references winner by name

---

## TC-26 — All Supported Tones Generate

**Command:** `generate_email(mock=True)` for each tone

### Input

Same scenario with tone set to each of:

`Formal`, `Casual`, `Urgent`, `Empathetic`, `Professional`

### Expected Output

Each run returns an email containing `Subject:` and non-empty body.

### Pass Criteria

- All 5 tones produce valid email structure in mock mode
- No validation error for any supported tone

---

## TC-27 — Structured Prompt Contains No-Hallucination Rules

**Command:** `build_prompt(scenario, "structured")`

### Input

Any valid scenario.

### Expected Output

Prompt string contains:

- `## Task`
- `## Output Requirements`
- `## Rules`
- `Do not invent`

Basic prompt must **not** contain `## Task`.

### Pass Criteria

- Structured prompt enforces section rules and fact constraints
- Basic prompt remains minimal

---

## TC-28 — Mock Client Tone-Specific Closings

**Command:** `mock_generate(scenario, prompt)`

### Input

| Tone | Key fact |
|------|----------|
| Casual | "Helped last week" |
| Urgent | "Deadline is tomorrow" |

### Expected Output

| Tone | Closing contains |
|------|------------------|
| Casual | `Thanks,` |
| Urgent | `earliest convenience` or formal sign-off |

### Pass Criteria

- Mock emails adapt closing to tone
- Structured mock includes all key facts (3+ facts)

---

## TC-29 — CLI Fact Parsing Edge Cases

**Command:** `parse_facts()` via `run_one`

### Input A

```
--fact "Fact one" --fact "Fact two"
```

**Output A:** `["Fact one", "Fact two"]`

### Input B

```
--fact "Fact one, Fact two,, Fact three, "
```

**Output B:** `["Fact one", "Fact two", "Fact three"]`

### Pass Criteria

- Comma-separated and repeated flags both work
- Empty segments stripped/skipped

---

## TC-30 — Trace Log Written

**Command:** `log_trace()`

### Input

```json
{
  "trace_id": "trace_test_001",
  "trace_name": "Test Trace",
  "category": "test",
  "input": { "intent": "Test" },
  "output": { "status": "ok" },
  "passed": true
}
```

### Expected Output

File: `traces/test/trace_test_001.json`

```json
{
  "trace_id": "trace_test_001",
  "passed": true,
  "category": "test",
  "timestamp": "<ISO-8601>",
  "input": { "intent": "Test" },
  "output": { "status": "ok" }
}
```

### Pass Criteria

- JSON file created under `traces/{category}/`
- All required fields present

---

## Test Case Summary

| ID | Feature | Input Type | Output Type |
|----|---------|------------|-------------|
| TC-01 | Valid generation | Scenario dict | Email text |
| TC-02 | Validation | Missing tone | Error JSON |
| TC-03 | Validation | Empty facts | Error JSON |
| TC-04 | No hallucination | Scenario dict | Constrained email |
| TC-05 | Structured prompt | Scenario dict | 4-section email |
| TC-06 | Load scenarios | JSON file | 10 scenarios |
| TC-07 | Batch generation | 10 scenarios × 2 strategies | 20 emails |
| TC-08 | Fact Recall | Email + facts | Score 0.0–1.0 |
| TC-09 | Tone & Format | Email + tone | Score 0.0–1.0 |
| TC-10 | Conciseness | Email text | Score 0.0–1.0 |
| TC-11 | Evaluation | 20 emails | evaluation_results.json |
| TC-12 | Comparison | Evaluation averages | comparison_summary.json |
| TC-13 | PDF report | Evaluation + comparison | final_report.pdf |
| TC-14 | run_one CLI | CLI flags | Terminal + JSON |
| TC-15 | Full pipeline (Groq) | scenarios.json | All outputs |
| TC-16 | Mock pipeline | scenarios.json + --mock | All outputs (offline) |
| TC-17 | Missing intent | Scenario dict | Error JSON |
| TC-18 | Whitespace fields | Scenario dict | Error JSON |
| TC-19 | Subject Line: prefix | Email text | Parsed sections |
| TC-20 | No closing section | Email text | Parsed sections |
| TC-21 | Partial fact recall | Email + facts | Score 0.67 |
| TC-22 | Invalid scenario file | JSON file | ValueError |
| TC-23 | Urgent tone scoring | Email + tone | Tone hits ≥ 1 |
| TC-24 | Conciseness penalties | Email text | Penalty list |
| TC-25 | Structured wins compare | Averages | Winner JSON |
| TC-26 | All 5 tones | Scenario × tones | 5 emails |
| TC-27 | Prompt rules | Scenario | Prompt string |
| TC-28 | Mock tone closings | Scenario + tone | Email text |
| TC-29 | CLI fact parsing | CLI flags | Fact list |
| TC-30 | Trace logging | Trace input | JSON file |

---

## Automated Test Coverage

Run: `python -m pytest tests/ -v`

| Test file | Tests | Maps to |
|-----------|-------|---------|
| `test_validation.py` | 9 | TC-02, TC-03, TC-17, TC-18 |
| `test_parser.py` | 4 | TC-19, TC-20 |
| `test_evaluator.py` | 10 | TC-08–TC-10, TC-21, TC-23, TC-24 |
| `test_compare.py` | 4 | TC-12, TC-25 |
| `test_generator.py` | 11 | TC-01, TC-06, TC-07, TC-22, TC-26 |
| `test_prompt_builder.py` | 5 | TC-05, TC-27 |
| `test_llm_client.py` | 4 | TC-16, TC-28 |
| `test_run_one.py` | 4 | TC-14, TC-29 |
| `test_trace_logger.py` | 1 | TC-30 |
| **Total** | **53** | TC-01 to TC-30 |

**Result:** 53 tests passed — no Groq API key required.

---

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | June 2026 | Initial technical design |
| 2.0 | June 2026 | Rewritten as input/output test case specification |
| 2.1 | June 2026 | Added TC-17 to TC-30 and 53 automated tests |
