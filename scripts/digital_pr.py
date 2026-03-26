"""
Claude Auto SEO — Digital PR & Link Earning System
Generates REAL backlink opportunities through legitimate outreach.

This is the right way to build backlinks:
- HARO/Connectively monitoring (journalists quote you = backlinks)
- Broken link finding on competitor pages
- Resource page outreach templates
- Guest posting opportunity discovery
- Unlinked brand mention tracking

Usage:
  python3 scripts/digital_pr.py --haro-digest       # Find HARO opportunities
  python3 scripts/digital_pr.py --broken-links <url> # Find broken links to replace
  python3 scripts/digital_pr.py --generate-outreach  # Generate outreach templates
  python3 scripts/digital_pr.py --brand-mentions     # Find unlinked brand mentions
"""

import os
import re
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def find_broken_links_on_page(url: str) -> List[Dict]:
    """
    Find broken links on a competitor's resource page.
    You can then offer your content as a replacement.
    This is called the Broken Link Building strategy — 100% white-hat.
    """
    print(f"🔍 Scanning {url} for broken links...")

    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; LinkChecker/1.0)"}
        r = requests.get(url, headers=headers, timeout=15)
        html = r.text
    except Exception as e:
        return [{"error": str(e)}]

    links = re.findall(r'href=["\'](https?://[^"\']+)["\']', html)
    links = list(set(links))

    broken = []
    print(f"  Checking {len(links)} links...")

    for link in links[:50]:  # Check first 50 to be respectful
        try:
            check = requests.head(link, timeout=5, allow_redirects=True)
            if check.status_code in (404, 410, 503):
                broken.append({
                    "url": link,
                    "status": check.status_code,
                    "found_on": url,
                    "opportunity": "Contact page owner offering your content as replacement",
                })
        except Exception:
            broken.append({
                "url": link,
                "status": "timeout/error",
                "found_on": url,
                "opportunity": "Link may be broken — contact page owner",
            })

    print(f"  Found {len(broken)} potentially broken links")
    return broken


def find_resource_pages(niche: str) -> List[str]:
    """
    Find resource pages in your niche that might link to you.
    Resource pages ('Best X resources', 'Useful tools for Y') are 
    ideal for outreach — owners WANT to add good resources.
    """
    # These are search queries you'd run in Google manually
    search_queries = [
        f'"{niche}" "resources" "useful links"',
        f'"{niche}" "best tools" "resources"',
        f'"{niche}" inurl:resources',
        f'"{niche}" "helpful links" site:edu',
        f'"{niche}" "further reading"',
    ]

    return search_queries


def generate_outreach_templates(site_info: Dict = None) -> Dict:
    """Generate professional link building outreach email templates."""
    site_name = (site_info or {}).get("title", "Your Site")
    site_url  = (site_info or {}).get("url", "https://yoursite.com")
    niche     = (site_info or {}).get("niche", "your industry")

    templates = {

        "broken_link_replacement": {
            "subject": "Quick heads up — broken link on your {page_title} page",
            "body": f"""Hi {{first_name}},

I was reading your {niche} resources page and noticed the link to "{{broken_link_title}}" returns a 404 error.

I've written a comprehensive guide on the same topic that your readers might find useful: {{your_article_url}}

It covers:
• {{key_point_1}}
• {{key_point_2}}
• {{key_point_3}}

Happy to send you a summary if that would help. Either way, you may want to fix the broken link.

Best,
{{your_name}}
{site_name}"""
        },

        "resource_page_addition": {
            "subject": "Resource suggestion for your {page_title} page",
            "body": f"""Hi {{first_name}},

I came across your {{page_title}} resource page and found it really helpful.

I recently published a guide on {{topic}} that covers {{unique_angle}} — I don't see anything like it on your list.

Here's the link: {{your_article_url}}

Would it be a good fit to add? No worries either way.

Best,
{{your_name}}
{site_name}"""
        },

        "guest_post_pitch": {
            "subject": "Guest post idea for {{site_name}}: {{headline}}",
            "body": f"""Hi {{first_name}},

I'm a writer covering {niche} and I love the content you publish on {{their_site}}.

I'd like to pitch a guest post: **{{headline}}**

Here's what it would cover:
• {{outline_point_1}}
• {{outline_point_2}}
• {{outline_point_3}}

I've written for {{previous_publication_1}} and {{previous_publication_2}}. Here are two relevant samples:
• {{sample_1}}
• {{sample_2}}

Would this be a good fit?

Best,
{{your_name}}
{site_name} | {site_url}"""
        },

        "unlinked_mention": {
            "subject": "You mentioned {{site_name}} — could you add a link?",
            "body": f"""Hi {{first_name}},

I noticed you mentioned {{site_name}} in your article "{{their_article_title}}" — thank you!

If you're open to it, would you be able to add a link to {{link_url}}? It would help your readers find the resource directly.

Totally understand if not — just wanted to ask!

Best,
{{your_name}}
{site_name}"""
        },

        "haro_response": {
            "subject": "RE: {{haro_query_headline}}",
            "body": f"""Hi {{journalist_name}},

I saw your query on HARO about {{topic}}.

**My background:** {{your_credentials_in_1_sentence}}

**My answer to your question:**

{{your_expert_quote_2_to_3_sentences}}

Happy to provide more detail, a longer quote, or get on a call if helpful.

Best,
{{your_name}}
{{your_title}} at {site_name}
{{phone_number}}
{site_url}"""
        },
    }

    return templates


