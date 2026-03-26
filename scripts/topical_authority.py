"""
Claude Auto SEO — Topical Authority Map Builder
Builds a complete content cluster structure for topical authority.
Google ranks sites higher when they comprehensively cover a topic.

Also includes: Review Monitor and Auto-Reply Generator
"""

import os
import json
import re
from datetime import date, datetime
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ── TOPICAL AUTHORITY MAP ─────────────────────────────────────────────────────

def build_topical_map(niche: str, site_url: str = "", depth: int = 3) -> Dict:
    """
    Build a complete topical authority map for a niche.
    Creates pillar → cluster → supporting content hierarchy.
    """
    
    # Niche-specific topic maps
    topic_maps = {
        "marketing": {
            "pillar": "Digital Marketing Guide",
            "clusters": [
                {
                    "name": "SEO",
                    "pillar_page": "/seo-guide/",
                    "cluster_articles": [
                        "Technical SEO checklist",
                        "Keyword research guide",
                        "On-page SEO tips",
                        "Link building strategies",
                        "Local SEO guide",
                        "SEO for beginners",
                        "SEO audit guide",
                        "Schema markup guide",
                    ],
                    "supporting": [
                        "What is a meta description",
                        "How to use Google Search Console",
                        "What is domain authority",
                        "How to check website traffic",
                    ]
                },
                {
                    "name": "Content Marketing",
                    "pillar_page": "/content-marketing/",
                    "cluster_articles": [
                        "How to create a content strategy",
                        "Blog writing tips",
                        "Content calendar template",
                        "How to write for SEO",
                    ],
                    "supporting": [
                        "What is content marketing",
                        "Content marketing examples",
                        "How often to publish blog posts",
                    ]
                },
            ]
        },
        "ecommerce": {
            "pillar": "Ecommerce Guide",
            "clusters": [
                {
                    "name": "Ecommerce SEO",
                    "pillar_page": "/ecommerce-seo/",
                    "cluster_articles": [
                        "Product page optimization",
                        "Category page SEO",
                        "Ecommerce keyword research",
                        "Technical SEO for online stores",
                    ],
                    "supporting": [
                        "What is ecommerce SEO",
                        "Ecommerce SEO checklist",
                    ]
                }
            ]
        },
        "general": {
            "pillar": "Complete Industry Guide",
            "clusters": [
                {
                    "name": "Getting Started",
                    "pillar_page": "/guide/",
                    "cluster_articles": [
                        "Beginners guide",
                        "How to get started",
                        "Best tools and resources",
                        "Common mistakes to avoid",
                    ],
                    "supporting": [
                        "FAQ",
                        "Glossary",
                        "Case studies",
                    ]
                }
            ]
        }
    }

    topic_data = topic_maps.get(niche, topic_maps["general"])
    
    # Count total articles needed
    total_articles = sum(
        len(c["cluster_articles"]) + len(c["supporting"])
        for c in topic_data["clusters"]
    )
    
    return {
        "niche": niche,
        "pillar": topic_data["pillar"],
        "clusters": topic_data["clusters"],
        "total_articles_needed": total_articles,
        "estimated_time_weeks": total_articles // 5,  # 5 articles per week
    }


def generate_topical_map_report(niche: str, site_url: str = "") -> str:
    """Generate a complete topical authority map as markdown."""
    topic_map = build_topical_map(niche, site_url)
    
    lines = [
        f"# Topical Authority Map — {niche.title()}",
        f"Site: {site_url or os.environ.get('WP_URL', 'yoursite.com')}",
        f"Generated: {date.today().isoformat()}",
        "",
        "## What is Topical Authority?",
        "Google ranks sites higher when they completely cover a topic.",
        "Build all pages in this map = dominate your niche in search.",
        "",
        f"## Your Content Roadmap",
        f"- **Total articles needed:** {topic_map['total_articles_needed']}",
        f"- **Estimated completion:** {topic_map['estimated_time_weeks']} weeks (at 5/week)",
        f"- **Your scheduler:** Already writing 1 post/day automatically!",
        "",
    ]

    for i, cluster in enumerate(topic_map["clusters"], 1):
        lines += [
            f"## Cluster {i}: {cluster['name']}",
            f"**Pillar page:** {site_url}{cluster['pillar_page']}",
            "",
            "### Cluster Articles (write these next — add to topics/queue.txt)",
        ]
        for article in cluster["cluster_articles"]:
            lines.append(f"- [ ] {article}")
        
        lines += ["", "### Supporting Articles"]
        for article in cluster["supporting"]:
            lines.append(f"- [ ] {article}")
        lines.append("")

    lines += [
        "## How to Build This Map Automatically",
        "",
        "1. These topics are in your `topics/queue.txt` automatically",
        "2. Your scheduler writes 1 article/day from the queue",
        "3. As you publish, check off items above",
        "4. Once a cluster is complete, Google sees you as an authority on it",
        "5. Rankings improve across ALL related keywords",
        "",
        "## Internal Linking Strategy",
        "",
        "**Rule:** Every cluster article must link to the pillar page.",
        "**Rule:** Every pillar page must link to all cluster articles.",
        "**Rule:** Cluster articles should cross-link to related cluster articles.",
        "",
        "The `/write` command already handles this using `context/internal-links-map.md`.",
    ]

    return "\n".join(lines)


