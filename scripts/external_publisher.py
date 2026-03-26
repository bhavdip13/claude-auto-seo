"""
Claude Auto SEO — External Publisher
Publishes content to Medium, Reddit, LinkedIn, Dev.to, and Hashnode.

Usage:
  python3 scripts/external_publisher.py drafts/my-article.md medium
  python3 scripts/external_publisher.py drafts/my-article.md reddit --subreddit r/SEO
  python3 scripts/external_publisher.py drafts/my-article.md all
"""

import os
import re
import sys
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FILE = os.path.join(BASE_DIR, "data", "external-publish-log.json")


def load_article(path: str) -> Dict:
    """Parse markdown article with front matter."""
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    meta = {}
    body = content

    # Parse YAML front matter
    fm_match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
    if fm_match:
        for line in fm_match.group(1).split("\n"):
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
        body = content[fm_match.end():]

    # Extract H1 as title
    h1_match = re.search(r"^# (.+)$", body, re.MULTILINE)
    if h1_match and not meta.get("title"):
        meta["title"] = h1_match.group(1)

    return {
        "title":            meta.get("title", "Untitled"),
        "slug":             meta.get("slug", ""),
        "primary_keyword":  meta.get("primary_keyword", ""),
        "seo_title":        meta.get("seo_title", meta.get("title", "")),
        "meta_description": meta.get("meta_description", ""),
        "tags":             [t.strip() for t in meta.get("tags", "").split(",") if t.strip()],
        "categories":       [c.strip() for c in meta.get("categories", "").split(",") if c.strip()],
        "wp_url":           meta.get("wp_url", ""),  # Canonical URL
        "body_markdown":    body,
        "body_text":        re.sub(r"<[^>]+>", "", body),
        "word_count":       len(re.findall(r"\b\w+\b", body)),
    }


def log_publish(platform: str, article_title: str, url: str, canonical: str = ""):
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    log = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            log = json.load(f)
    log.append({
        "platform": platform,
        "title": article_title,
        "published_url": url,
        "canonical": canonical,
        "published_at": datetime.now().isoformat(),
    })
    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)


# ── MEDIUM ────────────────────────────────────────────────────────────────────

def publish_medium(article: Dict) -> Dict:
    token = os.getenv("MEDIUM_INTEGRATION_TOKEN")
    if not token:
        return {"success": False, "error": "Set MEDIUM_INTEGRATION_TOKEN in .env"}

    wp_url = article.get("wp_url") or os.getenv("WP_URL", "")

    # Get author ID
    me = requests.get("https://api.medium.com/v1/me",
                      headers={"Authorization": f"Bearer {token}"})
    if me.status_code != 200:
        return {"success": False, "error": "Invalid Medium token"}
    author_id = me.json()["data"]["id"]

    # Append canonical notice
    content = article["body_markdown"]
    if wp_url:
        content += f"\n\n---\n*Originally published at [{wp_url}]({wp_url})*"

    payload = {
        "title": article["title"],
        "contentFormat": "markdown",
        "content": content,
        "tags": article["tags"][:5],
        "publishStatus": "draft",  # Draft for review
        "canonicalUrl": wp_url if wp_url else None,
    }

    r = requests.post(
        f"https://api.medium.com/v1/users/{author_id}/posts",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json=payload
    )

    if r.status_code == 201:
        post = r.json()["data"]
        url = post.get("url", "")
        log_publish("medium", article["title"], url, wp_url)
        return {"success": True, "url": url, "platform": "Medium",
                "note": "Published as DRAFT — review before making public"}
    return {"success": False, "error": r.text}


# ── REDDIT ────────────────────────────────────────────────────────────────────

def publish_reddit(article: Dict, subreddit: str = None) -> Dict:
    client_id  = os.getenv("REDDIT_CLIENT_ID")
    secret     = os.getenv("REDDIT_CLIENT_SECRET")
    username   = os.getenv("REDDIT_USERNAME")
    password   = os.getenv("REDDIT_PASSWORD")

    if not all([client_id, secret, username, password]):
        return {"success": False, "error": "Set REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USERNAME, REDDIT_PASSWORD in .env"}

    if not subreddit:
        # Load from config
        cfg_path = os.path.join(BASE_DIR, "config", "schedule.json")
        if os.path.exists(cfg_path):
            with open(cfg_path) as f:
                cfg = json.load(f)
            subreddits = cfg.get("external_platforms", {}).get("reddit", {}).get("subreddits", [])
            subreddit = subreddits[0] if subreddits else "r/SEO"
        else:
            subreddit = "r/SEO"

    subreddit = subreddit.lstrip("r/")

    # Get OAuth token
    auth = requests.auth.HTTPBasicAuth(client_id, secret)
    token_resp = requests.post(
        "https://www.reddit.com/api/v1/access_token",
        auth=auth,
        data={"grant_type": "password", "username": username, "password": password},
        headers={"User-Agent": "ClaudeAutoSEO/1.0"}
    )
    if token_resp.status_code != 200:
        return {"success": False, "error": "Reddit auth failed"}

    access_token = token_resp.json().get("access_token")
    headers = {"Authorization": f"bearer {access_token}", "User-Agent": "ClaudeAutoSEO/1.0"}

    # Build a discussion-style post (not just a link drop)
    wp_url = article.get("wp_url") or os.getenv("WP_URL", "")
    text = _build_reddit_post(article, wp_url)

    r = requests.post(
        "https://oauth.reddit.com/api/submit",
        headers=headers,
        data={
            "sr": subreddit,
            "kind": "self",
            "title": article["title"],
            "text": text,
            "resubmit": True,
        }
    )

    if r.status_code == 200:
        data = r.json()
        url = data.get("jquery", [[],[],[],[""]])[10][3] if "jquery" in data else ""
        log_publish("reddit", article["title"], url, wp_url)
        return {"success": True, "url": url, "platform": f"Reddit r/{subreddit}"}
    return {"success": False, "error": r.text[:200]}


