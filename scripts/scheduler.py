"""
Claude Auto SEO — Content Scheduler
Automates daily/weekly content generation and publishing.

Usage:
  python3 scripts/scheduler.py --run-now          # Generate and queue one post
  python3 scripts/scheduler.py --install-cron     # Set up daily cron job
  python3 scripts/scheduler.py --status           # Show schedule status
  python3 scripts/scheduler.py --queue            # Show topic queue
"""

import os
import sys
import json
import subprocess
from datetime import datetime, date
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR    = os.path.join(BASE_DIR, "data")
CONFIG_FILE = os.path.join(BASE_DIR, "config", "schedule.json")
QUEUE_FILE  = os.path.join(BASE_DIR, "topics", "queue.txt")
LOG_FILE    = os.path.join(DATA_DIR, "scheduler-log.json")


def load_config() -> Dict:
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {
        "wordpress_internal": {
            "enabled": True,
            "frequency": "daily",
            "time": "09:00",
            "posts_per_run": 1,
            "auto_publish": False,
            "review_required": True,
        },
        "external_platforms": {
            "medium": {"enabled": False},
            "reddit": {"enabled": False},
        }
    }


def load_queue() -> List[str]:
    os.makedirs(os.path.dirname(QUEUE_FILE), exist_ok=True)
    if not os.path.exists(QUEUE_FILE):
        return []
    with open(QUEUE_FILE) as f:
        lines = [l.strip() for l in f.readlines() if l.strip() and not l.startswith("#")]
    return lines


def pop_topic() -> Optional[str]:
    """Get and remove the next topic from the queue."""
    queue = load_queue()
    if not queue:
        return None
    topic = queue[0]
    with open(QUEUE_FILE, "w") as f:
        f.write("\n".join(queue[1:]) + "\n")
    return topic


def load_log() -> Dict:
    os.makedirs(DATA_DIR, exist_ok=True)
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            return json.load(f)
    return {"runs": [], "published": []}


def save_log(log: Dict):
    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)


def is_already_published(topic: str) -> bool:
    """Check if a topic has already been published."""
    log = load_log()
    published_topics = [p.get("topic", "").lower() for p in log.get("published", [])]
    return topic.lower() in published_topics


def generate_topic_from_keywords() -> Optional[str]:
    """Auto-generate a topic from target keywords."""
    kw_file = os.path.join(BASE_DIR, "context", "target-keywords.md")
    if not os.path.exists(kw_file):
        return None

    with open(kw_file) as f:
        content = f.read()

    # Extract keywords marked as "not written"
    import re
    not_written = re.findall(r"\|\s*([^|]+)\s*\|[^|]*\|[^|]*\|\s*not written", content, re.IGNORECASE)
    if not_written:
        return not_written[0].strip()

    return None


def run_claude_command(command: str) -> bool:
    """Run a Claude Code command via subprocess."""
    try:
        result = subprocess.run(
            ["claude", "--print", command],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout per article
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f"Error running Claude command: {e}")
        return False


