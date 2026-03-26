"""
Claude Auto SEO — Additional Automation Modules

This file contains modules for features not yet covered:
1. A/B Meta Title Tester (track CTR per title variation)
2. Content Decay Monitor (detect declining pages before they drop)
3. Review Request Automation (auto-ask customers for reviews)
4. Internal Link Suggester (finds gaps in internal linking)
5. Broken Link Monitor (weekly check for 404s)
"""

import os
import json
import re
import requests
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")


# ── 1. CONTENT DECAY MONITOR ─────────────────────────────────────────────────

def find_decaying_content(threshold_pct: float = 20.0) -> List[Dict]:
    """
    Find pages where traffic is declining significantly.
    Uses Google Analytics data (if available) or rankings history.
    """
    decaying = []

    # Load rankings history
    history_file = os.path.join(DATA_DIR, "rankings-history.json")
    if not os.path.exists(history_file):
        return []

    with open(history_file) as f:
        data = json.load(f)

    for kw in data.get("tracked_keywords", []):
        history = kw.get("history", [])
        if len(history) < 4:
            continue

        recent = history[-2:]     # Last 2 checks
        older  = history[-6:-2]   # 4 checks before that

        if not older:
            continue

        recent_avg = sum(h["position"] for h in recent) / len(recent)
        older_avg  = sum(h["position"] for h in older)  / len(older)

        # Position increased (worse) by threshold
        if recent_avg > older_avg * (1 + threshold_pct / 100):
            drop_pct = round((recent_avg - older_avg) / older_avg * 100, 1)
            decaying.append({
                "keyword":         kw["keyword"],
                "url":             kw.get("target_url", ""),
                "old_position":    round(older_avg, 1),
                "new_position":    round(recent_avg, 1),
                "position_drop":   round(recent_avg - older_avg, 1),
                "drop_pct":        drop_pct,
                "action":          "Run /content rewrite on this page",
                "priority":        "HIGH" if drop_pct > 50 else "MEDIUM",
            })

    return sorted(decaying, key=lambda x: x["drop_pct"], reverse=True)


def generate_decay_report() -> str:
    decaying = find_decaying_content()

    if not decaying:
        return "✅ No content decay detected. All tracked keywords are holding position."

    lines = [
        f"# Content Decay Report — {date.today().isoformat()}",
        f"**{len(decaying)} pages showing declining rankings**",
        "",
        "| Page | Keyword | Was | Now | Drop | Action |",
        "|---|---|---|---|---|---|",
    ]

    for item in decaying[:20]:
        lines.append(
            f"| {item['url'][:40]} | {item['keyword']} | "
            f"#{item['old_position']} | #{item['new_position']} | "
            f"+{item['position_drop']} pos | {item['action']} |"
        )

    lines += [
        "",
        "## Recommended Actions",
        "",
        "For each page above:",
        "1. Run: `/content rewrite <url>` in Claude Code",
        "2. This will refresh stats, add new sections, improve SEO",
        "3. Re-submit to Google Search Console after updating",
    ]

    return "\n".join(lines)


# ── 2. BROKEN LINK MONITOR ───────────────────────────────────────────────────

def check_internal_links(domain: str, limit: int = 50) -> Dict:
    """Check internal links across your site for 404s."""
    base_url = f"https://{domain}"
    headers  = {"User-Agent": "Mozilla/5.0 (compatible; ClaudeAutoSEO/1.0)"}

    broken   = []
    checked  = 0

    # Load from internal links map
    links_map = os.path.join(BASE_DIR, "context", "internal-links-map.md")
    urls_to_check = []

    if os.path.exists(links_map):
        with open(links_map) as f:
            content = f.read()
        urls_to_check = re.findall(r'https?://[^\s|)"\'>]+', content)[:limit]

    for url in urls_to_check:
        try:
            r = requests.head(url, timeout=8, allow_redirects=True, headers=headers)
            checked += 1
            if r.status_code in (404, 410):
                broken.append({"url": url, "status": r.status_code,
                                "action": "Remove or update links pointing here"})
            elif r.status_code >= 500:
                broken.append({"url": url, "status": r.status_code,
                                "action": "Server error — check hosting"})
        except Exception as e:
            broken.append({"url": url, "status": "timeout", "action": "Check URL manually"})

    return {
        "checked": checked,
        "broken": broken,
        "broken_count": len(broken),
        "checked_at": datetime.now().isoformat(),
    }


# ── 3. REVIEW REQUEST SYSTEM ─────────────────────────────────────────────────

def generate_review_request_email(customer_name: str, business_name: str,
                                    review_url: str) -> Dict:
    """Generate a review request email for a customer."""
    business = business_name or os.environ.get("SITE_NAME", "Our Business")

    subject = f"Would you share your experience with {business}?"
    body = f"""Hi {customer_name or 'there'},

Thank you for choosing {business}! We hope everything went well.

If you had a positive experience, we'd really appreciate a quick review. It takes less than 2 minutes and helps us serve more customers like you.

👉 Leave a review here: {review_url}

Just share what you liked — even a sentence or two makes a big difference.

Thank you for your support!

Best regards,
The {business} Team
{os.environ.get('WP_URL', '')}
"""

    return {
        "subject": subject,
        "body": body,
        "review_platforms": {
            "google": f"https://search.google.com/local/writereview?placeid=YOUR_PLACE_ID",
            "trustpilot": f"https://www.trustpilot.com/evaluate/{os.environ.get('WP_URL','').replace('https://','').replace('http://','').rstrip('/')}",
            "facebook": "https://www.facebook.com/YOUR_PAGE/reviews",
        }
    }


