"""
Claude Auto SEO — Digital Marketing Scheduler
Automatically schedules and publishes social media posts with random timing.

Features:
- Random post times within configured windows (appears natural)
- Google My Business: 2x/day or every 3 days with varied timing
- Instagram/Facebook/LinkedIn/Twitter: daily with different times
- Reads keywords from config/keywords.md for content generation
- Generates banner images automatically

Usage:
  python3 scripts/dm_scheduler.py --run              # Run all scheduled posts for today
  python3 scripts/dm_scheduler.py --install-cron     # Install cron jobs
  python3 scripts/dm_scheduler.py --status           # Show schedule
  python3 scripts/dm_scheduler.py --preview          # Preview what would post today
"""

import os
import sys
import json
import random
import subprocess
import re
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_FILE = os.path.join(BASE_DIR, "config", "schedule.json")
LOG_FILE    = os.path.join(BASE_DIR, "data", "dm-scheduler-log.json")
KW_FILE     = os.path.join(BASE_DIR, "config", "keywords.md")


def load_config() -> Dict:
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {}


def load_log() -> Dict:
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            try:
                return json.load(f)
            except Exception:
                pass
    return {"daily": {}, "posts": []}


def save_log(log: Dict):
    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)


def get_keywords_from_config() -> List[Dict]:
    """Parse keywords.md and return list of keyword objects."""
    keywords = []
    if not os.path.exists(KW_FILE):
        return keywords

    with open(KW_FILE) as f:
        content = f.read()

    # Parse table rows: | keyword | volume | difficulty | intent | status | notes |
    rows = re.findall(r"\|\s*([^|]+)\s*\|\s*([^|]*)\s*\|\s*([^|]*)\s*\|\s*([^|]*)\s*\|\s*(queue|published|in_progress|needs_refresh|skip)\s*\|",
                      content, re.IGNORECASE)
    for row in rows:
        kw, vol, diff, intent, status = [r.strip() for r in row]
        if status.lower() in ("queue", "published") and kw and not kw.startswith("-"):
            keywords.append({
                "keyword": kw,
                "volume": vol,
                "intent": intent,
                "status": status,
            })

    return keywords


def pick_random_topic(used_today: List[str] = None) -> Optional[Dict]:
    """Pick a random keyword that hasn't been used today."""
    keywords = get_keywords_from_config()
    if not keywords:
        # Fallback: use queue.txt
        queue_file = os.path.join(BASE_DIR, "topics", "queue.txt")
        if os.path.exists(queue_file):
            with open(queue_file) as f:
                lines = [l.strip() for l in f if l.strip() and not l.startswith("#")]
            if lines:
                topic = random.choice(lines)
                return {"keyword": topic, "intent": "informational"}
        return None

    used_today = used_today or []
    available = [k for k in keywords if k["keyword"] not in used_today]
    return random.choice(available) if available else random.choice(keywords)


def random_time_in_window(start_hour: int, end_hour: int) -> str:
    """Return a random HH:MM within a time window."""
    hour   = random.randint(start_hour, end_hour - 1)
    minute = random.choice([0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55])
    return f"{hour:02d}:{minute:02d}"


def should_post_gmb_today(log: Dict) -> bool:
    """GMB: post twice per day OR every 3 days depending on config."""
    config = load_config()
    gmb_cfg = config.get("social_media", {}).get("gmb", {})
    frequency = gmb_cfg.get("frequency", "every_3_days")

    today_str = date.today().isoformat()
    last_posts = [p for p in log.get("posts", [])
                  if p.get("platform") == "gmb"]

    if frequency == "twice_daily":
        today_gmb = [p for p in last_posts if p.get("date") == today_str]
        return len(today_gmb) < 2

    elif frequency == "every_3_days":
        if not last_posts:
            return True
        last_date = datetime.fromisoformat(last_posts[-1]["date"]).date()
        return (date.today() - last_date).days >= 3

    return True