def run_now(dry_run: bool = False):
    """Generate and optionally publish one post."""
    config = load_config()
    log = load_log()

    # Get topic
    topic = pop_topic()
    if not topic:
        print("Queue empty — auto-generating topic from keywords...")
        topic = generate_topic_from_keywords()
    if not topic:
        print("❌ No topics available. Add topics to topics/queue.txt")
        sys.exit(1)

    if is_already_published(topic):
        print(f"⚠️  Topic already published: {topic}. Skipping.")
        return

    print(f"\n🚀 Claude Auto SEO Scheduler")
    print(f"{'='*50}")
    print(f"Topic: {topic}")
    print(f"Date:  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Mode:  {'DRY RUN' if dry_run else 'LIVE'}")
    print(f"{'='*50}\n")

    if dry_run:
        print(f"[DRY RUN] Would generate article: '{topic}'")
        print(f"[DRY RUN] Would run: /research {topic}")
        print(f"[DRY RUN] Would run: /write {topic}")
        print(f"[DRY RUN] Would run: /scrub [draft file]")
        if config["wordpress_internal"].get("auto_publish"):
            print(f"[DRY RUN] Would publish to WordPress")
        return

    # Log run start
    run_entry = {"topic": topic, "started": datetime.now().isoformat(), "status": "running"}
    log["runs"].append(run_entry)
    save_log(log)

    print(f"Step 1/4: Researching '{topic}'...")
    success = run_claude_command(f"/research {topic}")
    if not success:
        print(f"⚠️  Research step failed — proceeding with write anyway")

    print(f"Step 2/4: Writing article...")
    success = run_claude_command(f"/write {topic}")
    if not success:
        print(f"❌ Write step failed for topic: {topic}")
        run_entry["status"] = "failed"
        save_log(log)
        return

    print(f"Step 3/4: Running scrub (removing AI patterns)...")
    # Find the draft file
    import glob
    slug = topic.lower().replace(" ", "-")[:30]
    today = date.today().isoformat()
    drafts = glob.glob(os.path.join(BASE_DIR, "drafts", f"*{today}*.md"))
    draft_file = drafts[-1] if drafts else None

    if draft_file:
        run_claude_command(f"/scrub {draft_file}")

    print(f"Step 4/4: Quality check...")
    # Check SEO score from agent report
    reports = glob.glob(os.path.join(BASE_DIR, "drafts", f"reports-*{today}*.md"))
    seo_score = 0
    if reports:
        with open(reports[-1]) as f:
            content = f.read()
        import re
        score_match = re.search(r"SEO Score[:\s]+(\d+)", content)
        if score_match:
            seo_score = int(score_match.group(1))

    print(f"\n✅ Article generated!")
    if draft_file:
        print(f"   File: {os.path.relpath(draft_file, BASE_DIR)}")
    print(f"   SEO Score: {seo_score}/100")

    # Publish or queue for review
    wp_config = config.get("wordpress_internal", {})
    if wp_config.get("auto_publish") and seo_score >= 75:
        if draft_file:
            print("\n📤 Auto-publishing to WordPress...")
            success = run_claude_command(f"/publish-draft {draft_file}")
            if success:
                print("✅ Published!")
                run_entry["status"] = "published"
            else:
                print("⚠️  Publish failed — saved as draft for manual publish")
                run_entry["status"] = "publish_failed"
    else:
        if seo_score < 75:
            print(f"\n⚠️  SEO score ({seo_score}) below 75 threshold — saved for review")
        else:
            print(f"\n📋 Saved to review-required/ for manual review before publishing")

        if draft_file:
            review_dir = os.path.join(BASE_DIR, "review-required")
            os.makedirs(review_dir, exist_ok=True)
            import shutil
            dest = os.path.join(review_dir, os.path.basename(draft_file))
            shutil.copy2(draft_file, dest)
            print(f"   Location: {os.path.relpath(dest, BASE_DIR)}")
        run_entry["status"] = "review_required"

    run_entry["completed"] = datetime.now().isoformat()
    run_entry["seo_score"] = seo_score
    if draft_file:
        run_entry["file"] = os.path.relpath(draft_file, BASE_DIR)

    log["published"].append({"topic": topic, "date": today, "seo_score": seo_score})
    save_log(log)


def install_cron():
    """Install a daily cron job."""
    script_path = os.path.abspath(__file__)
    cron_line = f"0 9 * * * cd {BASE_DIR} && python3 {script_path} --run-now >> {DATA_DIR}/scheduler.log 2>&1"

    print("Installing cron job...")
    print(f"Cron entry: {cron_line}")

    # Read existing crontab
    result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
    existing = result.stdout if result.returncode == 0 else ""

    if "wp_seo_fixer" in existing or "scheduler.py" in existing:
        print("⚠️  Cron job already exists. Remove manually with: crontab -e")
        return

    new_crontab = existing.rstrip() + "\n" + cron_line + "\n"
    proc = subprocess.run(["crontab", "-"], input=new_crontab, capture_output=True, text=True)

    if proc.returncode == 0:
        print("✅ Cron job installed! Will run daily at 9:00 AM.")
        print("   View with: crontab -l")
        print("   Edit with: crontab -e")
    else:
        print(f"❌ Failed to install cron: {proc.stderr}")
        print(f"   Manually add to crontab:\n   {cron_line}")


def show_status():
    config = load_config()
    log = load_log()
    queue = load_queue()

    print("\n📅 Claude Auto SEO — Scheduler Status")
    print("="*50)
    print(f"Enabled: {config['wordpress_internal'].get('enabled', False)}")
    print(f"Frequency: {config['wordpress_internal'].get('frequency', 'daily')}")
    print(f"Auto-publish: {config['wordpress_internal'].get('auto_publish', False)}")
    print(f"Review required: {config['wordpress_internal'].get('review_required', True)}")
    print(f"\nQueue: {len(queue)} topics")
    if queue:
        print(f"Next topic: {queue[0]}")
    print(f"\nTotal published: {len(log.get('published', []))}")
    recent = log.get("runs", [])[-5:]
    if recent:
        print("\nRecent runs:")
        for r in reversed(recent):
            print(f"  {r.get('started','')[:10]} — {r.get('topic','')} — {r.get('status','')}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Claude Auto SEO Scheduler")
    parser.add_argument("--run-now",       action="store_true", help="Generate one post now")
    parser.add_argument("--install-cron",  action="store_true", help="Install daily cron job")
    parser.add_argument("--status",        action="store_true", help="Show scheduler status")
    parser.add_argument("--queue",         action="store_true", help="Show topic queue")
    parser.add_argument("--dry-run",       action="store_true", help="Simulate without writing")
    args = parser.parse_args()

    if args.run_now:
        run_now(dry_run=args.dry_run)
    elif args.install_cron:
        install_cron()
    elif args.status:
        show_status()
    elif args.queue:
        q = load_queue()
        print(f"Topic queue ({len(q)} items):")
        for i, t in enumerate(q[:20], 1):
            print(f"  {i}. {t}")
    else:
        parser.print_help()
