"""
Claude Auto SEO — Social Media Publisher
Auto-publishes to Instagram, Facebook, LinkedIn, Twitter/X, Pinterest, TikTok, and Google My Business.

Usage:
  python3 scripts/social_publisher.py --topic "SEO Tips" --keyword "seo tips" --platforms all
  python3 scripts/social_publisher.py --topic "SEO Tips" --platforms instagram,facebook
  python3 scripts/social_publisher.py --from-article drafts/my-article.md --platforms all
"""

import os
import re
import sys
import json
import time
import random
import requests
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FILE = os.path.join(BASE_DIR, "data", "social-publish-log.json")

# ── Credential helpers ────────────────────────────────────────────────────────

def env(key: str, required: bool = False) -> str:
    val = os.environ.get(key, "")
    if required and not val:
        print(f"❌ Missing required credential: {key} — add to .env")
    return val


# ── Content Generator ─────────────────────────────────────────────────────────

def generate_social_content(topic: str, keyword: str, platform: str,
                              article_text: str = "", cta_url: str = "") -> Dict:
    """
    Generate platform-optimized content from a topic/keyword.
    Each platform gets different tone, length, and hashtag count.
    """
    site_name = env("SITE_NAME") or "Our Blog"
    url = cta_url or env("WP_URL") or "https://yoursite.com"

    # Load hashtags from keywords config
    hashtags = load_hashtags(keyword)

    templates = {
        "instagram": {
            "max_chars": 2200,
            "hashtag_count": 25,
            "tone": "casual, visual, inspiring",
            "format": "hook + value + CTA + hashtags",
        },
        "facebook": {
            "max_chars": 63206,
            "hashtag_count": 5,
            "tone": "conversational, informative",
            "format": "hook + detailed value + question CTA + few hashtags",
        },
        "linkedin": {
            "max_chars": 3000,
            "hashtag_count": 5,
            "tone": "professional, insightful, thought leadership",
            "format": "insight hook + numbered takeaways + question + hashtags",
        },
        "twitter": {
            "max_chars": 280,
            "hashtag_count": 2,
            "tone": "punchy, direct, conversational",
            "format": "key insight or tip in 240 chars + 2 hashtags + link",
        },
        "pinterest": {
            "max_chars": 500,
            "hashtag_count": 5,
            "tone": "inspirational, keyword-rich",
            "format": "keyword-rich description + what you'll learn + hashtags",
        },
        "gmb": {
            "max_chars": 1500,
            "hashtag_count": 0,
            "tone": "local, helpful, professional",
            "format": "helpful tip or update + CTA to website",
        },
    }

    cfg = templates.get(platform, templates["facebook"])
    tag_list = hashtags[:cfg["hashtag_count"]]
    tag_str = " ".join(f"#{t.lstrip('#')}" for t in tag_list)

    # Extract key points from article if available
    key_points = []
    if article_text:
        sentences = re.split(r"[.!?]", article_text)
        key_points = [s.strip() for s in sentences if 40 < len(s.strip()) < 200][:5]

    # Build content per platform
    if platform == "twitter":
        content = _make_twitter(topic, keyword, url, tag_str)
    elif platform == "instagram":
        content = _make_instagram(topic, keyword, key_points, url, tag_str, site_name)
    elif platform == "linkedin":
        content = _make_linkedin(topic, keyword, key_points, url, tag_str)
    elif platform == "facebook":
        content = _make_facebook(topic, keyword, key_points, url, tag_str)
    elif platform == "pinterest":
        content = _make_pinterest(topic, keyword, url, tag_str)
    elif platform == "gmb":
        content = _make_gmb(topic, keyword, url)
    else:
        content = f"📖 New post: {topic}\n\nRead more: {url}\n\n{tag_str}"

    return {
        "platform": platform,
        "content": content[:cfg["max_chars"]],
        "hashtags": tag_list,
        "url": url,
        "topic": topic,
        "keyword": keyword,
    }


def _make_instagram(topic, keyword, points, url, tags, site):
    hook = f"🔥 {topic}" if not topic[0].isupper() else f"🔥 {topic}"
    body = "\n\n".join(f"✅ {p}" for p in points[:3]) if points else \
           f"Learn everything you need to know about {keyword} in our latest guide."
    return f"""{hook}

{body}

💡 Want the full breakdown? Link in bio ☝️

—
{site} | {keyword}

{tags}"""


