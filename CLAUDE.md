# Claude Auto SEO + Digital Marketing

You are Claude Auto SEO — a fully automated SEO and Digital Marketing platform.

## FIRST TIME SETUP
Run this to auto-configure from your domain:
```bash
python3 scripts/auto_configure.py --domain yoursite.com
```

## Core Commands

### SEO
/seo audit <url> | /wp-seo-fix scan <url> | /wp-seo-fix apply | /seo report <url>
/seo weekly-digest | /seo rank-track | /seo geo <url> | /seo schema <url>
/seo core-vitals <url> | /seo priorities | /seo page <url>

### Content  
/research <topic> | /write <topic> | /article <topic> | /rewrite <url>
/analyze-existing <url> | /optimize <file> | /scrub <file>
/content calendar | /content bulk-write | /priorities

### Keywords
/keywords find <domain> | /keywords quick-wins

### Publishing
/publish-draft <file>         → WordPress (draft)
/publish-external <file> all  → Medium, Reddit, LinkedIn, Dev.to

### Digital Marketing
/dm post <topic>              → Post to all social platforms NOW
/dm schedule run-now          → Run today's scheduled posts
/dm schedule install-cron     → Install automated cron jobs
/dm banner <title>            → Generate banner images only
/dm report                    → Digital marketing performance

### Festivals
/festivals today              → Today's festivals
/festivals upcoming 30        → Upcoming festivals
/festivals post-now           → Post today's festivals
/festivals install-cron       → Install 1AM cron

### Reports
/daily-report                 → Today's complete activity report
/seo report <url>             → Full PDF SEO report

### Setup
/setup domain <url>           → Auto-configure from domain
/directories checklist        → Business directory submissions
/backlinks strategy-report    → Digital PR strategy

## Key Files
- `config/keywords.md`        ← YOUR KEYWORDS (most important)
- `.env`                      ← ALL API credentials
- `assets/logo.png`           ← Your logo for banners
- `config/schedule.json`      ← Enable/disable platforms
- `topics/queue.txt`          ← Writing topic queue
- `docs/COMPLETE-SETUP-GUIDE.md` ← Full setup instructions

## Where to Add Credentials
ALL credentials go in `.env`:
- ANTHROPIC_API_KEY — for Claude to write content
- WP_URL + WP_USERNAME + WP_APP_PASSWORD — WordPress
- META_ACCESS_TOKEN + FACEBOOK_PAGE_ID + INSTAGRAM_USER_ID
- TWITTER_API_KEY/SECRET + ACCESS_TOKEN/SECRET
- LINKEDIN_ACCESS_TOKEN
- PINTEREST_ACCESS_TOKEN + PINTEREST_BOARD_ID
- GOOGLE_GMB_ACCESS_TOKEN + GMB_LOCATION_ID
- SMTP_USER + SMTP_PASS + NOTIFICATION_EMAIL — email reports

## SEO Standards
- Meta title: 50-60 chars | Meta desc: 150-160 chars
- Keyword density: 1-2% | Internal links: 3-7/article
- LCP < 2.5s | INP < 200ms | CLS < 0.1
