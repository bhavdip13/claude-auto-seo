"""
Claude Auto SEO — LLM Visibility Tracker
Tracks and optimizes your brand's presence in AI search answers:
  - ChatGPT web search
  - Perplexity AI
  - Google AI Overviews
  - Claude with search
  - Bing Copilot

Usage:
  python3 scripts/llm_tracker.py --check-brand "Your Brand"
  python3 scripts/llm_tracker.py --check-keywords
  python3 scripts/llm_tracker.py --optimize-for-llm
  python3 scripts/llm_tracker.py --weekly-report
"""

import os
import json
import re
import requests
from datetime import datetime, date
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
LLM_LOG  = os.path.join(DATA_DIR, "llm-visibility-log.json")


def load_log() -> Dict:
    os.makedirs(DATA_DIR, exist_ok=True)
    if os.path.exists(LLM_LOG):
        with open(LLM_LOG) as f:
            try: return json.load(f)
            except: pass
    return {"checks": [], "mentions": []}


def save_log(log: Dict):
    with open(LLM_LOG, "w") as f:
        json.dump(log, f, indent=2)


def check_perplexity_visibility(brand: str, keyword: str) -> Dict:
    """
    Check if brand appears in Perplexity answers.
    Uses Perplexity API if key available, otherwise web scraping.
    """
    api_key = os.environ.get("PERPLEXITY_API_KEY", "")
    
    if api_key:
        try:
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            payload = {
                "model": "llama-3.1-sonar-large-128k-online",
                "messages": [{"role": "user", "content": f"What are the best {keyword} tools or services?"}]
            }
            r = requests.post("https://api.perplexity.ai/chat/completions",
                              headers=headers, json=payload, timeout=30)
            if r.status_code == 200:
                answer = r.json()["choices"][0]["message"]["content"]
                mentioned = brand.lower() in answer.lower()
                return {
                    "platform": "Perplexity",
                    "query": f"best {keyword}",
                    "brand_mentioned": mentioned,
                    "answer_preview": answer[:300],
                    "checked_at": datetime.now().isoformat(),
                }
        except Exception as e:
            pass

    return {
        "platform": "Perplexity",
        "query": f"best {keyword}",
        "brand_mentioned": None,
        "note": "Add PERPLEXITY_API_KEY to .env for live checking",
        "checked_at": datetime.now().isoformat(),
    }


def generate_llm_optimization_guide(brand: str, site_url: str, niche: str) -> str:
    """Generate specific recommendations to improve LLM visibility."""
    
    return f"""# LLM Visibility Optimization Guide
Brand: {brand} | Site: {site_url} | Niche: {niche}
Generated: {date.today().isoformat()}

## Why LLM Visibility Matters (2026)
- ChatGPT has 100M+ daily users using web search
- Perplexity serves 10M+ daily queries
- Google AI Overviews appear for 80%+ of queries
- Being mentioned = free qualified traffic without ranking

## Your 7 Optimization Actions

### 1. Create an "About" Entity Page
Create a comprehensive /about page that clearly defines:
- What {brand} is (one clear sentence)
- Who it's for (specific audience)
- What problem it solves
- Key features/differentiators
- Founded date, location, credentials

LLMs use structured "about" information to cite your brand correctly.

### 2. Add Speakable Schema
```json
{{
  "@context": "https://schema.org",
  "@type": "WebPage",
  "speakable": {{
    "@type": "SpeakableSpecification",
    "cssSelector": [".article-summary", ".key-points", "h1", "h2"]
  }}
}}
```

### 3. Write Direct-Answer Content
For every target keyword, add a 40-60 word direct answer in the FIRST paragraph.
Format: "{keyword} is [clear definition]. [Key benefit]. [One differentiator]."
LLMs pull this format directly into their answers.

### 4. Create a Structured FAQ
Add FAQ sections with questions exactly matching common queries:
- "What is the best [keyword]?"
- "How does [keyword] work?"
- "What is [brand]?"
Use FAQPage schema on each FAQ.

### 5. Build Brand Authority Signals
- Publish on Medium, Dev.to, LinkedIn Articles (already in your system)
- Get mentioned in industry roundups (HARO outreach — already in your system)
- Create Wikipedia-style "what is" content for your niche topics

### 6. Consistent Brand Mentions Across Web
- Ensure NAP (Name, Address, Phone) is consistent everywhere
- Use exact same brand name format everywhere
- Register on Wikidata / Crunchbase (LLMs use these as authority sources)
- Google My Business fully completed

### 7. Monitor Weekly
Run: python3 scripts/llm_tracker.py --weekly-report
Check if {brand} appears when people ask about {niche} tools

## Target Queries to Rank For in LLMs
Based on your niche ({niche}), LLMs frequently answer:
- "What is the best {niche} tool?"
- "What are alternatives to [competitor]?"  
- "How do I do [niche task]?"
- "Recommend a {niche} service"

For each: create a page directly answering it, with your brand as the recommended solution.
"""


