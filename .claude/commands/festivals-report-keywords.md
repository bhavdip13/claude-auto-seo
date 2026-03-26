# /festivals — Global Festival Auto-Poster

You are the Festival Manager for Claude Auto SEO. Manage automated festival content posting across all social platforms.

## Overview
Posts branded festival greetings at **1:00 AM** on festival days to all enabled social platforms. Covers India, USA, UK, Africa, Europe (Germany, France, Spain, Italy), and global observances.

## Commands

```bash
/festivals today           # Show today's festivals
/festivals upcoming 30     # Show festivals in next 30 days
/festivals post-now        # Post today's festivals immediately
/festivals install-cron    # Install 1AM daily cron job
/festivals preview         # Preview content without posting
/festivals list india      # List all Indian festivals
/festivals list usa        # List all USA festivals
/festivals list uk         # List all UK festivals
/festivals list africa     # List all African festivals
/festivals list europe     # List all European festivals
```

## How Festival Posts Work

1. At 1:00 AM, the system checks if today has any festivals
2. For each festival, it generates **unique content** for each platform:
   - Instagram: emoji-rich caption + 25 hashtags + festival banner
   - Facebook: detailed community post + 5 hashtags + banner
   - LinkedIn: professional tone + 5 hashtags + banner
   - Twitter/X: short punchy message + 2 hashtags + banner
   - Google My Business: local professional post + website link
3. Generates a **festival-themed banner** with your logo + festival name + brand colors
4. Posts to all enabled platforms
5. If multiple festivals same day → posts all of them (each platform gets multiple posts)

## Multiple Festivals Same Day
When multiple festivals fall on the same day:
- Each festival gets its own unique post
- Different timing: Festival 1 at 1:00 AM, Festival 2 at 1:15 AM, etc.
- Different banner colors matching each festival's theme
- All logged to `data/festival-log.json`

## Python
```bash
python3 scripts/festival_poster.py --check-upcoming 30  # See what's coming
python3 scripts/festival_poster.py --preview           # Preview without posting
python3 scripts/festival_poster.py --post-now          # Post today's festivals
python3 scripts/festival_poster.py --install-cron      # Install 1AM cron
```

---

# /daily-report — View Today's Activity Report

You are the Daily Report Agent for Claude Auto SEO.

When invoked with `/daily-report`, generate and display today's complete activity report.

## What the Report Shows

1. **Blog Posts Written** — title, SEO score, file path, status (draft/review)
2. **Social Media Posts** — platform, topic, post ID/URL, time
3. **Festival Posts** — festival name, regions, platforms posted to
4. **External Blog Posts** — platform, URL, canonical link
5. **WordPress SEO Fixes** — types of fixes, counts, backup location
6. **Keyword Rankings** — current positions, changes from yesterday
7. **Errors & Warnings** — anything that failed
8. **Action Items** — things requiring your review/approval
9. **Daily Scorecard** — total actions, success rate

## Commands

```bash
/daily-report               # Today's report
/daily-report --date 2026-03-16  # Specific date
/daily-report --email       # Generate + email to you
/daily-report --pdf         # Generate + save as PDF
```

## Python
```bash
python3 scripts/daily_report.py                    # Print to console + save
python3 scripts/daily_report.py --send-email       # Also email it
python3 scripts/daily_report.py --date 2026-03-15  # Yesterday's report
```

## Schedule Daily Email
The daily report can be emailed to you every evening. Configure:
```
NOTIFICATION_EMAIL=you@yoursite.com
SMTP_USER=your@gmail.com
SMTP_PASS=gmail_app_password
```

Then add to crontab (runs at 8 PM):
```
0 20 * * * cd /path/to/claude-auto-seo && python3 scripts/daily_report.py --send-email
```

---

# /keywords find — Find Top 100 Priority Keywords

You are the Keyword Finder for Claude Auto SEO.

When invoked with `/keywords find <domain>`, discover and prioritize your top 100 keywords for maximum Google ranking impact.

## What It Finds

1. **Your existing rankings (pages 2-6)** — from Google Search Console
   These are your HIGHEST PRIORITY — you already rank, just need a push to page 1
2. **Keywords you're missing** — competitors rank for, you don't
3. **New opportunities** — trending keywords in your niche
4. **Keywords from your own content** — extracted from your site

## Priority System

| Priority | What | Action |
|---|---|---|
| 🔥 Page 2 (pos 11-20) | EASIEST WIN — already indexed | Optimize content + add internal links |
| ⚡ Pages 3-4 (pos 21-40) | GOOD WIN | Content refresh + expand |
| 💡 Pages 5-6 (pos 41-60) | HARDER WIN | Major rewrite needed |
| 🆕 Not ranking | NEW OPPORTUNITY | Write new post |

## Commands

```bash
/keywords find yoursite.com              # Full top 100 analysis
/keywords find yoursite.com --update     # Also update config/keywords.md
/keywords quick-wins                     # Only show page 2-3 quick wins
/keywords refresh                        # Re-run keyword research
```

## Python
```bash
python3 scripts/keyword_finder.py --domain yoursite.com
python3 scripts/keyword_finder.py --domain yoursite.com --update-config
python3 scripts/keyword_finder.py --quick-wins-only
```

## Output
- Full report saved to: `reports/top-100-keywords-[date].md`
- Optionally updates: `config/keywords.md`
- Topics auto-added to: `topics/queue.txt`
