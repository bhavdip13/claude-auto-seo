# Architecture — Claude Auto SEO + Digital Marketing

```
claude-auto-seo/
│
├── 📋 QUICK-START.md           ← Start here
├── 📖 README.md                ← Full documentation
├── 🤖 CLAUDE.md                ← Claude Code context (read by AI)
├── 📝 CHANGELOG.md
├── 🔑 .env.example             ← Copy to .env, add credentials
│
├── ⚙️ config/
│   ├── keywords.md             ← YOUR KEYWORDS (fill this first!)
│   ├── schedule.json           ← Automation schedule settings
│   ├── site.json               ← Your site URL and settings
│   └── competitors.json        ← Competitor domains
│
├── 🎨 assets/
│   └── logo.png                ← Your logo (for banner images)
│
├── 🧠 context/                 ← Brand and SEO configuration
│   ├── brand-voice.md          ← Your tone and style
│   ├── writing-examples.md     ← Example posts for Claude to match
│   ├── seo-guidelines.md       ← SEO rules
│   ├── target-keywords.md      ← Keyword strategy
│   ├── internal-links-map.md   ← Pages for internal linking
│   ├── competitor-analysis.md  ← Competitive intelligence
│   ├── style-guide.md          ← Editorial standards
│   ├── features.md             ← Your product/service features
│   └── cro-best-practices.md   ← CRO guidelines
│
├── 💬 .claude/
│   ├── commands/               ← 35+ slash commands
│   │   ├── seo-*.md            ← Technical SEO commands
│   │   ├── content-*.md        ← Content commands
│   │   ├── write.md, research.md, ...
│   │   ├── wp-seo-fix.md       ← WordPress auto-fixer
│   │   ├── publish-*.md        ← Publishing commands
│   │   └── dm-commands.md      ← Digital marketing commands
│   ├── agents/                 ← 12 specialized AI agents
│   │   ├── seo-optimizer.md
│   │   ├── content-analyzer.md (in agents/ dir)
│   │   ├── headline-cro-agents.md
│   │   ├── landing-social-agents.md
│   │   └── ... (more in agents/ dir)
│   └── skills/
│       └── marketing-skills.md ← 26 marketing skills
│
├── 🤖 agents/                  ← Agent definitions (installed to ~/.claude/agents/)
│   ├── seo-auditor.md
│   ├── content-analyzer.md
│   ├── meta-linker-keyword-agents.md
│   ├── schema-geo-editor-rank-agents.md
│   └── report-performance-agents.md
│
├── 🛠️ skills/
│   └── seo/SKILL.md            ← Master SEO skill
│
├── 🐍 scripts/                 ← Python automation scripts
│   ├── wp_seo_fixer.py         ← WordPress SEO scanner + auto-fixer
│   ├── scheduler.py            ← Content auto-scheduler
│   ├── dm_scheduler.py         ← Digital marketing scheduler
│   ├── social_publisher.py     ← All social media platforms
│   ├── external_publisher.py   ← Medium, Reddit, LinkedIn, Dev.to
│   ├── image_generator.py      ← Banner image creator (all sizes)
│   ├── gmb_setup.py            ← Google My Business OAuth + setup
│   └── generate_pdf_report.py  ← PDF report generator
│
├── 📊 data_sources/
│   └── modules/                ← Python analysis modules
│       ├── keyword_analyzer.py
│       ├── readability_scorer.py
│       ├── seo_quality_rater.py
│       ├── search_intent_analyzer.py
│       ├── content_length_comparator.py
│       ├── content_scorer.py
│       ├── opportunity_scorer.py
│       ├── rank_tracker.py
│       ├── wordpress_publisher.py
│       ├── google_analytics.py
│       └── google_search_console.py
│
├── 🔌 extensions/
│   └── dataforseo/             ← DataForSEO MCP integration
│
├── 🗂️ schema/
│   └── templates.json          ← JSON-LD schema templates
│
├── 🌐 wordpress/
│   ├── claude-auto-seo-yoast-rest.php  ← MU plugin
│   └── README.md
│
├── 📁 Working Directories
│   ├── topics/queue.txt        ← Topic writing queue
│   ├── research/               ← Research briefs
│   ├── drafts/                 ← Articles in progress
│   ├── review-required/        ← Auto-written, awaiting review
│   ├── rewrites/               ← Updated content
│   ├── published/              ← Live content
│   ├── output/images/          ← Generated banner images
│   ├── reports/                ← SEO and DM reports
│   └── audits/                 ← Technical audit results
│
└── 📚 docs/
    ├── QUICK-START.md          ← 15-minute setup
    ├── COMMANDS.md             ← All commands reference
    ├── INSTALLATION.md         ← Full install guide
    ├── SOCIAL-CREDENTIALS.md   ← Social media API setup
    ├── GMB-SETUP.md            ← Google My Business setup
    ├── MCP-INTEGRATION.md      ← MCP server connections
    └── TROUBLESHOOTING.md      ← Common issues and fixes
```

---

## Data Flow

```
config/keywords.md
        │
        ▼
   Scheduler picks keyword
        │
        ├──► /research → research/brief-*.md
        │
        ├──► /write → drafts/article-*.md
        │       │
        │       ├──► SEO Optimizer Agent
        │       ├──► Meta Creator Agent  
        │       ├──► Internal Linker Agent
        │       └──► Keyword Mapper Agent
        │
        ├──► /scrub → removes AI patterns
        │
        ├──► Quality Gate (SEO score ≥ 75)
        │
        ├──► WordPress publish (draft)
        │
        ├──► image_generator.py → output/images/
        │
        └──► social_publisher.py → all platforms
```

---

## Automation Architecture

```
Cron Job 1 (9 AM daily):
  scheduler.py --run-now
    └── Generates + queues one WordPress blog post

Cron Job 2 (9:30 AM daily):
  dm_scheduler.py --run
    ├── Instagram (if enabled)
    ├── Facebook (if enabled)  
    ├── LinkedIn (if enabled)
    ├── Twitter x3/day (if enabled)
    ├── Pinterest x2/day (if enabled)
    └── GMB (every 3 days, random time)

Cron Job 3 (7 PM daily):
  dm_scheduler.py --run (evening posts)
```