def run_social_post(topic: Dict, platforms: List[str], preview: bool = False):
    """Run a social media post for the given topic."""
    keyword = topic["keyword"]
    script  = os.path.join(BASE_DIR, "scripts", "social_publisher.py")
    img_gen = os.path.join(BASE_DIR, "scripts", "image_generator.py")

    if preview:
        print(f"  [PREVIEW] Would post about '{keyword}' to: {', '.join(platforms)}")
        return {"success": True, "preview": True}

    # Step 1: Generate banner image
    print(f"  🎨 Generating banner for '{keyword}'...")
    img_result = subprocess.run(
        [sys.executable, img_gen, "--title", keyword,
         "--keyword", keyword, "--type", "all"],
        cwd=BASE_DIR, capture_output=True, text=True
    )

    # Find generated image
    import glob
    slug = re.sub(r"[^a-z0-9]+", "-", keyword.lower())[:40]
    images = glob.glob(os.path.join(BASE_DIR, "output", "images", f"{slug}*.jpg"))
    image_path = images[0] if images else ""

    # Step 2: Publish to all platforms
    print(f"  📤 Publishing '{keyword}' to {', '.join(platforms)}...")
    cmd = [sys.executable, script,
           "--topic", keyword,
           "--keyword", keyword,
           "--platforms", ",".join(platforms)]
    if image_path:
        cmd.extend(["--image", image_path])

    result = subprocess.run(cmd, cwd=BASE_DIR, capture_output=True, text=True)
    return {"success": result.returncode == 0, "output": result.stdout}


def run_todays_schedule(preview: bool = False):
    """Run all scheduled posts for today."""
    config = load_config()
    log    = load_log()
    today  = date.today().isoformat()
    now    = datetime.now()

    print(f"\n🚀 Claude Auto SEO — Digital Marketing Scheduler")
    print(f"{'='*55}")
    print(f"Date: {today} | Time: {now.strftime('%H:%M')}")
    print(f"Mode: {'PREVIEW' if preview else 'LIVE'}")
    print(f"{'='*55}\n")

    social_cfg = config.get("social_media", {})
    posted_today = [p["keyword"] for p in log.get("posts", [])
                    if p.get("date") == today]

    # ── Instagram ──────────────────────────────────────────────────────────
    ig_cfg = social_cfg.get("instagram", {})
    if ig_cfg.get("enabled", False):
        ig_today = [p for p in log.get("posts", [])
                    if p.get("platform") == "instagram" and p.get("date") == today]
        if len(ig_today) < ig_cfg.get("posts_per_day", 1):
            topic = pick_random_topic(posted_today)
            if topic:
                print(f"📸 Instagram: '{topic['keyword']}'")
                r = run_social_post(topic, ["instagram"], preview)
                if r.get("success") and not preview:
                    log["posts"].append({"platform": "instagram",
                                         "keyword": topic["keyword"], "date": today})
                    posted_today.append(topic["keyword"])

    # ── Facebook ───────────────────────────────────────────────────────────
    fb_cfg = social_cfg.get("facebook", {})
    if fb_cfg.get("enabled", False):
        fb_today = [p for p in log.get("posts", [])
                    if p.get("platform") == "facebook" and p.get("date") == today]
        if len(fb_today) < fb_cfg.get("posts_per_day", 1):
            topic = pick_random_topic(posted_today)
            if topic:
                print(f"📘 Facebook: '{topic['keyword']}'")
                r = run_social_post(topic, ["facebook"], preview)
                if r.get("success") and not preview:
                    log["posts"].append({"platform": "facebook",
                                         "keyword": topic["keyword"], "date": today})
                    posted_today.append(topic["keyword"])

    # ── LinkedIn ───────────────────────────────────────────────────────────
    li_cfg = social_cfg.get("linkedin", {})
    if li_cfg.get("enabled", False):
        li_today = [p for p in log.get("posts", [])
                    if p.get("platform") == "linkedin" and p.get("date") == today]
        if len(li_today) < li_cfg.get("posts_per_day", 1):
            topic = pick_random_topic(posted_today)
            if topic:
                print(f"💼 LinkedIn: '{topic['keyword']}'")
                r = run_social_post(topic, ["linkedin"], preview)
                if r.get("success") and not preview:
                    log["posts"].append({"platform": "linkedin",
                                         "keyword": topic["keyword"], "date": today})

    # ── Twitter/X ──────────────────────────────────────────────────────────
    tw_cfg = social_cfg.get("twitter", {})
    if tw_cfg.get("enabled", False):
        tw_today = [p for p in log.get("posts", [])
                    if p.get("platform") == "twitter" and p.get("date") == today]
        posts_per_day = tw_cfg.get("posts_per_day", 3)
        if len(tw_today) < posts_per_day:
            for _ in range(posts_per_day - len(tw_today)):
                topic = pick_random_topic(posted_today)
                if topic:
                    print(f"🐦 Twitter/X: '{topic['keyword']}'")
                    r = run_social_post(topic, ["twitter"], preview)
                    if r.get("success") and not preview:
                        log["posts"].append({"platform": "twitter",
                                             "keyword": topic["keyword"], "date": today})
                    posted_today.append(topic["keyword"] if topic else "")

    # ── Pinterest ──────────────────────────────────────────────────────────
    pi_cfg = social_cfg.get("pinterest", {})
    if pi_cfg.get("enabled", False):
        pi_today = [p for p in log.get("posts", [])
                    if p.get("platform") == "pinterest" and p.get("date") == today]
        if len(pi_today) < pi_cfg.get("pins_per_day", 2):
            for _ in range(pi_cfg.get("pins_per_day", 2) - len(pi_today)):
                topic = pick_random_topic(posted_today)
                if topic:
                    print(f"📌 Pinterest: '{topic['keyword']}'")
                    r = run_social_post(topic, ["pinterest"], preview)
                    if r.get("success") and not preview:
                        log["posts"].append({"platform": "pinterest",
                                             "keyword": topic["keyword"], "date": today})

    # ── Google My Business ─────────────────────────────────────────────────
    gmb_cfg = social_cfg.get("gmb", {})
    if gmb_cfg.get("enabled", False) and should_post_gmb_today(log):
        gmb_count = gmb_cfg.get("posts_per_session", 1)
        for _ in range(gmb_count):
            topic = pick_random_topic(posted_today)
            if topic:
                print(f"📍 Google My Business: '{topic['keyword']}'")
                r = run_social_post(topic, ["gmb"], preview)
                if r.get("success") and not preview:
                    log["posts"].append({"platform": "gmb",
                                         "keyword": topic["keyword"], "date": today})

    if not preview:
        save_log(log)
        print(f"\n✅ Digital marketing run complete. Log: {LOG_FILE}")
    else:
        print("\n[PREVIEW MODE — No posts were published]")


