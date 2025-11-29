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

```mermaid
flowchart TD
    A[User Query] --> B[Planner Agent]
    B --> C[Data Agent]
    C -->|Data Summary| D[Insight Agent]
    D -->|Hypotheses| E[Evaluator Agent]
    E -->|Validated Hypotheses| F[Creative Generator]
    F --> G[Reports & Logs]

This line is added to enable PR creation.