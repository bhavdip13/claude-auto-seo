"""
Claude Auto SEO — Opportunity Scorer
Scores SEO content opportunities to prioritize work by expected impact.
"""

import math
from typing import Dict, List, Optional


def score_ranking_opportunity(
    keyword: str,
    current_position: Optional[int],
    search_volume: int,
    keyword_difficulty: int,  # 0-100
    current_ctr: Optional[float] = None,
    business_value: str = "medium",  # low / medium / high
    content_exists: bool = True,
    content_quality_score: Optional[int] = None,  # 0-100
) -> Dict:
    """
    Score a keyword/page opportunity on a 0-100 scale.

    Factors:
    - Traffic potential (30%)
    - Keyword difficulty / effort (25%)
    - Business value (25%)
    - Current momentum (20%)
    """

    # ── Traffic Potential (0-30 pts) ──────────────────────────
    # Estimate traffic at target position (position 1-3)
    ctr_estimates = {1: 0.28, 2: 0.15, 3: 0.11, 4: 0.08, 5: 0.06,
                     6: 0.04, 7: 0.03, 8: 0.025, 9: 0.02, 10: 0.015}

    target_ctr = ctr_estimates.get(1, 0.28)  # Target position 1
    potential_clicks = search_volume * target_ctr

    if potential_clicks >= 5000:
        traffic_score = 30
    elif potential_clicks >= 2000:
        traffic_score = 25
    elif potential_clicks >= 1000:
        traffic_score = 20
    elif potential_clicks >= 500:
        traffic_score = 15
    elif potential_clicks >= 200:
        traffic_score = 10
    elif potential_clicks >= 50:
        traffic_score = 5
    else:
        traffic_score = 2

    # ── Effort / Difficulty (0-25 pts) ────────────────────────
    # Lower difficulty = higher score (easier = better ROI)
    if keyword_difficulty <= 20:
        effort_score = 25
    elif keyword_difficulty <= 35:
        effort_score = 20
    elif keyword_difficulty <= 50:
        effort_score = 15
    elif keyword_difficulty <= 65:
        effort_score = 10
    elif keyword_difficulty <= 80:
        effort_score = 5
    else:
        effort_score = 2

    # If content exists and needs refresh, effort is lower
    if content_exists and content_quality_score and content_quality_score >= 60:
        effort_score = min(25, effort_score + 5)

    # ── Business Value (0-25 pts) ─────────────────────────────
    bv_map = {"low": 8, "medium": 16, "high": 25}
    business_score = bv_map.get(business_value, 16)

    # ── Current Momentum (0-20 pts) ───────────────────────────
    momentum_score = 0

    if current_position is None:
        # No ranking — new content opportunity
        momentum_score = 10
    elif current_position <= 3:
        # Already top 3 — protect / maintain
        momentum_score = 5
    elif current_position <= 10:
        # Page 1 but not top 3 — push higher
        momentum_score = 15
    elif current_position <= 20:
        # Position 11-20 — QUICK WIN zone
        momentum_score = 20
    elif current_position <= 50:
        # Positions 21-50 — visible but needs work
        momentum_score = 12
    else:
        # Below 50 — needs new content or major refresh
        momentum_score = 8

    # CTR boost: if CTR is low for position, optimization easy win
    if current_position and current_ctr:
        expected_ctr = ctr_estimates.get(min(current_position, 10), 0.01)
        if current_ctr < expected_ctr * 0.6:  # CTR significantly below expected
            momentum_score = min(20, momentum_score + 5)

    # ── Total Score ───────────────────────────────────────────
    total = traffic_score + effort_score + business_score + momentum_score

    # Determine priority tier
    if total >= 75:
        tier = "critical"
        tier_label = "🔴 Critical — Do This Week"
    elif total >= 55:
        tier = "high"
        tier_label = "🟡 High Impact — Do This Month"
    elif total >= 35:
        tier = "medium"
        tier_label = "🟢 Quick Win — Schedule Soon"
    else:
        tier = "low"
        tier_label = "⚪ Low Priority — Backlog"

    # Recommended action
    action = _recommend_action(current_position, content_exists, content_quality_score,
                                keyword_difficulty, total)

    return {
        "keyword": keyword,
        "opportunity_score": total,
        "tier": tier,
        "tier_label": tier_label,
        "score_breakdown": {
            "traffic_potential": traffic_score,
            "effort_difficulty": effort_score,
            "business_value": business_score,
            "current_momentum": momentum_score,
        },
        "metrics": {
            "search_volume": search_volume,
            "keyword_difficulty": keyword_difficulty,
            "current_position": current_position,
            "estimated_monthly_clicks_at_rank1": round(potential_clicks),
        },
        "recommended_action": action,
        "is_quick_win": current_position and 11 <= current_position <= 20,
    }


