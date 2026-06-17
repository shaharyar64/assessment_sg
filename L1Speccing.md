# SPEC — Email Generation Assistant

## Summary

This project requires building a working Email Generation Assistant that uses an LLM to generate professional emails from structured user input. The assistant must accept an email intent, key facts, and a desired tone, then produce a complete email that is clear, well-written, and aligned with the user’s request. The project also includes a documented prompting approach, custom evaluation metrics, model or strategy comparison, and final deliverables.

## 1. Purpose

Build a working prototype of an Email Generation Assistant that generates professional emails from structured user input using an LLM.

The assistant must produce a complete, well-written email based on three inputs:

1. Intent
2. Key Facts
3. Tone

The project must also include a documented prompting approach, a custom evaluation strategy, model or strategy comparison, and final deliverables.

---

## 2. Product Scope

### In Scope

The system must include:

- A prompt template for email generation
- A script or application that accepts structured inputs
- 10 predefined evaluation scenarios
- One human reference email per scenario
- Three custom evaluation metrics
- A structured evaluation report in CSV or JSON
- Comparison between two models or two prompting strategies
- A final written analysis explaining which model or strategy performed better
- A README explaining setup and execution


---

## 3. Core Inputs

### 3.1 Intent

Defines the main purpose of the email.

Examples:

- Follow up after a meeting
- Request proposal details
- Apologize for a delay
- Confirm next steps

### 3.2 Key Facts

Defines the required information that must be included in the final email.

The generated email must include all provided key facts naturally and without changing their meaning.

### 3.3 Tone

Defines the desired writing style of the email.

Examples:

- Formal
- Casual
- Urgent
- Empathetic
- Professional

---

## 4. Expected Output

For each input scenario, the assistant must generate one professional email.

The generated email should include:

- Subject line
- Greeting
- Clear email body
- Required key facts
- Appropriate tone
- Closing/sign-off

The email must not invent information that was not provided in the input.

### Sample Input

```text
Intent: Follow up after a product demo

Key Facts:
- The demo was held on Monday
- The client asked for pricing details
- The proposal should be shared by Friday
- The client is interested in the automation dashboard

Tone: Formal
```

### Sample Expected Output

```text
Subject: Follow-Up on Product Demo

Hi [Recipient Name],

Thank you for attending the product demo on Monday. I appreciate your interest in the automation dashboard and the questions you shared during the session.

As discussed, I will prepare the pricing details and share the proposal with you by Friday.

Please let me know if there is any additional information you would like included.

Best regards,  
[Sender Name]
```

---

## 5. Main Flow

```text
Input Scenario
  ↓
Prompt Builder
  ↓
Model / Strategy A generates email
  ↓
Model / Strategy B generates email
  ↓
Evaluation metrics score both outputs
  ↓
Scores saved to CSV/JSON
  ↓
Comparison summary generated
```

---

## 6. Prompt Engineering Requirement

The assistant must use and document an advanced prompting technique to improve output quality and reliability.

Acceptable techniques include:

- Role-playing
- Few-shot examples
- Chain-of-thought prompting
- Structured prompting

The final report must include the prompt template used and explain how the selected prompting technique improves email quality.

---

## 7. Test Data Requirement

The project must include 10 unique input scenarios.

Each scenario must include:

- Intent
- Key Facts
- Tone
- Human Reference Email

The Human Reference Email represents the ideal output for that scenario.

---

## 8. Custom Evaluation Metrics

The project must define and implement three custom metrics for judging the quality of generated emails.

Each metric must include:

- Metric name
- Definition
- Scoring logic
- Raw score per scenario

The metrics should be specific to the email generation task.

### 8.1 Custom Metric 1

Recommended focus: Fact Recall, Specificity, or Clarity.

This metric should measure whether the generated email includes the required information from the key facts.

### 8.2 Custom Metric 2

Recommended focus: Tone Accuracy, Format Adherence, or Sentence Structure Complexity.

This metric should measure whether the generated email follows the requested tone and expected email style.

### 8.3 Custom Metric 3

Recommended focus: Conciseness, Introduction Effectiveness, or Grammar/Fluency.

This metric should measure the overall quality, readability, or polish of the generated email.

---

## 9. Evaluation Output Requirement

The evaluation script must run all 10 scenarios and output a structured file.

The output may be CSV, JSON, or another clearly structured format.

The evaluation output must include:

- Definitions and logic for all three custom metrics
- Raw scores for all 10 scenarios
- Scores for each custom metric
- Overall average score for the model or strategy

---

## 10. Model or Strategy Comparison Requirement

The same 10 scenarios and same evaluation metrics must be used to compare two models or two prompting strategies.

The comparison must answer:

- Which model or strategy performed better according to the three custom metrics?
- What was the biggest failure mode of the lower-performing model or strategy?
- Which model or strategy is recommended for production?
- Why is that recommendation supported by the evaluation data?

---


## 11 Final Report

The final report must be provided as a PDF or Google Doc.

It must include:

- Prompt template used
- Definitions and logic for the three custom metrics
- Raw evaluation data from the CSV/JSON output
- Comparative analysis summary

---

## 12. Acceptance Criteria

The project is complete when:

1. The assistant generates professional emails from Intent, Key Facts, and Tone.
2. An advanced prompting technique is used and documented.
3. There are 10 unique test scenarios.
4. Each scenario includes a Human Reference Email.
5. Three custom evaluation metrics are defined and implemented.
6. The evaluation script outputs raw scores for all 10 scenarios.
7. The evaluation script calculates an overall average score.
8. Two models or prompting strategies are compared using the same scenarios and metrics.
9. A final analysis recommends the better model or strategy using metric data.
