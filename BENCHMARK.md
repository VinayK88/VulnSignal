# VulnSignal — Benchmark & Reviewer Walkthrough

This page defines a reproducible review of finding quality and model routing. Every code path, finding, disposition, model score, cost, latency, and outcome in the repository is synthetic.

## What is being tested

VulnSignal measures an AI security system beyond finding volume:

~~~text
candidate finding
  → correctness and severity
  → evidence and actionability
  → duplicate reduction
  → developer acceptance
  → remediation
  → verified resolution
~~~

It also compares model architectures using scenario-specific objectives instead of assuming one model is best for every workload.

## Expected routing behavior

| Synthetic scenario | Expected architecture | Why |
| --- | --- | --- |
| High-volume IOC triage | Rules + ML | throughput, predictable precision, and low cost |
| Contextual vulnerability validation | RAG LLM | grounded context and finding quality |
| Multi-step incident investigation | Agentic reasoner | planning, task success, and reliable tool use |

The router evaluates precision, recall, task success, latency, cost, unsupported claims, and tool-call success. These are illustrative benchmark inputs, not vendor performance claims.

## Reproduce the evidence

~~~bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dashboard]'

# Integrated finding-quality, experiment, and routing report
vulnsignal

# Regression tests
python -m unittest discover -s tests -v

# Interactive executive + analyst review
streamlit run dashboard/app.py
~~~

GitHub Actions validates the executable workflow on Python 3.10, 3.11, and 3.12.

## Five-minute demo

1. Open the executive view and follow the funnel from detected findings to verified resolutions.
2. Filter the finding explorer by severity, CWE, and actionability.
3. Inspect duplicate clusters and quantify the triage burden removed.
4. Compare raw findings with evidence-enriched findings in the workflow experiment.
5. Open model evaluation and change the security scenario.
6. Explain why the selected architecture changes when latency, cost, groundedness, and tool reliability receive different weights.

## Reviewer scorecard

| Question | Evidence to inspect |
| --- | --- |
| Is the finding correct? | precision and recall |
| Is severity useful? | ordinal severity error |
| Can a developer act? | evidence, fix quality, and actionability |
| Is it redundant? | duplicate rate and reduction |
| Did it change behavior? | acceptance and triage completion |
| Did it reduce risk? | remediation and verified resolution |
| Is the architecture appropriate? | scenario utility and constraint trade-offs |

## Production benchmark plan

A credible production evaluation should add authorized real findings, blinded reviewer labels, time-aware splits, subgroup analysis by language/CWE/repository, confidence intervals, calibration, fallback routing, circuit breakers, drift monitoring, and telemetry that links findings to verified fixes.

The included benchmark validates the analytical workflow and software implementation only. It does not estimate real-world vulnerability accuracy, model economics, or product impact.