def find_unlinked_mentions(brand_name: str, domain: str) -> List[str]:
    """
    Generate search queries to find unlinked brand mentions.
    You run these in Google and contact sites to ask for a link.
    """
    queries = [
        f'"{brand_name}" -site:{domain} -site:twitter.com -site:facebook.com',
        f'"{brand_name}" review -site:{domain}',
        f'"{brand_name}" recommended -site:{domain}',
        f'"{brand_name}" mentioned -site:{domain}',
    ]
    return queries


def generate_haro_opportunities(niche: str) -> List[Dict]:
    """
    HARO (Help A Reporter Out) / Connectively opportunities.
    Journalists quote experts = you get a backlink from a news site.
    """
    instructions = {
        "service": "Connectively (formerly HARO)",
        "url": "https://www.connectively.us",
        "how_to_use": [
            "1. Sign up FREE at connectively.us as a 'Source'",
            "2. Select your expertise category (matches your niche)",
            "3. Receive daily emails with journalist queries",
            "4. Respond within hours to relevant queries",
            "5. Journalists cite you with a backlink from their publication",
        ],
        "what_to_watch_for": [
            f"Queries about {niche} tools/strategies",
            f"Queries asking for expert tips on {niche}",
            f"Queries about trends in {niche}",
            "Queries asking 'what's the best approach to...'",
            "Queries for personal experience/case studies",
        ],
        "response_tips": [
            "Respond within 2 hours (journalists work fast)",
            "Lead with your credentials",
            "Give a quotable 2-3 sentence answer",
            "Keep it under 200 words total",
            "Include your name, title, and website URL",
        ],
        "typical_results": "1-3 DA 50+ backlinks per month with consistent effort",
    }

    return instructions


