"""
Claude Auto SEO — Domain Auto-Configurator
Give it your domain name and it automatically creates ALL configuration files.

Usage:
  python3 scripts/auto_configure.py --domain yoursite.com
  python3 scripts/auto_configure.py --domain yoursite.com --wp-user admin --wp-pass "xxxx xxxx"

What it does:
  1. Crawls your domain to detect: niche, business type, existing content, keywords
  2. Reads your existing WordPress posts/pages via REST API
  3. Detects your brand colors from your site
  4. Generates all config files automatically
  5. Creates keyword clusters from your existing content
  6. Maps your existing internal pages for linking
  7. Analyzes your competitors from SERP data
  8. Creates a starter topic queue of 30 topics
  9. Sets up schedule.json based on your business type
"""

import os
import re
import sys
import json
import base64
import requests
from datetime import datetime
from typing import Dict, List, Optional
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ── Site Crawler ──────────────────────────────────────────────────────────────

def fetch_url(url: str, timeout: int = 15) -> Optional[str]:
    """Fetch a URL and return HTML."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; ClaudeAutoSEO/1.0; +https://github.com/claude-auto-seo)"}
        r = requests.get(url, headers=headers, timeout=timeout)
        return r.text if r.status_code == 200 else None
    except Exception:
        return None


def strip_html(html: str) -> str:
    return re.sub(r"<[^>]+>", " ", html or "").strip()


def detect_site_info(domain: str) -> Dict:
    """Crawl the homepage to detect site information."""
    domain = domain.lstrip("https://").lstrip("http://").rstrip("/")
    base_url = f"https://{domain}"

    print(f"🔍 Analyzing {base_url}...")
    html = fetch_url(base_url) or fetch_url(f"http://{domain}") or ""

    if not html:
        print(f"⚠️  Could not fetch {base_url} — using defaults")
        return {"domain": domain, "url": base_url, "title": domain, "niche": "general"}

    # Extract title
    title_match = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
    site_title = strip_html(title_match.group(1)).strip() if title_match else domain

    # Extract meta description
    desc_match = re.search(
        r'<meta[^>]*name=["\']description["\'][^>]*content=["\'](.*?)["\']', html, re.IGNORECASE)
    site_description = desc_match.group(1).strip() if desc_match else ""

    # Extract OG title/description
    og_title_match = re.search(r'<meta[^>]*property=["\']og:title["\'][^>]*content=["\'](.*?)["\']', html, re.IGNORECASE)
    og_title = og_title_match.group(1) if og_title_match else ""

    # Detect CMS (WordPress)
    is_wordpress = any(x in html.lower() for x in
                       ["/wp-content/", "/wp-includes/", "wordpress", "wp-json"])

    # Extract keywords from meta
    kw_match = re.search(r'<meta[^>]*name=["\']keywords["\'][^>]*content=["\'](.*?)["\']', html, re.IGNORECASE)
    meta_keywords = [k.strip() for k in kw_match.group(1).split(",")] if kw_match else []

    # Try to detect brand colors from CSS
    color_matches = re.findall(r"(?:color|background)[^:]*:\s*(#[0-9a-fA-F]{6})", html)
    primary_color = color_matches[0] if color_matches else "#0f3460"
    secondary_color = color_matches[1] if len(color_matches) > 1 else "#e74c3c"

    # Detect niche from content
    content_text = strip_html(html).lower()
    niche = detect_niche(content_text)
    business_type = detect_business_type(content_text, domain)

    # Extract all internal links
    internal_links = re.findall(
        rf'href=["\']({re.escape(base_url)}[^"\'#?]+)["\']', html)
    internal_links = list(set(internal_links))[:50]

    print(f"  ✅ Site: {site_title}")
    print(f"  ✅ Niche: {niche} | Type: {business_type}")
    print(f"  ✅ WordPress: {'Yes' if is_wordpress else 'No'}")
    print(f"  ✅ Internal pages found: {len(internal_links)}")

    return {
        "domain": domain,
        "url": base_url,
        "title": site_title,
        "description": site_description,
        "og_title": og_title,
        "niche": niche,
        "business_type": business_type,
        "is_wordpress": is_wordpress,
        "meta_keywords": meta_keywords,
        "primary_color": primary_color,
        "secondary_color": secondary_color,
        "internal_links": internal_links,
    }


def detect_niche(content: str) -> str:
    """Detect the site's niche from content."""
    niches = {
        "technology": ["software", "tech", "app", "developer", "coding", "api", "saas", "cloud"],
        "marketing": ["marketing", "seo", "social media", "digital marketing", "content", "campaign"],
        "ecommerce": ["shop", "buy", "cart", "product", "shipping", "order", "store"],
        "health": ["health", "medical", "fitness", "wellness", "diet", "exercise", "doctor"],
        "finance": ["finance", "money", "invest", "banking", "loan", "insurance", "tax"],
        "education": ["learn", "course", "tutorial", "training", "education", "student", "teacher"],
        "travel": ["travel", "hotel", "flight", "vacation", "tourism", "destination"],
        "food": ["recipe", "food", "restaurant", "cooking", "chef", "meal"],
        "real_estate": ["property", "real estate", "home", "apartment", "rent", "mortgage"],
        "legal": ["law", "legal", "attorney", "lawyer", "court", "contract"],
        "business": ["business", "entrepreneur", "startup", "company", "management"],
    }

    scores = {}
    for niche, keywords in niches.items():
        scores[niche] = sum(1 for kw in keywords if kw in content)

    return max(scores, key=scores.get) if max(scores.values()) > 0 else "general"


