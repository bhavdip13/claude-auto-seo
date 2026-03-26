"""
Claude Auto SEO — Master Cron Installer
ONE COMMAND to install ALL automation:
  - Daily blog post at 9:00 AM
  - Social media posts at 9:30 AM, 1:00 PM, 7:00 PM (random minutes)
  - Festival posts at 1:00 AM
  - Daily email report at 8:00 PM
  - Weekly SEO digest on Monday 8:00 AM
  - Keyword ranking check every Sunday 10:00 AM

Usage:
  python3 scripts/setup_crons.py --install    # Install all cron jobs
  python3 scripts/setup_crons.py --remove     # Remove all cron jobs
  python3 scripts/setup_crons.py --status     # Show installed cron jobs
  python3 scripts/setup_crons.py --test-all   # Test every module (dry run)
"""

import os
import sys
import json
import random
import subprocess
from dotenv import load_dotenv

load_dotenv()

BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
DATA_DIR    = os.path.join(BASE_DIR, "data")
PYTHON      = sys.executable
MARKER      = "# Claude Auto SEO"


def load_config():
    path = os.path.join(BASE_DIR, "config", "schedule.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}


def s(script: str) -> str:
    return os.path.join(SCRIPTS_DIR, script)


def log(script: str) -> str:
    return os.path.join(DATA_DIR, f"{script.replace('.py','')}.log")


def build_cron_jobs() -> list:
    """Build list of all cron jobs with random minutes for natural appearance."""
    # Random minutes so posts don't all land on the hour
    m1 = random.randint(0, 15)   # Blog post
    m2 = random.randint(16, 35)  # Morning social
    m3 = random.randint(0, 20)   # Afternoon social
    m4 = random.randint(21, 45)  # Evening social
    m5 = random.randint(0, 59)   # Festival (exact 1AM requested)
    m6 = random.randint(0, 30)   # Daily report
    m7 = random.randint(0, 30)   # Weekly digest
    m8 = random.randint(0, 59)   # Ranking check

    jobs = [
        # Daily blog post — 9 AM
        (f"{m1} 9 * * *",
         f"cd {BASE_DIR} && {PYTHON} {s('scheduler.py')} --run-now >> {log('scheduler')} 2>&1",
         "Daily blog post at 9 AM"),

        # Social media — Morning (9:30 AM)
        (f"{m2} 9 * * *",
         f"cd {BASE_DIR} && {PYTHON} {s('dm_scheduler.py')} --run >> {log('dm_scheduler')} 2>&1",
         "Morning social media posts"),

        # Social media — Afternoon (1 PM)
        (f"{m3} 13 * * *",
         f"cd {BASE_DIR} && {PYTHON} {s('dm_scheduler.py')} --run >> {log('dm_scheduler')} 2>&1",
         "Afternoon social media posts"),

        # Social media — Evening (7 PM)
        (f"{m4} 19 * * *",
         f"cd {BASE_DIR} && {PYTHON} {s('dm_scheduler.py')} --run >> {log('dm_scheduler')} 2>&1",
         "Evening social media posts"),

        # Festival posts — 1:00 AM every day
        (f"0 1 * * *",
         f"cd {BASE_DIR} && {PYTHON} {s('festival_poster.py')} --post-now >> {log('festival_poster')} 2>&1",
         "Festival posts at 1 AM"),

        # Daily email report — 8:00 PM
        (f"{m6} 20 * * *",
         f"cd {BASE_DIR} && {PYTHON} {s('daily_report.py')} --send-email >> {log('daily_report')} 2>&1",
         "Daily email report at 8 PM"),

        # Weekly SEO digest — Monday 8 AM
        (f"{m7} 8 * * 1",
         f"cd {BASE_DIR} && {PYTHON} {s('daily_report.py')} --send-email >> {log('daily_report')} 2>&1",
         "Weekly SEO digest Monday 8 AM"),

        # Keyword ranking check — Sunday 10 AM
        (f"{m8} 10 * * 0",
         f"cd {BASE_DIR} && {PYTHON} {s('keyword_finder.py')} --quick-wins-only >> {log('keyword_finder')} 2>&1",
         "Weekly keyword ranking check"),
    ]

    return jobs


def install_all_crons():
    """Install all automation cron jobs."""
    os.makedirs(DATA_DIR, exist_ok=True)

    # Get existing crontab
    result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
    existing = result.stdout if result.returncode == 0 else ""

    # Remove any existing Claude Auto SEO entries
    lines = [l for l in existing.split("\n")
             if MARKER not in l and "claude-auto-seo" not in l.lower()]
    clean_existing = "\n".join(lines).strip()

    # Build new jobs
    jobs = build_cron_jobs()
    new_lines = [f"\n{MARKER} — Installed {__import__('datetime').datetime.now().strftime('%Y-%m-%d')}"]
    for schedule, command, label in jobs:
        new_lines.append(f"{MARKER} — {label}")
        new_lines.append(f"{schedule} {command}")

    full_crontab = clean_existing + "\n" + "\n".join(new_lines) + "\n"

    proc = subprocess.run(["crontab", "-"], input=full_crontab, capture_output=True, text=True)

    if proc.returncode == 0:
        print("\n✅ ALL CRON JOBS INSTALLED SUCCESSFULLY!")
        print("="*60)
        for schedule, command, label in jobs:
            print(f"  ✓ {label}")
            print(f"    Schedule: {schedule}")
        print("\nVerify: crontab -l")
        print("Remove: python3 scripts/setup_crons.py --remove")
        return True
    else:
        print(f"❌ Cron install failed: {proc.stderr}")
        print("   Try manually: crontab -e")
        for schedule, command, label in jobs:
            print(f"   {schedule} {command}")
        return False


def remove_all_crons():
    """Remove all Claude Auto SEO cron jobs."""
    result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
    if result.returncode != 0:
        print("No crontab found.")
        return

    lines = [l for l in result.stdout.split("\n")
             if MARKER not in l and "claude-auto-seo" not in l.lower()]
    new_crontab = "\n".join(lines).strip() + "\n"

    subprocess.run(["crontab", "-"], input=new_crontab, capture_output=True, text=True)
    print("✅ All Claude Auto SEO cron jobs removed.")


def show_status():
    """Show which cron jobs are currently installed."""
    result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
    if result.returncode != 0:
        print("No crontab installed.")
        return

    seo_jobs = [l for l in result.stdout.split("\n")
                if "claude-auto-seo" in l.lower() or any(
                    s in l for s in ["scheduler.py", "dm_scheduler.py",
                                     "festival_poster.py", "daily_report.py",
                                     "keyword_finder.py"])]

    if seo_jobs:
        print(f"\n✅ Claude Auto SEO cron jobs installed ({len(seo_jobs)} jobs):")
        for job in seo_jobs:
            print(f"  {job}")
    else:
        print("⚠️  No Claude Auto SEO cron jobs found.")
        print("   Run: python3 scripts/setup_crons.py --install")


def test_all_modules(dry_run: bool = True):
    """Test every module to verify it's working."""
    print("\n🧪 Claude Auto SEO — Module Test Suite")
    print("="*60)
    mode = "DRY RUN (preview only)" if dry_run else "LIVE (will post/publish)"
    print(f"Mode: {mode}\n")

    tests = [
        ("WordPress Connection", ["wp_seo_fixer.py", "--scan"],
         "Checks if WordPress credentials work"),
        ("Image Generator", ["image_generator.py", "--title", "Test Banner", "--keyword", "seo", "--type", "blog"],
         "Creates a test banner image"),
        ("Festival Poster (preview)", ["festival_poster.py", "--preview"],
         "Shows festival content without posting"),
        ("Social Media (preview)", ["dm_scheduler.py", "--preview"],
         "Shows social posts without posting"),
        ("Daily Report", ["daily_report.py", "--print-only"],
         "Generates today's activity report"),
        ("Keyword Finder", ["keyword_finder.py", "--quick-wins-only"],
         "Checks GSC keyword data"),
        ("Directory Manager", ["directory_manager.py", "--status"],
         "Shows directory submission status"),
    ]

    results = []
    for test_name, cmd_args, description in tests:
        print(f"Testing: {test_name}")
        print(f"  → {description}")

        script = os.path.join(SCRIPTS_DIR, cmd_args[0])
        full_cmd = [PYTHON, script] + cmd_args[1:]

        try:
            result = subprocess.run(
                full_cmd, capture_output=True, text=True,
                timeout=30, cwd=BASE_DIR
            )
            success = result.returncode == 0
            status = "✅ PASS" if success else "❌ FAIL"
            results.append((test_name, success, result.stderr[:100] if not success else ""))
            print(f"  {status}")
            if not success and result.stderr:
                print(f"  Error: {result.stderr[:150]}")
        except subprocess.TimeoutExpired:
            results.append((test_name, False, "Timeout"))
            print(f"  ⏱️  TIMEOUT (30s)")
        except Exception as e:
            results.append((test_name, False, str(e)))
            print(f"  ❌ ERROR: {e}")
        print()

    # Summary
    passed = sum(1 for _, ok, _ in results if ok)
    total = len(results)
    print(f"{'='*60}")
    print(f"Results: {passed}/{total} tests passed")

    if passed < total:
        print("\n⚠️  Failed tests:")
        for name, ok, err in results:
            if not ok:
                print(f"  ✗ {name}: {err}")
        print("\nFix credentials in .env and re-run: python3 scripts/setup_crons.py --test-all")
    else:
        print("🎉 All tests passed! System is ready.")
        print("Run: python3 scripts/setup_crons.py --install")


def check_env_credentials():
    """Check which credentials are configured."""
    print("\n🔑 Credential Status")
    print("="*60)

    checks = [
        ("ANTHROPIC_API_KEY",   "Claude AI (content writing)"),
        ("WP_URL",              "WordPress URL"),
        ("WP_USERNAME",         "WordPress username"),
        ("WP_APP_PASSWORD",     "WordPress App Password"),
        ("META_ACCESS_TOKEN",   "Facebook + Instagram"),
        ("FACEBOOK_PAGE_ID",    "Facebook Page ID"),
        ("INSTAGRAM_USER_ID",   "Instagram User ID"),
        ("TWITTER_API_KEY",     "Twitter/X"),
        ("LINKEDIN_ACCESS_TOKEN", "LinkedIn"),
        ("PINTEREST_ACCESS_TOKEN", "Pinterest"),
        ("GOOGLE_GMB_ACCESS_TOKEN", "Google My Business"),
        ("GMB_LOCATION_ID",     "GMB Location ID"),
        ("DATAFORSEO_LOGIN",    "DataForSEO (SERP data)"),
        ("UNSPLASH_ACCESS_KEY", "Unsplash (banner images)"),
        ("SMTP_USER",           "Email (daily reports)"),
        ("NOTIFICATION_EMAIL",  "Report recipient email"),
    ]

    configured = 0
    for key, label in checks:
        val = os.environ.get(key, "")
        if val and val not in ("your_wordpress_username", "xxxx xxxx xxxx xxxx xxxx xxxx", ""):
            print(f"  ✅ {label}")
            configured += 1
        else:
            print(f"  ⬜ {label} — not set")

    print(f"\n{configured}/{len(checks)} credentials configured")
    if configured < 4:
        print("\n⚠️  Configure .env before running. See docs/COMPLETE-SETUP-GUIDE.md")
    elif configured < 10:
        print("\n⚡ Basic setup ready. Add more credentials to unlock all features.")
    else:
        print("\n🎉 Excellent! Most features are configured.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="Claude Auto SEO — Master Setup & Cron Installer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Quick Start:
  1. python3 scripts/auto_configure.py --domain yoursite.com
  2. Edit .env with your API credentials
  3. python3 scripts/setup_crons.py --check-credentials
  4. python3 scripts/setup_crons.py --test-all
  5. python3 scripts/setup_crons.py --install
        """
    )
    parser.add_argument("--install",            action="store_true", help="Install all cron jobs")
    parser.add_argument("--remove",             action="store_true", help="Remove all cron jobs")
    parser.add_argument("--status",             action="store_true", help="Show cron job status")
    parser.add_argument("--test-all",           action="store_true", help="Test all modules (dry run)")
    parser.add_argument("--check-credentials",  action="store_true", help="Check .env credentials")
    args = parser.parse_args()

    if args.install:
        install_all_crons()
    elif args.remove:
        remove_all_crons()
    elif args.status:
        show_status()
    elif args.test_all:
        test_all_modules()
    elif args.check_credentials:
        check_env_credentials()
    else:
        check_env_credentials()
        print("\nRun with --install to start automation.")
        print("Run with --test-all to verify everything works.")
        parser.print_help()