def generate_pr_report(site_info: Dict = None) -> str:
    """Generate a complete digital PR action plan."""
    niche     = (site_info or {}).get("niche", "your industry")
    site_name = (site_info or {}).get("title", "Your Site")
    site_url  = (site_info or {}).get("url", "https://yoursite.com")

    report = f"""# Digital PR & Link Building Strategy
Site: {site_name} ({site_url})
Generated: {datetime.now().strftime('%Y-%m-%d')}

---

## Why This Approach

Real backlinks come from real value. These strategies work because:
- They provide genuine value to the linking site and their readers
- They pass full link equity (unlike spam links which Google ignores)
- They build real relationships in your industry
- They create compounding returns over time
- Google actively rewards these and penalizes the alternatives

---

## Strategy 1: HARO / Connectively (Easiest Wins)

**What it is:** Journalists query experts → You respond → They cite you with backlink
**Typical DA:** 50-90 (news sites, major publications)
**Time required:** 30 min/day monitoring + quick responses
**Setup:** Free account at connectively.us

### Your {niche.title()} Topics to Watch For:
{chr(10).join(f'- {t}' for t in generate_haro_opportunities(niche)['what_to_watch_for'])}

**Response Template:** See `reports/outreach-templates-[date].md`

---

## Strategy 2: Broken Link Building

**What it is:** Find broken links on resource pages → offer your content as replacement
**Typical DA:** Varies (whatever the page has)
**Time required:** 2-3 hours per target page
**Conversion rate:** 5-15% of emails sent

### Run This Search in Google:
```
{niche} "resources" OR "helpful links" OR "useful tools"
```
Then run: `python3 scripts/digital_pr.py --broken-links <resource-page-url>`

---

## Strategy 3: Guest Posting

**What it is:** Write a guest article for another site → get author bio backlink
**Typical DA:** 40-80+ (authority sites in your niche)
**Time required:** 3-5 hours per article

### How to Find Guest Post Opportunities:
```
"{niche}" "write for us"
"{niche}" "guest post guidelines"
"{niche}" "contribute"
"{niche}" "submit article"
```

---

## Strategy 4: Unlinked Brand Mentions

**What it is:** Sites mention your brand but don't link → ask them to add a link
**Typical DA:** Varies
**Conversion rate:** 20-40% (they already like you!)

### Search for Your Mentions:
{chr(10).join(f'`{q}`' for q in find_unlinked_mentions(site_name, site_url))}

---

## Strategy 5: Create Linkable Assets

**What it is:** Publish data, tools, or resources so good that people link naturally
**Types:**
- Original research / surveys ("We surveyed 500 {niche} professionals...")
- Free tools (calculators, generators, analyzers)
- Comprehensive data studies
- Original infographics
- Industry reports

**These earn backlinks on autopilot once published.**

---

## 90-Day Action Plan

### Month 1: Foundation
- [ ] Sign up for HARO/Connectively
- [ ] Submit to all Tier 1 directories (see directory_manager.py)
- [ ] Find 10 resource pages in your niche
- [ ] Write outreach emails for top 5

### Month 2: Scale
- [ ] Respond to HARO daily
- [ ] Complete Tier 2 directory submissions
- [ ] Find broken link opportunities on 5 competitor pages
- [ ] Identify 3 guest post targets

### Month 3: Growth
- [ ] Publish 1 original research piece
- [ ] Complete guest post outreach
- [ ] Track brand mentions weekly
- [ ] Submit to Tier 3 directories

---

## Expected Results

| Month | New Backlinks | DA Range | Traffic Impact |
|---|---|---|---|
| 1 | 3-8 | 40-100 | Baseline |
| 2 | 8-15 | 40-90 | +5-15% |
| 3 | 15-25 | 40-90 | +15-30% |
| 6 | 40-80 | varies | +30-80% |

*Results vary based on niche competitiveness and effort.*
"""
    return report


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Claude Auto SEO — Digital PR System")
    parser.add_argument("--broken-links",    metavar="URL", help="Find broken links on a page")
    parser.add_argument("--generate-outreach", action="store_true", help="Generate outreach templates")
    parser.add_argument("--brand-mentions",  metavar="BRAND", help="Find unlinked brand mentions")
    parser.add_argument("--pr-report",       action="store_true", help="Generate full PR strategy report")
    parser.add_argument("--haro-setup",      action="store_true", help="HARO setup guide")
    args = parser.parse_args()

    if args.broken_links:
        broken = find_broken_links_on_page(args.broken_links)
        print(f"\nBroken links found: {len(broken)}")
        for b in broken:
            print(f"  {b['status']} — {b['url']}")

    elif args.generate_outreach:
        templates = generate_outreach_templates()
        path = os.path.join(BASE_DIR, "reports", f"outreach-templates-{datetime.now().strftime('%Y%m%d')}.md")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write("# Link Building Outreach Templates\n\n")
            for name, t in templates.items():
                f.write(f"## {name.replace('_', ' ').title()}\n")
                f.write(f"**Subject:** {t['subject']}\n\n")
                f.write(f"```\n{t['body']}\n```\n\n---\n\n")
        print(f"✅ Templates saved: {path}")

    elif args.brand_mentions:
        queries = find_unlinked_mentions(args.brand_mentions, "")
        print(f"\nSearch these in Google to find unlinked mentions of '{args.brand_mentions}':")
        for q in queries:
            print(f"  {q}")

    elif args.pr_report:
        report = generate_pr_report()
        path = os.path.join(BASE_DIR, "reports", f"digital-pr-strategy-{datetime.now().strftime('%Y%m%d')}.md")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(report)
        print(f"✅ PR Strategy report saved: {path}")
        print(report[:3000])

    elif args.haro_setup:
        guide = generate_haro_opportunities("your niche")
        print("\nHARO / Connectively Setup Guide:")
        for step in guide["how_to_use"]:
            print(f"  {step}")

    else:
        parser.print_help()