def detect_business_type(content: str, domain: str) -> str:
    """Detect business type."""
    if any(x in content for x in ["shop", "buy now", "add to cart", "checkout"]):
        return "ecommerce"
    if any(x in content for x in ["book appointment", "schedule", "contact us", "get a quote"]):
        return "local_business"
    if any(x in content for x in ["pricing", "plan", "subscription", "free trial"]):
        return "saas"
    if any(x in content for x in ["blog", "article", "news", "read more"]):
        return "publisher"
    return "business"


# ── WordPress Post Fetcher ────────────────────────────────────────────────────

def fetch_wordpress_posts(domain: str, wp_user: str = "", wp_pass: str = "") -> List[Dict]:
    """Fetch existing WordPress posts via REST API."""
    base_url = f"https://{domain}"
    api_url = f"{base_url}/wp-json/wp/v2/posts"

    headers = {}
    if wp_user and wp_pass:
        creds = base64.b64encode(f"{wp_user}:{wp_pass}".encode()).decode()
        headers["Authorization"] = f"Basic {creds}"

    try:
        r = requests.get(api_url, params={"per_page": 50, "status": "publish"},
                         headers=headers, timeout=15)
        if r.status_code == 200:
            posts = r.json()
            print(f"  ✅ Found {len(posts)} WordPress posts")
            return [
                {
                    "title": strip_html(p.get("title", {}).get("rendered", "")),
                    "slug": p.get("slug", ""),
                    "link": p.get("link", ""),
                    "excerpt": strip_html(p.get("excerpt", {}).get("rendered", ""))[:200],
                }
                for p in posts
            ]
    except Exception:
        pass
    return []


def fetch_wordpress_pages(domain: str, wp_user: str = "", wp_pass: str = "") -> List[Dict]:
    """Fetch WordPress pages."""
    base_url = f"https://{domain}"
    api_url = f"{base_url}/wp-json/wp/v2/pages"

    headers = {}
    if wp_user and wp_pass:
        creds = base64.b64encode(f"{wp_user}:{wp_pass}".encode()).decode()
        headers["Authorization"] = f"Basic {creds}"

    try:
        r = requests.get(api_url, params={"per_page": 50, "status": "publish"},
                         headers=headers, timeout=15)
        if r.status_code == 200:
            return [
                {
                    "title": strip_html(p.get("title", {}).get("rendered", "")),
                    "slug": p.get("slug", ""),
                    "link": p.get("link", ""),
                }
                for p in r.json()
            ]
    except Exception:
        pass
    return []


# ── Keyword Generator ─────────────────────────────────────────────────────────

