"""
Claude Auto SEO — Legitimate Business Directory Manager
Manages submissions to REAL, high-authority business directories that:
  - Have genuine human editorial review
  - Pass real PageRank/link equity
  - Are trusted by Google
  - Improve local SEO and brand visibility

These are NOT spam directories. Each one has:
  - Domain Authority 40+
  - Human review process
  - Real traffic and users
  - Google's approval (they appear in SERPs themselves)

Usage:
  python3 scripts/directory_manager.py --generate-checklist
  python3 scripts/directory_manager.py --status
  python3 scripts/directory_manager.py --mark-submitted google_business
"""

import os
import json
import webbrowser
from datetime import datetime
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()

BASE_DIR     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATUS_FILE  = os.path.join(BASE_DIR, "data", "directory-status.json")

# ── LEGITIMATE HIGH-AUTHORITY DIRECTORIES ────────────────────────────────────
# These are real, editorially reviewed directories that Google trusts.
# Submitting to these is standard white-hat SEO practice.

DIRECTORIES = {

    # ── TIER 1: CRITICAL (Every business must be here) ──────────────────────
    "google_business": {
        "name": "Google Business Profile",
        "url": "https://business.google.com",
        "da": 100, "tier": 1, "free": True,
        "regions": ["global"],
        "type": "business_profile",
        "why": "CRITICAL: Controls your Google Maps listing, GMB posts, reviews. #1 local SEO factor.",
        "instructions": "Sign in with Google → Manage Now → Add your business"
    },
    "bing_places": {
        "name": "Bing Places for Business",
        "url": "https://www.bingplaces.com",
        "da": 95, "tier": 1, "free": True,
        "regions": ["USA", "UK", "global"],
        "type": "business_profile",
        "why": "Bing powers Yahoo, DuckDuckGo, and Cortana searches. 8% of all searches.",
        "instructions": "Sign in with Microsoft account → Add business"
    },
    "apple_maps": {
        "name": "Apple Maps Connect",
        "url": "https://mapsconnect.apple.com",
        "da": 100, "tier": 1, "free": True,
        "regions": ["global"],
        "type": "business_profile",
        "why": "Default maps on all iPhones, iPads, Macs. 1 billion active Apple devices.",
        "instructions": "Sign in with Apple ID → Add your place"
    },

    # ── TIER 2: HIGH VALUE (Strong DA, real editorial review) ───────────────
    "yelp": {
        "name": "Yelp for Business",
        "url": "https://biz.yelp.com",
        "da": 93, "tier": 2, "free": True,
        "regions": ["USA", "UK", "Europe"],
        "type": "reviews",
        "why": "Massive review platform. DA 93. Ranks in Google for '[business] + city' searches.",
        "instructions": "Claim or add your business at biz.yelp.com"
    },
    "trustpilot": {
        "name": "Trustpilot",
        "url": "https://business.trustpilot.com",
        "da": 91, "tier": 2, "free": True,
        "regions": ["global", "UK", "Europe", "USA"],
        "type": "reviews",
        "why": "Top review platform in Europe and UK. DA 91. Strong trust signals to Google.",
        "instructions": "Free plan available. Claim your profile at business.trustpilot.com"
    },
    "bbb": {
        "name": "Better Business Bureau (BBB)",
        "url": "https://www.bbb.org",
        "da": 91, "tier": 2, "free": False,
        "regions": ["USA", "Canada"],
        "type": "business_directory",
        "why": "Strongest trust signal for USA businesses. DA 91. Google trusts BBB listings heavily.",
        "instructions": "Apply at bbb.org/become-accredited (~$400/year, USA only)"
    },
    "linkedin_company": {
        "name": "LinkedIn Company Page",
        "url": "https://www.linkedin.com/company/setup/new/",
        "da": 99, "tier": 2, "free": True,
        "regions": ["global"],
        "type": "social_business",
        "why": "DA 99. Google indexes LinkedIn pages. Essential for B2B and professional credibility.",
        "instructions": "Create company page → Fill all fields → Add website URL"
    },

    # ── TIER 3: IMPORTANT (Real directories with good DA) ───────────────────
    "yellow_pages": {
        "name": "YellowPages.com",
        "url": "https://www.yellowpages.com",
        "da": 84, "tier": 3, "free": True,
        "regions": ["USA"],
        "type": "business_directory",
        "why": "Traditional US business directory. DA 84. Still appears in local searches.",
        "instructions": "Free basic listing at yp.com/advertise"
    },
    "yell": {
        "name": "Yell.com (UK)",
        "url": "https://www.yell.com",
        "da": 82, "tier": 3, "free": True,
        "regions": ["UK"],
        "type": "business_directory",
        "why": "UK's most established business directory. Free basic listing.",
        "instructions": "Register at business.yell.com"
    },
    "hotfrog": {
        "name": "Hotfrog",
        "url": "https://www.hotfrog.com",
        "da": 64, "tier": 3, "free": True,
        "regions": ["USA", "UK", "Australia", "Europe"],
        "type": "business_directory",
        "why": "Free global business directory with decent DA. Multi-region.",
        "instructions": "Add free listing at hotfrog.com"
    },
    "foursquare": {
        "name": "Foursquare",
        "url": "https://business.foursquare.com",
        "da": 91, "tier": 3, "free": True,
        "regions": ["global"],
        "type": "location",
        "why": "Powers location data for many apps. DA 91. Important for local SEO.",
        "instructions": "Claim your venue at business.foursquare.com"
    },
    "cylex": {
        "name": "Cylex",
        "url": "https://www.cylex.us.com",
        "da": 60, "tier": 3, "free": True,
        "regions": ["USA", "UK", "Europe", "Africa"],
        "type": "business_directory",
        "why": "Multi-country directory present in USA, UK, Germany, and many African countries.",
        "instructions": "Free listing at cylex.us.com (USA) or cylex.co.uk (UK)"
    },

    # ── UK SPECIFIC ──────────────────────────────────────────────────────────
    "thomson_local": {
        "name": "Thomson Local (UK)",
        "url": "https://www.thomsonlocal.com",
        "da": 64, "tier": 3, "free": True,
        "regions": ["UK"],
        "type": "business_directory",
        "why": "UK local business directory. Good for UK local SEO.",
        "instructions": "Add free listing at thomsonlocal.com"
    },
    "freeindex": {
        "name": "FreeIndex (UK)",
        "url": "https://www.freeindex.co.uk",
        "da": 55, "tier": 3, "free": True,
        "regions": ["UK"],
        "type": "business_directory",
        "why": "UK business directory with free listings.",
        "instructions": "Register at freeindex.co.uk"
    },
    "scoot": {
        "name": "Scoot (UK)",
        "url": "https://www.scoot.co.uk",
        "da": 55, "tier": 3, "free": True,
        "regions": ["UK"],
        "type": "business_directory",
        "why": "UK business search directory.",
        "instructions": "Add free listing at scoot.co.uk"
    },

    # ── EUROPE ───────────────────────────────────────────────────────────────
    "europages": {
        "name": "Europages",
        "url": "https://www.europages.co.uk",
        "da": 68, "tier": 3, "free": True,
        "regions": ["Europe", "UK"],
        "type": "business_directory",
        "why": "30M+ visits/year. Europe's largest B2B directory. DA 68.",
        "instructions": "Free company listing at europages.co.uk"
    },
    "kompass": {
        "name": "Kompass",
        "url": "https://www.kompass.com",
        "da": 70, "tier": 3, "free": True,
        "regions": ["Europe", "global"],
        "type": "b2b_directory",
        "why": "World's largest B2B directory. 70 countries. Strong for B2B businesses.",
        "instructions": "Free basic listing at kompass.com"
    },

    # ── AFRICA ───────────────────────────────────────────────────────────────
    "yellow_africa": {
        "name": "Yellow Africa",
        "url": "https://www.yellowafrica.com",
        "da": 44, "tier": 3, "free": True,
        "regions": ["Africa"],
        "type": "business_directory",
        "why": "Pan-African business directory.",
        "instructions": "Add listing at yellowafrica.com"
    },
    "nigerian_finder": {
        "name": "Nigerian Finder",
        "url": "https://www.nigerianfinder.com",
        "da": 40, "tier": 4, "free": True,
        "regions": ["Africa", "Nigeria"],
        "type": "business_directory",
        "why": "Nigeria-focused directory for African market reach.",
        "instructions": "Submit listing at nigerianfinder.com"
    },

    # ── INDUSTRY/NICHE DIRECTORIES ───────────────────────────────────────────
    "clutch": {
        "name": "Clutch.co (B2B Services)",
        "url": "https://clutch.co",
        "da": 76, "tier": 2, "free": True,
        "regions": ["global"],
        "type": "b2b_reviews",
        "why": "Top B2B review platform. DA 76. Critical for agencies and service businesses.",
        "instructions": "Claim free profile at clutch.co/profile/create"
    },
    "g2": {
        "name": "G2 (Software)",
        "url": "https://www.g2.com",
        "da": 89, "tier": 2, "free": True,
        "regions": ["global"],
        "type": "software_reviews",
        "why": "Largest software review platform. DA 89. Critical for SaaS companies.",
        "instructions": "Free listing at g2.com/products/create"
    },
    "capterra": {
        "name": "Capterra (Software)",
        "url": "https://www.capterra.com",
        "da": 87, "tier": 2, "free": True,
        "regions": ["global", "USA", "UK"],
        "type": "software_reviews",
        "why": "Gartner-owned software directory. DA 87. High-intent buyers browse here.",
        "instructions": "Submit at capterra.com/vendors/sign-up"
    },
    "producthunt": {
        "name": "Product Hunt",
        "url": "https://www.producthunt.com",
        "da": 90, "tier": 2, "free": True,
        "regions": ["global"],
        "type": "product_launch",
        "why": "DA 90. Launch your product to 500K+ early adopters. Huge backlink + traffic opportunity.",
        "instructions": "Submit at producthunt.com/posts/create"
    },
    "crunchbase": {
        "name": "Crunchbase",
        "url": "https://www.crunchbase.com",
        "da": 90, "tier": 2, "free": True,
        "regions": ["global"],
        "type": "startup_directory",
        "why": "DA 90. Google shows Crunchbase profiles for company searches. Free basic listing.",
        "instructions": "Add company at crunchbase.com/add-new-entity"
    },

    # ── CONTENT/MEDIA PLATFORMS ──────────────────────────────────────────────
    "medium": {
        "name": "Medium Publication",
        "url": "https://medium.com",
        "da": 95, "tier": 2, "free": True,
        "regions": ["global"],
        "type": "content_platform",
        "why": "DA 95. Republish articles with canonical link = authority signal + traffic.",
        "instructions": "Create account → Write articles → Set canonical to your site"
    },
    "substack": {
        "name": "Substack",
        "url": "https://substack.com",
        "da": 90, "tier": 2, "free": True,
        "regions": ["global"],
        "type": "newsletter_platform",
        "why": "DA 90. Newsletter + blog hybrid. Google indexes Substack posts.",
        "instructions": "Create newsletter at substack.com"
    },
    "github": {
        "name": "GitHub (Tech/Dev sites)",
        "url": "https://github.com",
        "da": 96, "tier": 2, "free": True,
        "regions": ["global"],
        "type": "developer_platform",
        "why": "DA 96. If you have any open source tool, a GitHub repo with website link is a strong backlink.",
        "instructions": "Create repo → Add website URL in About section"
    },
    "devto": {
        "name": "Dev.to",
        "url": "https://dev.to",
        "da": 88, "tier": 2, "free": True,
        "regions": ["global"],
        "type": "developer_blog",
        "why": "DA 88 developer community. Republish tech articles with canonical link.",
        "instructions": "Create account → Publish articles with canonical_url set"
    },
}


