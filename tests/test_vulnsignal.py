import unittest

from vulnsignal.dedupe import duplicate_summary
from vulnsignal.experiment import compare_workflows
from vulnsignal.fixtures import synthetic_findings, synthetic_triage_experiment
from vulnsignal.metrics import finding_quality_report


class VulnSignalTests(unittest.TestCase):
    def test_finding_metrics(self):
        report = finding_quality_report(synthetic_findings())
        self.assertGreater(report["precision"], 0.70)
        self.assertGreater(report["recall"], 0.60)
        self.assertGreater(report["verified_resolution_rate"], 0.40)

    def test_duplicate_reduction(self):
        report = duplicate_summary(synthetic_findings())
        self.assertGreaterEqual(report["duplicate_findings"], 1)
        self.assertLess(report["unique_clusters"], report["flagged_findings"])

    def test_enriched_triage_improves_remediation_and_speed(self):
        control, treatment = synthetic_triage_experiment()
        comparison = compare_workflows(control, treatment)
        delta = comparison["delta_treatment_minus_control"]
        self.assertGreater(delta["remediation_rate"], 0)
        self.assertLess(delta["median_triage_minutes"], 0)


if __name__ == "__main__":
    unittest.main()
