"""
Evaluator: run quantitative checks on hypotheses and adjust confidence.
Uses simple rule-based checks (percent change, sample size).
"""
from typing import Dict, List, Any
import math

class Evaluator:
    def __init__(self, cfg: Dict[str, Any]):
        self.cfg = cfg

    def _percent_change(self, a, b):
        if b == 0:
            return float("inf") if a != 0 else 0.0
        return (a - b) / abs(b)

    def validate(self, hypotheses: List[Dict[str, Any]], data_summary: Dict[str, Any]) -> List[Dict[str, Any]]:
        results = []
        median_ctr = data_summary.get("summary_meta", {}).get("median_ctr", 0.0)
        for h in hypotheses:
            ev = h.get("evidence_summary", {})
            tests = []
            adjusted_conf = h.get("confidence", 0.5)
            verdict = "needs_more_data"
            # Example check: if evidence contains ctr and impressions, do sample-size & magnitude checks
            ctr = ev.get("ctr")
            impressions = ev.get("impressions", 0)
            if ctr is not None:
                # sample size check
                pass_sample_size = impressions >= self.cfg.get("min_impressions", 1000)
                tests.append({"name": "min_impressions", "value": impressions, "pass": pass_sample_size})
                # effect vs median
                if median_ctr > 0:
                    pct_delta = (ctr - median_ctr) / median_ctr
                else:
                    pct_delta = 0.0
                tests.append({"name": "pct_delta_vs_median", "value": pct_delta, "pass": pct_delta < -0.05})
                # adjust confidence
                adjusted_conf = min(0.99, adjusted_conf + (-pct_delta) * 0.5 if pct_delta < 0 else adjusted_conf * 0.9)
                # decide
                if pass_sample_size and pct_delta < -0.05:
                    verdict = "accept"
                elif not pass_sample_size:
                    verdict = "needs_more_data"
                else:
                    verdict = "reject"
            else:
                # fallback checks (for roas etc)
                roas = ev.get("roas")
                if roas is not None:
                    tests.append({"name": "roas_value", "value": roas, "pass": roas < 0.5})
                    adjusted_conf = min(0.95, adjusted_conf + (0.5 - roas) * 0.3 if roas < 0.5 else adjusted_conf*0.9)
                    verdict = "accept" if roas < 0.5 else "reject"
                else:
                    tests.append({"name": "no_numeric_evidence", "value": 0, "pass": False})
                    verdict = "needs_more_data"
            res = {
                "id": h.get("id"),
                "text": h.get("text"),
                "evidence": ev,
                "validation": {"tests": tests},
                "adjusted_confidence": float(max(0.0, min(1.0, adjusted_conf))),
                "final_verdict": verdict
            }
            results.append(res)
        return results