def install_cron_jobs():
    """Install multiple cron jobs for different posting times."""
    script = os.path.abspath(__file__)

    # Random times for natural appearance
    morning   = random_time_in_window(8, 10)
    afternoon = random_time_in_window(13, 16)
    evening   = random_time_in_window(19, 21)

    m_h, m_m   = morning.split(":")
    a_h, a_m   = afternoon.split(":")
    e_h, e_m   = evening.split(":")

    jobs = [
        f"{m_m} {m_h} * * * cd {BASE_DIR} && {sys.executable} {script} --run >> {BASE_DIR}/data/dm-scheduler.log 2>&1",
        f"{a_m} {a_h} * * * cd {BASE_DIR} && {sys.executable} {script} --run >> {BASE_DIR}/data/dm-scheduler.log 2>&1",
        f"{e_m} {e_h} * * * cd {BASE_DIR} && {sys.executable} {script} --run >> {BASE_DIR}/data/dm-scheduler.log 2>&1",
    ]

    result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
    existing = result.stdout if result.returncode == 0 else ""

    if "dm_scheduler" in existing or "social_publisher" in existing:
        print("⚠️  Cron jobs may already exist. Check with: crontab -l")
        return

    new_crontab = existing.rstrip() + "\n" + "\n".join(jobs) + "\n"
    proc = subprocess.run(["crontab", "-"], input=new_crontab,
                          capture_output=True, text=True)

    if proc.returncode == 0:
        print("✅ Digital marketing cron jobs installed!")
        print(f"  Morning post:   {morning}")
        print(f"  Afternoon post: {afternoon}")
        print(f"  Evening post:   {evening}")
        print("View/edit with: crontab -e")
    else:
        print("❌ Cron install failed. Add manually:")
        for job in jobs:
            print(f"  {job}")


def show_status():
    log = load_log()
    today = date.today().isoformat()
    today_posts = [p for p in log.get("posts", []) if p.get("date") == today]

    print("\n📊 Digital Marketing Scheduler Status")
    print("="*50)
    print(f"Today's posts: {len(today_posts)}")
    for p in today_posts:
        print(f"  ✅ {p['platform']} — {p['keyword']}")

    print(f"\nTotal posts this week: {sum(1 for p in log.get('posts',[]) if p.get('date','') >= (date.today()-timedelta(7)).isoformat())}")
    print(f"Total all time: {len(log.get('posts', []))}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Claude Auto SEO — DM Scheduler")
    parser.add_argument("--run",          action="store_true", help="Run today's scheduled posts")
    parser.add_argument("--install-cron", action="store_true", help="Install cron jobs")
    parser.add_argument("--status",       action="store_true", help="Show schedule status")
    parser.add_argument("--preview",      action="store_true", help="Preview without posting")
    args = parser.parse_args()

    if args.run or args.preview:
        run_todays_schedule(preview=args.preview)
    elif args.install_cron:
        install_cron_jobs()
    elif args.status:
        show_status()
    else:
        parser.print_help()
