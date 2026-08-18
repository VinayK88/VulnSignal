from __future__ import annotations

from dataclasses import dataclass
from random import Random
from statistics import median


@dataclass(frozen=True)
class TriageObservation:
    finding_id: str
    workflow: str
    completed: bool
    accepted: bool
    remediated: bool
    triage_minutes: float


def summarize_workflow(rows: list[TriageObservation]) -> dict[str, float | int]:
    if not rows:
        raise ValueError("rows must not be empty")
    return {
        "n": len(rows),
        "triage_completion_rate": round(sum(r.completed for r in rows) / len(rows), 4),
        "acceptance_rate": round(sum(r.accepted for r in rows) / len(rows), 4),
        "remediation_rate": round(sum(r.remediated for r in rows) / len(rows), 4),
        "median_triage_minutes": round(median(r.triage_minutes for r in rows), 2),
    }


def compare_workflows(control: list[TriageObservation], treatment: list[TriageObservation]) -> dict:
    a = summarize_workflow(control)
    b = summarize_workflow(treatment)
    keys = ["triage_completion_rate", "acceptance_rate", "remediation_rate", "median_triage_minutes"]
    return {
        "control": a,
        "treatment": b,
        "delta_treatment_minus_control": {k: round(float(b[k]) - float(a[k]), 4) for k in keys},
    }


def bootstrap_remediation_difference(
    control: list[TriageObservation],
    treatment: list[TriageObservation],
    iterations: int = 2000,
    seed: int = 17,
) -> dict[str, float]:
    if not control or not treatment:
        raise ValueError("both groups are required")
    rng = Random(seed)
    diffs = []
    for _ in range(iterations):
        a = [control[rng.randrange(len(control))] for _ in control]
        b = [treatment[rng.randrange(len(treatment))] for _ in treatment]
        diffs.append(sum(x.remediated for x in b) / len(b) - sum(x.remediated for x in a) / len(a))
    diffs.sort()
    observed = sum(x.remediated for x in treatment) / len(treatment) - sum(x.remediated for x in control) / len(control)
    return {
        "observed_difference": round(observed, 4),
        "ci95_low": round(diffs[int(0.025 * (iterations - 1))], 4),
        "ci95_high": round(diffs[int(0.975 * (iterations - 1))], 4),
    }
