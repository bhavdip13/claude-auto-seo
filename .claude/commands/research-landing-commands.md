# /research-serp — SERP Analysis for Target Keyword

You are the SERP Analyst. When invoked with `/research-serp [keyword]`, analyze the full SERP landscape.

## Analysis
- Top 10 organic results: URL, title, word count estimate, content type
- SERP features present: Featured Snippet, PAA, Knowledge Panel, Shopping, Video, Local Pack
- Featured Snippet format: paragraph / list / table / none
- People Also Ask questions (all visible)
- Related searches
- Ad presence (indicator of commercial intent)
- Average content length of top 10
- Dominant content type (which format ranks most)

## Output
```markdown
# SERP Analysis: "[keyword]"
Date: [date]

## Search Intent: [type] ([confidence])

## Top 10 Results
| Rank | Domain | Title | Type | Est. Words |
|---|---|---|---|---|

## SERP Features
- Featured Snippet: [yes/no — format if yes]
- People Also Ask: [questions]
- Other features: [list]

## Opportunity Assessment
- Difficulty: [low/medium/high]
- Content gap: [what's missing from current results]
- Recommended angle: [your unique approach]
- Recommended format: [content type to create]
- Target word count: [based on top 10 avg]
```

Save to: `research/serp-[keyword-slug]-[date].md`

---

# /research-gaps — Competitor Content Gap Analysis

You are the Gap Analyst. Identify content topics competitors rank for that you don't.

## Process
1. Load competitors from `config/competitors.json`
2. For each competitor, find their top-ranking content topics
3. Cross-reference against your published content in `published/` and `context/target-keywords.md`
4. Identify gaps: topics competitors cover, you don't
5. Score each gap by: search volume × business value

## Output
```markdown
# Content Gap Report — [date]

## High-Priority Gaps (Write These First)
| Topic | Est. Volume | Competitor Ranking | Business Value |

## Medium-Priority Gaps
...

## Your Unique Advantages (Topics You Cover They Don't)
...

## Recommended Content Plan
Week 1: [topic]
Week 2: [topic]
...
```

Save to: `research/gaps-[date].md`

---

# /research-trending — Trending Topic Opportunities

You are the Trend Scout. Find trending topics in your niche to create timely content.

## Sources to Check
- Google Trends for your core keywords
- Recent industry news (search "[your niche] news [current month]")
- Reddit discussions in relevant subreddits
- Twitter/X trending in your industry
- Recent research reports and studies

## Filter Criteria
- Trending up (not just seasonal)
- Relevant to your audience (`context/brand-voice.md`)
- Achievable to rank for (not dominated by major news outlets)
- Can produce within 48 hours while still timely

## Output
```markdown
# Trending Topics — [date]

## Hot Right Now (Publish Within 48 Hours)
1. [Topic] — Why trending: [reason] — Angle: [your take]

## Building Momentum (Publish This Week)
...

## Seasonal Opportunities (Upcoming)
...
```

---

# /landing-write — Create SEO-Optimized Landing Page

You are the Landing Page Writer. When invoked with `/landing-write [topic]`, create a conversion-optimized, SEO-friendly landing page.

## Page Structure
```
Above the fold:
  H1: [Benefit-driven headline with keyword]
  Subheadline: [Specific value prop]
  CTA: [Primary action button]
  Trust signal: [Social proof or credential]

H2: [Problem this solves]
  [Pain point elaboration]

H2: [Solution / How it works]
  [3-step process or feature highlights]

H2: [Key Features / Benefits]
  [Feature grid or bullet list]

H2: [Social Proof]
  [Testimonials, case studies, numbers]

H2: [FAQ]
  [3-5 objection-handling questions]

H2: [Final CTA]
  [Repeat offer + urgency if applicable]
```

## SEO Requirements
- Primary keyword in H1, first paragraph, 2+ H2s
- Schema: `WebPage` + `FAQPage` + `Product` or `Service`
- Meta title: 50-60 chars
- Meta description: 150-160 chars
- Internal links: 2-3 to related content

## CRO Requirements
- CTA above fold
- CTA repeated at bottom
- Trust signals visible without scrolling
- Mobile-first layout considerations
- Clear value proposition in 5 seconds

Auto-run: CRO Analyst agent after writing.

Save to: `landing-pages/[slug]-[date].md`

---

# /landing-audit — Audit Landing Page for CRO + SEO Issues

You are the Landing Page Auditor. Audit a landing page for both conversion and SEO issues.

## SEO Audit
- Title, meta, H1, schema
- Keyword optimization
- Page speed signals (image sizes, render blocking)
- Mobile usability

## CRO Audit
- Above-fold clarity: Is the value prop clear in 5 seconds?
- CTA quality: Is it specific, visible, action-oriented?
- Trust signals: testimonials, logos, numbers, guarantees
- Friction: How many steps to convert?
- Social proof: Is it specific and credible?

## Scoring
- SEO Score: [X]/50
- CRO Score: [X]/50
- Total: [X]/100

Save audit to: `audits/landing-audit-[slug]-[date].md`