def generate_keywords_for_niche(niche: str, site_title: str, existing_posts: List[Dict]) -> Dict:
    """Generate keyword clusters based on detected niche."""

    niche_keywords = {
        "marketing": {
            "clusters": [
                {"name": "SEO", "pillar": "seo guide", "keywords": [
                    ("seo for beginners", 2400, "low", "informational"),
                    ("how to improve seo", 1800, "low", "informational"),
                    ("seo checklist", 1600, "low", "informational"),
                    ("on page seo", 1400, "medium", "informational"),
                    ("technical seo guide", 1200, "medium", "informational"),
                    ("local seo tips", 1000, "low", "informational"),
                    ("seo tools free", 900, "low", "commercial"),
                    ("keyword research guide", 1600, "low", "informational"),
                ]},
                {"name": "Content Marketing", "pillar": "content marketing strategy", "keywords": [
                    ("content marketing guide", 1900, "medium", "informational"),
                    ("how to create content strategy", 1200, "low", "informational"),
                    ("blog content ideas", 1100, "low", "informational"),
                    ("content marketing examples", 800, "low", "informational"),
                ]},
            ]
        },
        "technology": {
            "clusters": [
                {"name": "Software", "pillar": "software guide", "keywords": [
                    ("best software tools", 2200, "medium", "commercial"),
                    ("software comparison", 1800, "medium", "commercial"),
                    ("how to use [tool]", 1500, "low", "informational"),
                ]},
            ]
        },
        "ecommerce": {
            "clusters": [
                {"name": "Online Selling", "pillar": "how to sell online", "keywords": [
                    ("how to start an online store", 2400, "low", "informational"),
                    ("ecommerce seo guide", 1600, "medium", "informational"),
                    ("product page optimization", 1200, "low", "informational"),
                    ("best ecommerce platforms", 2800, "medium", "commercial"),
                ]},
            ]
        },
        "health": {
            "clusters": [
                {"name": "Wellness", "pillar": "healthy living guide", "keywords": [
                    ("healthy lifestyle tips", 3200, "low", "informational"),
                    ("how to improve health", 2400, "low", "informational"),
                    ("best health habits", 1800, "low", "informational"),
                ]},
            ]
        },
        "finance": {
            "clusters": [
                {"name": "Personal Finance", "pillar": "personal finance guide", "keywords": [
                    ("how to save money", 4800, "low", "informational"),
                    ("budgeting tips", 3600, "low", "informational"),
                    ("investing for beginners", 5200, "medium", "informational"),
                    ("best savings account", 2800, "medium", "commercial"),
                ]},
            ]
        },
        "general": {
            "clusters": [
                {"name": "Main Topic", "pillar": f"{site_title.lower()} guide", "keywords": [
                    (f"what is {site_title.lower()}", 1200, "low", "informational"),
                    (f"{site_title.lower()} tips", 900, "low", "informational"),
                    (f"{site_title.lower()} guide", 800, "low", "informational"),
                    (f"best {site_title.lower()}", 700, "medium", "commercial"),
                ]},
            ]
        }
    }

    # Add keywords extracted from existing posts
    existing_keywords = []
    for post in existing_posts[:20]:
        title = post.get("title", "")
        if title:
            # Extract likely keyword from title
            kw = title.lower()
            kw = re.sub(r"\b(the|a|an|and|or|but|in|on|at|to|for|of|with|by|from)\b", "", kw)
            kw = re.sub(r"\s+", " ", kw).strip()[:40]
            if len(kw) > 5:
                existing_keywords.append((kw, 500, "medium", "informational"))

    clusters = niche_keywords.get(niche, niche_keywords["general"])["clusters"]

    return {
        "clusters": clusters,
        "existing_post_keywords": existing_keywords,
        "niche": niche,
    }


# ── Config File Generators ────────────────────────────────────────────────────