# ── Status Manager ────────────────────────────────────────────────────────────

def load_status() -> Dict:
    os.makedirs(os.path.dirname(STATUS_FILE), exist_ok=True)
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE) as f:
            return json.load(f)
    return {"submissions": {}, "last_updated": None}


def save_status(status: Dict):
    with open(STATUS_FILE, "w") as f:
        json.dump(status, f, indent=2)


def mark_submitted(directory_key: str, notes: str = ""):
    status = load_status()
    status["submissions"][directory_key] = {
        "submitted_at": datetime.now().isoformat(),
        "notes": notes,
        "status": "submitted"
    }
    status["last_updated"] = datetime.now().isoformat()
    save_status(status)
    print(f"✅ Marked as submitted: {DIRECTORIES.get(directory_key, {}).get('name', directory_key)}")


def generate_checklist(region: str = "all") -> str:
    """Generate a prioritized submission checklist."""
    status = load_status()
    submitted = set(status["submissions"].keys())

    lines = [
        "# Business Directory Submission Checklist",
        f"Generated: {datetime.now().strftime('%Y-%m-%d')}",
        "",
        "## How to Use",
        "1. Work through Tier 1 first (critical — do these TODAY)",
        "2. Then Tier 2 (high value — do this week)",
        "3. Then Tier 3 (good for local SEO — do this month)",
        "4. Mark complete: `python3 scripts/directory_manager.py --mark-submitted [key]`",
        "",
    ]

    for tier in [1, 2, 3, 4]:
        tier_dirs = {k: v for k, v in DIRECTORIES.items() if v["tier"] == tier}
        if not tier_dirs:
            continue

        tier_labels = {1: "🔴 TIER 1 — CRITICAL (Do Today)", 2: "🟡 TIER 2 — High Value (Do This Week)",
                       3: "🟢 TIER 3 — Good Value (Do This Month)", 4: "⚪ TIER 4 — Optional"}
        lines.append(f"## {tier_labels[tier]}")
        lines.append("")
        lines.append("| # | Directory | DA | Free? | Regions | Status |")
        lines.append("|---|---|---|---|---|---|")

        for i, (key, d) in enumerate(tier_dirs.items(), 1):
            if region != "all" and region not in d["regions"] and "global" not in d["regions"]:
                continue
            done = "✅ Done" if key in submitted else "⬜ Todo"
            free = "Free" if d["free"] else "Paid"
            regions = ", ".join(d["regions"][:3])
            lines.append(f"| {i} | [{d['name']}]({d['url']}) | {d['da']} | {free} | {regions} | {done} |")

        lines.append("")

    # Progress summary
    total = len(DIRECTORIES)
    done = len(submitted)
    lines += [
        f"## Progress: {done}/{total} submitted ({int(done/total*100)}%)",
        "",
        "Run `python3 scripts/directory_manager.py --status` to see full status.",
    ]

    return "\n".join(lines)