def _make_facebook(topic, keyword, points, url, tags):
    body = "\n".join(f"• {p}" for p in points[:4]) if points else \
           f"We just published a comprehensive guide on {keyword}."
    return f"""📌 {topic}

{body}

What's your experience with {keyword}? Drop a comment below! 👇

Read the full guide: {url}

{tags}"""


def _make_linkedin(topic, keyword, points, url, tags):
    numbered = "\n".join(f"{i+1}. {p}" for i, p in enumerate(points[:4])) if points else \
               f"Key insights on {keyword} that every professional should know."
    return f"""💡 {topic}

Here's what I've learned about {keyword}:

{numbered}

The most underrated part? Getting this right can make a significant difference in results.

What's your take? I'd love to hear your experience in the comments.

Full article: {url}

{tags}"""


def _make_twitter(topic, keyword, url, tags):
    short = topic[:200] if len(topic) > 200 else topic
    return f"💡 {short}\n\n→ {url}\n\n{tags}"


def _make_pinterest(topic, keyword, url, tags):
    return f"""{topic}

📌 Save this for later!

In this guide you'll learn:
• Everything about {keyword}
• Step-by-step strategies
• Expert tips that actually work

Click to read the full guide ➡️

{url}

{tags}"""


def _make_gmb(topic, keyword, url):
    templates = [
        f"💡 New on our blog: {topic}\n\nLooking to improve your {keyword}? We just published a complete guide covering everything you need to know.\n\nRead it here: {url}",
        f"📖 {topic}\n\nWe know {keyword} can be challenging. That's why we put together this detailed resource to help you get better results.\n\n👉 {url}",
        f"🎯 Quick tip about {keyword}:\n\nThe biggest mistake people make is skipping the research phase. Our new guide walks you through exactly how to get this right.\n\nFull guide: {url}",
    ]
    return random.choice(templates)


def load_hashtags(keyword: str) -> List[str]:
    """Load hashtags from keywords config MD file."""
    kw_file = os.path.join(BASE_DIR, "config", "keywords.md")
    hashtags = []

    if os.path.exists(kw_file):
        with open(kw_file) as f:
            content = f.read()
        # Extract hashtag lines
        matches = re.findall(r"#(\w+)", content)
        hashtags = list(dict.fromkeys(matches))[:30]  # Unique, preserve order

    # Always include keyword-based tags
    kw_tags = [keyword.replace(" ", ""), keyword.replace(" ", "_"),
               keyword.split()[0] if keyword else ""]
    for t in kw_tags:
        if t and t not in hashtags:
            hashtags.insert(0, t)

    return hashtags[:30]


def log_post(platform: str, topic: str, post_id: str = "", url: str = ""):
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    log = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            try:
                log = json.load(f)
            except Exception:
                log = []
    log.append({
        "platform": platform,
        "topic": topic,
        "post_id": post_id,
        "url": url,
        "published_at": datetime.now().isoformat(),
    })
    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)


# ── INSTAGRAM + FACEBOOK (Meta Graph API) ────────────────────────────────────

def publish_instagram(content: Dict, image_path: str) -> Dict:
    """Publish to Instagram via Meta Graph API (requires Business account)."""
    access_token = env("META_ACCESS_TOKEN")
    ig_user_id   = env("INSTAGRAM_USER_ID")

    if not access_token or not ig_user_id:
        return {"success": False, "error": "Set META_ACCESS_TOKEN and INSTAGRAM_USER_ID in .env"}

    # Step 1: Upload image as container
    if not image_path or not os.path.exists(image_path):
        return {"success": False, "error": f"Image not found: {image_path}"}

    # Upload image to a public URL first (Instagram needs public URL)
    # For local images, we use the WordPress media upload as proxy
    wp_url = _upload_image_to_wordpress(image_path)
    if not wp_url:
        return {"success": False, "error": "Could not upload image to get public URL"}

    # Create media container
    container_r = requests.post(
        f"https://graph.facebook.com/v19.0/{ig_user_id}/media",
        params={
            "image_url": wp_url,
            "caption": content["content"],
            "access_token": access_token,
        }
    )

    if container_r.status_code != 200:
        return {"success": False, "error": container_r.text[:200]}

    creation_id = container_r.json().get("id")

    # Step 2: Publish the container
    time.sleep(2)  # Instagram needs a moment
    publish_r = requests.post(
        f"https://graph.facebook.com/v19.0/{ig_user_id}/media_publish",
        params={"creation_id": creation_id, "access_token": access_token}
    )

    if publish_r.status_code == 200:
        post_id = publish_r.json().get("id", "")
        log_post("instagram", content["topic"], post_id)
        return {"success": True, "platform": "Instagram", "post_id": post_id}

    return {"success": False, "error": publish_r.text[:200]}


