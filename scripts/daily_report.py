"""
Claude Auto SEO — Daily Activity Report Generator
Generates a complete daily report of everything the system did:
  - Blog posts written and published (with URLs)
  - Social media posts sent (with post IDs/URLs)
  - SEO fixes applied (with before/after)
  - Festival posts sent
  - External blog posts published
  - Keyword rankings checked
  - Errors and failures

Usage:
  python3 scripts/daily_report.py                    # Today's report
  python3 scripts/daily_report.py --date 2026-03-16  # Specific date
  python3 scripts/daily_report.py --send-email       # Email the report
  python3 scripts/daily_report.py --save-pdf         # Save as PDF
"""

import os
import json
import re
import smtplib
import subprocess
import sys
from datetime import datetime, date, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")


def load_json_log(filename: str) -> Dict:
    path = os.path.join(DATA_DIR, filename)
    if os.path.exists(path):
        try:
            with open(path) as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def load_list_log(filename: str) -> List:
    data = load_json_log(filename)
    if isinstance(data, list):
        return data
    return data.get("posts", data.get("runs", data.get("fixes", [])))


def filter_today(items: List, date_str: str, date_field: str = "date") -> List:
    """Filter list items to only those from today."""
    result = []
    for item in items:
        item_date = item.get(date_field, item.get("published_at", item.get("started", "")))
        if isinstance(item_date, str) and item_date.startswith(date_str):
            result.append(item)
    return result


