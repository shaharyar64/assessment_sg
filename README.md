# Email Generation Assistant

Generates professional emails from **Intent**, **Key Facts**, and **Tone** using **LangChain + Groq**. The system validates input, generates emails with two prompting strategies, scores them with three custom metrics, compares strategies, and produces a PDF report.

Full **input → output test cases** are documented in **[TDD.md](TDD.md)** (TC-01 to TC-30).

---

## Requirements

- Python 3.10+
- Dependencies in `requirements.txt`

---

## Setup

```powershell
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux

pip install -r requirements.txt
```

Create `.env` in the project root for live Groq generation:

```env
GROQ_API_KEY=gsk_your-key-here
```

Get a free key at [console.groq.com](https://console.groq.com).

Without a key (or with `--mock`), the pipeline uses offline template generation.

---

## Commands

### Full pipeline — TC-15 (Groq) / TC-16 (mock)

Runs: 10 scenarios × 2 strategies → evaluate → compare → PDF.

```powershell
python -m src.run_all                  # TC-15 — live Groq
python -m src.run_all --mock           # TC-16 — offline, no API key
python -m src.run_all --skip-report    # skip PDF (TC-13)
```

### Single custom email — TC-01 / TC-14

```powershell
python -m src.run_one `
  --intent "Follow up after a product demo" `
  --fact "The demo was held on Monday" `
  --fact "The client asked for pricing details" `
  --fact "The proposal should be shared by Friday" `
  --tone "Formal" `
  --output "outputs/my_email.json"
```

| Flag | Description |
|------|-------------|
| `--intent` | Email purpose (required) |
| `--fact` | Key fact — repeat for multiple |
| `--tone` | `Formal`, `Casual`, `Urgent`, `Empathetic`, `Professional` |
| `--strategy` | `structured` (default) or `basic` |
| `--output` | Save result JSON |
| `--mock` | Offline mode |
| `--model` | Groq model (default: `llama-3.3-70b-versatile`) |

**Expected output:** email printed to terminal + saved JSON (`"email"` field). See TC-01 in [TDD.md](TDD.md).

### Automated tests

```powershell
python -m pytest tests/ -v
```

53 tests — no API key required. Maps to [TDD.md](TDD.md#automated-test-coverage).

---

## Test Cases (summary)

| ID | Feature | Command / trigger |
|----|---------|-------------------|
| TC-01 | Valid email generation | `run_one` / `generate_email()` |
| TC-02 | Missing tone rejected | `validate_scenario()` |
| TC-03 | Empty key facts rejected | `validate_scenario()` |
| TC-04 | No invented information | structured strategy |
| TC-05 | Structured 4-section email | `strategy=structured` |
| TC-06 | Load 10 scenarios | `data/scenarios.json` |
| TC-07 | Batch — 20 emails | `run_all` step 3 |
| TC-08 | Fact Recall metric | `evaluator.py` |
| TC-09 | Tone & Format metric | `evaluator.py` |
| TC-10 | Conciseness metric | `evaluator.py` |
| TC-11 | Evaluation JSON | `run_all` step 4 |
| TC-12 | Strategy comparison | `run_all` step 5 |
| TC-13 | PDF report | `run_all` step 6 |
| TC-14 | `run_one` CLI | CLI flags |
| TC-15 | Full pipeline (Groq) | `python -m src.run_all` |
| TC-16 | Mock pipeline | `python -m src.run_all --mock` |
| TC-17 | Missing intent rejected | `validate_scenario()` |
| TC-18 | Whitespace-only fields rejected | `validate_scenario()` |
| TC-19 | Parse `Subject Line:` variant | `parser.py` |
| TC-20 | Parse email without closing | `parser.py` |
| TC-21 | Partial fact recall (2/3) | `evaluator.py` |
| TC-22 | Invalid scenario file | `load_scenarios()` |
| TC-23 | Urgent tone scoring | `evaluator.py` |
| TC-24 | Conciseness penalties | `evaluator.py` |
| TC-25 | Structured wins comparison | `compare.py` |
| TC-26 | All 5 tones generate | `generate_email(mock=True)` |
| TC-27 | No-hallucination prompt rules | `prompt_builder.py` |
| TC-28 | Mock tone-specific closings | `llm_client.py` |
| TC-29 | CLI fact parsing edge cases | `run_one.py` |
| TC-30 | Trace log written | `trace_logger.py` |

Each test case in [TDD.md](TDD.md) includes **Input**, **Expected Output**, and **Pass Criteria**.

---

## Outputs

| Path | Test case | Contents |
|------|-----------|----------|
| `outputs/generated_emails.json` | TC-07 | 20 emails (10 scenarios × 2 strategies) |
| `outputs/evaluation_results.json` | TC-11 | Scores + strategy averages |
| `outputs/comparison_summary.json` | TC-12 | Winner + recommendation |
| `outputs/my_email.json` | TC-01 / TC-14 | Single custom email |
| `reports/final_report.pdf` | TC-13 | Final analysis PDF |
| `traces/` | TC-02, TC-03, … | Validation and pipeline trace logs |

Re-running overwrites outputs — nothing to delete first.

---

## Project layout

```
assessment_sg/
├── data/
│   └── scenarios.json              # 10 evaluation scenarios (TC-06)
├── src/
│   ├── run_all.py                  # Full pipeline (TC-15, TC-16)
│   ├── run_one.py                  # Single email CLI (TC-14)
│   ├── validation.py               # TC-02, TC-03
│   ├── generator.py                # TC-01, TC-07
│   ├── evaluator.py                # TC-08, TC-09, TC-10
│   ├── compare.py                  # TC-12
│   └── report.py                   # TC-13
├── tests/                          # Automated tests (53 passed)
├── outputs/
├── reports/
├── traces/
├── TDD.md                          # Test cases — input → output
├── Traces.md                       # Acceptance traces
└── L1Speccing.md                   # Product specification
```

---

## How it works

**Input:** Intent + Key Facts + Tone

**Two strategies** (same Groq model, different prompts):

| Strategy | Description |
|----------|-------------|
| `basic` | Minimal prompt template |
| `structured` | Role instruction, section rules, no-hallucination constraints |

**Three metrics:**

1. **Fact Recall** — all key facts included?
2. **Tone and Format Accuracy** — correct tone + subject, greeting, body, closing?
3. **Conciseness and Fluency** — readable and polished?

**Chain:** `ChatPromptTemplate | ChatGroq | StrOutputParser`

---

## Documentation

| Doc | Description |
|-----|-------------|
| [TDD.md](TDD.md) | Test cases TC-01 to TC-30 — input, expected output, pass criteria |
| [Traces.md](Traces.md) | 14 acceptance traces |
| [L1Speccing.md](L1Speccing.md) | Product specification |

---

## License

Assessment project — for evaluation purposes.
