# Commands Reference — Claude Auto SEO + Digital Marketing

Complete list of all available slash commands.

---

## 🔍 Technical SEO Commands

| Command | Description |
|---|---|
| `/seo audit <url>` | Full site audit with parallel subagent delegation |
| `/seo page <url>` | Deep single-page SEO analysis |
| `/seo fix <url>` | Auto-detect and generate fixes for SEO issues |
| `/seo technical <url>` | Technical audit across 9 categories |
| `/seo content <url>` | E-E-A-T and content quality analysis |
| `/seo images <url>` | Image optimization audit + alt text generator |
| `/seo core-vitals <url>` | LCP, INP, CLS audit and fix guide |
| `/seo schema <url>` | Detect, validate, and generate Schema.org markup |
| `/seo sitemap <url>` | Analyze existing sitemap |
| `/seo sitemap generate` | Generate new sitemap with industry templates |
| `/seo hreflang <url>` | Multi-language hreflang audit and generation |
| `/seo geo <url>` | AI search optimization (Google AI Overviews, ChatGPT, Perplexity) |
| `/seo programmatic <url>` | Programmatic SEO analysis and planning |
| `/seo competitor-pages <url>` | Competitor comparison page generator |
| `/seo plan <type>` | 90-day strategic SEO plan (saas/local/ecommerce/publisher/agency) |

---

## 📊 Reporting & Analytics Commands

| Command | Description |
|---|---|
| `/seo report <url>` | Full PDF SEO report |
| `/seo weekly-digest <url>` | Automated weekly SEO summary |
| `/seo rank-track <url>` | Keyword ranking report with history |
| `/seo priorities` | Data-driven priority matrix |
| `/seo competitor-report <url>` | Full competitor intelligence report |
| `/performance-review` | Analytics-based content performance review |

---

## ✍️ Content Commands

| Command | Description |
|---|---|
| `/research <topic>` | Full keyword and competitor research brief |
| `/write <topic>` | Complete article: research → write → optimize |
| `/article <topic>` | Quick one-command article creation |
| `/rewrite <url\|file>` | Refresh and improve existing content |
| `/analyze-existing <url\|file>` | Content health score and improvement plan |
| `/optimize <file>` | Final SEO optimization pass before publishing |
| `/scrub <file>` | Remove AI patterns, humanize content |
| `/content calendar` | Generate 30-day content calendar |
| `/content bulk-write <file>` | Write multiple articles from topic list |
| `/content gaps` | Identify content gaps vs competitors |
| `/content cluster <keyword>` | Build complete topic cluster |
| `/priorities` | Content prioritization matrix |

---

## 📐 Research Commands

| Command | Description |
|---|---|
| `/content research <topic>` | Keyword + competitor research |
| `/research-serp <keyword>` | SERP analysis for target keyword |
| `/research-gaps` | Competitor content gap analysis |
| `/research-trending` | Trending topic opportunities |
| `/research-performance` | Performance-based content priorities |
| `/research-topics` | Topic cluster research |

---

## 🏠 Landing Page Commands

| Command | Description |
|---|---|
| `/landing-write <topic>` | Create SEO-optimized landing page |
| `/landing-audit <file>` | CRO + SEO audit for landing pages |
| `/landing-research <topic>` | Competitor and positioning research |
| `/landing-competitor <url>` | Deep competitor landing page analysis |

---

## 🔧 WordPress Commands

| Command | Description |
|---|---|
| `/publish-draft <file>` | Publish to WordPress as draft |
| `/wp-seo-fix scan <url>` | Scan entire WordPress site for SEO issues |
| `/wp-seo-fix apply` | Auto-fix all detected issues |
| `/wp-seo-fix verify` | Re-scan to confirm fixes applied |
| `/wp-seo-fix rollback` | Undo all applied fixes |
| `/wp-seo-fix --fix-post <id>` | Fix a single post by ID |

---

## 🌐 External Publishing Commands