def generate_daily_report(report_date: str = None) -> str:
    """Generate the complete daily activity report."""
    report_date = report_date or date.today().isoformat()
    site_name = os.environ.get("SITE_NAME", "Your Site")
    site_url  = os.environ.get("WP_URL", "https://yoursite.com")
    now       = datetime.now().strftime("%B %d, %Y at %H:%M")

    # Load all logs
    scheduler_log    = load_json_log("scheduler-log.json")
    social_log       = load_list_log("social-publish-log.json")
    external_log     = load_list_log("external-publish-log.json")
    festival_log     = load_list_log("festival-log.json")
    dm_log           = load_list_log("dm-scheduler-log.json")
    wp_backup        = load_json_log(f"wp-fix-backup-{report_date.replace('-', '')}.json")
    rankings_history = load_json_log("rankings-history.json")

    # Filter to today
    scheduler_runs     = filter_today(scheduler_log.get("runs", []), report_date, "started")
    scheduler_published = filter_today(scheduler_log.get("published", []), report_date)
    social_posts_today = filter_today(social_log if isinstance(social_log, list) else [], report_date, "published_at")
    external_today     = filter_today(external_log if isinstance(external_log, list) else [], report_date, "published_at")
    festival_today     = filter_today(festival_log if isinstance(festival_log, list) else [], report_date)
    dm_today           = filter_today(dm_log if isinstance(dm_log, list) else [], report_date)

    # Count successes / failures
    total_actions = 0
    total_success = 0

    lines = [
        f"# 📊 Daily SEO & Digital Marketing Report",
        f"**Site:** {site_name} ({site_url})",
        f"**Report Date:** {report_date}",
        f"**Generated:** {now}",
        f"",
        "---",
        "",
    ]

    # ── SECTION 1: BLOG POSTS ────────────────────────────────────────────────
    lines.append("## ✍️ Blog Posts Written & Published")
    lines.append("")

    if scheduler_runs:
        for run in scheduler_runs:
            total_actions += 1
            status = run.get("status", "unknown")
            emoji = "✅" if status in ("published", "review_required") else "❌"
            if status != "failed":
                total_success += 1

            lines.append(f"### {emoji} {run.get('topic', 'Unknown Topic')}")
            lines.append(f"- **Status:** {status}")
            lines.append(f"- **SEO Score:** {run.get('seo_score', 'N/A')}/100")
            if run.get("file"):
                lines.append(f"- **File:** `{run.get('file')}`")
            if status == "published":
                lines.append(f"- **WordPress:** Draft created — review at {site_url}/wp-admin")
            elif status == "review_required":
                lines.append(f"- **Location:** `review-required/` — needs your approval before publishing")
            lines.append(f"- **Started:** {run.get('started', 'N/A')[:16]}")
            lines.append("")
    else:
        lines.append("_No blog posts generated today._")
        lines.append("")

    # ── SECTION 2: SOCIAL MEDIA ──────────────────────────────────────────────
    lines.append("## 📱 Social Media Posts")
    lines.append("")

    all_social = social_posts_today + dm_today
    if all_social:
        # Group by platform
        by_platform = {}
        for post in all_social:
            platform = post.get("platform", "unknown")
            by_platform.setdefault(platform, []).append(post)

        for platform, posts in by_platform.items():
            lines.append(f"### {_platform_emoji(platform)} {platform.title()}")
            for post in posts:
                total_actions += 1
                total_success += 1
                lines.append(f"- **Topic:** {post.get('topic', post.get('keyword', 'N/A'))}")
                if post.get("url") and post["url"] != "":
                    lines.append(f"- **URL:** {post.get('url')}")
                if post.get("post_id"):
                    lines.append(f"- **Post ID:** {post.get('post_id')}")
                lines.append(f"- **Time:** {post.get('published_at', 'N/A')[:16]}")
            lines.append("")
    else:
        lines.append("_No social media posts today._")
        lines.append("")

    # ── SECTION 3: FESTIVAL POSTS ────────────────────────────────────────────
    lines.append("## 🎊 Festival Posts")
    lines.append("")

    if festival_today:
        for fest in festival_today:
            total_actions += 1
            total_success += 1
            success = fest.get("platforms_success", 0)
            total_p = fest.get("platforms_total", 0)
            lines.append(f"- **{fest.get('festival', 'Festival')}** — {success}/{total_p} platforms ✅")
            lines.append(f"  Regions: {', '.join(fest.get('regions', []))}")
        lines.append("")
    else:
        lines.append("_No festivals today._")
        lines.append("")

    # ── SECTION 4: EXTERNAL BLOG POSTS ──────────────────────────────────────
    lines.append("## 🌐 External Blog Posts")
    lines.append("")

    if external_today:
        for post in external_today:
            total_actions += 1
            total_success += 1
            lines.append(f"### ✅ {post.get('platform', 'Platform').title()}")
            lines.append(f"- **Article:** {post.get('title', 'N/A')}")
            if post.get("published_url"):
                lines.append(f"- **URL:** {post.get('published_url')}")
            if post.get("canonical"):
                lines.append(f"- **Canonical → Your Site:** {post.get('canonical')}")
            lines.append("")
    else:
        lines.append("_No external posts today._")
        lines.append("")

    # ── SECTION 5: WordPress SEO FIXES ──────────────────────────────────────
    lines.append("## 🔧 WordPress SEO Fixes")
    lines.append("")

    if wp_backup and wp_backup.get("fixes"):
        fixes = wp_backup["fixes"]
        fix_types = {}
        for fix in fixes:
            ft = fix.get("fix_type", "other")
            fix_types[ft] = fix_types.get(ft, 0) + 1

        total_actions += len(fixes)
        total_success += len(fixes)
        lines.append(f"**{len(fixes)} fixes applied today:**")
        for fix_type, count in fix_types.items():
            lines.append(f"- {fix_type.replace('_', ' ').title()}: {count} items")
        lines.append(f"- **Backup file:** `data/wp-fix-backup-{report_date.replace('-', '')}.json`")
        lines.append(f"- **Rollback:** `python3 scripts/wp_seo_fixer.py --rollback`")
        lines.append("")
    else:
        lines.append("_No WordPress SEO fixes applied today._")
        lines.append("")

    # ── SECTION 6: KEYWORD RANKINGS ─────────────────────────────────────────
    lines.append("## 📈 Keyword Rankings")
    lines.append("")

    tracked_keywords = rankings_history.get("tracked_keywords", [])
    if tracked_keywords:
        recent = []
        for kw in tracked_keywords:
            history = kw.get("history", [])
            if history and history[-1].get("date") == report_date:
                recent.append(kw)

        if recent:
            lines.append("| Keyword | Position | Best Ever | Change |")
            lines.append("|---|---|---|---|")
            for kw in recent[:15]:
                latest = kw["history"][-1]
                pos = latest.get("position", "N/A")
                best = kw.get("best_position", "N/A")
                change = ""
                if len(kw["history"]) >= 2:
                    prev = kw["history"][-2].get("position", pos)
                    diff = prev - pos if isinstance(prev, (int, float)) and isinstance(pos, (int, float)) else 0
                    change = f"▲{diff}" if diff > 0 else f"▼{abs(diff)}" if diff < 0 else "→"
                lines.append(f"| {kw['keyword']} | #{pos} | #{best} | {change} |")
            lines.append("")
        else:
            lines.append("_Rankings not checked today._")
            lines.append("")
    else:
        lines.append("_No keywords being tracked yet. Run `/seo rank-track` to start._")
        lines.append("")

    # ── SECTION 7: ERRORS & WARNINGS ────────────────────────────────────────
    lines.append("## ⚠️ Errors & Warnings")
    lines.append("")

    errors = []
    for run in scheduler_runs:
        if run.get("status") == "failed":
            errors.append(f"Blog post FAILED: {run.get('topic', 'Unknown')}")

    if errors:
        for err in errors:
            lines.append(f"- 🔴 {err}")
    else:
        lines.append("✅ No errors today.")
    lines.append("")

    # ── SECTION 8: SUMMARY SCORECARD ────────────────────────────────────────
    success_rate = int(total_success / max(total_actions, 1) * 100)

    lines += [
        "---",
        "",
        "## 📊 Today's Scorecard",
        "",
        f"| Metric | Count |",
        f"|---|---|",
        f"| Blog posts created | {len(scheduler_runs)} |",
        f"| Social media posts | {len(all_social)} |",
        f"| Festival posts | {len(festival_today)} |",
        f"| External blog posts | {len(external_today)} |",
        f"| WP SEO fixes | {len(wp_backup.get('fixes', [])) if wp_backup else 0} |",
        f"| Total actions | {total_actions} |",
        f"| Success rate | {success_rate}% |",
        "",
        "## ✅ Action Items for Review",
        "",
    ]

    # Generate specific action items
    for run in scheduler_runs:
        if run.get("status") == "review_required":
            lines.append(f"- [ ] Review blog post: `{run.get('file', 'check review-required/')}` — then publish or edit")

    if not all_social and not festival_today:
        lines.append("- [ ] Check social media credentials in `.env` — no posts were made today")

    lines += [
        "",
        "---",
        f"*Report generated by Claude Auto SEO — {now}*",
        f"*Site: {site_name} | {site_url}*",
    ]

    return "\n".join(lines)


