from __future__ import annotations

from dataclasses import asdict

import pandas as pd
import streamlit as st

from vulnsignal.dedupe import duplicate_summary
from vulnsignal.experiment import compare_workflows
from vulnsignal.fixtures import synthetic_findings, synthetic_triage_experiment
from vulnsignal.metrics import actionability_score, finding_quality_report

st.set_page_config(
    page_title="VulnSignal | AI Security Finding Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
.block-container {padding-top: 1.6rem; padding-bottom: 3rem; max-width: 1500px;}
[data-testid="stMetric"] {
    background: linear-gradient(145deg, rgba(32,39,55,.96), rgba(18,23,34,.96));
    border: 1px solid rgba(148,163,184,.20);
    padding: 14px 16px;
    border-radius: 14px;
}
[data-testid="stMetricLabel"] {font-size: .82rem; color: #a8b3c7;}
[data-testid="stMetricValue"] {font-size: 1.75rem;}
.vs-hero {
    border: 1px solid rgba(148,163,184,.18);
    border-radius: 18px;
    padding: 22px 24px;
    margin-bottom: 18px;
    background: linear-gradient(120deg, rgba(14,165,233,.10), rgba(99,102,241,.08), rgba(15,23,42,.15));
}
.vs-kicker {font-size:.78rem; text-transform:uppercase; letter-spacing:.13em; color:#7dd3fc; font-weight:700;}
.vs-title {font-size:2.15rem; font-weight:800; margin:.2rem 0 .3rem 0;}
.vs-sub {color:#aeb9cc; font-size:1rem; max-width:900px; line-height:1.55;}
.vs-note {color:#94a3b8; font-size:.82rem;}
</style>
""",
    unsafe_allow_html=True,
)

findings = synthetic_findings()
control, treatment = synthetic_triage_experiment()
quality = finding_quality_report(findings)
dedupe = duplicate_summary(findings)
experiment = compare_workflows(control, treatment)

rows = []
for finding in findings:
    row = asdict(finding)
    row["actionability_score"] = actionability_score(finding)
    row["status"] = (
        "Verified"
        if finding.resolution_verified
        else "Remediated"
        if finding.remediated
        else "Accepted"
        if finding.developer_accepted
        else "Open"
    )
    rows.append(row)

df = pd.DataFrame(rows)
flagged_df = df[df["model_flagged"]].copy()

st.markdown(
    """
<div class="vs-hero">
  <div class="vs-kicker">AI Security Finding Intelligence</div>
  <div class="vs-title">VulnSignal</div>
  <div class="vs-sub">Measure whether AI-generated security findings are accurate, actionable, non-duplicative, accepted by developers, remediated, and ultimately verified as resolved.</div>
</div>
""",
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Filters")
    severities = sorted(flagged_df["predicted_severity"].unique().tolist())
    selected_severity = st.multiselect("Predicted severity", severities, default=severities)
    cwes = sorted(flagged_df["cwe"].unique().tolist())
    selected_cwe = st.multiselect("CWE", cwes, default=cwes)
    min_actionability = st.slider("Minimum actionability", 0.0, 1.0, 0.0, 0.05)
    st.divider()
    st.caption("Synthetic portfolio benchmark. Metrics demonstrate the evaluation workflow, not production efficacy.")

filtered = flagged_df[
    flagged_df["predicted_severity"].isin(selected_severity)
    & flagged_df["cwe"].isin(selected_cwe)
    & (flagged_df["actionability_score"] >= min_actionability)
].copy()

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Finding precision", f"{quality['precision']:.1%}")
m2.metric("Actionability", f"{quality['actionability_rate']:.1%}")
m3.metric("Developer acceptance", f"{quality['developer_acceptance_rate']:.1%}")
m4.metric("Verified resolution", f"{quality['verified_resolution_rate']:.1%}")
m5.metric("Median triage", f"{quality['median_triage_minutes']:.0f} min")

st.caption(
    f"{quality['flagged_findings']} AI findings · {quality['true_vulnerabilities']} confirmed vulnerabilities · "
    f"{quality['duplicate_rate']:.1%} duplicate burden · {quality['median_remediation_hours']:.1f}h median remediation"
)

overview, findings_tab, workflow_tab, quality_tab = st.tabs(
    ["Executive overview", "Finding explorer", "Workflow experiment", "Quality diagnostics"]
)

with overview:
    left, right = st.columns([1.05, 0.95])
    with left:
        st.subheader("Security outcome funnel")
        funnel = pd.DataFrame(
            {
                "stage": ["AI flagged", "Actionable", "Accepted", "Remediated", "Verified"],
                "findings": [
                    len(flagged_df),
                    int(flagged_df["actionable"].sum()),
                    int(flagged_df["developer_accepted"].sum()),
                    int(flagged_df["remediated"].sum()),
                    int(flagged_df["resolution_verified"].sum()),
                ],
            }
        ).set_index("stage")
        st.bar_chart(funnel)

    with right:
        st.subheader("Finding status")
        status_counts = flagged_df["status"].value_counts().rename_axis("status").to_frame("count")
        st.bar_chart(status_counts)

    st.subheader("Highest-value findings")
    top = filtered.sort_values(["actionability_score", "asset_criticality"], ascending=False).head(8)
    st.dataframe(
        top[
            [
                "finding_id",
                "predicted_severity",
                "cwe",
                "code_path",
                "confidence",
                "actionability_score",
                "status",
            ]
        ],
        use_container_width=True,
        hide_index=True,
        column_config={
            "confidence": st.column_config.ProgressColumn("Confidence", min_value=0.0, max_value=1.0, format="%.2f"),
            "actionability_score": st.column_config.ProgressColumn(
                "Actionability", min_value=0.0, max_value=1.0, format="%.2f"
            ),
        },
    )

with findings_tab:
    st.subheader("Finding explorer")
    st.caption("Filter by severity, CWE, and actionability to inspect the developer-facing queue.")
    st.dataframe(
        filtered[
            [
                "finding_id",
                "predicted_severity",
                "confirmed_severity",
                "cwe",
                "code_path",
                "description",
                "confidence",
                "evidence_quality",
                "fix_quality",
                "asset_criticality",
                "actionability_score",
                "status",
            ]
        ].sort_values("actionability_score", ascending=False),
        use_container_width=True,
        hide_index=True,
        column_config={
            "confidence": st.column_config.NumberColumn(format="%.2f"),
            "evidence_quality": st.column_config.NumberColumn(format="%.2f"),
            "fix_quality": st.column_config.NumberColumn(format="%.2f"),
            "asset_criticality": st.column_config.NumberColumn(format="%.2f"),
            "actionability_score": st.column_config.ProgressColumn(
                "Actionability", min_value=0.0, max_value=1.0, format="%.2f"
            ),
        },
    )

with workflow_tab:
    st.subheader("Triage workflow experiment")
    st.markdown(
        "Compare the raw-finding workflow with an enriched workflow that adds stronger evidence, prioritization context, and remediation guidance."
    )
    c = experiment["control"]
    t = experiment["treatment"]
    delta = experiment["delta_treatment_minus_control"]

    a, b, c1, d = st.columns(4)
    a.metric("Triage completion", f"{t['triage_completion_rate']:.1%}", f"{delta['triage_completion_rate']:+.1%}")
    b.metric("Acceptance", f"{t['acceptance_rate']:.1%}", f"{delta['acceptance_rate']:+.1%}")
    c1.metric("Remediation", f"{t['remediation_rate']:.1%}", f"{delta['remediation_rate']:+.1%}")
    d.metric("Median triage", f"{t['median_triage_minutes']:.0f} min", f"{delta['median_triage_minutes']:+.0f} min")

    comparison = pd.DataFrame(
        {
            "Control": [c["triage_completion_rate"], c["acceptance_rate"], c["remediation_rate"]],
            "Enriched": [t["triage_completion_rate"], t["acceptance_rate"], t["remediation_rate"]],
        },
        index=["Completion", "Acceptance", "Remediation"],
    )
    st.bar_chart(comparison)
    st.caption("Synthetic deterministic experiment; deltas demonstrate measurement mechanics, not a causal claim about a real product.")

with quality_tab:
    st.subheader("Quality diagnostics")
    q1, q2, q3, q4 = st.columns(4)
    q1.metric("Recall", f"{quality['recall']:.1%}")
    q2.metric("Severity MAE", f"{quality['severity_mae_levels']:.2f} levels")
    q3.metric("Duplicate rate", f"{quality['duplicate_rate']:.1%}")
    q4.metric("Dedup reduction", f"{dedupe['reduction_rate']:.1%}")

    left, right = st.columns(2)
    with left:
        st.markdown("#### Predicted severity mix")
        severity_counts = flagged_df["predicted_severity"].value_counts().to_frame("findings")
        st.bar_chart(severity_counts)
    with right:
        st.markdown("#### CWE mix")
        cwe_counts = flagged_df["cwe"].value_counts().to_frame("findings")
        st.bar_chart(cwe_counts)

    st.markdown("#### Measurement contract")
    st.info(
        "VulnSignal intentionally separates model quality (precision/recall), finding quality (severity/actionability/duplication), "
        "workflow quality (triage and acceptance), and security outcomes (remediation and verified resolution)."
    )