def show_status():
    status = load_status()
    submitted = status["submissions"]
    total = len(DIRECTORIES)
    done = len(submitted)

    print(f"\n📊 Directory Submission Status")
    print(f"{'='*50}")
    print(f"Submitted: {done}/{total} ({int(done/total*100)}%)")
    print(f"\n✅ Done:")
    for key in submitted:
        d = DIRECTORIES.get(key, {})
        print(f"  - {d.get('name', key)} ({submitted[key]['submitted_at'][:10]})")
    print(f"\n⬜ Remaining (by priority):")
    for tier in [1, 2, 3]:
        not_done = [(k, v) for k, v in DIRECTORIES.items() if v["tier"] == tier and k not in submitted]
        if not_done:
            print(f"\n  Tier {tier}:")
            for k, v in not_done[:5]:
                print(f"    {v['name']} — DA {v['da']} — {v['url']}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Claude Auto SEO — Directory Manager")
    parser.add_argument("--generate-checklist", action="store_true", help="Generate submission checklist")
    parser.add_argument("--status", action="store_true", help="Show submission status")
    parser.add_argument("--mark-submitted", metavar="KEY", help="Mark a directory as submitted")
    parser.add_argument("--region", default="all", help="Filter by region (USA/UK/Europe/Africa/global)")
    parser.add_argument("--open", metavar="KEY", help="Open a directory URL in browser")
    parser.add_argument("--notes", default="", help="Notes for mark-submitted")
    args = parser.parse_args()

    if args.generate_checklist:
        checklist = generate_checklist(args.region)
        path = os.path.join(BASE_DIR, "reports", f"directory-checklist-{datetime.now().strftime('%Y%m%d')}.md")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(checklist)
        print(f"✅ Checklist saved: {path}")
        print(checklist[:2000])
    elif args.status:
        show_status()
    elif args.mark_submitted:
        mark_submitted(args.mark_submitted, args.notes)
    elif args.open:
        d = DIRECTORIES.get(args.open)
        if d:
            webbrowser.open(d["url"])
            print(f"Opened: {d['name']} — {d['url']}")
        else:
            print(f"Unknown directory key: {args.open}")
            print(f"Available: {', '.join(DIRECTORIES.keys())}")
    else:
        parser.print_help()
        print(f"\nAvailable directory keys: {', '.join(DIRECTORIES.keys())}")
