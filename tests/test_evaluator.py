import yaml
from src.agents.data_agent import load_and_summarize
from src.agents.insight_agent import InsightAgent
from src.agents.evaluator import Evaluator

def test_pipeline_basic():
    cfg = yaml.safe_load(open("config/config.yaml"))
    summary = load_and_summarize(cfg)
    assert "campaigns" in summary
    # instantiate insight agent
    ia = InsightAgent(cfg)
    hyps = ia.generate_hypotheses(summary, "Analyze ROAS drop")
    assert isinstance(hyps, list)
    # evaluator should run and return list
    ev = Evaluator(cfg)
    validated = ev.validate(hyps, summary)
    assert isinstance(validated, list)
    # validated items should have final_verdict
    for v in validated:
        assert "final_verdict" in v
