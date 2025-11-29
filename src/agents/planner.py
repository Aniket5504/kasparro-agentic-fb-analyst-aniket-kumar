"""
Planner: simple rule-based decomposer.
"""
from typing import Dict, List, Any

class Planner:
    def __init__(self, cfg: Dict[str, Any]):
        self.cfg = cfg

    def decompose(self, query: str) -> List[Dict[str, Any]]:
        tasks = [
            {"task_id": "load_data", "description": "Load and validate dataset", "required_inputs": [], "expected_output": "data_summary"},
            {"task_id": "summarize_metrics", "description": "Compute campaign-level metrics and detect low-CTR campaigns", "required_inputs": ["data_summary"], "expected_output": "campaign_summaries"},
            {"task_id": "generate_hypotheses", "description": "Create hypotheses explaining ROAS/CTR patterns", "required_inputs": ["campaign_summaries"], "expected_output": "hypotheses"},
            {"task_id": "validate_hypotheses", "description": "Quantitatively validate each hypothesis", "required_inputs": ["hypotheses", "data_summary"], "expected_output": "validated_hypotheses"},
            {"task_id": "generate_creatives", "description": "Produce creative variants for low-CTR campaigns", "required_inputs": ["low_ctr_campaigns", "top_creative_messages"], "expected_output": "creatives"}
        ]
        return {"query": query, "tasks": tasks, "confidence": 0.9}
