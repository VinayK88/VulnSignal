from __future__ import annotations

import re
from typing import Iterable

from .models import Finding


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9_]+", text.lower()))


def similarity(a: Finding, b: Finding) -> float:
    left = _tokens(f"{a.cwe} {a.code_path} {a.description}")
    right = _tokens(f"{b.cwe} {b.code_path} {b.description}")
    if not left and not right:
        return 1.0
    return len(left & right) / len(left | right)


def cluster_duplicates(findings: Iterable[Finding], threshold: float = 0.58) -> list[list[str]]:
    """Greedy transparent baseline for duplicate finding clustering."""
    rows = [f for f in findings if f.model_flagged]
    clusters: list[list[Finding]] = []
    for finding in rows:
        placed = False
        for cluster in clusters:
            if max(similarity(finding, existing) for existing in cluster) >= threshold:
                cluster.append(finding)
                placed = True
                break
        if not placed:
            clusters.append([finding])
    return [[f.finding_id for f in cluster] for cluster in clusters]


def duplicate_summary(findings: Iterable[Finding], threshold: float = 0.58) -> dict[str, int | float]:
    rows = [f for f in findings if f.model_flagged]
    clusters = cluster_duplicates(rows, threshold)
    duplicate_count = sum(max(0, len(c) - 1) for c in clusters)
    return {
        "flagged_findings": len(rows),
        "unique_clusters": len(clusters),
        "duplicate_findings": duplicate_count,
        "duplicate_reduction_rate": round(duplicate_count / len(rows), 4) if rows else 0.0,
    }
