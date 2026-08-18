<div align="center">

# VulnSignal

### AI Security Finding Quality · Triage · Remediation Intelligence

**Measure what happens after an AI system says “this looks vulnerable.”**

</div>

---

VulnSignal is a security data-science project for evaluating AI-generated security findings across the full workflow: detection, validation, severity, actionability, duplication, developer triage, remediation, and verified resolution.

The core question is not only:

> **Did the model find a vulnerability?**

It is:

> **Was the finding correct, appropriately severe, actionable, non-duplicative, accepted by the developer, remediated, and actually verified as resolved?**

## Why this project exists

Security products can look impressive on raw finding counts while creating large downstream costs: duplicate alerts, inflated severity, low-actionability reports, wasted developer time, and findings that never turn into fixes. VulnSignal treats those downstream outcomes as first-class product and security metrics.

## Architecture

```text
Repository / code changes
        ↓
AI security analyzer
        ↓
Candidate findings
        ↓
Ground-truth / disposition join
        ↓
Finding quality evaluation
  ├─ precision / recall
  ├─ severity calibration
  ├─ actionability
  ├─ duplicate burden
  └─ developer acceptance
        ↓
Triage workflow
        ↓
Remediation
        ↓
Resolution verification
        ↓
Product + security outcome report
```

## Metrics

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
- transparent actionability scores;
- treatment-vs-control triage workflow effects;
- bootstrap uncertainty for remediation-rate improvement.

## Finding schema

```text
finding_id
model_flagged
actually_vulnerable
predicted_severity
confirmed_severity
confidence
cwe
code_path
description
evidence_quality
fix_quality
asset_criticality
developer_accepted
actionable
remediated
resolution_verified
triage_minutes
remediation_hours
```

The schema intentionally connects model behavior to downstream product outcomes rather than stopping at classification accuracy.

## Actionability score

VulnSignal includes a transparent prioritization score:

```text
actionability =
    0.30 × model confidence
  + 0.25 × evidence quality
  + 0.20 × fix quality
  + 0.25 × asset criticality
  - 0.15 × duplicate penalty
```

This is **not** presented as a calibrated vulnerability probability. It is an inspectable decision-support score whose assumptions can be challenged and sensitivity-tested.

## Duplicate finding reduction

The baseline duplicate engine clusters AI findings using token overlap across CWE, code path, and finding description. It is deliberately simple and interpretable so the project can measure a practical question:

> How much developer triage work disappears when near-duplicate findings are consolidated?

A production evolution could compare lexical similarity with embedding-based retrieval, learned pairwise duplicate classification, or graph-based root-cause grouping.

## Triage experiment

The synthetic experiment compares two workflows:

**Control** — developer receives the raw AI finding.

**Treatment** — developer receives an enriched finding with stronger evidence, prioritization context, and remediation guidance.

The analysis compares:

```text
triage completion
finding acceptance
remediation
median triage time
```

and bootstraps the treatment-minus-control remediation difference rather than reporting only a point estimate.

The fixture is deterministic and synthetic. It demonstrates experimentation mechanics, not a causal claim about any real product.

## SQL data foundation

`sql/finding_quality.sql` shows how the same metrics could be computed from a warehouse after joining AI findings to validation, developer disposition, and remediation outcomes.

A production data model would typically connect:

```text
finding event
  → model/version metadata
  → code asset / owner
  → triage disposition
  → duplicate/root-cause cluster
  → remediation change
  → resolution verification
```

That linkage is essential because finding quality cannot be inferred from model output alone.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .

vulnsignal
python -m unittest discover -s tests -v
```

## Repository map

```text
VulnSignal/
├── vulnsignal/
│   ├── models.py       finding contract
│   ├── metrics.py      quality + downstream metrics
│   ├── dedupe.py       transparent duplicate clustering
│   ├── experiment.py   workflow comparison + bootstrap
│   ├── fixtures.py     deterministic synthetic benchmark
│   ├── report.py       integrated evidence report
│   └── cli.py
├── sql/
│   └── finding_quality.sql
├── tests/
├── .github/workflows/ci.yml
├── SECURITY.md
└── pyproject.toml
```

## Production evolution

High-value next steps would be:

1. Add versioned adapters for real code-security model outputs while keeping evaluation data authorized and privacy-reviewed.
2. Build severity reliability diagrams and calibration metrics by CWE and asset class.
3. Replace lexical duplicate clustering with embeddings plus human-reviewed duplicate labels.
4. Train a remediation-likelihood model using only pre-triage features and time-aware validation.
5. Measure subgroup performance by repository, language, CWE, severity, and customer segment.
6. Track time-to-triage and time-to-remediation with censoring-aware analysis for unresolved findings.
7. Evaluate staged product changes with assignment-aware experiments, guardrails, and confidence intervals.
8. Connect finding quality to customer value: activation, repeated use, accepted recommendations, vulnerability reduction, and enterprise retention.

## Evaluation boundary

All code paths, findings, developers, dispositions, and outcomes in this repository are synthetic. The included metrics validate the analytical workflow and software implementation only. They do not estimate real-world vulnerability-detection accuracy or product impact.

---

**A security finding is valuable only when it is trustworthy enough to act on—and the action measurably reduces risk.**