def _build_reddit_post(article: Dict, wp_url: str) -> str:
    """Build a discussion-style Reddit post (not spam)."""
    # Extract 3 key insights from article
    sentences = re.split(r"[.!?]", article["body_text"])
    insights = [s.strip() for s in sentences if len(s.strip()) > 50][:3]

    text = f"I've been working on {article['primary_keyword'] or article['title']} lately and wanted to share some findings:\n\n"
    for i, insight in enumerate(insights, 1):
        text += f"**{i}.** {insight}.\n\n"

    if wp_url:
        text += f"I wrote a more detailed breakdown here if useful: {wp_url}\n\n"

    text += "What's your experience with this? Any other approaches that have worked well?"
    return text


# ── LINKEDIN ──────────────────────────────────────────────────────────────────

def publish_linkedin(article: Dict) -> Dict:
    token = os.getenv("LINKEDIN_ACCESS_TOKEN")
    if not token:
        return {"success": False, "error": "Set LINKEDIN_ACCESS_TOKEN in .env"}

    wp_url = article.get("wp_url") or os.getenv("WP_URL", "")

    # Shorten for LinkedIn (1200-1500 words)
    truncated_body = " ".join(article["body_text"].split()[:1200])
    if wp_url:
        truncated_body += f"\n\nFull guide: {wp_url}"

    # LinkedIn uses URN for author
    profile_r = requests.get(
        "https://api.linkedin.com/v2/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    if profile_r.status_code != 200:
        return {"success": False, "error": "Invalid LinkedIn token"}

    author_urn = f"urn:li:person:{profile_r.json()['id']}"

    payload = {
        "author": author_urn,
        "lifecycleState": "DRAFT",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": truncated_body[:2900]},
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
    }

    r = requests.post(
        "https://api.linkedin.com/v2/ugcPosts",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json=payload
    )

    if r.status_code == 201:
        post_id = r.headers.get("x-restli-id", "")
        log_publish("linkedin", article["title"], post_id, wp_url)
        return {"success": True, "post_id": post_id, "platform": "LinkedIn",
                "note": "Published as DRAFT"}
    return {"success": False, "error": r.text[:200]}


# ── DEV.TO ────────────────────────────────────────────────────────────────────

def publish_devto(article: Dict) -> Dict:
    api_key = os.getenv("DEVTO_API_KEY")
    if not api_key:
        return {"success": False, "error": "Set DEVTO_API_KEY in .env"}

    wp_url = article.get("wp_url") or os.getenv("WP_URL", "")
    body = article["body_markdown"]
    if wp_url:
        body += f"\n\n---\n*Originally published at [{wp_url}]({wp_url})*"

    payload = {
        "article": {
            "title": article["title"],
            "body_markdown": body,
            "published": False,  # Draft
            "tags": article["tags"][:4],
            "canonical_url": wp_url or None,
            "description": article["meta_description"],
        }
    }

    r = requests.post(
        "https://dev.to/api/articles",
        headers={"api-key": api_key, "Content-Type": "application/json"},
        json=payload
    )

    if r.status_code == 201:
        data = r.json()
        url = data.get("url", "")
        log_publish("devto", article["title"], url, wp_url)
        return {"success": True, "url": url, "platform": "Dev.to", "note": "Draft — publish manually"}
    return {"success": False, "error": r.text[:200]}


# ── Main ──────────────────────────────────────────────────────────────────────

def publish(md_path: str, platform: str, subreddit: str = None):
    if not os.path.exists(md_path):
        print(f"❌ File not found: {md_path}")
        sys.exit(1)

    article = load_article(md_path)
    platforms = ["medium", "reddit", "linkedin", "devto"] if platform == "all" else [platform.lower()]

    results = []
    for p in platforms:
        print(f"\n📤 Publishing to {p.title()}...")
        if p == "medium":
            r = publish_medium(article)
        elif p == "reddit":
            r = publish_reddit(article, subreddit)
        elif p == "linkedin":
            r = publish_linkedin(article)
        elif p == "devto":
            r = publish_devto(article)
        else:
            r = {"success": False, "error": f"Unknown platform: {p}"}

        results.append(r)
        if r.get("success"):
            print(f"   ✅ Published to {r.get('platform', p)}")
            if r.get("url"):
                print(f"   URL: {r['url']}")
            if r.get("note"):
                print(f"   Note: {r['note']}")
        else:
            print(f"   ❌ Failed: {r.get('error', 'Unknown error')}")

    print(f"\n{'='*40}")
    success_count = sum(1 for r in results if r.get("success"))
    print(f"Published: {success_count}/{len(results)} platforms")
    print(f"Log: {LOG_FILE}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Claude Auto SEO — External Publisher")
    parser.add_argument("file",                          help="Markdown article file")
    parser.add_argument("platform",                      help="Platform: medium/reddit/linkedin/devto/all")
    parser.add_argument("--subreddit", default=None,     help="Reddit subreddit (e.g. r/SEO)")
    args = parser.parse_args()
    publish(args.file, args.platform, args.subreddit)
