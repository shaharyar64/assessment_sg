# Email Generation Assistant

Generates professional emails from **Intent**, **Key Facts**, and **Tone** using **LangChain + OpenAI**. The system validates input, generates emails with two prompting strategies, scores them with three custom metrics, compares strategies, and writes reports to the `reports/` folder.

Full **input → output test cases** are documented in **[TDD.md](TDD.md)** (TC-01 to TC-30).

---

## Requirements

- Python 3.10+
- Dependencies in `requirements.txt`

---

## Setup

```powershell
# 1. Clone or open the project folder, then create a virtual environment
python -m venv .venv

# 2. Activate it
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt
```

Create `.env` in the project root for live OpenAI generation:

```env
OPENAI_API_KEY=sk-your-key-here
```

Get a key at [platform.openai.com](https://platform.openai.com/api-keys).

Without a key (or with `--mock`), the pipeline uses offline template generation.

---

## How to Run

### Full pipeline (recommended)

Runs all 10 scenarios with both strategies → evaluate → compare → **save reports to `reports/`**.

```powershell
python -m src.run_all                  # live OpenAI (gpt-4o-mini)
python -m src.run_all --model gpt-4o   # highest quality, higher cost
python -m src.run_all --mock           # offline, no API key
python -m src.run_all --skip-report    # skip report generation (no files in reports/)
```

**What you get:**

| Folder | Files written when you run `python -m src.run_all` |
|--------|------------------------------------------------------|
| `outputs/` | `generated_emails.json`, `evaluation_results.json`, `evaluation_results.csv`, `comparison_summary.json` |
| **`reports/`** | **`final_report.docx`** |

Step 6 saves the final report to **`reports/final_report.docx`**. Close the file in Word before re-running, or the pipeline saves **`final_report_new.docx`** instead. Use `--skip-report` if you only want the JSON/CSV outputs in `outputs/`.

**Final report location:** `reports/final_report.docx` — open in Word or upload to Google Drive → Open with Google Docs.

See [Outputs](#outputs) for full details.

### Single custom email

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
| `--model` | OpenAI model (default: `gpt-4o-mini`; try `gpt-4o` for best quality) |

### Automated tests

```powershell
python -m pytest tests/ -v
```

No API key required. Maps to [TDD.md](TDD.md#automated-test-coverage).

---

## Evaluation Scenarios (10 → 20 emails)

All batch evaluation uses **`data/scenarios.json`**. Each scenario is run twice — once with the **basic** prompt and once with the **structured** prompt — producing **20 emails total**.

| ID | Intent | Tone | Key facts |
|----|--------|------|-----------|
| SCN-001 | Follow up after a product demo | Formal | 4 |
| SCN-002 | Apologize for a delayed response | Empathetic | 3 |
| SCN-003 | Request proposal details | Professional | 3 |
| SCN-004 | Confirm next steps after a call | Professional | 3 |
| SCN-005 | Send an urgent reminder about a deadline | Urgent | 3 |
| SCN-006 | Thank a colleague for project support | Casual | 3 |
| SCN-007 | Schedule a quarterly business review | Formal | 3 |
| SCN-008 | Notify about a planned maintenance window | Professional | 3 |
| SCN-009 | Follow up on an unanswered RFP question | Formal | 3 |
| SCN-010 | Invite a client to a product roadmap session | Professional | 3 |

Each scenario includes a **Human Reference Email** in `data/scenarios.json` for qualitative comparison. To inspect or edit scenarios, open that file directly.

**Two prompting strategies** (same model, different templates):

| Strategy | Description |
|----------|-------------|
| `basic` | Minimal LangChain template — intent, facts, tone, four sections |
| `structured` | Role instruction, tone guide, section rules, no-hallucination constraints (**recommended**) |

---

## Outputs

Evaluation artifacts go to **`outputs/`**. Report documents go to **`reports/`** whenever you run the full pipeline (`python -m src.run_all`) without `--skip-report`.

| Path | Contents |
|------|----------|
| `outputs/generated_emails.json` | 20 emails (10 scenarios × 2 strategies) |
| `outputs/evaluation_results.json` | Raw scores, metric definitions, strategy averages |
| `outputs/evaluation_results.csv` | Same evaluation data in CSV format |
| `outputs/comparison_summary.json` | Winner, metric comparison, production recommendation |
| `outputs/my_email.json` | Single custom email from `run_one` |
| **`reports/final_report.docx`** | Final report (Word) — see [Final report](#final-report) |
| `traces/` | Validation and pipeline trace logs |

Re-running `python -m src.run_all` overwrites files in `outputs/` and `reports/` — nothing to delete first.

### Final report

When you run `python -m src.run_all` (without `--skip-report`), the assessment **Final Report** is saved as:

```
reports/final_report.docx
```

Upload to Google Drive and open with Google Docs if a Google Doc link is required.

The report matches the assessment deliverable and includes:

1. **Prompt templates used** — basic and structured (with examples)
2. **Custom evaluation metrics** — definitions and logic for all 3 metrics
3. **Comparative analysis summary (Section 3)** — winner, scores, failure mode, production recommendation
4. **Raw evaluation data** — per-scenario score table and strategy averages (same data as `evaluation_results.json` / `evaluation_results.csv`)

Example terminal output when step 6 finishes:

```
  Final report (Word): .../assessment_sg/reports/final_report.docx
```

If Word has the file open:

```
  Final report (Word): .../assessment_sg/reports/final_report_new.docx
  Note: Close final_report.docx in Word, then re-run to overwrite it.
```

Regenerate after any pipeline run:

```powershell
python -m src.run_all
```

---

## How It Works

**Input:** Intent + Key Facts + Tone

**Three custom metrics** (each 0.0–1.0; overall = average of three):

1. **Fact Recall** — all key facts included?
2. **Tone and Format Accuracy** — correct tone + subject, greeting, body, closing?
3. **Conciseness and Fluency** — readable, concise, polished?

**Chain:** `ChatPromptTemplate | ChatOpenAI | StrOutputParser`

**Recommended models:** `gpt-4o-mini` (default) · `gpt-4o` (best tone/fluency)

---

## Project Layout

```
assessment_sg/
├── data/
│   └── scenarios.json              # 10 evaluation scenarios + reference emails
├── src/
│   ├── run_all.py                  # Full pipeline
│   ├── run_one.py                  # Single email CLI
│   ├── prompt_builder.py           # Basic + structured prompt templates
│   ├── evaluator.py                # Three custom metrics
│   ├── compare.py                  # Strategy comparison
│   ├── evaluation_export.py        # Evaluation CSV export
│   └── report.py                   # Final report Word doc
├── tests/
├── outputs/                        # JSON + CSV from run_all (steps 3–5)
├── reports/                        # final_report.docx (run_all step 6)
├── traces/
├── TDD.md                          # Test cases TC-01 to TC-30
├── Traces.md                       # Acceptance traces
└── L1Speccing.md                   # Product specification
```

---

## Test Cases (summary)

| ID | Feature | Command / trigger |
|----|---------|-------------------|
| TC-01 | Valid email generation | `run_one` / `generate_email()` |
| TC-06 | Load 10 scenarios | `data/scenarios.json` |
| TC-07 | Batch — 20 emails | `run_all` step 3 |
| TC-08–TC-10 | Custom metrics | `evaluator.py` |
| TC-11 | Evaluation JSON + CSV | `run_all` step 4 |
| TC-12 | Strategy comparison | `run_all` step 5 |
| TC-13 | Report files in `reports/` | `run_all` step 6 |
| TC-15 | Full pipeline (OpenAI) | `python -m src.run_all` |
| TC-16 | Mock pipeline | `python -m src.run_all --mock` |

Each test case in [TDD.md](TDD.md) includes **Input**, **Expected Output**, and **Pass Criteria**.

---

## Documentation

| Doc | Description |
|-----|-------------|
| [TDD.md](TDD.md) | Test cases TC-01 to TC-30 |
| [Traces.md](Traces.md) | 14 acceptance traces |
| [L1Speccing.md](L1Speccing.md) | Product specification |

---

## License

Assessment project — for evaluation purposes.
