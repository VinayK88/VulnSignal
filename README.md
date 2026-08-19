<div align="center">

# VulnSignal

### AI Security Finding Quality · Model Routing · Triage · Remediation Intelligence

**Measure what happens after an AI system says “this looks vulnerable”—and choose the right AI architecture for the security workflow.**

[![Python](https://img.shields.io/badge/Python-3.10--3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Dashboard-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](dashboard/app.py)
[![CI](https://github.com/VinayK88/VulnSignal/actions/workflows/ci.yml/badge.svg)](https://github.com/VinayK88/VulnSignal/actions/workflows/ci.yml)
[![Safety](https://img.shields.io/badge/Data-Synthetic%20Only-7B61FF)](#evaluation-boundary)

**Evaluate → route → detect → validate → calibrate → deduplicate → triage → remediate → verify**

</div>

---

![VulnSignal dashboard preview](assets/dashboard-preview.svg)

VulnSignal is a security data-science and AI-systems platform for evaluating AI-generated security findings across the **full security workflow**—not just raw model accuracy.

It answers two hard questions:

> **Was the finding correct, appropriately severe, actionable, non-duplicative, accepted by the developer, remediated, and actually verified as resolved?**

> **Which AI model or architecture should handle this security scenario when quality, latency, cost, groundedness, and tool reliability all matter?**

## Why this project matters

AI security products can look successful on finding volume while creating downstream costs: duplicate alerts, inflated severity, weak evidence, wasted developer time, and findings that never turn into verified fixes.

A second failure mode is architectural: using the same large model for every task, even when deterministic rules, classical ML, a specialized transformer, grounded RAG, or an agentic workflow would be safer, faster, or cheaper.

VulnSignal treats both downstream security outcomes and model-selection trade-offs as first-class metrics.

```text
Security scenario
   ↓
Which model / architecture is the best fit?
   ↓
AI finding
   ↓
Is it correct?
   ↓
Is severity calibrated?
   ↓
Is it actionable and unique?
   ↓
Does a developer accept it?
   ↓
Does it get remediated?
   ↓
Is the resolution verified?
```

## Dashboard

The Streamlit dashboard turns the synthetic benchmark into an executive + analyst workflow with five views:

1. **Executive overview** — precision, actionability, acceptance, verified resolution, security-outcome funnel, and highest-value findings.
2. **Finding explorer** — interactive filtering by predicted severity, CWE, and actionability score.
3. **Workflow experiment** — control vs enriched-finding workflow for completion, acceptance, remediation, and triage time.
4. **Quality diagnostics** — recall, severity error, duplicate burden, deduplication reduction, severity mix, and CWE mix.
5. **Model evaluation & routing** — scenario-specific comparison of Rules + ML, fine-tuned transformers, RAG LLMs, and agentic reasoning using security and production metrics.

Run it locally:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dashboard]'
streamlit run dashboard/app.py
```

## Architecture

```mermaid
flowchart LR
    EVENT[Security scenario / event] --> EVAL[Model + architecture evaluation]
    EVAL --> ROUTER[Scenario-aware router]
    ROUTER --> MODEL[Rules / ML / Transformer / RAG / Agent]
    CODE[Repository / code changes] --> MODEL
    MODEL --> F[Candidate findings]
    F --> JOIN[Ground truth + dispositions]
    JOIN --> Q[Finding quality engine]
    Q --> DEDUPE[Duplicate clustering]
    Q --> SCORE[Actionability scoring]
    DEDUPE --> TRIAGE[Developer triage]
    SCORE --> TRIAGE
    TRIAGE --> FIX[Remediation]
    FIX --> VERIFY[Resolution verification]
    VERIFY --> OUT[Security + product outcomes]
    OUT --> DASH[Dashboard / report]
    OUT --> EVAL
```

## Measurement framework

VulnSignal deliberately separates five layers that are often collapsed into one model score:

| Layer | Core question | Metrics |
|---|---|---|
| **Architecture selection** | Which AI approach is appropriate for this security scenario? | Precision, recall, task success, latency, cost, unsupported claims, tool reliability, utility |
| **Model quality** | Did the system identify real vulnerabilities? | Precision, recall |
| **Finding quality** | Is the output useful and correctly prioritized? | Severity MAE, actionability, duplication |
| **Workflow quality** | Can developers act efficiently? | Acceptance, triage completion, triage time |
| **Security outcome** | Did the finding lead to real risk reduction? | Remediation, verified resolution |

## Model evaluation & routing

`vulnsignal/model_selection.py` demonstrates a scenario-aware decision layer instead of a one-model-for-everything design.

The synthetic benchmark compares four approaches:

```text
Rules + ML
Fine-tuned transformer
RAG LLM
Agentic reasoner
```

against three security scenarios:

```text
High-volume IOC triage
Contextual vulnerability validation
Multi-step incident investigation
```

The router uses scenario-specific objectives so the winning architecture changes with the workload:

- **High-volume IOC triage → Rules + ML** when throughput, predictable precision, and low cost dominate.
- **Contextual vulnerability validation → RAG LLM** when grounded context and finding quality matter more.
- **Multi-step incident investigation → Agentic reasoner** when planning, end-to-end task success, and reliable tool use justify higher latency and cost.

The production utility score combines:

```text
precision
recall
task success
latency
cost per task
unsupported-claim rate
tool-call success
```

The goal is not to claim that one architecture is universally superior. It is to demonstrate how a production security platform can **evaluate, compare, select, and continuously re-evaluate the right AI approach for each scenario**.

## Core metrics

The executable synthetic benchmark reports:

- finding precision and recall;
- severity error in ordinal severity levels;
- actionability rate;
- developer acceptance rate;
- duplicate rate and deduplication reduction;
- remediation rate;
- verified-resolution rate;
- median time to triage;
- median time to remediation;
- treatment-vs-control workflow effects;
- bootstrap uncertainty for remediation-rate improvement;
- model/architecture task success, latency, cost, unsupported-claim rate, tool reliability, and scenario-level utility.

## Actionability score

VulnSignal includes an inspectable prioritization score:

```text
actionability =
    0.30 × model confidence
  + 0.25 × evidence quality
  + 0.20 × fix quality
  + 0.25 × asset criticality
  - 0.15 × duplicate penalty
```

This is **not** presented as a calibrated vulnerability probability. It is a transparent decision-support score whose assumptions can be challenged and sensitivity-tested.

## Duplicate reduction

The baseline duplicate engine clusters findings using token overlap across CWE, code path, and description. The goal is to quantify a practical security-product question:

> **How much developer triage work disappears when near-duplicate findings are consolidated?**

A production evolution could compare this baseline with embedding retrieval, pairwise duplicate classification, or graph-based root-cause grouping.

## Triage experiment

The synthetic experiment compares:

**Control** — developer receives the raw AI finding.

**Treatment** — developer receives stronger evidence, prioritization context, and remediation guidance.

The analysis measures:

```text
triage completion
finding acceptance
remediation
median triage time
```

and bootstraps the treatment-minus-control remediation difference rather than reporting only a point estimate.

## SQL data foundation

`sql/finding_quality.sql` demonstrates how warehouse data can connect:

```text
finding event
  → model/version metadata
  → code asset / owner
  → validation / disposition
  → duplicate/root-cause cluster
  → remediation change
  → resolution verification
```

That linkage matters because security finding quality cannot be inferred from model output alone.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .

vulnsignal
python -m unittest discover -s tests -v
```

Dashboard:

```bash
pip install -e '.[dashboard]'
streamlit run dashboard/app.py
```

## Repository map

```text
VulnSignal/
├── dashboard/
│   ├── app.py                                  executive + analyst dashboard
│   └── pages/
│       └── 1_Model_Evaluation_and_Routing.py  architecture benchmark + router view
├── assets/
│   └── dashboard-preview.svg
├── vulnsignal/
│   ├── models.py         finding contract
│   ├── model_selection.py scenario-aware model evaluation + routing
│   ├── metrics.py        quality + downstream metrics
│   ├── dedupe.py         transparent duplicate clustering
│   ├── experiment.py     workflow comparison + bootstrap
│   ├── fixtures.py       deterministic synthetic benchmark
│   ├── report.py         integrated evidence report
│   └── cli.py
├── sql/
│   └── finding_quality.sql
├── tests/
│   ├── test_vulnsignal.py
│   └── test_model_selection.py
├── .github/workflows/ci.yml
├── SECURITY.md
└── pyproject.toml
```

## Production evolution

High-value extensions would include:

- versioned adapters for real code-security model outputs;
- live adapters for multiple hosted and self-hosted models;
- offline benchmark gates before promoting a model/router configuration;
- online telemetry that re-estimates routing utility by scenario and model version;
- fallback routing, circuit breakers, budget constraints, and human escalation policies;
- calibration curves by CWE, language, repository, and severity;
- embedding-based duplicate detection with human-reviewed labels;
- remediation-likelihood modeling using pre-triage features only;
- time-aware validation and subgroup performance analysis;
- censoring-aware time-to-remediation analysis;
- staged product experiments with guardrails and confidence intervals;
- telemetry linking finding quality to activation, repeat use, accepted recommendations, vulnerability reduction, and enterprise value.

## Evaluation boundary

All code paths, findings, developer dispositions, outcomes, model comparisons, and routing scores in this repository are synthetic. The included metrics validate the analytical workflow and software implementation only; they do not estimate real-world vulnerability-detection accuracy, production model economics, or product impact.

---

<div align="center">

**A security finding is valuable only when it is trustworthy enough to act on—and the action measurably reduces risk.**

</div>
