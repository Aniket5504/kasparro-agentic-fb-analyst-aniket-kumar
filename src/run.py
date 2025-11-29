#!/usr/bin/env python3
"""
Orchestrator CLI for Kasparro Agentic FB Analyst.
Usage:
    python src/run.py "Analyze ROAS drop in last 7 days"
"""
import argparse
import json
import os
import random
import sys
from datetime import datetime

import yaml

from src.agents.data_agent import DataAgent
from src.agents.planner import Planner
from src.agents.insight_agent import InsightAgent
from src.agents.evaluator import Evaluator
from src.agents.creative_generator import CreativeGenerator

def ensure_dirs(cfg):
    os.makedirs(os.path.dirname(cfg["insights_path"]), exist_ok=True)
    os.makedirs(cfg["logs_path"], exist_ok=True)
    os.makedirs(os.path.dirname(cfg["report_path"]), exist_ok=True)

def write_json(path, payload):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

def write_text(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

class Orchestrator:
    def __init__(self, cfg):
        self.cfg = cfg
        random.seed(cfg.get("random_seed", 42))
        self.data_agent = DataAgent(cfg)
        self.planner = Planner(cfg)
        self.insight_agent = InsightAgent(cfg)
        self.evaluator = Evaluator(cfg)
        self.creative_gen = CreativeGenerator(cfg)

    def run(self, query: str):
        run_id = datetime.utcnow().strftime("run-%Y%m%dT%H%M%SZ")
        start = datetime.utcnow().isoformat() + "Z"

        # 1) Planner decomposes
        plan = self.planner.decompose(query)

        # 2) Load data & summarize
        data_summary = self.data_agent.load_and_summarize()

        # 3) Insight Agent -> hypotheses
        hypotheses = self.insight_agent.generate_hypotheses(data_summary, query)

        # 4) Evaluator -> validate hypotheses
        validated = self.evaluator.validate(hypotheses, data_summary)

        # 5) Creative generator -> creatives for low-CTR campaigns
        low_ctr_campaigns = data_summary.get("low_ctr_campaigns", [])
        creatives = self.creative_gen.generate(low_ctr_campaigns, data_summary)

        # 6) Build report text
        report_lines = [
            f"# Kasparro Agentic FB Analyst Report",
            f"Run ID: {run_id}",
            f"Query: {query}",
            "",
            "## Executive Summary",
            f"- Hypotheses generated: {len(hypotheses)}",
            f"- Hypotheses accepted: {sum(1 for h in validated if h.get('final_verdict')=='accept')}",
            f"- Low-CTR campaigns: {len(low_ctr_campaigns)}",
            "",
            "## Hypotheses (brief)"
        ]
        for h in validated:
            report_lines.append(f"- {h['id']}: {h['text']} (verdict: {h['final_verdict']}, confidence: {h.get('adjusted_confidence'):.2f})")

        report_lines += ["", "## Creative Recommendations (brief)"]
        for c in creatives:
            report_lines.append(f"- Campaign: {c['campaign']}, recommendations: {len(c['recommendations'])} variants")

        report_text = "\n".join(report_lines)

        outputs = {
            "run_id": run_id,
            "query": query,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "plan": plan,
            "insights": {"hypotheses": validated},
            "creatives": creatives,
            "report": report_text,
            "data_summary": data_summary,
            "meta": {"started_at": start}
        }
        return outputs

def main():
    p = argparse.ArgumentParser()
    p.add_argument("query", type=str)
    args = p.parse_args()

    cfg_path = os.path.join("config", "config.yaml")
    if not os.path.exists(cfg_path):
        print("Missing config/config.yaml", file=sys.stderr)
        sys.exit(2)
    cfg = yaml.safe_load(open(cfg_path, "r", encoding="utf-8"))
    ensure_dirs(cfg)
    orch = Orchestrator(cfg)
    outputs = orch.run(args.query)

    # write outputs
    write_json(cfg["insights_path"], outputs["insights"])
    write_json(cfg["creatives_path"], outputs["creatives"])
    write_text(cfg["report_path"], outputs["report"])
    run_log = os.path.join(cfg["logs_path"], f"{outputs['run_id']}.json")
    write_json(run_log, outputs)

    print("Run complete.")
    print(f"- insights: {cfg['insights_path']}")
    print(f"- creatives: {cfg['creatives_path']}")
    print(f"- report: {cfg['report_path']}")
    print(f"- run log: {run_log}")

if __name__ == "__main__":
    main()
