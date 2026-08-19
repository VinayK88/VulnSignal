from __future__ import annotations

import pandas as pd
import streamlit as st

from vulnsignal.model_selection import benchmark_rows, routing_table


st.set_page_config(
    page_title="VulnSignal | Model Evaluation & Routing",
    page_icon="🧠",
    layout="wide",
)

st.title("Model Evaluation & Routing")
st.caption(
    "Compare AI approaches by security scenario and route each workload to the architecture "
    "with the strongest security + production utility. All benchmark values are synthetic."
)

benchmark = pd.DataFrame(benchmark_rows())
routes = pd.DataFrame(routing_table())

r1, r2, r3 = st.columns(3)
for column, (_, route) in zip((r1, r2, r3), routes.iterrows()):
    with column:
        st.metric(route["scenario"], route["selected_approach"], f"utility {route['utility_score']:.3f}")
        st.caption(
            f"Precision {route['precision']:.0%} · Recall {route['recall']:.0%} · "
            f"Task success {route['task_success_rate']:.0%}"
        )

st.divider()

selected_scenario = st.selectbox(
    "Security scenario",
    routes["scenario"].tolist(),
)
scenario_df = benchmark[benchmark["scenario"] == selected_scenario].copy()
scenario_df = scenario_df.sort_values("utility_score", ascending=False)

best = scenario_df.iloc[0]

left, right = st.columns([1.15, 0.85])
with left:
    st.subheader("Architecture comparison")
    chart_df = scenario_df.set_index("approach")[["precision", "recall", "task_success_rate", "utility_score"]]
    st.bar_chart(chart_df)

with right:
    st.subheader("Selected production route")
    st.success(f"{best['approach']} is the highest-utility approach for this scenario.")
    a, b = st.columns(2)
    a.metric("Precision", f"{best['precision']:.1%}")
    b.metric("Recall", f"{best['recall']:.1%}")
    c, d = st.columns(2)
    c.metric("Task success", f"{best['task_success_rate']:.1%}")
    d.metric("Tool success", f"{best['tool_success_rate']:.1%}")
    e, f = st.columns(2)
    e.metric("Latency", f"{int(best['latency_ms'])} ms")
    f.metric("Cost / task", f"${best['cost_usd']:.3f}")
    st.metric("Unsupported claims", f"{best['unsupported_claim_rate']:.1%}")

st.subheader("Full benchmark")
st.dataframe(
    scenario_df[
        [
            "approach",
            "precision",
            "recall",
            "task_success_rate",
            "tool_success_rate",
            "unsupported_claim_rate",
            "latency_ms",
            "cost_usd",
            "utility_score",
        ]
    ],
    use_container_width=True,
    hide_index=True,
    column_config={
        "precision": st.column_config.NumberColumn("Precision", format="%.1%%"),
        "recall": st.column_config.NumberColumn("Recall", format="%.1%%"),
        "task_success_rate": st.column_config.NumberColumn("Task success", format="%.1%%"),
        "tool_success_rate": st.column_config.NumberColumn("Tool success", format="%.1%%"),
        "unsupported_claim_rate": st.column_config.NumberColumn("Unsupported claims", format="%.1%%"),
        "latency_ms": st.column_config.NumberColumn("Latency (ms)", format="%d"),
        "cost_usd": st.column_config.NumberColumn("Cost / task", format="$%.3f"),
        "utility_score": st.column_config.ProgressColumn(
            "Utility", min_value=0.0, max_value=1.0, format="%.3f"
        ),
    },
)

st.divider()
st.subheader("Routing architecture")
st.code(
    """Security event
    ↓
Scenario / complexity classifier
    ↓
Model & architecture router
    ├── Rules + ML              → high-volume deterministic triage
    ├── Fine-tuned transformer  → specialized classification
    ├── RAG LLM                 → grounded contextual validation
    └── Agentic reasoner        → multi-step investigation + tools
    ↓
Policy / safety checks
    ↓
Security decision + telemetry
    ↓
Continuous evaluation and routing updates""",
    language="text",
)

st.info(
    "The router does not optimize for model accuracy alone. It combines precision, recall, task success, "
    "latency, cost, groundedness, and tool reliability using scenario-specific weights. This demonstrates "
    "architecture selection rather than one-model-for-everything behavior."
)
