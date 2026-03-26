"""
Claude Auto SEO — Google Analytics 4 Integration
Fetches traffic, engagement, and conversion data from GA4.

Setup:
1. Create a Google Cloud service account
2. Grant it Viewer access to your GA4 property
3. Download the JSON key to config/google-service-account.json
4. Set GA4_PROPERTY_ID in .env
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

PROPERTY_ID = os.environ.get("GA4_PROPERTY_ID", "")
CREDENTIALS  = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS",
                               "config/google-service-account.json")


def get_analytics_client():
    """Return an authenticated GA4 Analytics Data client."""
    try:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        from google.oauth2 import service_account

        if os.path.exists(CREDENTIALS):
            creds = service_account.Credentials.from_service_account_file(
                CREDENTIALS,
                scopes=["https://www.googleapis.com/auth/analytics.readonly"]
            )
            return BetaAnalyticsDataClient(credentials=creds)
        else:
            # Try application default credentials
            return BetaAnalyticsDataClient()
    except ImportError:
        print("Install: pip install google-analytics-data")
        return None


def get_top_pages(days: int = 30, limit: int = 20) -> List[Dict]:
    """Get top pages by organic sessions in the last N days."""
    client = get_analytics_client()
    if not client or not PROPERTY_ID:
        return _mock_top_pages()

    try:
        from google.analytics.data_v1beta.types import (
            RunReportRequest, DateRange, Dimension, Metric, FilterExpression,
            Filter, DimensionFilter
        )

        request = RunReportRequest(
            property=f"properties/{PROPERTY_ID}",
            dimensions=[Dimension(name="pagePath"), Dimension(name="pageTitle")],
            metrics=[
                Metric(name="sessions"),
                Metric(name="organicGoogleSearchSessions"),
                Metric(name="bounceRate"),
                Metric(name="averageSessionDuration"),
            ],
            date_ranges=[DateRange(
                start_date=f"{days}daysAgo",
                end_date="today"
            )],
            limit=limit,
            order_bys=[{"metric": {"metric_name": "organicGoogleSearchSessions"},
                        "desc": True}]
        )

        response = client.run_report(request)
        pages = []
        for row in response.rows:
            pages.append({
                "path": row.dimension_values[0].value,
                "title": row.dimension_values[1].value,
                "sessions": int(row.metric_values[0].value),
                "organic_sessions": int(row.metric_values[1].value),
                "bounce_rate": float(row.metric_values[2].value),
                "avg_duration_sec": float(row.metric_values[3].value),
            })
        return pages

    except Exception as e:
        print(f"GA4 error: {e}")
        return _mock_top_pages()


def get_traffic_trend(days: int = 90) -> List[Dict]:
    """Get daily organic traffic for the last N days."""
    client = get_analytics_client()
    if not client or not PROPERTY_ID:
        return []

    try:
        from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Dimension, Metric

        request = RunReportRequest(
            property=f"properties/{PROPERTY_ID}",
            dimensions=[Dimension(name="date")],
            metrics=[Metric(name="organicGoogleSearchSessions"),
                     Metric(name="sessions")],
            date_ranges=[DateRange(start_date=f"{days}daysAgo", end_date="today")],
            order_bys=[{"dimension": {"dimension_name": "date"}, "desc": False}]
        )

        response = client.run_report(request)
        return [
            {
                "date": row.dimension_values[0].value,
                "organic_sessions": int(row.metric_values[0].value),
                "total_sessions": int(row.metric_values[1].value),
            }
            for row in response.rows
        ]
    except Exception as e:
        print(f"GA4 trend error: {e}")
        return []


def get_declining_pages(days: int = 90, threshold_pct: float = 20.0) -> List[Dict]:
    """Find pages with significant traffic decline."""
    client = get_analytics_client()
    if not client or not PROPERTY_ID:
        return []

    try:
        from google.analytics.data_v1beta.types import (
            RunReportRequest, DateRange, Dimension, Metric
        )

        half = days // 2
        request = RunReportRequest(
            property=f"properties/{PROPERTY_ID}",
            dimensions=[Dimension(name="pagePath")],
            metrics=[Metric(name="organicGoogleSearchSessions")],
            date_ranges=[
                DateRange(start_date=f"{days}daysAgo", end_date=f"{half}daysAgo"),
                DateRange(start_date=f"{half}daysAgo", end_date="today"),
            ],
            limit=50
        )

        response = client.run_report(request)
        declining = []
        for row in response.rows:
            path = row.dimension_values[0].value
            old_sessions = int(row.metric_values[0].value)
            new_sessions = int(row.metric_values[1].value)

            if old_sessions > 10 and new_sessions < old_sessions:
                decline_pct = (old_sessions - new_sessions) / old_sessions * 100
                if decline_pct >= threshold_pct:
                    declining.append({
                        "path": path,
                        "old_sessions": old_sessions,
                        "new_sessions": new_sessions,
                        "decline_pct": round(decline_pct, 1),
                        "action": "Content refresh needed",
                    })

        return sorted(declining, key=lambda x: x["decline_pct"], reverse=True)

    except Exception as e:
        print(f"GA4 decline error: {e}")
        return []


def _mock_top_pages() -> List[Dict]:
    """Return mock data when GA4 is not configured."""
    return [
        {"path": "/blog/seo-guide", "title": "SEO Guide", "sessions": 1200,
         "organic_sessions": 980, "bounce_rate": 0.42, "avg_duration_sec": 185},
        {"path": "/blog/keyword-research", "title": "Keyword Research",
         "sessions": 850, "organic_sessions": 720, "bounce_rate": 0.38,
         "avg_duration_sec": 210},
    ]


def generate_ga4_summary(days: int = 30) -> str:
    """Generate a markdown summary of GA4 data."""
    pages = get_top_pages(days)
    declining = get_declining_pages(days)

    total_organic = sum(p["organic_sessions"] for p in pages)

    lines = [
        f"## Google Analytics 4 Summary (Last {days} days)",
        f"",
        f"**Total organic sessions:** {total_organic:,}",
        f"",
        f"### Top Pages by Organic Traffic",
        "| Page | Organic Sessions | Bounce Rate |",
        "|---|---|---|",
    ]

    for p in pages[:10]:
        lines.append(f"| {p['path'][:50]} | {p['organic_sessions']:,} | {p['bounce_rate']:.0%} |")

    if declining:
        lines += [
            "",
            "### ⚠️ Declining Pages (Need Refresh)",
            "| Page | Old Sessions | New Sessions | Decline |",
            "|---|---|---|---|",
        ]
        for p in declining[:5]:
            lines.append(f"| {p['path'][:40]} | {p['old_sessions']:,} | {p['new_sessions']:,} | -{p['decline_pct']}% |")

    return "\n".join(lines)


if __name__ == "__main__":
    print(generate_ga4_summary())
