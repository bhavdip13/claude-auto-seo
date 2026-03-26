"""
Claude Auto SEO — Top 100 Keyword Finder
Finds your best keywords from multiple sources and prioritizes them for maximum Google impact.

Priority order:
1. Keywords YOU already rank on pages 2-6 (easiest to push to page 1)
2. High-performing keywords you're missing (competitors rank, you don't)
3. New high-value keywords in your niche
4. Long-tail keywords from your existing content

Usage:
  python3 scripts/keyword_finder.py --domain yoursite.com
  python3 scripts/keyword_finder.py --domain yoursite.com --update-config
  python3 scripts/keyword_finder.py --quick-wins-only
"""

import os
import re
import sys
import json
import requests
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")


# ── GSC Quick Wins (best source — your actual ranking data) ──────────────────

def get_gsc_quick_wins(limit: int = 50) -> List[Dict]:
    """
    Get keywords from Google Search Console where you rank pages 2-6.
    These are your highest-priority keywords — already indexed, just need a push.
    """
    try:
        sys.path.insert(0, os.path.join(BASE_DIR, "data_sources", "modules"))
        from google_search_console import get_top_keywords, get_quick_wins
        print("  📊 Loading keywords from Google Search Console...")

        all_kws = get_top_keywords(days=90, limit=200)
        quick_wins = []

        for kw in all_kws:
            pos = kw.get("position", 0)
            impressions = kw.get("impressions", 0)

            # Pages 2-6 = positions 11-60 = QUICK WINS
            if 11 <= pos <= 60 and impressions >= 20:
                priority = "🔥 PAGE 2 — HIGHEST PRIORITY" if pos <= 20 else \
                           "⚡ PAGE 3-4 — HIGH PRIORITY" if pos <= 40 else \
                           "💡 PAGE 5-6 — GOOD OPPORTUNITY"

                expected_ctr_gain = {
                    11: 0.08, 12: 0.07, 13: 0.06, 14: 0.05, 15: 0.045,
                    16: 0.04, 17: 0.035, 18: 0.03, 19: 0.025, 20: 0.02,
                }
                target_ctr = expected_ctr_gain.get(min(int(pos), 20), 0.015)
                estimated_gain = round(impressions * target_ctr)

                quick_wins.append({
                    "keyword": kw["keyword"],
                    "current_position": round(pos, 1),
                    "impressions": impressions,
                    "clicks": kw.get("clicks", 0),
                    "current_ctr": kw.get("ctr", 0),
                    "priority": priority,
                    "estimated_traffic_gain": estimated_gain,
                    "source": "gsc",
                    "action": _get_action_for_position(pos),
                })

        return sorted(quick_wins, key=lambda x: x["estimated_traffic_gain"], reverse=True)[:limit]

    except Exception as e:
        print(f"  ⚠️  GSC not available: {e}")
        return []


def _get_action_for_position(pos: float) -> str:
    if pos <= 15:
        return "Optimize meta title for CTR + add 2 internal links"
    elif pos <= 25:
        return "Expand content by 500+ words, add FAQ section, improve internal linking"
    elif pos <= 40:
        return "Major content refresh: research top 5 competitors, expand to beat them"
    else:
        return "Full content rewrite based on current top 10 analysis"


# ── DataForSEO Keyword Research ───────────────────────────────────────────────

def get_dataforseo_keywords(domain: str, limit: int = 50) -> List[Dict]:
    """Get competitor keywords using DataForSEO."""
    login    = os.environ.get("DATAFORSEO_LOGIN")
    password = os.environ.get("DATAFORSEO_PASSWORD")

    if not login or not password:
        print("  ⚠️  DataForSEO not configured. Skipping competitor keywords.")
        return []

    try:
        import base64
        auth = base64.b64encode(f"{login}:{password}".encode()).decode()
        headers = {"Authorization": f"Basic {auth}", "Content-Type": "application/json"}

        # Get domain's organic keywords
        r = requests.post(
            "https://api.dataforseo.com/v3/dataforseo_labs/google/ranked_keywords/live",
            headers=headers,
            json=[{"target": domain, "language_code": "en", "location_code": 2840,
                   "limit": limit, "filters": [["keyword_data.keyword_info.search_volume", ">", 100]]}],
            timeout=30
        )

        if r.status_code == 200:
            items = r.json().get("tasks", [{}])[0].get("result", [{}])[0].get("items", [])
            keywords = []
            for item in items:
                kd = item.get("keyword_data", {})
                ki = kd.get("keyword_info", {})
                rank = item.get("ranked_serp_element", {}).get("serp_item", {}).get("rank_absolute", 999)

                keywords.append({
                    "keyword": kd.get("keyword", ""),
                    "volume": ki.get("search_volume", 0),
                    "difficulty": kd.get("keyword_properties", {}).get("keyword_difficulty", 0),
                    "cpc": ki.get("cpc", 0),
                    "current_position": rank,
                    "source": "dataforseo",
                    "priority": "🔥 PAGE 2" if 11 <= rank <= 20 else "📊 Tracked",
                })
            return keywords

    except Exception as e:
        print(f"  ⚠️  DataForSEO error: {e}")
    return []


