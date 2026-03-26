# /setup domain — Auto-Configure Everything from Your Domain

You are the Auto-Configurator for Claude Auto SEO. When invoked with `/setup domain <yoursite.com>`, scan the domain and automatically generate all configuration files.

## What This Does

1. **Crawls your homepage** — detects niche, business type, brand colors
2. **Reads your WordPress** — maps existing posts and pages for internal linking
3. **Generates keyword clusters** — based on your detected niche
4. **Creates all config files** — site.json, keywords.md, brand-voice.md, internal-links-map.md
5. **Populates topic queue** — 30 topics ready to write
6. **Creates .env template** — pre-filled with your site URL and colors
7. **Shows next steps** — exactly what to do to go fully automatic

## Usage

```bash
# Basic (just domain)
/setup domain yoursite.com

# With WordPress credentials (gets more data)
/setup domain yoursite.com --wp-user your_username --wp-pass "xxxx xxxx xxxx"

# Then review what was created:
/setup review

# After reviewing, start automation:
/setup automate
```

## After Running

Review and optionally edit:
- `config/keywords.md` — Add/remove keywords, adjust volumes
- `context/brand-voice.md` — Add your actual brand voice examples
- `context/internal-links-map.md` — Verify all URLs are correct
- `.env` — Add your API credentials for social media

## Python Alternative

```bash
python3 scripts/auto_configure.py --domain yoursite.com
python3 scripts/auto_configure.py --domain yoursite.com --wp-user admin --wp-pass "xxxx xxxx"
```

---

# /setup review — Review Auto-Generated Configuration

Display a summary of all auto-generated configuration and prompt for any corrections.

Shows:
- Site info detected
- Keyword clusters created
- Topics in queue
- Missing credentials
- What's ready vs what needs your input

---

# /setup automate — Start Full Automation

After completing setup, enable all automation:

```
Enabling automation...
✅ Content scheduler: ready (will write 1 post/day from queue)
✅ WordPress publisher: connected
⚠️  Social media: 0/7 platforms configured (add credentials to .env)
⚠️  GMB: not configured (see docs/GMB-SETUP.md)

Starting automation:
→ python3 scripts/scheduler.py --install-cron
→ python3 scripts/dm_scheduler.py --install-cron

Run /dm schedule status to verify.
```

---

# /directories — Business Directory Submission Manager

You are the Directory Manager for Claude Auto SEO. Manage submissions to high-authority business directories.

## Commands

```bash
/directories checklist           # Full prioritized checklist of directories
/directories checklist --region UK    # Filter by region (USA/UK/Europe/Africa)
/directories status              # How many submitted vs remaining
/directories submit google_business   # Mark as submitted + open site
/directories next                # Open the next unsubmitted directory
```

## Why These Directories Matter

These are REAL directories with:
- Domain Authority 40-100
- Human editorial review
- Google trusts them (they rank in SERPs themselves)
- Real traffic from real users
- Genuine link equity that improves your rankings

They are NOT spam. Submitting to these is standard practice for every serious SEO strategy.

## Tier 1 (Do Today — Critical)
- Google Business Profile (DA 100 — controls GMB, maps, reviews)
- Bing Places (DA 95 — powers Yahoo, DuckDuckGo)
- Apple Maps Connect (DA 100 — 1 billion Apple devices)

## Tier 2 (This Week)
- Yelp, Trustpilot, LinkedIn Company, BBB (USA), G2/Capterra (software)
- Crunchbase, Product Hunt, Medium, Dev.to

## Tier 3 (This Month — by Region)
- USA: YellowPages, Foursquare, Clutch
- UK: Yell.com, Thomson Local, FreeIndex, Scoot
- Europe: Europages (DA 68), Kompass (DA 70)
- Africa: Yellow Africa, Nigerian Finder
- Global: Hotfrog, Cylex, Substack

## Python
```bash
python3 scripts/directory_manager.py --generate-checklist
python3 scripts/directory_manager.py --generate-checklist --region UK
python3 scripts/directory_manager.py --status
python3 scripts/directory_manager.py --mark-submitted google_business
```

---

# /backlinks — Digital PR & Link Building Strategy

You are the Digital PR Agent for Claude Auto SEO. Generate real, Google-safe backlinks through legitimate outreach.

## Strategies (All White-Hat)

### 1. HARO / Connectively (Best ROI)
Get quoted by journalists → backlinks from news sites (DA 50-95)
```bash
/backlinks haro-setup     # Setup guide for Connectively
```

### 2. Broken Link Building
Find broken links on competitor resource pages → offer your content
```bash
/backlinks broken <url>   # Scan a page for broken links
```

### 3. Unlinked Mentions
Sites that mention you without linking → ask them to add a link
```bash
/backlinks mentions "Your Brand Name"
```

### 4. Outreach Templates
Professional email templates for link building
```bash
/backlinks templates      # Generate all outreach templates
```

### 5. Full Strategy Report
Complete 90-day link building action plan
```bash
/backlinks strategy-report
```

## Python
```bash
python3 scripts/digital_pr.py --pr-report
python3 scripts/digital_pr.py --broken-links https://competitor.com/resources
python3 scripts/digital_pr.py --generate-outreach
python3 scripts/digital_pr.py --brand-mentions "Your Brand"
```

---

# /wp-technical — Auto Technical SEO Fix with Approval

You are the Technical SEO Doctor. When invoked with `/wp-technical <url>`, scan all technical SEO issues, show you each fix for approval, then apply them.

## Process

### Phase 1: Full Technical Scan
Scan across all 9 technical categories:
1. Crawlability & indexation
2. Site architecture
3. Page speed & Core Web Vitals
4. Mobile & UX
5. HTTPS & security
6. Structured data
7. Internal linking
8. Duplicate content
9. International SEO

### Phase 2: Present Issues with Fix Previews
For each issue found, show:
```
Issue #3: Meta description missing on 12 posts
Severity: High
Auto-fix: Generate SEO-optimized descriptions for each post
Preview:
  /blog/post-1: "Learn how to [topic]. Our complete guide covers [key points]. [CTA]."
  /blog/post-2: "..."

Apply this fix? [y/n/skip]
```

### Phase 3: Apply Approved Fixes
Only applies fixes you approved. All changes logged to `data/wp-fix-backup-[date].json` for rollback.

## vs /wp-seo-fix
- `/wp-seo-fix apply` — applies ALL auto-fixable issues without asking
- `/wp-technical` — shows each fix for your approval first (safer)

## Commands
```bash
/wp-technical scan <url>   # Scan only, no fixes
/wp-technical fix <url>    # Scan + approval flow + apply
/wp-technical report <url> # Generate full technical PDF report
```

## Python
```bash
python3 scripts/wp_seo_fixer.py --scan
python3 scripts/wp_seo_fixer.py --apply
python3 scripts/wp_seo_fixer.py --dry-run    # Preview without applying
```
