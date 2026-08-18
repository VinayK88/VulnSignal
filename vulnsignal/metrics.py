from __future__ import annotations

from collections import Counter
from statistics import median
from typing import Iterable

from .models import Finding

SEVERITY_RANK = {"none": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}


def _rate(n: int, d: int) -> float:
    return n / d if d else 0.0


def finding_quality_report(findings: Iterable[Finding]) -> dict[str, float | int]:
    rows = list(findings)
    if not rows:
        raise ValueError("findings must not be empty")

    flagged = [f for f in rows if f.model_flagged]
    true_vulns = [f for f in rows if f.actually_vulnerable]
    true_positives = [f for f in flagged if f.actually_vulnerable]
    accepted = [f for f in flagged if f.developer_accepted]
    actionable = [f for f in flagged if f.actionable]
    remediated = [f for f in flagged if f.remediated]
    verified = [f for f in flagged if f.resolution_verified]

    severity_errors = [
        abs(SEVERITY_RANK[f.predicted_severity] - SEVERITY_RANK[f.confirmed_severity])
        for f in true_positives
    ]
    triage = [f.triage_minutes for f in flagged if f.triage_minutes >= 0]
    remediation = [f.remediation_hours for f in remediated if f.remediation_hours >= 0]

    cluster_counts = Counter((f.cwe, f.code_path) for f in flagged)
    duplicate_findings = sum(max(0, count - 1) for count in cluster_counts.values())

    return {
        "candidates": len(rows),
        "flagged_findings": len(flagged),
        "true_vulnerabilities": len(true_vulns),
        "precision": round(_rate(len(true_positives), len(flagged)), 4),
        "recall": round(_rate(len(true_positives), len(true_vulns)), 4),
        "severity_mae_levels": round(sum(severity_errors) / len(severity_errors), 4)
        if severity_errors
        else 0.0,
        "actionability_rate": round(_rate(len(actionable), len(flagged)), 4),
        "developer_acceptance_rate": round(_rate(len(accepted), len(flagged)), 4),
        "duplicate_rate": round(_rate(duplicate_findings, len(flagged)), 4),
        "remediation_rate": round(_rate(len(remediated), len(flagged)), 4),
        "verified_resolution_rate": round(_rate(len(verified), len(flagged)), 4),
        "median_triage_minutes": round(median(triage), 2) if triage else 0.0,
        "median_remediation_hours": round(median(remediation), 2) if remediation else 0.0,
    }


def actionability_score(finding: Finding, duplicate_penalty: float = 0.0) -> float:
    """Transparent finding-quality score, not a vulnerability probability."""
    score = (
        0.30 * finding.confidence
        + 0.25 * finding.evidence_quality
        + 0.20 * finding.fix_quality
        + 0.25 * finding.asset_criticality
        - 0.15 * duplicate_penalty
    )
    return round(max(0.0, min(1.0, score)), 4)
