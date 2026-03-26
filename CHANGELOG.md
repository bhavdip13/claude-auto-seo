# Changelog

All notable changes to Claude Auto SEO are documented here.
Format: [Version] — Date — Description

---

## [1.0.0] — 2026-03-16

### Initial Release

#### Core Features
- Full technical SEO auditor with 0-100 scoring across 5 dimensions
- Automated content pipeline: research → write → optimize → publish
- 40+ slash commands for all SEO tasks
- 15 specialized AI agents running in parallel
- PDF report generation with professional styling
- WordPress auto-publishing with Yoast SEO metadata

#### Technical SEO
- Core Web Vitals audit (LCP, INP, CLS — 2026 standards)
- Schema markup generator for 10+ content types
- Sitemap analyzer and generator with industry templates
- Hreflang audit and tag generator for multi-language sites
- Robots.txt analyzer
- Canonical tag auditor
- Redirect chain detector

#### Content Automation
- `/content write` — Full research-to-draft pipeline
- `/content bulk-write` — Process multiple topics at once
- `/content calendar` — 30-day editorial calendar generator
- `/content rewrite` — Stale content refresh system
- `/content analyze` — 5-dimension content health score
- `/content scrub` — AI pattern removal

#### Analytics & Reporting
- Weekly SEO digest with traffic and ranking summaries
- Keyword rank tracking with historical data
- Competitor analysis and gap detection
- Priority matrix using real analytics data
- PDF report generation

#### AI Search Optimization
- GEO (Generative Engine Optimization) for 2026
- Optimization for Google AI Overviews, ChatGPT, Perplexity, Bing Copilot
- Entity-based SEO and brand entity optimization
- Speakable schema for voice/AI readout

#### Integrations
- DataForSEO MCP — live SERP data, keyword volumes, backlinks
- Google Analytics 4 — traffic and conversion data
- Google Search Console — rankings, impressions, CTR
- Ahrefs MCP — backlink and keyword data
- Semrush MCP — comprehensive SEO data
- WordPress REST API — auto-publish with full metadata

#### Python Modules
- `keyword_analyzer.py` — density, distribution, stuffing detection
- `readability_scorer.py` — Flesch-Kincaid, passive voice, transitions
- `seo_quality_rater.py` — 100-point scoring system
- `wordpress_publisher.py` — REST API publishing
- `generate_pdf_report.py` — Markdown to PDF conversion
- `dataforseo_client.py` — DataForSEO API wrapper

---

## Roadmap

### [1.1.0] — Planned
- [ ] Google Search Console live data integration
- [ ] Automated weekly digest email via SMTP
- [ ] Competitor content monitoring alerts
- [ ] A/B test title/description suggestions

### [1.2.0] — Planned
- [ ] Bulk URL technical audit
- [ ] Content performance decay detection
- [ ] Automated internal linking across entire site
- [ ] Multi-site management

### [2.0.0] — Planned
- [ ] Visual SEO dashboard (web UI)
- [ ] Scheduled automated audits
- [ ] Team collaboration features
- [ ] White-label PDF reports