| Command | Description |
|---|---|
| `/publish-external <file> medium` | Publish to Medium (with canonical) |
| `/publish-external <file> reddit` | Post to Reddit (discussion format) |
| `/publish-external <file> linkedin` | Publish LinkedIn article |
| `/publish-external <file> devto` | Publish to Dev.to |
| `/publish-external <file> all` | Publish to all configured external platforms |

---

## 📱 Digital Marketing Commands

| Command | Description |
|---|---|
| `/dm post <topic>` | Generate content + banners + post to all social platforms |
| `/dm post <topic> --platforms instagram,facebook` | Post to specific platforms |
| `/dm post --from-article <file>` | Convert article to social posts |
| `/dm schedule setup` | Interactive schedule setup wizard |
| `/dm schedule run-now` | Run all today's scheduled posts |
| `/dm schedule install-cron` | Install automated cron jobs |
| `/dm schedule status` | Show scheduling status |
| `/dm schedule preview` | Preview posts without publishing |
| `/dm schedule pause` | Pause scheduled posting |
| `/dm banner <title>` | Generate banner images only |
| `/dm banner <title> --type instagram` | Specific platform banner |
| `/dm report` | Digital marketing performance report |

---

## 📅 Automation Commands

| Command | Description |
|---|---|
| `/seo schedule setup` | Configure content auto-scheduling |
| `/seo schedule run-now` | Generate and queue one post now |
| `/seo schedule install-cron` | Install daily content cron job |
| `/seo schedule status` | Show schedule and queue |
| `/seo schedule queue` | View and manage topic queue |

---

## 🛠️ Marketing Skills (26 Available)

| Skill | Command |
|---|---|
| Copywriting | `/copywriting` |
| Copy editing | `/copy-editing` |
| Landing page CRO | `/page-cro` |
| Form optimization | `/form-cro` |
| Signup flow CRO | `/signup-flow-cro` |
| Onboarding CRO | `/onboarding-cro` |
| Popup optimization | `/popup-cro` |
| Paywall CRO | `/paywall-upgrade-cro` |
| Content strategy | `/content-strategy` |
| Pricing strategy | `/pricing-strategy` |
| Launch strategy | `/launch-strategy` |
| Marketing ideas | `/marketing-ideas` |
| Email sequences | `/email-sequence` |
| Social content | `/social-content` |
| Paid ads copy | `/paid-ads` |
| Quick SEO audit | `/seo-audit` |
| Schema markup | `/schema-markup` |
| Programmatic SEO | `/programmatic-seo` |
| Competitor alternatives | `/competitor-alternatives` |
| Analytics setup | `/analytics-tracking` |
| A/B test planning | `/ab-test-setup` |
| Referral program | `/referral-program` |
| Free tool strategy | `/free-tool-strategy` |
| Marketing psychology | `/marketing-psychology` |
| Headline generator | `/headline-generator` |
| CRO checklist | `/cro-checklist` |

---

## Python Scripts (Run Directly)

```bash
# WordPress SEO auto-fixer
python3 scripts/wp_seo_fixer.py --scan
python3 scripts/wp_seo_fixer.py --apply
python3 scripts/wp_seo_fixer.py --verify

# Content scheduler
python3 scripts/scheduler.py --run-now
python3 scripts/scheduler.py --install-cron
python3 scripts/scheduler.py --status

# Social media / digital marketing scheduler
python3 scripts/dm_scheduler.py --run
python3 scripts/dm_scheduler.py --install-cron
python3 scripts/dm_scheduler.py --preview

# Banner image generator
python3 scripts/image_generator.py --title "Your Title" --keyword "seo" --type all

# External blog publisher
python3 scripts/external_publisher.py drafts/article.md medium

# Social media publisher
python3 scripts/social_publisher.py --topic "SEO Tips" --platforms all

# GMB setup and auth
python3 scripts/gmb_setup.py --auth
python3 scripts/gmb_setup.py --list-locations

# PDF report generator
python3 scripts/generate_pdf_report.py reports/seo-report.md
```
