import unittest

from vulnsignal.model_selection import (
    benchmark_rows,
    routing_table,
    select_best_approach,
    synthetic_model_benchmark,
    utility_score,
)


class ModelSelectionTests(unittest.TestCase):
    def test_utility_score_is_bounded(self):
        for evaluation in synthetic_model_benchmark():
            self.assertGreaterEqual(utility_score(evaluation), 0.0)
            self.assertLessEqual(utility_score(evaluation), 1.0)

    def test_routes_match_scenario_tradeoffs(self):
        self.assertEqual(select_best_approach("High-volume IOC triage").approach, "Rules + ML")
        self.assertEqual(
            select_best_approach("Contextual vulnerability validation").approach,
            "RAG LLM",
        )
        self.assertEqual(
            select_best_approach("Multi-step incident investigation").approach,
            "Agentic reasoner",
        )

    def test_routing_table_has_one_route_per_scenario(self):
        routes = routing_table()
        self.assertEqual(len(routes), 3)
        self.assertEqual(len({row["scenario"] for row in routes}), 3)

    def test_benchmark_rows_include_operational_metrics(self):
        rows = benchmark_rows()
        self.assertTrue(rows)
        required = {
            "precision",
            "recall",
            "task_success_rate",
            "latency_ms",
            "cost_usd",
            "unsupported_claim_rate",
            "tool_success_rate",
            "utility_score",
        }
        self.assertTrue(required.issubset(rows[0]))


if __name__ == "__main__":
    unittest.main()