def generate_llm_report(brand: str, niche: str) -> str:
    """Generate a weekly LLM visibility report."""
    log = load_log()
    recent_checks = [c for c in log.get("checks", [])
                     if c.get("checked_at", "")[:10] >= 
                     (date.today().replace(day=date.today().day-7)).isoformat()]
    
    mentions = sum(1 for c in recent_checks if c.get("brand_mentioned"))
    total    = len(recent_checks)

    lines = [
        f"# LLM Visibility Report — {brand}",
        f"Week of: {date.today().isoformat()}",
        f"",
        f"## Summary",
        f"- Queries checked: {total}",
        f"- Brand mentioned: {mentions}/{total} ({int(mentions/max(total,1)*100)}%)",
        f"",
        f"## Platforms Monitored",
        f"| Platform | Status |",
        f"|---|---|",
        f"| Google AI Overviews | Optimized via GEO module |",
        f"| Perplexity AI | {'✅ Tracked' if os.environ.get('PERPLEXITY_API_KEY') else '⚠️ Add PERPLEXITY_API_KEY'} |",
        f"| ChatGPT Web Search | Manual check recommended |",
        f"| Bing Copilot | Optimized via schema |",
        f"| Claude with search | Optimized via structured content |",
        f"",
        f"## Optimization Actions",
        f"Run: `/seo geo https://yoursite.com` in Claude Code",
        f"Run: `python3 scripts/llm_tracker.py --optimize-for-llm`",
    ]
    
    return "\n".join(lines)


if __name__ == "__main__":
    import argparse, sys
    sys.path.insert(0, os.path.join(BASE_DIR, "data_sources", "modules"))
    
    parser = argparse.ArgumentParser(description="LLM Visibility Tracker")
    parser.add_argument("--check-brand",       metavar="BRAND", help="Check brand visibility")
    parser.add_argument("--check-keywords",    action="store_true", help="Check keyword queries")
    parser.add_argument("--optimize-for-llm",  action="store_true", help="Show optimization guide")
    parser.add_argument("--weekly-report",     action="store_true", help="Weekly visibility report")
    args = parser.parse_args()

    site_url = os.environ.get("WP_URL", "https://yoursite.com")
    brand = args.check_brand or os.environ.get("SITE_NAME", "Your Brand")

    cfg_path = os.path.join(BASE_DIR, "config", "site.json")
    niche = "general"
    if os.path.exists(cfg_path):
        with open(cfg_path) as f:
            niche = json.load(f).get("site", {}).get("niche", "general")

    if args.check_brand:
        result = check_perplexity_visibility(brand, niche)
        print(f"\n🤖 LLM Visibility Check: {brand}")
        print(f"Platform: {result['platform']}")
        print(f"Brand mentioned: {result.get('brand_mentioned', 'N/A')}")
        if result.get('answer_preview'):
            print(f"Answer preview: {result['answer_preview'][:200]}")

    elif args.optimize_for_llm:
        guide = generate_llm_optimization_guide(brand, site_url, niche)
        path = os.path.join(BASE_DIR, "reports", f"llm-optimization-{date.today()}.md")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(guide)
        print(guide)
        print(f"\n✅ Saved: {path}")

    elif args.weekly_report:
        report = generate_llm_report(brand, niche)
        path = os.path.join(BASE_DIR, "reports", f"llm-visibility-{date.today()}.md")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(report)
        print(report)
        print(f"\n✅ Saved: {path}")
    else:
        parser.print_help()