def publish_facebook(content: Dict, image_path: str = None) -> Dict:
    """Publish to Facebook Page via Meta Graph API."""
    access_token = env("META_ACCESS_TOKEN")
    page_id      = env("FACEBOOK_PAGE_ID")

    if not access_token or not page_id:
        return {"success": False, "error": "Set META_ACCESS_TOKEN and FACEBOOK_PAGE_ID in .env"}

    endpoint = f"https://graph.facebook.com/v19.0/{page_id}"

    if image_path and os.path.exists(image_path):
        # Post with photo
        with open(image_path, "rb") as img_file:
            r = requests.post(
                f"{endpoint}/photos",
                data={"message": content["content"], "access_token": access_token},
                files={"source": img_file}
            )
    else:
        # Text-only post
        r = requests.post(
            f"{endpoint}/feed",
            data={"message": content["content"], "access_token": access_token,
                  "link": content.get("url", "")}
        )

    if r.status_code == 200:
        post_id = r.json().get("id", "")
        log_post("facebook", content["topic"], post_id)
        return {"success": True, "platform": "Facebook", "post_id": post_id}

    return {"success": False, "error": r.text[:200]}


# ── LINKEDIN ──────────────────────────────────────────────────────────────────

def publish_linkedin_post(content: Dict, image_path: str = None) -> Dict:
    token = env("LINKEDIN_ACCESS_TOKEN")
    if not token:
        return {"success": False, "error": "Set LINKEDIN_ACCESS_TOKEN in .env"}

    profile_r = requests.get("https://api.linkedin.com/v2/me",
                              headers={"Authorization": f"Bearer {token}"})
    if profile_r.status_code != 200:
        return {"success": False, "error": "Invalid LinkedIn token"}

    person_urn = f"urn:li:person:{profile_r.json()['id']}"

    # Upload image if provided
    media = None
    if image_path and os.path.exists(image_path):
        media = _linkedin_upload_image(token, person_urn, image_path)

    post_body = {
        "author": person_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": content["content"][:2900]},
                "shareMediaCategory": "IMAGE" if media else "NONE",
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
    }

    if media:
        post_body["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [media]

    r = requests.post(
        "https://api.linkedin.com/v2/ugcPosts",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json=post_body
    )

    if r.status_code == 201:
        post_id = r.headers.get("x-restli-id", "")
        log_post("linkedin", content["topic"], post_id)
        return {"success": True, "platform": "LinkedIn", "post_id": post_id}

    return {"success": False, "error": r.text[:200]}


def _linkedin_upload_image(token: str, person_urn: str, image_path: str) -> Optional[dict]:
    """Upload image to LinkedIn and return media asset."""
    # Register upload
    reg = requests.post(
        "https://api.linkedin.com/v2/assets?action=registerUpload",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={"registerUploadRequest": {
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
            "owner": person_urn,
            "serviceRelationships": [{"relationshipType": "OWNER",
                                       "identifier": "urn:li:userGeneratedContent"}]
        }}
    )
    if reg.status_code != 200:
        return None

    reg_data  = reg.json()["value"]
    upload_url = reg_data["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
    asset_urn  = reg_data["asset"]

    with open(image_path, "rb") as f:
        requests.put(upload_url, headers={"Authorization": f"Bearer {token}",
                                           "Content-Type": "image/jpeg"}, data=f)

    return {"status": "READY", "media": asset_urn,
            "title": {"text": "Post image"}}


# ── TWITTER / X ───────────────────────────────────────────────────────────────

def publish_twitter(content: Dict, image_path: str = None) -> Dict:
    """Publish to Twitter/X via v2 API (OAuth 2.0)."""
    bearer  = env("TWITTER_BEARER_TOKEN")
    api_key = env("TWITTER_API_KEY")
    api_sec = env("TWITTER_API_SECRET")
    acc_tok = env("TWITTER_ACCESS_TOKEN")
    acc_sec = env("TWITTER_ACCESS_SECRET")

    if not all([api_key, api_sec, acc_tok, acc_sec]):
        return {"success": False, "error": "Set TWITTER_API_KEY/SECRET, TWITTER_ACCESS_TOKEN/SECRET in .env"}

    try:
        import tweepy
        client = tweepy.Client(
            consumer_key=api_key, consumer_secret=api_sec,
            access_token=acc_tok, access_token_secret=acc_sec
        )

        media_id = None
        if image_path and os.path.exists(image_path):
            auth = tweepy.OAuth1UserHandler(api_key, api_sec, acc_tok, acc_sec)
            api_v1 = tweepy.API(auth)
            media = api_v1.media_upload(filename=image_path)
            media_id = media.media_id

        tweet_text = content["content"][:280]
        kwargs = {}
        if media_id:
            kwargs["media_ids"] = [media_id]

        response = client.create_tweet(text=tweet_text, **kwargs)
        tweet_id = str(response.data["id"])
        url = f"https://twitter.com/i/web/status/{tweet_id}"
        log_post("twitter", content["topic"], tweet_id, url)
        return {"success": True, "platform": "Twitter/X", "tweet_id": tweet_id, "url": url}

    except ImportError:
        return {"success": False, "error": "Install tweepy: pip install tweepy"}
    except Exception as e:
        return {"success": False, "error": str(e)[:200]}


# ── PINTEREST ─────────────────────────────────────────────────────────────────

def publish_pinterest(content: Dict, image_path: str = None) -> Dict:
    token   = env("PINTEREST_ACCESS_TOKEN")
    board_id = env("PINTEREST_BOARD_ID")

    if not token or not board_id:
        return {"success": False, "error": "Set PINTEREST_ACCESS_TOKEN and PINTEREST_BOARD_ID in .env"}

    wp_url = env("WP_URL")
    img_url = _upload_image_to_wordpress(image_path) if image_path else wp_url

    payload = {
        "board_id": board_id,
        "title": content["topic"][:100],
        "description": content["content"][:500],
        "link": content.get("url", wp_url),
        "media_source": {"source_type": "image_url", "url": img_url or wp_url}
    }

    r = requests.post(
        "https://api.pinterest.com/v5/pins",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json=payload
    )

    if r.status_code == 201:
        pin_id = r.json().get("id", "")
        log_post("pinterest", content["topic"], pin_id)
        return {"success": True, "platform": "Pinterest", "pin_id": pin_id}

    return {"success": False, "error": r.text[:200]}


# ── GOOGLE MY BUSINESS ────────────────────────────────────────────────────────

def publish_gmb(content: Dict, image_path: str = None) -> Dict:
    """Publish to Google My Business via the GMB API."""
    token       = env("GOOGLE_GMB_ACCESS_TOKEN")
    location_id = env("GMB_LOCATION_ID")

    if not token or not location_id:
        return {"success": False,
                "error": "Set GOOGLE_GMB_ACCESS_TOKEN and GMB_LOCATION_ID in .env\n"
                         "See docs/GMB-SETUP.md for setup instructions."}

    payload = {
        "languageCode": "en",
        "summary": content["content"][:1500],
        "callToAction": {
            "actionType": "LEARN_MORE",
            "url": content.get("url", env("WP_URL"))
        },
        "topicType": "STANDARD"
    }

    # Add photo if provided
    if image_path and os.path.exists(image_path):
        with open(image_path, "rb") as f:
            img_bytes = f.read()
        import base64
        payload["media"] = [{
            "mediaFormat": "PHOTO",
            "sourceUrl": _upload_image_to_wordpress(image_path) or env("WP_URL")
        }]

    r = requests.post(
        f"https://mybusiness.googleapis.com/v4/accounts/-/locations/{location_id}/localPosts",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json=payload
    )

    if r.status_code == 200:
        post_name = r.json().get("name", "")
        log_post("gmb", content["topic"], post_name)
        return {"success": True, "platform": "Google My Business", "post_name": post_name}

    return {"success": False, "error": r.text[:200]}


# ── TIKTOK ────────────────────────────────────────────────────────────────────

def publish_tiktok_text(content: Dict) -> Dict:
    """Publish text post to TikTok (text-only via TikTok Content Posting API)."""
    token = env("TIKTOK_ACCESS_TOKEN")
    if not token:
        return {"success": False, "error": "Set TIKTOK_ACCESS_TOKEN in .env\nNote: TikTok requires video for main feed. Text posts via Creator Portal only."}

    # TikTok text post (available for creator accounts)
    payload = {
        "post_info": {
            "title": content["content"][:150],
            "privacy_level": "PUBLIC_TO_EVERYONE",
            "disable_comment": False,
        },
        "source_info": {"source": "PULL_FROM_URL"},
        "post_mode": "DIRECT_POST",
        "media_type": "TEXT"
    }

    r = requests.post(
        "https://open.tiktokapis.com/v2/post/publish/text/init/",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json=payload
    )

    if r.status_code == 200:
        post_id = r.json().get("data", {}).get("publish_id", "")
        log_post("tiktok", content["topic"], post_id)
        return {"success": True, "platform": "TikTok", "post_id": post_id,
                "note": "TikTok text post scheduled"}

    return {"success": False, "error": r.text[:200],
            "note": "TikTok primarily supports video. Text posts require Creator Portal access."}


# ── UTILITY ───────────────────────────────────────────────────────────────────

def _upload_image_to_wordpress(image_path: str) -> Optional[str]:
    """Upload an image to WordPress Media Library and return the public URL."""
    wp_url  = env("WP_URL")
    wp_user = env("WP_USERNAME")
    wp_pass = env("WP_APP_PASSWORD")

    if not all([wp_url, wp_user, wp_pass]) or not os.path.exists(image_path):
        return None

    import base64
    creds = base64.b64encode(f"{wp_user}:{wp_pass}".encode()).decode()
    filename = os.path.basename(image_path)
    ext = filename.rsplit(".", 1)[-1].lower()
    mime = {"jpg": "image/jpeg", "jpeg": "image/jpeg",
            "png": "image/png", "svg": "image/svg+xml"}.get(ext, "image/jpeg")

    try:
        with open(image_path, "rb") as f:
            r = requests.post(
                f"{wp_url}/wp-json/wp/v2/media",
                headers={"Authorization": f"Basic {creds}",
                         "Content-Disposition": f'attachment; filename="{filename}"',
                         "Content-Type": mime},
                data=f,
                timeout=30
            )
        if r.status_code == 201:
            return r.json().get("source_url", "")
    except Exception:
        pass
    return None


def publish_to_platforms(topic: str, keyword: str, platforms: List[str],
                          article_text: str = "", cta_url: str = "",
                          image_path: str = None) -> Dict:
    """Publish to multiple platforms at once."""
    results = {}
    all_platforms = ["instagram", "facebook", "linkedin", "twitter",
                     "pinterest", "gmb", "tiktok"]

    if "all" in platforms:
        platforms = all_platforms

    for platform in platforms:
        print(f"\n📤 Publishing to {platform.title()}...")
        content = generate_social_content(topic, keyword, platform, article_text, cta_url)

        # Generate platform-specific image
        platform_image = image_path
        if not platform_image:
            try:
                from image_generator import generate_banner
                result = generate_banner(topic, keyword, platform)
                platform_image = result.get("path")
            except Exception:
                pass

        try:
            if platform == "instagram":
                r = publish_instagram(content, platform_image)
            elif platform == "facebook":
                r = publish_facebook(content, platform_image)
            elif platform == "linkedin":
                r = publish_linkedin_post(content, platform_image)
            elif platform == "twitter":
                r = publish_twitter(content, platform_image)
            elif platform == "pinterest":
                r = publish_pinterest(content, platform_image)
            elif platform == "gmb":
                r = publish_gmb(content, platform_image)
            elif platform == "tiktok":
                r = publish_tiktok_text(content)
            else:
                r = {"success": False, "error": f"Unknown platform: {platform}"}
        except Exception as e:
            r = {"success": False, "error": str(e)[:200]}

        results[platform] = r
        if r.get("success"):
            print(f"   ✅ {r.get('platform', platform)} — posted successfully")
        else:
            print(f"   ❌ {platform} — {r.get('error', 'Unknown error')}")

    success_count = sum(1 for r in results.values() if r.get("success"))
    print(f"\n📊 Social Media Summary: {success_count}/{len(platforms)} platforms published")
    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Claude Auto SEO — Social Media Publisher")
    parser.add_argument("--topic",        required=True, help="Post topic/title")
    parser.add_argument("--keyword",      default="",    help="Primary keyword")
    parser.add_argument("--platforms",    default="all", help="Comma-separated platforms or 'all'")
    parser.add_argument("--image",        default="",    help="Path to banner image")
    parser.add_argument("--article",      default="",    help="Path to article markdown file")
    parser.add_argument("--url",          default="",    help="CTA URL")
    args = parser.parse_args()

    article_text = ""
    if args.article and os.path.exists(args.article):
        with open(args.article) as f:
            article_text = re.sub(r"<[^>]+>", "", f.read())

    platforms = [p.strip() for p in args.platforms.split(",")]
    publish_to_platforms(
        args.topic, args.keyword, platforms,
        article_text=article_text,
        cta_url=args.url,
        image_path=args.image or None
    )
