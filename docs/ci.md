# VulnSignal CI validation

VulnSignal CI runs on pushes to `main`, pull requests targeting `main`, and manual `workflow_dispatch` runs.

The workflow validates Python 3.10, 3.11, and 3.12 and performs the following checks:

- installs the package with dashboard dependencies;
- runs the complete unit-test suite;
- smoke-tests scenario-aware model routing;
- smoke-tests the CLI;
- compiles package and dashboard Python sources;
- explicitly compiles the main Streamlit app and the Model Evaluation & Routing page.

The routing smoke test verifies these expected architecture choices:

- High-volume IOC triage → Rules + ML
- Contextual vulnerability validation → RAG LLM
- Multi-step incident investigation → Agentic reasoner

All benchmark values used by the model-selection demo are synthetic and are intended to demonstrate evaluation and routing mechanics rather than production efficacy.
