"""
InsightAgent: generate heuristic hypotheses from data_summary.
"""
from typing import Dict, List, Any
import uuid

class InsightAgent:
    def __init__(self, cfg: Dict[str, Any]):
        self.cfg = cfg

    def generate_hypotheses(self, data_summary: Dict[str, Any], query: str) -> List[Dict[str, Any]]:
        hypotheses = []
        campaigns = data_summary.get("campaigns", [])
        median_ctr = data_summary.get("summary_meta", {}).get("median_ctr", 0.0)
        top_msgs = data_summary.get("top_creative_messages", {})

        # Hypothesis: low CTR campaigns exist -> creative underperformance
        for c in data_summary.get("low_ctr_campaigns", []):
            hid = str(uuid.uuid4())[:8]
            text = f"Creative underperformance in campaign '{c['campaign_name']}' (CTR {c['ctr']:.4f})"
            confidence = 0.5 + max(0.0, (median_ctr - c["ctr"]))  # heuristic
            evidence = {
                "campaign": c["campaign_name"],
                "ctr": c["ctr"],
                "ctr_vs_median": c["ctr_vs_median"],
                "impressions": c["impressions"]
            }
            hypotheses.append({
                "id": hid,
                "text": text,
                "confidence": min(confidence, 0.95),
                "evidence_summary": evidence,
                "required_checks": ["ctr_trend_check", "creative_message_analysis"],
                "rationale": "CTR significantly below median and campaign has sufficient impressions."
            })

        # Hypothesis: audiences with low ROAS
        for c in campaigns:
            if c.get("roas", 0.0) < 0.5:
                hid = str(uuid.uuid4())[:8]
                text = f"Low ROAS in campaign '{c['campaign_name']}' (ROAS {c['roas']:.2f}) — possible audience mismatch or offer issue"
                hypotheses.append({
                    "id": hid,
                    "text": text,
                    "confidence": 0.45,
                    "evidence_summary": {"campaign": c["campaign_name"], "roas": c["roas"]},
                    "required_checks": ["roas_by_audience", "spend_efficiency"],
                    "rationale": "ROAS below typical threshold; further split by audience/platform recommended."
                })

        # If no hypotheses, add a generic one
        if not hypotheses:
            hid = str(uuid.uuid4())[:8]
            hypotheses.append({
                "id": hid,
                "text": "No obvious campaign-level low CTR or low ROAS detected",
                "confidence": 0.4,
                "evidence_summary": {},
                "required_checks": ["detailed_time_series"],
                "rationale": "Dataset appears balanced at campaign aggregate level; recommend time-series checks."
            })

        return hypotheses