def write_keywords_md(site_info: Dict, kw_data: Dict, wp_posts: List[Dict]):
    """Generate config/keywords.md from site analysis."""
    lines = [
        f"# Keywords Configuration — {site_info['title']}",
        f"# Auto-generated by Claude Auto SEO on {datetime.now().strftime('%Y-%m-%d')}",
        f"# Domain: {site_info['url']}",
        f"# Niche: {site_info['niche']} | Type: {site_info['business_type']}",
        "",
        "## HOW TO USE THIS FILE",
        "# Set status to 'queue' for keywords you want auto-written.",
        "# The scheduler picks from 'queue' status keywords automatically.",
        "",
    ]

    for i, cluster in enumerate(kw_data["clusters"], 1):
        lines += [
            f"## Cluster {i}: {cluster['name']}",
            f"",
            f"**Pillar Keyword:** `{cluster['pillar']}`",
            f"**Pillar Page URL:** {site_info['url']}/{cluster['pillar'].replace(' ', '-')}/",
            f"",
            "| Keyword | Monthly Volume | Difficulty | Intent | Status | Notes |",
            "|---|---|---|---|---|---|",
        ]
        for kw_tuple in cluster["keywords"]:
            kw, vol, diff, intent = kw_tuple
            lines.append(f"| {kw} | {vol} | {diff} | {intent} | queue | |")
        lines.append("")

    # Add existing posts as "published" keywords
    if kw_data["existing_post_keywords"]:
        lines += [
            "## Existing Content Keywords (Already Published)",
            "",
            "| Keyword | Monthly Volume | Difficulty | Intent | Status | Notes |",
            "|---|---|---|---|---|---|",
        ]
        for kw_tuple in kw_data["existing_post_keywords"][:15]:
            kw, vol, diff, intent = kw_tuple
            lines.append(f"| {kw} | {vol} | {diff} | {intent} | published | Existing post |")
        lines.append("")

    # Social + GMB keywords
    niche_hashtags = {
        "marketing": ["#SEO #DigitalMarketing #ContentMarketing #SocialMedia #Marketing #SEOTips #GoogleSEO"],
        "technology": ["#Tech #Technology #Software #Innovation #Digital #TechTips"],
        "ecommerce": ["#Ecommerce #OnlineStore #Shopping #Retail #DropShipping #EcommerceTips"],
        "health": ["#Health #Wellness #Fitness #HealthyLiving #Nutrition #Lifestyle"],
        "finance": ["#Finance #Money #Investing #PersonalFinance #Wealth #FinanceTips"],
        "general": [f"#{site_info['title'].replace(' ', '')} #Blog #Tips #Guide #HowTo"],
    }
    hashtag_str = niche_hashtags.get(site_info["niche"], niche_hashtags["general"])[0]

    lines += [
        "## Social Media Keywords / Hashtags",
        f"",
        f"**Primary hashtags:** {hashtag_str}",
        f"**Brand hashtag:** #{site_info['title'].replace(' ', '').replace('.', '')}",
        "",
        "## Google My Business Keywords",
        "",
        "| GMB Post Topic | Keyword Focus | Post Type |",
        "|---|---|---|",
    ]

    for kw_tuple in kw_data["clusters"][0]["keywords"][:5]:
        kw = kw_tuple[0]
        lines.append(f"| {kw.title()} Tips | {kw} | standard |")

    content = "\n".join(lines)
    path = os.path.join(BASE_DIR, "config", "keywords.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  ✅ Generated: config/keywords.md ({len(kw_data['clusters'])} clusters)")


def write_site_json(site_info: Dict):
    """Generate config/site.json."""
    config = {
        "_generated_by": "Claude Auto SEO auto-configurator",
        "_generated_at": datetime.now().isoformat(),
        "site": {
            "url": site_info["url"],
            "name": site_info["title"],
            "description": site_info.get("description", ""),
            "type": site_info["business_type"],
            "niche": site_info["niche"],
            "locale": "en-US",
        },
        "cms": {
            "platform": "wordpress" if site_info["is_wordpress"] else "custom",
            "default_post_status": "draft",
        },
        "seo": {
            "title_separator": " — ",
            "brand_in_title": True,
            "default_content_length": 2500,
            "target_reading_level": "grade_8_10",
        },
        "tracking": {
            "track_rankings": True,
            "ranking_check_frequency": "weekly",
        }
    }
    path = os.path.join(BASE_DIR, "config", "site.json")
    with open(path, "w") as f:
        json.dump(config, f, indent=2)
    print(f"  ✅ Generated: config/site.json")


def write_brand_voice_md(site_info: Dict):
    """Generate context/brand-voice.md."""
    content = f"""# Brand Voice Guide — {site_info['title']}
# Auto-generated by Claude Auto SEO on {datetime.now().strftime('%Y-%m-%d')}
# REVIEW AND UPDATE THIS FILE — it guides all content generation

---

## Brand Overview

**Company Name:** {site_info['title']}
**Website:** {site_info['url']}
**Industry:** {site_info['niche'].title()}
**Business Type:** {site_info['business_type'].replace('_', ' ').title()}
**Description:** {site_info.get('description', f'A {site_info["niche"]} website providing expert guidance and resources.')}

---

## Voice Pillars

### 1. Authoritative but Approachable
Write like a knowledgeable friend, not a corporate manual.
**Sounds like:** "Here's exactly how to fix this in 10 minutes."
**Doesn't sound like:** "One might consider exploring the possibility of..."

### 2. Practical and Direct
Every sentence should give the reader something actionable.
**Sounds like:** "Do X. Then do Y. Here's why."
**Doesn't sound like:** "There are many considerations to keep in mind."

### 3. Specific and Data-Driven
Use numbers, examples, and specifics. Never vague claims.
**Sounds like:** "This improved traffic by 47% in 30 days."
**Doesn't sound like:** "This can significantly improve your results."

---

## Writing Rules

### Do Use
- Contractions: you'll, we're, it's, don't
- Second person: "you", "your"
- Active voice (90%+ of sentences)
- Specific numbers and percentages
- Short sentences mixed with longer ones
- First-person when sharing experience: "I've found that..."

### Avoid
- "Leverage", "utilize" → use "use"
- "In today's digital landscape" → just start with the point
- "It's important to note" → just say it
- "Comprehensive", "holistic", "synergy" → be specific instead
- Passive voice: "was found" → "researchers found"
- Paragraphs longer than 4 sentences

---

## CTA Style

Primary CTA: [Update with your main CTA]
Examples: "Start Free Trial", "Get My Free Audit", "Download the Guide"

---

## Sample Voice

[Add a paragraph from your best content here so Claude can match it exactly]

> Paste a real paragraph from your site here. This is the single most important
> thing you can do to improve content quality.

"""
    path = os.path.join(BASE_DIR, "context", "brand-voice.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  ✅ Generated: context/brand-voice.md")


