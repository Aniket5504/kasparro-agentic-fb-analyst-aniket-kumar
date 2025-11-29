"""
DataAgent: load CSV, validate, compute summaries used by other agents.
"""
import os
from typing import Dict, Any
import pandas as pd

REQUIRED_COLS = [
    "campaign_name", "adset_name", "date", "spend", "impressions",
    "clicks", "ctr", "purchases", "revenue", "roas",
    "creative_type", "creative_message", "audience_type", "platform", "country"
]

class DataAgent:
    def __init__(self, cfg: Dict[str, Any]):
        self.cfg = cfg
        self.csv_path = cfg.get("data_csv") or os.getenv("DATA_CSV")
        if not self.csv_path:
            raise ValueError("data_csv not set in config or DATA_CSV env var")

    def _validate(self, df: pd.DataFrame):
        missing = [c for c in REQUIRED_COLS if c not in df.columns]
        if missing:
            raise ValueError(f"Missing columns: {missing}")

    def load_and_summarize(self) -> Dict[str, Any]:
        df = pd.read_csv(self.csv_path, parse_dates=["date"])
        self._validate(df)

        # numeric cleaning
        for col in ["impressions", "clicks"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
        for col in ["spend", "revenue", "ctr", "roas"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

        n_rows = int(df.shape[0])
        date_min = df["date"].min()
        date_max = df["date"].max()
        n_campaigns = int(df["campaign_name"].nunique())

        # campaign aggregates
        grp = df.groupby("campaign_name").agg({
            "impressions": "sum",
            "clicks": "sum",
            "spend": "sum",
            "revenue": "sum"
        }).reset_index()
        grp["ctr"] = grp["clicks"] / grp["impressions"].replace({0: 1})
        grp["roas"] = grp["revenue"] / grp["spend"].replace({0: 1.0})

        median_ctr = float(grp["ctr"].median()) if not grp.empty else 0.0

        campaigns = []
        low_ctr_campaigns = []
        for _, r in grp.iterrows():
            c = {
                "campaign_name": r["campaign_name"],
                "impressions": int(r["impressions"]),
                "clicks": int(r["clicks"]),
                "ctr": float(r["ctr"]),
                "spend": float(r["spend"]),
                "revenue": float(r["revenue"]),
                "roas": float(r["roas"])
            }
            c["ctr_vs_median"] = c["ctr"] - median_ctr
            campaigns.append(c)
            if (c["ctr"] < self.cfg.get("low_ctr_threshold", 0.015)
                and c["impressions"] >= self.cfg.get("min_impressions", 1000)):
                low_ctr_campaigns.append(c)

        # top creative messages
        top_msgs = df["creative_message"].fillna("").value_counts().head(10).to_dict()

        summary = {
            "summary_meta": {
                "n_rows": n_rows,
                "date_min": str(date_min.date()) if pd.notnull(date_min) else None,
                "date_max": str(date_max.date()) if pd.notnull(date_max) else None,
                "n_campaigns": n_campaigns,
                "median_ctr": median_ctr
            },
            "campaigns": campaigns,
            "low_ctr_campaigns": low_ctr_campaigns,
            "top_creative_messages": top_msgs
        }
        return summary

# convenience
def load_and_summarize(cfg):
    da = DataAgent(cfg)
    return da.load_and_summarize()
