# Kasparro — Agentic Facebook Performance Analyst

Purpose: multi-agent system to diagnose ROAS changes and propose creative improvements.

## Quick start

```bash
python -m venv .venv

Windows (PowerShell):
.venv\Scripts\Activate.ps1

macOS/Linux:
source .venv/bin/activate
 
pip install -r requirements.txt
python src/run.py "Analyze ROAS drop in last 7 days"


## Architecture Diagram (flow)
User Query
  ↓
Planner Agent
  ↓
Data Agent -> Data Summary
  ↓
Insight Agent -> Hypotheses
  ↓
Evaluator Agent -> Validated Hypotheses
  ↓
Creative Generator -> Creative Variants
  ↓
Reports + Logs (reports/, logs/)