def _platform_emoji(platform: str) -> str:
    return {"instagram": "📸", "facebook": "📘", "linkedin": "💼",
            "twitter": "🐦", "pinterest": "📌", "gmb": "📍",
            "tiktok": "🎵", "medium": "✍️", "reddit": "🔴"}.get(platform, "📱")


def save_report(report_content: str, report_date: str) -> str:
    """Save report to reports/ directory."""
    os.makedirs(REPORTS_DIR, exist_ok=True)
    path = os.path.join(REPORTS_DIR, f"daily-report-{report_date}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(report_content)
    return path


def send_email_report(report_content: str, report_date: str):
    """Send the daily report via email."""
    smtp_host  = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    smtp_port  = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user  = os.environ.get("SMTP_USER", "")
    smtp_pass  = os.environ.get("SMTP_PASS", "")
    to_email   = os.environ.get("NOTIFICATION_EMAIL", smtp_user)
    site_name  = os.environ.get("SITE_NAME", "Claude Auto SEO")

    if not smtp_user or not smtp_pass:
        print("⚠️  Email not configured. Add SMTP_USER, SMTP_PASS, NOTIFICATION_EMAIL to .env")
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"📊 Daily SEO Report — {site_name} — {report_date}"
    msg["From"]    = smtp_user
    msg["To"]      = to_email

    # Plain text version
    msg.attach(MIMEText(report_content, "plain"))

    # Simple HTML version
    html = f"""
<html><body style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px;">
<h1 style="color: #0f3460;">📊 Daily SEO Report</h1>
<p><strong>Site:</strong> {os.environ.get('SITE_NAME', '')} | <strong>Date:</strong> {report_date}</p>
<hr>
<pre style="background: #f5f5f5; padding: 20px; border-radius: 8px; white-space: pre-wrap;">{report_content}</pre>
<hr>
<p style="color: #888; font-size: 12px;">Generated by Claude Auto SEO</p>
</body></html>"""
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, to_email, msg.as_string())
        print(f"✅ Report emailed to: {to_email}")
    except Exception as e:
        print(f"❌ Email failed: {e}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Claude Auto SEO — Daily Report")
    parser.add_argument("--date",       default=None, help="Report date (YYYY-MM-DD)")
    parser.add_argument("--send-email", action="store_true", help="Email the report")
    parser.add_argument("--save-pdf",   action="store_true", help="Save as PDF")
    parser.add_argument("--print-only", action="store_true", help="Print to console only")
    args = parser.parse_args()

    report_date = args.date or date.today().isoformat()
    report = generate_daily_report(report_date)

    # Always save as markdown
    saved_path = save_report(report, report_date)
    print(report)
    print(f"\n✅ Report saved: {saved_path}")

    if args.send_email:
        send_email_report(report, report_date)

    if args.save_pdf:
        pdf_script = os.path.join(BASE_DIR, "scripts", "generate_pdf_report.py")
        subprocess.run([sys.executable, pdf_script, saved_path], cwd=BASE_DIR)