# ── Content-Based Keyword Extraction ─────────────────────────────────────────

def extract_keywords_from_site_content(domain: str) -> List[Dict]:
    """Extract likely keywords from existing site content."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; ClaudeAutoSEO/1.0)"}
        base_url = f"https://{domain}"

        # Fetch homepage + blog page
        keywords = set()

        for url in [base_url, f"{base_url}/blog/", f"{base_url}/blog"]:
            try:
                r = requests.get(url, headers=headers, timeout=10)
                if r.status_code != 200:
                    continue
                html = r.text

                # Extract H1, H2, H3, title tags
                for tag in ["h1", "h2", "h3", "title"]:
                    matches = re.findall(rf"<{tag}[^>]*>(.*?)</{tag}>",
                                         html, re.IGNORECASE | re.DOTALL)
                    for m in matches:
                        text = re.sub(r"<[^>]+>", "", m).strip().lower()
                        if 5 < len(text) < 80:
                            # Clean to keyword-like phrase
                            clean = re.sub(r"[^\w\s-]", "", text).strip()
                            clean = re.sub(r"\s+", " ", clean)
                            if clean:
                                keywords.add(clean)

            except Exception:
                continue

        result = []
        for kw in list(keywords)[:30]:
            result.append({
                "keyword": kw,
                "volume": 500,
                "difficulty": "medium",
                "source": "site_content",
                "priority": "📄 From Your Content",
                "action": "Track and optimize existing pages",
            })
        return result

    except Exception:
        return []


# ── Niche Keyword Generator ───────────────────────────────────────────────────

def generate_niche_keywords(niche: str, site_title: str) -> List[Dict]:
    """Generate new keyword ideas based on detected niche."""
    niche_templates = {
        "marketing": [
            ("seo strategy {year}", 3200, "medium"),
            ("content marketing guide {year}", 2800, "medium"),
            ("digital marketing tips", 4500, "low"),
            ("how to rank on google {year}", 2200, "low"),
            ("local seo guide", 1800, "low"),
            ("email marketing best practices", 2400, "medium"),
            ("social media marketing strategy", 3600, "medium"),
            ("seo audit checklist", 1600, "low"),
        ],
        "technology": [
            ("best {niche} software {year}", 2800, "medium"),
            ("how to use {niche} tools", 1900, "low"),
            ("top tech tools {year}", 3200, "medium"),
            ("{niche} for beginners", 2400, "low"),
        ],
        "ecommerce": [
            ("how to start an online store {year}", 4200, "low"),
            ("ecommerce seo tips", 1800, "medium"),
            ("increase online sales {year}", 2600, "medium"),
            ("product photography tips", 1200, "low"),
            ("dropshipping guide {year}", 5800, "medium"),
        ],
        "health": [
            ("healthy lifestyle tips {year}", 5400, "low"),
            ("how to improve health naturally", 3800, "low"),
            ("best health supplements {year}", 4200, "medium"),
            ("mental health tips", 6200, "medium"),
        ],
        "finance": [
            ("how to save money fast", 8800, "low"),
            ("investing for beginners {year}", 9200, "medium"),
            ("personal finance tips {year}", 5400, "low"),
            ("best budgeting apps {year}", 4800, "low"),
            ("how to get out of debt {year}", 7200, "low"),
        ],
        "general": [
            (f"best {site_title.lower()} guide {year}", 1200, "low"),
            (f"how to {site_title.lower()}", 900, "low"),
            (f"{site_title.lower()} tips for beginners", 800, "low"),
            (f"{site_title.lower()} vs alternatives", 600, "medium"),
        ]
    }

    year = date.today().year
    templates = niche_templates.get(niche, niche_templates["general"])

    result = []
    for kw_template, vol, diff in templates:
        kw = kw_template.replace("{year}", str(year)).replace("{niche}", niche)
        result.append({
            "keyword": kw,
            "volume": vol,
            "difficulty": diff,
            "source": "generated",
            "priority": "🆕 New Opportunity",
            "action": f"Create new blog post targeting this keyword",
        })
    return result


# ── Main Report Generator ─────────────────────────────────────────────────────

def find_top_100_keywords(domain: str, update_config: bool = False) -> Dict:
    """Find and prioritize top 100 keywords for maximum Google impact."""
    print(f"\n🔍 Finding Top 100 Keywords for {domain}")
    print("="*60)

    # Load config for context
    site_json_path = os.path.join(BASE_DIR, "config", "site.json")
    niche = "general"
    site_title = domain
    if os.path.exists(site_json_path):
        with open(site_json_path) as f:
            site_cfg = json.load(f)
        niche = site_cfg.get("site", {}).get("niche", "general")
        site_title = site_cfg.get("site", {}).get("name", domain)

    all_keywords = []

    # Source 1: GSC quick wins (highest priority — you already rank!)
    print("\n1️⃣  Fetching YOUR existing rankings (Google Search Console)...")
    gsc_kws = get_gsc_quick_wins(50)
    print(f"  Found {len(gsc_kws)} quick win keywords")
    all_keywords.extend(gsc_kws)

    # Source 2: DataForSEO domain keywords
    print("\n2️⃣  Fetching domain keywords (DataForSEO)...")
    dfs_kws = get_dataforseo_keywords(domain, 30)
    print(f"  Found {len(dfs_kws)} keywords from DataForSEO")
    all_keywords.extend(dfs_kws)

    # Source 3: Extract from your own content
    print("\n3️⃣  Extracting keywords from your site content...")
    content_kws = extract_keywords_from_site_content(domain)
    print(f"  Found {len(content_kws)} keywords from your content")
    all_keywords.extend(content_kws)

    # Source 4: New opportunities
    print("\n4️⃣  Generating new keyword opportunities for your niche...")
    new_kws = generate_niche_keywords(niche, site_title)
    print(f"  Generated {len(new_kws)} new keyword ideas")
    all_keywords.extend(new_kws)

    # Deduplicate
    seen = set()
    unique_kws = []
    for kw in all_keywords:
        key = kw["keyword"].lower().strip()
        if key and key not in seen:
            seen.add(key)
            unique_kws.append(kw)

    # Sort by priority (GSC quick wins first, then by volume)
    def sort_key(k):
        source_order = {"gsc": 0, "dataforseo": 1, "site_content": 2, "generated": 3}
        return (source_order.get(k.get("source", "generated"), 4),
                -k.get("estimated_traffic_gain", k.get("volume", 0)))

    unique_kws.sort(key=sort_key)
    top_100 = unique_kws[:100]

    print(f"\n✅ Total unique keywords found: {len(unique_kws)}")
    print(f"✅ Top 100 selected and prioritized")

    # Generate report
    report = _generate_keyword_report(top_100, domain, niche)

    # Save report
    os.makedirs(REPORTS_DIR, exist_ok=True)
    report_path = os.path.join(REPORTS_DIR, f"top-100-keywords-{date.today()}.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\n📄 Report saved: {report_path}")

    # Optionally update keywords.md
    if update_config:
        _update_keywords_config(top_100)
        print(f"✅ Updated config/keywords.md with prioritized keywords")

    return {"keywords": top_100, "report_path": report_path}


def _generate_keyword_report(keywords: List[Dict], domain: str, niche: str) -> str:
    lines = [
        f"# Top 100 Keywords Report — {domain}",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"**Niche:** {niche}",
        f"**Total keywords:** {len(keywords)}",
        "",
        "## Priority Legend",
        "- 🔥 PAGE 2 — HIGHEST PRIORITY: You rank 11-20. Small push → Page 1.",
        "- ⚡ PAGE 3-4 — HIGH PRIORITY: You rank 21-40. Content refresh needed.",
        "- 💡 PAGE 5-6 — GOOD OPPORTUNITY: You rank 41-60. Major work, good reward.",
        "- 🆕 NEW OPPORTUNITY: Not ranking yet. Create new content.",
        "- 📄 FROM CONTENT: Extracted from your site.",
        "",
        "---",
        "",
        "## 🔥 IMMEDIATE PRIORITY — Push These to Page 1 First",
        "_(Already ranking pages 2-3 — easiest wins)_",
        "",
        "| Keyword | Position | Impressions | Est. Traffic Gain | Action |",
        "|---|---|---|---|---|",
    ]

    # Section 1: Page 2-3 quick wins
    page_2_3 = [k for k in keywords if k.get("source") == "gsc" and k.get("current_position", 999) <= 30]
    for k in page_2_3[:20]:
        lines.append(
            f"| {k['keyword']} | #{k.get('current_position', '?')} | "
            f"{k.get('impressions', 0):,} | +{k.get('estimated_traffic_gain', 0):,}/mo | "
            f"{k.get('action', 'Optimize')} |"
        )

    lines += [
        "",
        "## ⚡ HIGH PRIORITY — Push from Pages 4-6",
        "",
        "| Keyword | Position | Impressions | Est. Traffic Gain | Action |",
        "|---|---|---|---|---|",
    ]

    # Section 2: Page 4-6
    page_4_6 = [k for k in keywords if k.get("source") == "gsc" and 30 < k.get("current_position", 999) <= 60]
    for k in page_4_6[:15]:
        lines.append(
            f"| {k['keyword']} | #{k.get('current_position', '?')} | "
            f"{k.get('impressions', 0):,} | +{k.get('estimated_traffic_gain', 0):,}/mo | "
            f"{k.get('action', 'Refresh content')} |"
        )

    lines += [
        "",
        "## 🆕 NEW KEYWORDS — Create Content for These",
        "",
        "| Keyword | Volume | Difficulty | Action |",
        "|---|---|---|---|",
    ]

    # Section 3: New keywords
    new_kws = [k for k in keywords if k.get("source") in ("generated", "site_content")]
    for k in new_kws[:25]:
        lines.append(
            f"| {k['keyword']} | {k.get('volume', '?'):,} | "
            f"{k.get('difficulty', '?')} | {k.get('action', 'Write new post')} |"
        )

    lines += [
        "",
        "## 🚀 Your 30-Day Action Plan",
        "",
        "### Week 1: Quick Wins (Push Page 2 → Page 1)",
        "_For each keyword in the 'IMMEDIATE PRIORITY' table:_",
        "1. Open the existing page that ranks for it",
        "2. Run `/content rewrite [URL]` to refresh the content",
        "3. Add 2-3 more internal links pointing to it",
        "4. Improve meta title CTR (use `/content optimize [file]`)",
        "5. Submit updated URL to Google Search Console for re-crawl",
        "",
        "### Week 2-3: Content Expansion",
        "_For each 'HIGH PRIORITY' keyword:_",
        "1. Run `/research [keyword]` for full competitive analysis",
        "2. Run `/write [keyword]` to create comprehensive new content",
        "3. Interlink with related existing pages",
        "",
        "### Week 4+: New Content",
        "_For 'NEW KEYWORDS':_",
        "1. Already in your `topics/queue.txt` — scheduler will handle these",
        "2. Or manually run: `/write [keyword]`",
        "",
        "---",
        f"*Run `python3 scripts/keyword_finder.py --domain {domain} --update-config`*",
        "*to automatically update config/keywords.md with these priorities.*",
    ]

    return "\n".join(lines)


def _update_keywords_config(keywords: List[Dict]):
    """Update config/keywords.md with prioritized keywords."""
    kw_path = os.path.join(BASE_DIR, "config", "keywords.md")

    # Append quick wins section at top
    quick_wins = [k for k in keywords if k.get("source") == "gsc" and k.get("current_position", 999) <= 30]

    if not quick_wins:
        return

    section = "\n\n## 🔥 QUICK WINS — Push to Page 1 (Auto-generated)\n\n"
    section += "| Keyword | Current Position | Volume | Difficulty | Intent | Status | Priority |\n"
    section += "|---|---|---|---|---|---|---|\n"

    for k in quick_wins[:20]:
        kw = k["keyword"]
        pos = k.get("current_position", "?")
        vol = k.get("impressions", 500)
        section += f"| {kw} | #{pos} | {vol} | medium | informational | queue | 🔥 High |\n"

    # Prepend to existing file
    if os.path.exists(kw_path):
        with open(kw_path, "r") as f:
            existing = f.read()
        with open(kw_path, "w") as f:
            f.write(existing + section)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Claude Auto SEO — Top 100 Keyword Finder")
    parser.add_argument("--domain",        default="", help="Your domain")
    parser.add_argument("--update-config", action="store_true", help="Update keywords.md")
    parser.add_argument("--quick-wins-only", action="store_true", help="Only show GSC quick wins")
    args = parser.parse_args()

    domain = args.domain or os.environ.get("WP_URL", "").replace("https://", "").replace("http://", "").rstrip("/")

    if not domain:
        print("❌ Provide --domain yoursite.com or set WP_URL in .env")
        sys.exit(1)

    if args.quick_wins_only:
        wins = get_gsc_quick_wins()
        print(f"\n⭐ Quick Win Keywords ({len(wins)} found):")
        for k in wins[:20]:
            print(f"  #{k['current_position']}: {k['keyword']} (+{k['estimated_traffic_gain']}/mo)")
    else:
        find_top_100_keywords(domain, args.update_config)
