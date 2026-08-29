from __future__ import annotations

from dataclasses import asdict
import pandas as pd
import streamlit as st

from vulnsignal.dedupe import duplicate_summary
from vulnsignal.experiment import compare_workflows
from vulnsignal.fixtures import synthetic_findings, synthetic_triage_experiment
from vulnsignal.metrics import actionability_score, finding_quality_report

st.set_page_config(page_title="VulnSignal", page_icon="◉", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
<style>
:root{--ink:#1d1d1f;--muted:#6e6e73;--soft:#f5f5f7;--line:#e8e8ed;--blue:#0071e3}
html,body,[class*="css"]{font-family:-apple-system,BlinkMacSystemFont,"SF Pro Display","SF Pro Text","Helvetica Neue",Arial,sans-serif;color:var(--ink)}.stApp{background:#fff}.block-container{max-width:1500px;padding:1.4rem 2.4rem 5rem}[data-testid="stSidebar"]{background:rgba(245,245,247,.96);border-right:1px solid var(--line)}[data-testid="stMetric"]{background:var(--soft);border:1px solid rgba(0,0,0,.04);border-radius:26px;padding:1.1rem 1.2rem;min-height:116px;box-shadow:0 10px 30px rgba(0,0,0,.03)}[data-testid="stMetricLabel"]{color:var(--muted);font-size:.72rem;font-weight:650}[data-testid="stMetricValue"]{font-size:1.85rem;font-weight:650;letter-spacing:-.045em}[data-testid="stDataFrame"]{border:1px solid var(--line);border-radius:22px;overflow:hidden}.hero{text-align:center;max-width:1080px;margin:0 auto;padding:4.4rem 1rem 2.9rem}.eyebrow{color:var(--blue);font-size:.76rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase}.title{font-size:4.8rem;line-height:.98;font-weight:650;letter-spacing:-.07em;margin:.8rem 0 0}.sub{font-size:1.2rem;line-height:1.55;color:var(--muted);max-width:900px;margin:1.2rem auto}.pills{display:flex;gap:.5rem;flex-wrap:wrap;justify-content:center}.pill{background:var(--soft);border:1px solid rgba(0,0,0,.04);border-radius:999px;padding:.45rem .8rem;font-size:.74rem;color:#424245}.section{font-size:1.8rem;font-weight:650;letter-spacing:-.04em;margin-top:1.4rem}.section-sub{color:#86868b;font-size:.94rem;margin-bottom:1rem}.note{background:var(--soft);border:1px solid rgba(0,0,0,.04);border-radius:22px;padding:1rem 1.2rem;color:var(--muted)}.stTabs [data-baseweb="tab"]{border-radius:999px;font-weight:600}
</style>
""",unsafe_allow_html=True)

findings=synthetic_findings(); control,treatment=synthetic_triage_experiment(); quality=finding_quality_report(findings); dedupe=duplicate_summary(findings); experiment=compare_workflows(control,treatment)
rows=[]
for finding in findings:
    row=asdict(finding); row["actionability_score"]=actionability_score(finding); row["status"]=("Verified" if finding.resolution_verified else "Remediated" if finding.remediated else "Accepted" if finding.developer_accepted else "Open"); rows.append(row)
df=pd.DataFrame(rows); flagged_df=df[df["model_flagged"]].copy()

with st.sidebar:
    st.markdown("### VulnSignal"); st.caption("Finding quality controls"); st.markdown("**Overview**\n\nFindings\n\nDuplicates\n\nTriage experiment\n\nOutcomes")

st.markdown("""<div class="hero"><div class="eyebrow">AI Security Finding Intelligence</div><div class="title">VulnSignal</div><div class="sub">Measure whether AI-generated security findings are accurate, actionable, non-duplicative, accepted by developers, remediated, and ultimately verified as resolved.</div><div class="pills"><span class="pill">Finding quality</span><span class="pill">Dedupe</span><span class="pill">Triage</span><span class="pill">Developer acceptance</span><span class="pill">Verification</span></div></div>""",unsafe_allow_html=True)

precision=float(quality.get("precision",0)); actionable=float(quality.get("actionable_rate",quality.get("actionability_rate",0))); accepted=float(quality.get("accepted_rate",0)); verified=float(quality.get("verified_rate",0)); flagged=len(flagged_df); total=len(df); open_count=int((df.status=="Open").sum()); accepted_count=int((df.status=="Accepted").sum()); remediated_count=int((df.status=="Remediated").sum()); verified_count=int((df.status=="Verified").sum()); avg_action=float(df.actionability_score.mean()) if total else 0; duplicate_groups=int(dedupe.get("duplicate_groups",dedupe.get("clusters",0)) or 0)
metric_rows=[
[("Findings",total),("Flagged",flagged),("Precision",f"{precision:.1%}"),("Actionable",f"{actionable:.1%}"),("Accepted",f"{accepted:.1%}"),("Verified",f"{verified:.1%}")],
[("Open",open_count),("Accepted state",accepted_count),("Remediated",remediated_count),("Verified state",verified_count),("Avg actionability",f"{avg_action:.2f}"),("Duplicate groups",duplicate_groups)],
[("Control cases",len(control)),("Treatment cases",len(treatment)),("Triage experiment","Enabled"),("Human review","Required"),("Auto-remediation","Off"),("Synthetic data","100%")]
]
for row in metric_rows:
    cols=st.columns(6)
    for col,(label,value) in zip(cols,row): col.metric(label,value)

st.markdown('<div class="section">Finding quality</div><div class="section-sub">Quality is measured through the full security outcome funnel, not raw finding volume.</div>',unsafe_allow_html=True)
a,b=st.columns(2)
with a: st.bar_chart(df.status.value_counts())
with b:
    if "severity" in df: st.bar_chart(df.severity.value_counts())

t1,t2,t3,t4=st.tabs(["Finding queue","Quality metrics","Duplicate intelligence","Triage experiment"])
with t1:
    cols=[c for c in ["finding_id","severity","category","title","model_flagged","actionability_score","status"] if c in df.columns]; st.dataframe(df[cols],use_container_width=True,hide_index=True)
with t2: st.json(quality)
with t3: st.json(dedupe)
with t4:
    st.json(experiment); st.caption("The experiment is synthetic and demonstrates workflow-measurement mechanics rather than production causal impact.")

st.markdown('<div class="note"><b>Evaluation boundary.</b> All findings, developer outcomes, and workflow measurements are synthetic. No repository is modified and no remediation is executed automatically.</div>',unsafe_allow_html=True)
