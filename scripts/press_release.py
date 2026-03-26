"""
Claude Auto SEO — Press Release Distributor
Distributes press releases to free and paid news distribution sites.

Usage:
  python3 scripts/press_release.py --generate "product launch"
  python3 scripts/press_release.py --distribute reports/press-release.md
  python3 scripts/press_release.py --list-sites
"""

import os
import json
import re
import requests
from datetime import datetime, date
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Free PR distribution sites
PR_SITES = [
    {
        "name": "PR.com",
        "url": "https://www.pr.com/press-release/submit",
        "da": 68, "free": True,
        "instructions": "Register free → Submit → Indexed by Google News"
    },
    {
        "name": "PRLog",
        "url": "https://www.prlog.org/",
        "da": 72, "free": True,
        "instructions": "Create free account → Submit press release"
    },
    {
        "name": "OpenPR",
        "url": "https://www.openpr.com/",
        "da": 65, "free": True,
        "instructions": "Free submission → European + global audience"
    },
    {
        "name": "1888PressRelease",
        "url": "https://www.1888pressrelease.com/",
        "da": 58, "free": True,
        "instructions": "Free account → Distribute to 100+ sites"
    },
    {
        "name": "Free-Press-Release.com",
        "url": "https://www.free-press-release.com/",
        "da": 55, "free": True,
        "instructions": "Free tier available"
    },
    {
        "name": "PRNewswire",
        "url": "https://www.prnewswire.com/",
        "da": 94, "free": False,
        "instructions": "Paid — most powerful. $400-800 per release. Google News + AP + Reuters"
    },
    {
        "name": "BusinessWire",
        "url": "https://www.businesswire.com/",
        "da": 93, "free": False,
        "instructions": "Paid — strong for finance/tech. $475+ per release"
    },
    {
        "name": "EIN Presswire",
        "url": "https://www.einpresswire.com/",
        "da": 71, "free": False,
        "instructions": "Affordable paid — $49.95 per release. Good distribution"
    },
]


def generate_press_release(topic: str, site_name: str = "", site_url: str = "") -> str:
    """Generate a professional press release template."""
    site  = site_name or os.environ.get("SITE_NAME", "Company Name")
    url   = site_url  or os.environ.get("WP_URL", "https://yoursite.com")
    today = date.today().strftime("%B %d, %Y")

    cfg_path = os.path.join(BASE_DIR, "config", "business.json")
    email = phone = city = ""
    if os.path.exists(cfg_path):
        with open(cfg_path) as f:
            biz = json.load(f)
        email = biz.get("contact", {}).get("email", "")
        phone = biz.get("contact", {}).get("phone", "")
        city  = biz.get("contact", {}).get("address", {}).get("city", "")

    pr = f"""FOR IMMEDIATE RELEASE

**{site.upper()} ANNOUNCES {topic.upper()}**

*[Add a compelling subtitle here — one sentence expanding the headline]*

{city or "City, State"} — {today} — {site}, a leading provider of [describe what you do in your industry], today announced [what you're announcing about {topic}].

**[Opening paragraph]**
[2-3 sentences describing the announcement. What is it? Why does it matter? Who benefits?]

**[Quote from leadership]**
"[Insert a genuine quote from your CEO/founder about why this matters]," said [Name], [Title] of {site}. "[Continue the quote with specific impact or vision statement]."

**[Details paragraph]**
[Expand on the announcement. Include: key features, benefits, availability, pricing if relevant, how it works]

**[Industry context]**
[1-2 sentences about why this is relevant now. Reference a trend, statistic, or market need.]

**[Second quote or customer quote if available]**
"[Customer testimonial or analyst quote]," said [Name], [Title/Company].

**[Closing paragraph + CTA]**
{site} is committed to [your mission]. For more information, visit {url} or contact us at {email or '[email]'}.

---

**About {site}**
[2-3 sentences about your company. Founded year, what you do, who you serve, key achievement.]
Website: {url}

**Media Contact:**
[Contact Name]
{site}
Email: {email or '[email]'}
Phone: {phone or '[phone]'}
Website: {url}

###

*Note: ### signals end of press release in journalism format*
"""
    return pr


def list_distribution_sites() -> str:
    """List all PR distribution sites with details."""
    lines = [
        "# Press Release Distribution Sites",
        "",
        "## Free Sites (Start Here)",
        "",
        "| Site | DA | Instructions |",
        "|---|---|---|",
    ]
    for site in [s for s in PR_SITES if s["free"]]:
        lines.append(f"| [{site['name']}]({site['url']}) | {site['da']} | {site['instructions']} |")

    lines += ["", "## Paid Sites (Higher Impact)", "", "| Site | DA | Cost | Instructions |", "|---|---|---|---|"]
    for site in [s for s in PR_SITES if not s["free"]]:
        lines.append(f"| [{site['name']}]({site['url']}) | {site['da']} | See site | {site['instructions']} |")

    return "\n".join(lines)


if __name__ == "__main__":
    import argparse, sys
    parser = argparse.ArgumentParser(description="Claude Auto SEO — Press Release Distributor")
    parser.add_argument("--generate",    metavar="TOPIC", help="Generate press release for topic")
    parser.add_argument("--list-sites",  action="store_true", help="List all distribution sites")
    args = parser.parse_args()

    if args.generate:
        pr = generate_press_release(args.generate)
        path = os.path.join(BASE_DIR, "output", f"press-release-{date.today()}.md")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(pr)
        print(pr)
        print(f"\n✅ Saved: {path}")
        print("\nDistribute to:")
        for site in [s for s in PR_SITES if s["free"]][:3]:
            print(f"  → {site['name']}: {site['url']}")
    elif args.list_sites:
        print(list_distribution_sites())
    else:
        parser.print_help()
