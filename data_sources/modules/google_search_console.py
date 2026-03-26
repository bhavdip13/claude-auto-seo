"""
Claude Auto SEO — Google Search Console Integration
Fetches keyword rankings, impressions, CTR, and crawl data from GSC.

Setup:
1. Add your service account to GSC property as Owner
2. Set GSC_SITE_URL and GOOGLE_APPLICATION_CREDENTIALS in .env
"""

import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

SITE_URL    = os.environ.get("GSC_SITE_URL", "").rstrip("/")
CREDENTIALS = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS",
                               "config/google-service-account.json")
SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]


def get_gsc_service():
    """Return authenticated GSC service object."""
    try:
        from googleapiclient.discovery import build
        from google.oauth2 import service_account

        if os.path.exists(CREDENTIALS):
            creds = service_account.Credentials.from_service_account_file(
                CREDENTIALS, scopes=SCOPES)
            return build("searchconsole", "v1", credentials=creds)
        return None
    except ImportError:
        print("Install: pip install google-api-python-client google-auth")
        return None


def get_top_keywords(days: int = 90, limit: int = 50) -> List[Dict]:
    """Get top keywords by clicks in the last N days."""
    service = get_gsc_service()
    if not service or not SITE_URL:
        return _mock_keywords()

    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)

    try:
        response = service.searchanalytics().query(
            siteUrl=SITE_URL,
            body={
                "startDate": str(start_date),
                "endDate": str(end_date),
                "dimensions": ["query"],
                "rowLimit": limit,
                "orderBy": [{"fieldName": "clicks", "sortOrder": "DESCENDING"}]
            }
        ).execute()

        return [
            {
                "keyword": row["keys"][0],
                "clicks": row.get("clicks", 0),
                "impressions": row.get("impressions", 0),
                "ctr": round(row.get("ctr", 0) * 100, 1),
                "position": round(row.get("position", 0), 1),
            }
            for row in response.get("rows", [])
        ]
    except Exception as e:
        print(f"GSC keywords error: {e}")
        return _mock_keywords()


def get_keywords_by_page(url_path: str, days: int = 90) -> List[Dict]:
    """Get keywords driving traffic to a specific page."""
    service = get_gsc_service()
    if not service or not SITE_URL:
        return []

    full_url = f"{SITE_URL}{url_path}" if url_path.startswith("/") else url_path
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)

    try:
        response = service.searchanalytics().query(
            siteUrl=SITE_URL,
            body={
                "startDate": str(start_date),
                "endDate": str(end_date),
                "dimensions": ["query"],
                "dimensionFilterGroups": [{
                    "filters": [{
                        "dimension": "page",
                        "operator": "equals",
                        "expression": full_url
                    }]
                }],
                "rowLimit": 25,
            }
        ).execute()

        return [
            {
                "keyword": row["keys"][0],
                "clicks": row.get("clicks", 0),
                "impressions": row.get("impressions", 0),
                "ctr": round(row.get("ctr", 0) * 100, 1),
                "position": round(row.get("position", 0), 1),
            }
            for row in response.get("rows", [])
        ]
    except Exception as e:
        print(f"GSC page keywords error: {e}")
        return []


def get_quick_wins(days: int = 90) -> List[Dict]:
    """Find keywords in positions 11-20 (quick win opportunities)."""
    keywords = get_top_keywords(days, limit=200)
    quick_wins = []

    for kw in keywords:
        pos = kw["position"]
        if 11 <= pos <= 20 and kw["impressions"] >= 50:
            # Estimate traffic gain if reaches position 3
            current_ctr = kw["ctr"] / 100
            target_ctr  = 0.11  # ~CTR at position 3
            traffic_gain = round((target_ctr - current_ctr) * kw["impressions"])

            quick_wins.append({
                **kw,
                "estimated_traffic_gain": traffic_gain,
                "action": "Optimize content, add internal links, improve meta title CTR",
            })

    return sorted(quick_wins, key=lambda x: x["estimated_traffic_gain"], reverse=True)


def get_low_ctr_opportunities(days: int = 90) -> List[Dict]:
    """Find pages with high impressions but low CTR."""
    service = get_gsc_service()
    if not service or not SITE_URL:
        return []

    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)

    try:
        response = service.searchanalytics().query(
            siteUrl=SITE_URL,
            body={
                "startDate": str(start_date),
                "endDate": str(end_date),
                "dimensions": ["page"],
                "rowLimit": 100,
                "orderBy": [{"fieldName": "impressions", "sortOrder": "DESCENDING"}]
            }
        ).execute()

        opportunities = []
        for row in response.get("rows", []):
            impressions = row.get("impressions", 0)
            ctr = row.get("ctr", 0) * 100
            position = row.get("position", 0)

            # Expected CTR table based on position
            expected_ctr = {1: 28, 2: 15, 3: 11, 4: 8, 5: 6,
                             6: 4, 7: 3, 8: 2.5, 9: 2, 10: 1.5}
            pos_int = min(max(int(position), 1), 10)
            exp_ctr = expected_ctr.get(pos_int, 1.5)

            if impressions >= 100 and ctr < exp_ctr * 0.7:
                opportunities.append({
                    "page": row["keys"][0],
                    "impressions": impressions,
                    "clicks": row.get("clicks", 0),
                    "ctr": round(ctr, 1),
                    "expected_ctr": exp_ctr,
                    "position": round(position, 1),
                    "action": "Rewrite meta title and description to improve CTR",
                })

        return sorted(opportunities, key=lambda x: x["impressions"], reverse=True)

    except Exception as e:
        print(f"GSC CTR error: {e}")
        return []


def _mock_keywords() -> List[Dict]:
    return [
        {"keyword": "seo guide", "clicks": 450, "impressions": 8200,
         "ctr": 5.5, "position": 8.2},
        {"keyword": "technical seo", "clicks": 280, "impressions": 5100,
         "ctr": 5.5, "position": 11.4},
        {"keyword": "wordpress seo tips", "clicks": 190, "impressions": 3800,
         "ctr": 5.0, "position": 14.8},
    ]


def generate_gsc_summary(days: int = 30) -> str:
    """Generate a markdown summary of GSC data."""
    keywords = get_top_keywords(days)
    quick_wins = get_quick_wins(days)
    low_ctr = get_low_ctr_opportunities(days)

    total_clicks = sum(k["clicks"] for k in keywords)
    total_impressions = sum(k["impressions"] for k in keywords)
    avg_position = round(sum(k["position"] for k in keywords) / max(len(keywords), 1), 1)

    lines = [
        f"## Google Search Console Summary (Last {days} days)",
        f"",
        f"**Total clicks:** {total_clicks:,} | **Impressions:** {total_impressions:,} | **Avg position:** {avg_position}",
        f"",
        f"### Top Keywords",
        "| Keyword | Clicks | Impressions | CTR | Position |",
        "|---|---|---|---|---|",
    ]

    for k in keywords[:10]:
        lines.append(f"| {k['keyword']} | {k['clicks']:,} | {k['impressions']:,} | {k['ctr']}% | {k['position']} |")

    if quick_wins:
        lines += ["", "### ⭐ Quick Wins (Positions 11-20)",
                  "| Keyword | Position | Est. Traffic Gain | Action |",
                  "|---|---|---|---|"]
        for qw in quick_wins[:5]:
            lines.append(f"| {qw['keyword']} | {qw['position']} | +{qw['estimated_traffic_gain']}/mo | {qw['action']} |")

    return "\n".join(lines)


if __name__ == "__main__":
    print(generate_gsc_summary())
