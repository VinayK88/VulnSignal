from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable


@dataclass(frozen=True)
class ModelEvaluation:
    """Scenario-level evaluation record for an AI/security architecture candidate."""

    scenario: str
    approach: str
    precision: float
    recall: float
    task_success_rate: float
    latency_ms: int
    cost_usd: float
    unsupported_claim_rate: float
    tool_success_rate: float


def synthetic_model_benchmark() -> list[ModelEvaluation]:
    """Deterministic benchmark used to demonstrate model/architecture selection.

    The values are synthetic by design. They model the trade-offs a production
    security platform would evaluate before routing a workflow to an approach.
    """

    return [
        # High-volume IOC triage rewards speed, low cost, and stable precision.
        ModelEvaluation("High-volume IOC triage", "Rules + ML", 0.94, 0.82, 0.90, 45, 0.002, 0.00, 1.00),
        ModelEvaluation("High-volume IOC triage", "Fine-tuned transformer", 0.92, 0.88, 0.91, 120, 0.008, 0.01, 1.00),
        ModelEvaluation("High-volume IOC triage", "RAG LLM", 0.91, 0.90, 0.89, 950, 0.075, 0.04, 0.98),
        ModelEvaluation("High-volume IOC triage", "Agentic reasoner", 0.93, 0.91, 0.90, 2300, 0.210, 0.03, 0.94),
        # Vulnerability validation benefits from grounded context and explanation quality.
        ModelEvaluation("Contextual vulnerability validation", "Rules + ML", 0.89, 0.70, 0.76, 55, 0.003, 0.00, 1.00),
        ModelEvaluation("Contextual vulnerability validation", "Fine-tuned transformer", 0.91, 0.82, 0.84, 145, 0.010, 0.01, 1.00),
        ModelEvaluation("Contextual vulnerability validation", "RAG LLM", 0.95, 0.90, 0.93, 1100, 0.090, 0.02, 0.99),
        ModelEvaluation("Contextual vulnerability validation", "Agentic reasoner", 0.95, 0.92, 0.92, 2600, 0.240, 0.02, 0.95),
        # Multi-step investigations reward planning and tool use despite higher cost/latency.
        ModelEvaluation("Multi-step incident investigation", "Rules + ML", 0.86, 0.62, 0.68, 70, 0.004, 0.00, 1.00),
        ModelEvaluation("Multi-step incident investigation", "Fine-tuned transformer", 0.89, 0.76, 0.79, 170, 0.012, 0.01, 1.00),
        ModelEvaluation("Multi-step incident investigation", "RAG LLM", 0.92, 0.86, 0.88, 1250, 0.105, 0.03, 0.98),
        ModelEvaluation("Multi-step incident investigation", "Agentic reasoner", 0.94, 0.91, 0.95, 2850, 0.270, 0.02, 0.97),
    ]


def utility_score(evaluation: ModelEvaluation) -> float:
    """Return a normalized production utility score in [0, 1].

    The score intentionally balances security quality with operational concerns.
    Latency and cost are softly normalized so a stronger reasoning system can win
    when a scenario needs it, while lightweight approaches remain preferred for
    high-volume workflows.
    """

    latency_score = max(0.0, 1.0 - min(evaluation.latency_ms, 3000) / 3000)
    cost_score = max(0.0, 1.0 - min(evaluation.cost_usd, 0.30) / 0.30)
    grounded_score = 1.0 - evaluation.unsupported_claim_rate

    # Scenario-specific priorities represent the fact that security workloads do
    # not share one universal objective function.
    if evaluation.scenario == "High-volume IOC triage":
        weights = {
            "precision": 0.24,
            "recall": 0.12,
            "task": 0.18,
            "latency": 0.20,
            "cost": 0.16,
            "grounded": 0.05,
            "tools": 0.05,
        }
    elif evaluation.scenario == "Contextual vulnerability validation":
        weights = {
            "precision": 0.27,
            "recall": 0.17,
            "task": 0.22,
            "latency": 0.07,
            "cost": 0.05,
            "grounded": 0.15,
            "tools": 0.07,
        }
    else:
        weights = {
            "precision": 0.20,
            "recall": 0.16,
            "task": 0.28,
            "latency": 0.04,
            "cost": 0.03,
            "grounded": 0.12,
            "tools": 0.17,
        }

    score = (
        weights["precision"] * evaluation.precision
        + weights["recall"] * evaluation.recall
        + weights["task"] * evaluation.task_success_rate
        + weights["latency"] * latency_score
        + weights["cost"] * cost_score
        + weights["grounded"] * grounded_score
        + weights["tools"] * evaluation.tool_success_rate
    )
    return round(max(0.0, min(score, 1.0)), 4)


def benchmark_rows(evaluations: Iterable[ModelEvaluation] | None = None) -> list[dict[str, object]]:
    """Return dashboard/report-friendly benchmark rows."""

    rows = []
    for evaluation in evaluations or synthetic_model_benchmark():
        row = asdict(evaluation)
        row["utility_score"] = utility_score(evaluation)
        rows.append(row)
    return rows


def select_best_approach(
    scenario: str,
    evaluations: Iterable[ModelEvaluation] | None = None,
) -> ModelEvaluation:
    """Select the highest-utility architecture for a security scenario."""

    candidates = [
        evaluation
        for evaluation in (evaluations or synthetic_model_benchmark())
        if evaluation.scenario == scenario
    ]
    if not candidates:
        raise ValueError(f"Unknown security scenario: {scenario}")
    return max(candidates, key=utility_score)


def routing_table(evaluations: Iterable[ModelEvaluation] | None = None) -> list[dict[str, object]]:
    """Return the recommended production route for each benchmark scenario."""

    benchmark = list(evaluations or synthetic_model_benchmark())
    scenarios = list(dict.fromkeys(item.scenario for item in benchmark))
    routes: list[dict[str, object]] = []
    for scenario in scenarios:
        selected = select_best_approach(scenario, benchmark)
        routes.append(
            {
                "scenario": scenario,
                "selected_approach": selected.approach,
                "utility_score": utility_score(selected),
                "precision": selected.precision,
                "recall": selected.recall,
                "task_success_rate": selected.task_success_rate,
                "latency_ms": selected.latency_ms,
                "cost_usd": selected.cost_usd,
                "unsupported_claim_rate": selected.unsupported_claim_rate,
                "tool_success_rate": selected.tool_success_rate,
            }
        )
    return routes