def add_topics_to_queue(topic_map: Dict):
    """Add all topical map articles to the writing queue."""
    queue_path = os.path.join(BASE_DIR, "topics", "queue.txt")
    
    existing = ""
    if os.path.exists(queue_path):
        with open(queue_path) as f:
            existing = f.read()
    
    new_topics = []
    for cluster in topic_map["clusters"]:
        new_topics.extend(cluster["cluster_articles"])
        new_topics.extend(cluster["supporting"])
    
    # Add only if not already in queue
    to_add = [t for t in new_topics if t.lower() not in existing.lower()]
    
    with open(queue_path, "a") as f:
        f.write("\n# Topical Authority Map Topics\n")
        for topic in to_add:
            f.write(f"{topic}\n")
    
    return len(to_add)


# ── REVIEW MONITOR ────────────────────────────────────────────────────────────

def generate_review_reply(review_text: str, rating: int, business_name: str = "") -> Dict:
    """
    Generate appropriate review reply based on rating and content.
    Returns both a positive and template reply.
    """
    biz = business_name or os.environ.get("SITE_NAME", "Our Business")
    
    if rating >= 4:
        reply = f"""Thank you so much for your wonderful review! 🙏

We're thrilled to hear you had such a positive experience with {biz}. Your kind words mean the world to our team.

We look forward to serving you again soon!

Warm regards,
The {biz} Team"""
    
    elif rating == 3:
        reply = f"""Thank you for taking the time to share your feedback!

We appreciate your honest review and are always looking to improve. We'd love to learn more about how we can better serve you — please feel free to reach out to us directly at {os.environ.get('NOTIFICATION_EMAIL', '[email]')}.

Best regards,
The {biz} Team"""
    
    else:  # 1-2 stars
        reply = f"""Thank you for sharing your experience, and we sincerely apologize that we didn't meet your expectations.

At {biz}, we take all feedback seriously. We'd very much like the opportunity to make this right. Please contact us directly at {os.environ.get('NOTIFICATION_EMAIL', '[email]')} so we can address your concerns personally.

Sincerely,
The {biz} Team"""
    
    return {
        "rating": rating,
        "reply": reply,
        "tone": "positive" if rating >= 4 else "neutral" if rating == 3 else "apologetic",
        "action_needed": rating <= 2,
    }


def generate_review_request_templates() -> Dict:
    """Generate review request templates for different channels."""
    biz = os.environ.get("SITE_NAME", "Our Business")
    site_url = os.environ.get("WP_URL", "https://yoursite.com")
    
    return {
        "email_subject": f"How was your experience with {biz}?",
        "email_template": f"""Hi {{customer_name}},

Thank you for choosing {biz}! We hope everything went well.

If you have 2 minutes, we'd love to hear about your experience. Reviews help us improve and help others find us.

⭐ Leave a Google Review: {{google_review_url}}
⭐ Leave a Trustpilot Review: {{trustpilot_url}}

Even a sentence or two makes a big difference for a small business like ours.

Thank you!
The {biz} Team
{site_url}""",
        
        "sms_template": f"Hi {{name}}! Thank you for using {biz}. Would you mind leaving us a quick review? It takes 2 mins: {{review_url}} — The {biz} Team",
        
        "whatsapp_template": f"Hi {{name}}! 👋 Thank you for choosing {biz}. We'd really appreciate if you could share your experience: {{review_url}} 🙏",
    }


if __name__ == "__main__":
    import argparse, sys
    
    parser = argparse.ArgumentParser(description="Topical Map + Review Tools")
    parser.add_argument("--topical-map",       metavar="NICHE", help="Build topical authority map")
    parser.add_argument("--add-to-queue",      action="store_true", help="Add topics to writing queue")
    parser.add_argument("--review-reply",      metavar="RATING", type=int, help="Generate review reply (1-5)")
    parser.add_argument("--review-templates",  action="store_true", help="Get review request templates")
    args = parser.parse_args()

    cfg_path = os.path.join(BASE_DIR, "config", "site.json")
    niche = args.topical_map or "general"
    site_url = os.environ.get("WP_URL", "")
    
    if os.path.exists(cfg_path):
        with open(cfg_path) as f:
            cfg = json.load(f)
        niche = cfg.get("site", {}).get("niche", niche)
        site_url = site_url or cfg.get("site", {}).get("url", "")

    if args.topical_map or True:
        report = generate_topical_map_report(niche, site_url)
        path = os.path.join(BASE_DIR, "reports", f"topical-map-{date.today()}.md")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(report)
        print(report[:3000])
        print(f"\n✅ Saved: {path}")
        
        if args.add_to_queue:
            topic_map = build_topical_map(niche)
            added = add_topics_to_queue(topic_map)
            print(f"✅ Added {added} topics to topics/queue.txt")

    if args.review_reply:
        result = generate_review_reply("Sample review text", args.review_reply)
        print(f"\n⭐ {'⭐' * args.review_reply} Review Reply:")
        print(result["reply"])

    if args.review_templates:
        templates = generate_review_request_templates()
        print("\n📧 Email Template:")
        print(templates["email_template"])
        print("\n📱 SMS Template:")
        print(templates["sms_template"])
