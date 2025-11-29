"""
CreativeGenerator: produce simple template-based creative variants for low-CTR campaigns.
"""
from typing import Dict, List, Any
import uuid

class CreativeGenerator:
    def __init__(self, cfg: Dict[str, Any]):
        self.cfg = cfg

    def _make_variant(self, campaign_name: str, variant_type: str, seed_note=""):
        vid = str(uuid.uuid4())[:8]
        if variant_type == "benefit":
            headline = f"{campaign_name}: Comfort & Fit You Can Trust"
            body = "Discover superior comfort engineered for every day. Free shipping on first order."
            cta = "Shop Comfort"
            rationale = "Benefit-led messaging to highlight product USP."
        elif variant_type == "social":
            headline = f"Why Customers Love {campaign_name}"
            body = "Thousands rated us 4.5+ for comfort and durability. See what they say."
            cta = "Read Reviews"
            rationale = "Social proof angle to build trust."
        elif variant_type == "offer":
            headline = f"Limited Offer — {campaign_name} 20% Off"
            body = "Limited-time discount. Try our best-selling undergarments — satisfaction guaranteed."
            cta = "Claim Offer"
            rationale = "Offer-driven message to boost CTR with urgency."
        else:  # curiosity
            headline = f"What's New with {campaign_name}?"
            body = "A surprising feature customers love — see why it's trending now."
            cta = "Learn More"
            rationale = "Curiosity-driven messaging to increase clicks."
        return {
            "id": vid,
            "headline": headline,
            "body": body,
            "cta": cta,
            "rationale": rationale,
            "variant_type": variant_type,
            "seed_note": seed_note
        }

    def generate(self, low_ctr_campaigns: List[Dict[str, Any]], data_summary: Dict[str, Any]) -> List[Dict[str, Any]]:
        output = []
        for c in low_ctr_campaigns:
            campaign = c.get("campaign_name")
            variants = [
                self._make_variant(campaign, "benefit"),
                self._make_variant(campaign, "social"),
                self._make_variant(campaign, "offer"),
                self._make_variant(campaign, "curiosity")
            ]
            # include tie to top creative messages as rationale
            top_msg_sample = list(data_summary.get("top_creative_messages", {}).keys())[:3]
            output.append({
                "campaign": campaign,
                "low_ctr": c.get("ctr"),
                "recommendations": variants,
                "top_existing_messages_sample": top_msg_sample
            })
        return output
