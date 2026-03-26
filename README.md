# 🚀 Claude Auto SEO + Digital Marketing

> **One command. Your domain. Full automation.**
>
> Give it your domain and it handles SEO, content, social media, and digital marketing — every day.

[![Claude Code](https://img.shields.io/badge/Claude%20Code-Powered-blue)](https://claude.ai/claude-code)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-green)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)
[![Platforms](https://img.shields.io/badge/Social%20Platforms-7%2B-orange)](#)

---

## ⚡ Quick Start (3 Commands)

```bash
# 1. Clone and install
git clone https://github.com/YOUR_USERNAME/claude-auto-seo.git
cd claude-auto-seo && ./install.sh && pip install -r requirements.txt

# 2. Auto-configure from your domain (2 minutes)
python3 scripts/auto_configure.py --domain yoursite.com

# 3. Add credentials to .env, then start everything
python3 scripts/setup_crons.py --install
```

**That's it. Everything runs automatically.**

---

## 🎯 What It Does

| Feature | Description |
|---|---|
| 🔍 **SEO Audit** | Full technical audit, auto-fixes meta/schema/alt-text via WordPress API |
| ✍️ **Daily Blog Posts** | Writes SEO-optimized articles from your keywords, publishes to WordPress |
| 🖼️ **Banner Images** | Auto-generates branded images with logo + title + CTA for every platform |
| 📱 **Social Media** | Posts to Instagram, Facebook, LinkedIn, Twitter/X, Pinterest, GMB daily |
| 🎊 **Festival Posts** | 60+ festivals (India, USA, UK, Africa, Europe) auto-posted at 1:00 AM |
| 🌐 **External Blogs** | Republishes to Medium, Reddit, Dev.to, LinkedIn Articles (40+ platforms) |
| 📊 **Daily Reports** | Emails you at 8 PM showing everything done — with URLs to verify |
| 📈 **Keyword Rankings** | Tracks positions, prioritizes page 2-6 keywords to push to page 1 |

---

## 🛠️ Installation

### Requirements
- Python 3.10+ — [Download](https://python.org/downloads)
- Claude Code CLI — [Install](https://claude.ai/claude-code)
- WordPress site — for auto-publishing and SEO fixing
- Anthropic API key — [Get one](https://console.anthropic.com/api-keys)

### Install Steps

```bash
git clone https://github.com/YOUR_USERNAME/claude-auto-seo.git
cd claude-auto-seo
chmod +x install.sh && ./install.sh
pip install -r requirements.txt
```

---

## ⚙️ Configuration

### Auto-Configure from Your Domain

```bash
python3 scripts/auto_configure.py --domain yoursite.com
# With WordPress credentials for richer data:
python3 scripts/auto_configure.py --domain yoursite.com --wp-user admin --wp-pass "xxxx xxxx"
```

This scans your site and **automatically creates**:
- `config/site.json` — site settings + niche detection
- `config/business.json` — email, phone, social profiles, CTA settings
- `config/keywords.md` — keyword clusters for your industry
- `context/brand-voice.md` — brand voice template
- `context/internal-links-map.md` — all your WordPress pages mapped
- `topics/queue.txt` — 30 topics ready to write
- `.env` — credentials template pre-filled with your URL + colors

### Edit `.env` (Most Important Step)

```env
# Content writing (required)
ANTHROPIC_API_KEY=sk-ant-api03-...

# WordPress (required for publishing + SEO fixing)
WP_URL=https://yoursite.com
WP_USERNAME=your_wordpress_username
WP_APP_PASSWORD=xxxx xxxx xxxx xxxx xxxx xxxx

# Daily email reports at 8PM (required for notifications)
SMTP_USER=your@gmail.com
SMTP_PASS=gmail_app_password
NOTIFICATION_EMAIL=you@yoursite.com

# Social Media (add platforms you want to use)
META_ACCESS_TOKEN=...     # Facebook + Instagram
FACEBOOK_PAGE_ID=...
INSTAGRAM_USER_ID=...
TWITTER_API_KEY=...
LINKEDIN_ACCESS_TOKEN=...
PINTEREST_ACCESS_TOKEN=...
GOOGLE_GMB_ACCESS_TOKEN=...
GMB_LOCATION_ID=...
```

**How to get WordPress App Password:**
1. WordPress Admin → Users → Your Profile
2. Scroll to "Application Passwords"
3. Name: "Claude Auto SEO" → Click "Add New"
4. Copy the generated password

### Add Your Logo

```bash
cp /path/to/your/logo.png assets/logo.png
```

The logo appears in the top-left corner of every generated banner image.

### Enable Social Platforms

Edit `config/schedule.json` — set `"enabled": true` for each platform:

```json
"social_media": {
  "instagram": { "enabled": true },
  "facebook":  { "enabled": true },
  "linkedin":  { "enabled": true },
  "twitter":   { "enabled": true, "posts_per_day": 3 },
  "gmb":       { "enabled": true, "frequency": "every_3_days" }
}
```

### Configure CTA (Call-to-Action)

Auto-configured from your domain scan. Verify/edit in `config/business.json`:

```json
"contact": {
  "website": "https://yoursite.com",
  "email": "hello@yoursite.com",
  "phone": "+1 234 567 8900"
},
"cta": {
  "blog_post_cta": {
    "heading": "Ready to Get Started?",
    "button_text": "Contact Us"
  }
}
```

Every blog post and social media post includes this CTA automatically.

---

## 📅 Automation Schedule

Once `setup_crons.py --install` runs, everything happens automatically:

| Time | What Happens |
|---|---|
| **1:00 AM** | Festival posts to all social platforms (on festival days) |
| **9:00 AM** | Daily blog post written and saved to `review-required/` |
| **9:30 AM** | Morning social media posts to all enabled platforms |
| **1:00 PM** | Afternoon social media posts |
| **7:00 PM** | Evening social media posts |
| **8:00 PM** | Daily report emailed to you |
| **Sunday 10 AM** | Weekly keyword ranking check |

---

## 🎊 Festival Auto-Posting

Posts at **1:00 AM** on festival days — no action needed.

**Covered festivals:**
- 🇮🇳 India (20+): Diwali, Holi, Navratri, Republic Day, Independence Day, Janmashtami, Baisakhi...
- 🇺🇸 USA (10+): 4th July, Thanksgiving, Memorial Day, Halloween, Juneteenth...
- 🇬🇧 UK (8+): Bonfire Night, Boxing Day, Bank Holidays, St. George's Day...
- 🌍 Africa (6+): Africa Day, Mandela Day, Youth Day SA...
- 🇩🇪 Europe/Germany (12+): Oktoberfest, Unity Day, May Day, Midsummer...
- 🌐 Global (15+): Earth Day, Women's Day, Valentine's Day, New Year...

Multiple festivals same day → multiple posts with unique content + festival-themed banners.

```bash
python3 scripts/festival_poster.py --check-upcoming 30  # Preview upcoming
python3 scripts/festival_poster.py --preview            # Test without posting
```

---

## 📊 Daily Reports

Every evening at **8:00 PM** you receive an email:

```
📊 Daily SEO & Digital Marketing Report
Site: YourSite.com | Date: 2026-03-16

✍️ Blog Posts Written
  ✅ "Best SEO Tips for 2026" — Score: 82/100
     File: review-required/best-seo-tips-2026-03-16.md

📱 Social Media Posts
  📸 Instagram — "seo tips" — Post ID: 123456
  📘 Facebook  — "seo tips" — https://facebook.com/...

🎊 Festival Posts: Holi 2026 — 5/5 platforms

🔧 WordPress Fixes: 12 applied (meta: 8, alt-text: 4)

📈 Rankings: "seo guide" #14 → #11 (+3 positions) ✅

📊 Scorecard: 25 actions | 96% success rate
```

---

## 🧪 Testing Guide

```bash
# 1. Check credentials
python3 scripts/setup_crons.py --check-credentials

# 2. Test all modules at once
python3 scripts/setup_crons.py --test-all

# 3. Test WordPress connection
python3 scripts/wp_seo_fixer.py --scan

# 4. Test banner generation
python3 scripts/image_generator.py --title "Test" --keyword "seo" --type blog
ls output/images/

# 5. Preview social posts (no posting)
python3 scripts/dm_scheduler.py --preview

# 6. Preview festival posts (no posting)
python3 scripts/festival_poster.py --preview

# 7. Test daily report
python3 scripts/daily_report.py --print-only

# 8. Test email report
python3 scripts/daily_report.py --send-email
```

See `docs/COMPLETE-SETUP-GUIDE.md` for the full step-by-step testing guide.

---

## 📁 File Structure

```
claude-auto-seo/
├── scripts/               Automation scripts
│   ├── auto_configure.py  → Scan domain, create all config
│   ├── setup_crons.py     → Install ALL automation (one command)
│   ├── scheduler.py       → Daily blog writing
│   ├── dm_scheduler.py    → Social media posting
│   ├── festival_poster.py → Festival auto-posts at 1AM
│   ├── daily_report.py    → Daily email report at 8PM
│   ├── wp_seo_fixer.py    → WordPress SEO auto-fixer
│   ├── image_generator.py → Banner image creator
│   ├── social_publisher.py→ All social platforms
│   ├── keyword_finder.py  → Top 100 keyword finder
│   └── ...
├── config/
│   ├── keywords.md        ← YOUR KEYWORDS (most important)
│   ├── business.json      ← Contact info + CTA
│   ├── schedule.json      ← Platform settings
│   └── site.json
├── .env                   ← ALL credentials
├── assets/logo.png        ← Your logo
├── topics/queue.txt       ← Writing queue
├── review-required/       ← Articles awaiting your review
├── output/images/         ← Generated banners
├── reports/               ← Daily + SEO reports
└── docs/                  ← Full documentation
```

---

## 📚 Documentation

| Doc | Description |
|---|---|
| [QUICK-START.md](QUICK-START.md) | 15-minute setup guide |
| [docs/COMPLETE-SETUP-GUIDE.md](docs/COMPLETE-SETUP-GUIDE.md) | Full setup + testing guide |
| [docs/COMMANDS.md](docs/COMMANDS.md) | All commands reference |
| [docs/SOCIAL-CREDENTIALS.md](docs/SOCIAL-CREDENTIALS.md) | Social media API setup |
| [docs/GMB-SETUP.md](docs/GMB-SETUP.md) | Google My Business setup |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | System architecture |
| [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Common issues |

---

## ❓ FAQ

**Does it write unique content?** Yes — every post, article, social post, and banner is uniquely generated.

**How does it know about my business?** `auto_configure.py` scans your site and extracts niche, colors, email, phone, social profiles automatically.

**Do I need coding skills?** No. Just run the commands above. Everything is configured through `.env` and JSON files.

**Does it work without WordPress?** Social media, festivals, and content writing work. SEO fixing requires WordPress.

**What about duplicate content?** External posts always include a canonical URL pointing to your WordPress site.

---

## 📄 License

MIT License — see [LICENSE](LICENSE)

---

<p align="center">
  <strong>Give it your domain. It does the rest.</strong><br><br>
  <code>python3 scripts/auto_configure.py --domain yoursite.com</code>
</p>