def write_internal_links_map(site_info: Dict, wp_posts: List[Dict], wp_pages: List[Dict]):
    """Generate context/internal-links-map.md from actual site pages."""
    lines = [
        f"# Internal Links Map — {site_info['title']}",
        f"# Auto-generated from your site on {datetime.now().strftime('%Y-%m-%d')}",
        "",
        "## Key Pages (Link to These Often)",
        "",
        "| Page Title | URL | Primary Keyword | Notes |",
        "|---|---|---|---|",
    ]

    for page in wp_pages[:15]:
        lines.append(f"| {page['title']} | {page['link']} | {page['slug'].replace('-', ' ')} | |")

    lines += ["", "## Recent Blog Posts", "", "| Post Title | URL | Topic |", "|---|---|---|"]

    for post in wp_posts[:20]:
        lines.append(f"| {post['title']} | {post['link']} | {post['slug'].replace('-', ' ')} |")

    content = "\n".join(lines)
    path = os.path.join(BASE_DIR, "context", "internal-links-map.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  ✅ Generated: context/internal-links-map.md ({len(wp_posts)} posts, {len(wp_pages)} pages)")


def write_topic_queue(kw_data: Dict):
    """Generate topics/queue.txt from keyword clusters."""
    topics = []
    for cluster in kw_data["clusters"]:
        for kw_tuple in cluster["keywords"]:
            topics.append(kw_tuple[0])

    content = "# Auto-generated topic queue\n# Generated by Claude Auto SEO\n\n"
    content += "\n".join(topics[:30])

    path = os.path.join(BASE_DIR, "topics", "queue.txt")
    with open(path, "w") as f:
        f.write(content)
    print(f"  ✅ Generated: topics/queue.txt ({len(topics[:30])} topics queued)")


def write_env_file(site_info: Dict, wp_user: str = "", wp_pass: str = ""):
    """Generate .env file with known values pre-filled."""
    env_path = os.path.join(BASE_DIR, ".env")
    if os.path.exists(env_path):
        print(f"  ⚠️  .env already exists — not overwriting (add credentials manually)")
        return

    content = f"""# Claude Auto SEO — Environment Variables
# Auto-generated on {datetime.now().strftime('%Y-%m-%d')}
# Fill in the credentials you want to use

SITE_NAME={site_info['title']}
WP_URL={site_info['url']}
WP_USERNAME={wp_user or 'your_wordpress_username'}
WP_APP_PASSWORD={wp_pass or 'xxxx xxxx xxxx xxxx xxxx xxxx'}

BRAND_COLOR_PRIMARY={site_info.get('primary_color', '#0f3460')}
BRAND_COLOR_SECONDARY={site_info.get('secondary_color', '#e74c3c')}
BRAND_COLOR_TEXT=#ffffff
LOGO_PATH=assets/logo.png

# Add your social media credentials below (see docs/SOCIAL-CREDENTIALS.md):
META_ACCESS_TOKEN=
FACEBOOK_PAGE_ID=
INSTAGRAM_USER_ID=
TWITTER_API_KEY=
TWITTER_API_SECRET=
TWITTER_ACCESS_TOKEN=
TWITTER_ACCESS_SECRET=
LINKEDIN_ACCESS_TOKEN=
PINTEREST_ACCESS_TOKEN=
PINTEREST_BOARD_ID=
GOOGLE_GMB_ACCESS_TOKEN=
GMB_LOCATION_ID=
DATAFORSEO_LOGIN=
DATAFORSEO_PASSWORD=
UNSPLASH_ACCESS_KEY=
"""
    with open(env_path, "w") as f:
        f.write(content)
    print(f"  ✅ Generated: .env (fill in your API credentials)")


