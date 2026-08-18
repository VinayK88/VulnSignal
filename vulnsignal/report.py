from .dedupe import duplicate_summary
from .experiment import bootstrap_remediation_difference, compare_workflows
from .fixtures import synthetic_findings, synthetic_triage_experiment
from .metrics import actionability_score, finding_quality_report


def build_report() -> dict:
    findings = synthetic_findings()
    control, treatment = synthetic_triage_experiment()
    scores = {f.finding_id: actionability_score(f) for f in findings if f.model_flagged}
    return {
        "finding_quality": finding_quality_report(findings),
        "deduplication": duplicate_summary(findings),
        "top_actionability": sorted(scores.items(), key=lambda x: x[1], reverse=True)[:5],
        "triage_experiment": compare_workflows(control, treatment),
        "remediation_bootstrap": bootstrap_remediation_difference(control, treatment),
        "boundary": "Synthetic portfolio benchmark only; no production efficacy claim.",
    }