def _recommend_action(position, content_exists, quality_score, difficulty, score) -> str:
    if position and 11 <= position <= 20:
        return "Quick win: Add internal links, improve meta title CTR, expand content by 500+ words."
    elif position and position <= 10 and quality_score and quality_score < 70:
        return "Optimize existing page: improve E-E-A-T, add schema, strengthen internal linking."
    elif not content_exists or position is None or (position and position > 50):
        if difficulty <= 35:
            return "Create new content: research → write → optimize pipeline. Low competition."
        else:
            return "Create new content with comprehensive coverage. High competition — needs strong E-E-A-T."
    elif quality_score and quality_score < 50:
        return "Full content rewrite needed. Current quality score too low to rank well."
    else:
        return "Monitor and iterate. Run A/B test on title/meta for CTR improvement."


def prioritize_opportunities(opportunities: List[Dict]) -> List[Dict]:
    """Sort and tier a list of opportunity score results."""
    return sorted(opportunities, key=lambda x: x["opportunity_score"], reverse=True)


def generate_priority_matrix(opportunities: List[Dict]) -> Dict:
    """Group opportunities into priority tiers."""
    scored = prioritize_opportunities(opportunities)

    matrix = {
        "critical": [],
        "high": [],
        "medium": [],
        "low": [],
        "summary": {}
    }

    for opp in scored:
        tier = opp.get("tier", "low")
        matrix[tier].append(opp)

    matrix["summary"] = {
        "total_opportunities": len(scored),
        "critical_count": len(matrix["critical"]),
        "high_count": len(matrix["high"]),
        "medium_count": len(matrix["medium"]),
        "low_count": len(matrix["low"]),
        "quick_wins": [o for o in scored if o.get("is_quick_win")],
        "estimated_traffic_if_all_done": sum(
            o["metrics"]["estimated_monthly_clicks_at_rank1"] for o in scored
        ),
    }

    return matrix


if __name__ == "__main__":
    # Example opportunities
    test_opps = [
        score_ranking_opportunity("seo audit tool", 14, 2400, 42, 0.015, "high", True, 65),
        score_ranking_opportunity("technical seo checklist", None, 1800, 35, None, "high", False),
        score_ranking_opportunity("best seo software", 7, 5500, 78, 0.045, "high", True, 72),
        score_ranking_opportunity("what is a sitemap", 22, 900, 20, 0.008, "low", True, 55),
    ]

    matrix = generate_priority_matrix(test_opps)
    print(f"Priority Matrix Summary:")
    print(f"  Critical: {matrix['summary']['critical_count']}")
    print(f"  High: {matrix['summary']['high_count']}")
    print(f"  Medium: {matrix['summary']['medium_count']}")
    print(f"  Quick Wins: {len(matrix['summary']['quick_wins'])}")

    print("\nTop Opportunities:")
    for opp in (matrix["critical"] + matrix["high"])[:5]:
        print(f"  [{opp['opportunity_score']}] {opp['keyword']} — {opp['tier_label']}")
        print(f"       → {opp['recommended_action']}")
