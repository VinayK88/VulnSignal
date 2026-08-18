from dataclasses import dataclass


@dataclass(frozen=True)
class Finding:
    finding_id: str
    model_flagged: bool
    actually_vulnerable: bool
    predicted_severity: str
    confirmed_severity: str
    confidence: float
    cwe: str
    code_path: str
    description: str
    evidence_quality: float
    fix_quality: float
    asset_criticality: float
    developer_accepted: bool
    actionable: bool
    remediated: bool
    resolution_verified: bool
    triage_minutes: float
    remediation_hours: float