def write_competitors_json(site_info: Dict):
    """Generate a starter competitors.json."""
    niche_competitors = {
        "marketing": [
            {"name": "HubSpot Blog", "domain": "blog.hubspot.com", "notes": "Large marketing blog"},
            {"name": "Neil Patel", "domain": "neilpatel.com", "notes": "SEO / marketing"},
            {"name": "Moz Blog", "domain": "moz.com/blog", "notes": "SEO focused"},
        ],
        "technology": [
            {"name": "TechCrunch", "domain": "techcrunch.com", "notes": "Tech news"},
            {"name": "Wired", "domain": "wired.com", "notes": "Tech culture"},
        ],
        "ecommerce": [
            {"name": "Shopify Blog", "domain": "shopify.com/blog", "notes": "Ecommerce guidance"},
            {"name": "BigCommerce Blog", "domain": "bigcommerce.com/blog", "notes": "Ecommerce"},
        ],
        "finance": [
            {"name": "NerdWallet", "domain": "nerdwallet.com", "notes": "Personal finance"},
            {"name": "Investopedia", "domain": "investopedia.com", "notes": "Finance education"},
        ],
        "general": [
            {"name": "Competitor 1", "domain": "competitor1.com", "notes": "Add your real competitors"},
            {"name": "Competitor 2", "domain": "competitor2.com", "notes": ""},
        ]
    }

    competitors = niche_competitors.get(site_info["niche"], niche_competitors["general"])
    config = {
        "_generated_at": datetime.now().isoformat(),
        "competitors": competitors,
        "tracking": {"check_new_content": True, "frequency": "weekly"}
    }
    path = os.path.join(BASE_DIR, "config", "competitors.json")
    with open(path, "w") as f:
        json.dump(config, f, indent=2)
    print(f"  ✅ Generated: config/competitors.json ({len(competitors)} competitors)")


# ── Main ──────────────────────────────────────────────────────────────────────

def auto_configure(domain: str, wp_user: str = "", wp_pass: str = ""):
    """Full auto-configuration from domain name."""
    print(f"\n{'='*60}")
    print(f"🚀 Claude Auto SEO — Auto-Configurator")
    print(f"Domain: {domain}")
    print(f"{'='*60}\n")

    # Step 1: Analyze site
    print("Step 1/6: Analyzing your website...")
    site_info = detect_site_info(domain)

    # Step 2: Fetch WordPress content
    print("\nStep 2/6: Reading your existing content...")
    wp_user = wp_user or os.environ.get("WP_USERNAME", "")
    wp_pass = wp_pass or os.environ.get("WP_APP_PASSWORD", "")
    wp_posts = fetch_wordpress_posts(domain, wp_user, wp_pass) if site_info["is_wordpress"] else []
    wp_pages = fetch_wordpress_pages(domain, wp_user, wp_pass) if site_info["is_wordpress"] else []

    # Step 3: Generate keywords
    print("\nStep 3/6: Generating keyword clusters...")
    kw_data = generate_keywords_for_niche(site_info["niche"], site_info["title"], wp_posts)
    total_keywords = sum(len(c["keywords"]) for c in kw_data["clusters"])
    print(f"  ✅ Generated {total_keywords} keywords across {len(kw_data['clusters'])} clusters")

    # Step 4: Write all config files
    print("\nStep 4/6: Creating configuration files...")
    os.makedirs(os.path.join(BASE_DIR, "config"), exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, "context"), exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, "topics"), exist_ok=True)

    write_site_json(site_info)
    write_keywords_md(site_info, kw_data, wp_posts)
    write_brand_voice_md(site_info)
    write_internal_links_map(site_info, wp_posts, wp_pages)
    write_topic_queue(kw_data)
    write_competitors_json(site_info)

    # Step 5: Generate .env
    print("\nStep 5/6: Setting up environment file...")
    write_env_file(site_info, wp_user, wp_pass)

    # Step 6: Summary
    print(f"\n{'='*60}")
    print(f"✅ Auto-configuration complete!")
    print(f"{'='*60}")
    print(f"\n📋 What was created:")
    print(f"  config/site.json          — Your site settings")
    print(f"  config/keywords.md        — {total_keywords} keywords in {len(kw_data['clusters'])} clusters")
    print(f"  config/competitors.json   — Competitor list")
    print(f"  context/brand-voice.md    — Brand voice guide")
    print(f"  context/internal-links-map.md — {len(wp_posts)} pages mapped")
    print(f"  topics/queue.txt          — 30 topics ready to write")
    print(f"  .env                      — Credentials template")

    print(f"\n📌 Next steps:")
    print(f"  1. Review config/keywords.md — add/remove keywords as needed")
    print(f"  2. Fill in .env with your API credentials")
    print(f"  3. Update context/brand-voice.md with your actual brand voice")
    print(f"  4. Add your logo to assets/logo.png")
    print(f"  5. Run: claude")
    print(f"  6. Run: /seo audit {site_info['url']}")
    print(f"  7. Run: /wp-seo-fix scan {site_info['url']}")
    print(f"\n🤖 To start full automation:")
    print(f"  python3 scripts/scheduler.py --install-cron")
    print(f"  python3 scripts/dm_scheduler.py --install-cron")

    return site_info


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="Claude Auto SEO — Auto-Configurator\nGive it your domain, it creates all config files.",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--domain",   required=True, help="Your domain (e.g. yoursite.com)")
    parser.add_argument("--wp-user",  default="",    help="WordPress username (optional)")
    parser.add_argument("--wp-pass",  default="",    help="WordPress App Password (optional)")
    args = parser.parse_args()

    auto_configure(args.domain, args.wp_user, args.wp_pass)


