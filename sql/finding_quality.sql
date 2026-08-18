-- Example analytics query for model finding quality and remediation outcomes.
SELECT
  model_version,
  COUNT(*) AS findings,
  AVG(CASE WHEN validated THEN 1.0 ELSE 0.0 END) AS validation_rate,
  AVG(CASE WHEN actionable THEN 1.0 ELSE 0.0 END) AS actionability_rate,
  AVG(CASE WHEN accepted THEN 1.0 ELSE 0.0 END) AS acceptance_rate,
  AVG(CASE WHEN resolved THEN 1.0 ELSE 0.0 END) AS resolution_rate
FROM ai_finding_outcomes
GROUP BY model_version
ORDER BY model_version;