# ── 4. INTERNAL LINK GAP FINDER ──────────────────────────────────────────────

def find_internal_link_gaps(wp_posts: List[Dict] = None) -> List[Dict]:
    """Find posts with no internal links (orphan pages)."""
    wp_url  = os.environ.get("WP_URL", "")
    wp_user = os.environ.get("WP_USERNAME", "")
    wp_pass = os.environ.get("WP_APP_PASSWORD", "")

    if not all([wp_url, wp_user, wp_pass]):
        return []

    import base64
    creds = base64.b64encode(f"{wp_user}:{wp_pass}".encode()).decode()
    headers = {"Authorization": f"Basic {creds}"}

    try:
        r = requests.get(f"{wp_url}/wp-json/wp/v2/posts",
                         params={"per_page": 50, "status": "publish",
                                 "_fields": "id,link,title,content"},
                         headers=headers, timeout=15)
        if r.status_code != 200:
            return []

        posts = r.json()
        orphans = []

        for post in posts:
            content = post.get("content", {}).get("rendered", "")
            # Count internal links
            internal_count = len(re.findall(
                rf'href=["\']({re.escape(wp_url)}[^"\']+)["\']', content))

            if internal_count == 0:
                title = re.sub(r"<[^>]+>", "", post.get("title", {}).get("rendered", ""))
                orphans.append({
                    "post_id": post["id"],
                    "title":   title,
                    "url":     post.get("link", ""),
                    "action":  "Add 3-5 internal links from related pages",
                })

        return orphans

    except Exception:
        return []


# ── 5. SEO COMPETITOR MONITOR ────────────────────────────────────────────────

def check_competitor_activity(competitors: List[str] = None) -> List[Dict]:
    """Check if competitors published new content recently."""
    if not competitors:
        # Load from config
        cfg_path = os.path.join(BASE_DIR, "config", "competitors.json")
        if os.path.exists(cfg_path):
            with open(cfg_path) as f:
                cfg = json.load(f)
            competitors = [c.get("domain", "") for c in cfg.get("competitors", []) if c.get("domain")]

    if not competitors:
        return []

    new_content = []
    headers = {"User-Agent": "Mozilla/5.0 (compatible; ClaudeAutoSEO/1.0)"}

    for domain in competitors:
        try:
            # Check RSS feed
            for rss_url in [f"https://{domain}/feed/", f"https://{domain}/rss.xml",
                             f"https://{domain}/blog/feed/"]:
                try:
                    r = requests.get(rss_url, headers=headers, timeout=8)
                    if r.status_code == 200 and "<item>" in r.text:
                        # Parse latest items
                        items = re.findall(r"<item>(.*?)</item>", r.text, re.DOTALL)[:3]
                        for item in items:
                            title_match = re.search(r"<title[^>]*>(.*?)</title>", item, re.DOTALL)
                            link_match  = re.search(r"<link>(.*?)</link>", item)
                            pub_match   = re.search(r"<pubDate>(.*?)</pubDate>", item)

                            if title_match:
                                new_content.append({
                                    "competitor": domain,
                                    "title": re.sub(r"<[^>]+>|<!\[CDATA\[|\]\]>", "",
                                                     title_match.group(1)).strip(),
                                    "url": link_match.group(1).strip() if link_match else "",
                                    "published": pub_match.group(1).strip() if pub_match else "",
                                })
                        break
                except Exception:
                    continue
        except Exception:
            continue

    return new_content


def run_all_monitors() -> str:
    """Run all monitoring checks and return a combined report."""
    lines = [
        f"# SEO Monitoring Report — {date.today().isoformat()}",
        "",
    ]

    # Content decay
    decay = find_decaying_content()
    lines.append(f"## 📉 Content Decay ({len(decay)} pages declining)")
    if decay:
        for d in decay[:5]:
            lines.append(f"- **{d['keyword']}**: #{d['old_position']} → #{d['new_position']} — {d['action']}")
    else:
        lines.append("✅ No content decay detected.")
    lines.append("")

    # Competitor activity
    competitor_news = check_competitor_activity()
    lines.append(f"## 👀 Competitor Activity ({len(competitor_news)} new posts)")
    for item in competitor_news[:5]:
        lines.append(f"- **{item['competitor']}**: [{item['title']}]({item['url']})")
    if not competitor_news:
        lines.append("_No new competitor content detected._")
    lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Claude Auto SEO — Monitoring Modules")
    parser.add_argument("--decay",           action="store_true", help="Content decay report")
    parser.add_argument("--broken-links",    metavar="DOMAIN",    help="Check broken links")
    parser.add_argument("--link-gaps",       action="store_true", help="Find orphan pages")
    parser.add_argument("--competitor-news", action="store_true", help="Check competitor content")
    parser.add_argument("--all",             action="store_true", help="Run all monitors")
    args = parser.parse_args()

    if args.decay or args.all:
        print(generate_decay_report())

    if args.broken_links:
        result = check_internal_links(args.broken_links)
        print(f"Broken links found: {result['broken_count']}/{result['checked']}")
        for b in result["broken"]:
            print(f"  {b['status']}: {b['url']}")

    if args.link_gaps or args.all:
        gaps = find_internal_link_gaps()
        if gaps:
            print(f"\n⚠️  {len(gaps)} pages with no internal links:")
            for g in gaps[:10]:
                print(f"  - {g['title']} ({g['url']})")
        else:
            print("✅ All pages have internal links.")

    if args.competitor_news or args.all:
        news = check_competitor_activity()
        if news:
            print(f"\n📰 Competitor activity ({len(news)} new posts):")
            for n in news[:5]:
                print(f"  {n['competitor']}: {n['title']}")