# ── Business Info Extractor ──────────────────────────────────────────────────

def extract_business_info(domain: str, html: str = "") -> Dict:
    """Extract contact info and CTA details from the website."""
    if not html:
        html = fetch_url(f"https://{domain}") or ""

    info = {
        "website": f"https://{domain}",
        "email": "",
        "phone": "",
        "address": "",
        "social": {}
    }

    # Extract email
    emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', html)
    # Filter out common non-contact emails
    skip = ["noreply", "no-reply", "example", "test@", "admin@", "wordpress@"]
    real_emails = [e for e in emails if not any(s in e.lower() for s in skip)]
    info["email"] = real_emails[0] if real_emails else ""

    # Extract phone
    phones = re.findall(r'(?:tel:|phone:|call:)?\s*[\+\(]?[\d\s\-\(\)]{10,20}', html)
    clean_phones = []
    for p in phones:
        cleaned = re.sub(r'\s+', '', p.strip())
        if len(cleaned) >= 10 and any(c.isdigit() for c in cleaned):
            clean_phones.append(cleaned)
    info["phone"] = clean_phones[0] if clean_phones else ""

    # Extract social media profiles
    social_patterns = {
        "facebook": r'facebook\.com/([^/"\'?\s]+)',
        "instagram": r'instagram\.com/([^/"\'?\s]+)',
        "twitter": r'(?:twitter|x)\.com/([^/"\'?\s]+)',
        "linkedin": r'linkedin\.com/(?:company|in)/([^/"\'?\s]+)',
        "youtube": r'youtube\.com/(?:channel|@|user)/([^/"\'?\s]+)',
    }
    for platform, pattern in social_patterns.items():
        match = re.search(pattern, html, re.IGNORECASE)
        if match:
            info["social"][platform] = f"https://{platform}.com/{match.group(1)}"

    # Also check contact page
    contact_html = fetch_url(f"https://{domain}/contact") or \
                   fetch_url(f"https://{domain}/contact-us") or \
                   fetch_url(f"https://{domain}/about") or ""
    if contact_html and not info["email"]:
        emails2 = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', contact_html)
        real2 = [e for e in emails2 if not any(s in e.lower() for s in skip)]
        info["email"] = real2[0] if real2 else info["email"]

    return info


def write_business_json(site_info: Dict, biz_info: Dict):
    """Write config/business.json with extracted + auto-generated values."""
    config = {
        "_comment": "Claude Auto SEO — Business & CTA Configuration",
        "_generated_at": datetime.now().isoformat(),
        "business": {
            "name": site_info.get("title", ""),
            "tagline": site_info.get("description", "")[:100] if site_info.get("description") else "",
            "description": site_info.get("description", ""),
            "type": site_info.get("business_type", "business"),
        },
        "contact": {
            "_note": "Auto-extracted. Update if incorrect.",
            "website": biz_info.get("website", f"https://{site_info.get('domain','')}"),
            "email": biz_info.get("email", ""),
            "phone": biz_info.get("phone", ""),
            "whatsapp": "",
            "address": {"street": "", "city": "", "state": "", "country": "", "postal_code": ""},
            "google_maps_url": ""
        },
        "cta": {
            "primary_action": "Visit Our Website",
            "primary_url": biz_info.get("website", ""),
            "primary_button_text": "Get Started",
            "blog_post_cta": {
                "enabled": True,
                "heading": f"Ready to Work With {site_info.get('title', 'Us')}?",
                "body": f"Contact us today. We're here to help.",
                "show_email": bool(biz_info.get("email")),
                "show_phone": bool(biz_info.get("phone")),
                "show_website": True,
                "button_text": "Get In Touch",
                "button_url": f"{biz_info.get('website','')}/contact"
            },
            "social_media_cta": {
                "enabled": True,
                "instagram": f"🔗 Link in bio | 📧 {biz_info.get('email','')}",
                "facebook": f"👉 {biz_info.get('website','')} | 📧 {biz_info.get('email','')} | 📞 {biz_info.get('phone','')}",
                "linkedin": f"Learn more at {biz_info.get('website','')}",
                "twitter": f"🔗 {biz_info.get('website','')}",
                "gmb": f"Visit: {biz_info.get('website','')} | Call: {biz_info.get('phone','')} | Email: {biz_info.get('email','')}"
            },
            "banner_image_cta": {"enabled": True, "show_website": True, "show_phone": bool(biz_info.get("phone")), "show_email": False}
        },
        "social_profiles": biz_info.get("social", {}),
        "notifications": {
            "daily_report_email": {"enabled": True, "time": "20:00"},
            "festival_posts": {"enabled": True, "time": "01:00"}
        }
    }

    path = os.path.join(BASE_DIR, "config", "business.json")
    with open(path, "w") as f:
        json.dump(config, f, indent=2)

    found = []
    if biz_info.get("email"): found.append(f"email: {biz_info['email']}")
    if biz_info.get("phone"): found.append(f"phone: {biz_info['phone']}")
    if biz_info.get("social"): found.append(f"social profiles: {', '.join(biz_info['social'].keys())}")
    note = f" ({', '.join(found)})" if found else " (update manually if needed)"
    print(f"  ✅ Generated: config/business.json{note}")


# Monkey-patch auto_configure to also extract business info
_original_auto_configure = auto_configure

def auto_configure(domain: str, wp_user: str = "", wp_pass: str = ""):
    """Extended auto_configure that also extracts business info and CTA."""
    # Run original
    site_info = detect_site_info(domain)

    # Extract business contact info
    print("\nStep 2b/6: Extracting business contact info (email, phone, social)...")
    biz_info = extract_business_info(domain)
    if biz_info.get("email"):
        print(f"  ✅ Found email: {biz_info['email']}")
    if biz_info.get("phone"):
        print(f"  ✅ Found phone: {biz_info['phone']}")
    if biz_info.get("social"):
        print(f"  ✅ Found social: {', '.join(biz_info['social'].keys())}")

    write_business_json(site_info, biz_info)

    # Continue with rest of original logic
    wp_user = wp_user or os.environ.get("WP_USERNAME", "")
    wp_pass = wp_pass or os.environ.get("WP_APP_PASSWORD", "")
    wp_posts = fetch_wordpress_posts(domain, wp_user, wp_pass) if site_info["is_wordpress"] else []
    wp_pages = fetch_wordpress_pages(domain, wp_user, wp_pass) if site_info["is_wordpress"] else []

    kw_data = generate_keywords_for_niche(site_info["niche"], site_info["title"], wp_posts)

    os.makedirs(os.path.join(BASE_DIR, "config"), exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, "context"), exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, "topics"), exist_ok=True)

    write_site_json(site_info)
    write_keywords_md(site_info, kw_data, wp_posts)
    write_brand_voice_md(site_info)
    write_internal_links_map(site_info, wp_posts, wp_pages)
    write_topic_queue(kw_data)
    write_competitors_json(site_info)
    write_env_file(site_info, wp_user, wp_pass)

    total_keywords = sum(len(c["keywords"]) for c in kw_data["clusters"])

    print(f"\n{'='*60}")
    print(f"✅ Auto-configuration complete for {domain}!")
    print(f"{'='*60}")
    print(f"\n  config/site.json             — Site settings")
    print(f"  config/business.json         — Business info + CTA")
    print(f"  config/keywords.md           — {total_keywords} keywords")
    print(f"  config/competitors.json      — Competitors")
    print(f"  context/brand-voice.md       — Brand voice")
    print(f"  context/internal-links-map.md — {len(wp_posts)} pages")
    print(f"  topics/queue.txt             — 30 topics")
    print(f"  .env                         — Credentials template")
    print(f"\n📌 Next: Edit .env → add your API credentials → then run:")
    print(f"  python3 scripts/setup_crons.py  (installs ALL automation)")

    return site_info
