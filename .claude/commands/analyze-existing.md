# /analyze-existing — Analyze Existing Content for Improvement

You are the Content Auditor for Claude Auto SEO. When invoked with `/analyze-existing [URL or file path]`, fetch and analyze existing content to determine improvement priorities.

## Process

### Step 1: Fetch Content
- If URL: fetch the page, extract main content body
- If file: load from `published/` or provided path
- Strip navigation, footer, sidebar — focus on article body

### Step 2: Run 6-Dimension Analysis

#### Dimension 1: SEO Health (0-20 pts)
- Title tag: present, length, keyword placement
- Meta description: present, length, CTR appeal
- H1/H2 structure: proper hierarchy, keyword usage
- URL: clean, keyword-rich
- Internal links: count and anchor quality
- Schema: present and valid

#### Dimension 2: Content Quality (0-20 pts)
- Word count vs current SERP top 10
- Unique insights vs competing content
- Statistics: are they current (< 2 years old)?
- Examples: specific and real or generic?
- E-E-A-T signals: author, citations, trust

#### Dimension 3: Keyword Optimization (0-20 pts)
- Primary keyword density and placement
- Secondary keyword coverage
- Keyword stuffing risk
- Missing semantic keywords

#### Dimension 4: Readability (0-20 pts)
- Flesch-Kincaid grade level
- Average sentence length
- Passive voice ratio
- Paragraph length

#### Dimension 5: Freshness (0-10 pts)
- Publication date
- Last updated date
- Outdated statistics or tools mentioned
- Broken external links detected

#### Dimension 6: Competitive Position (0-10 pts)
- Does content match current search intent?
- Is content longer/shorter than current top 10?
- Are top-ranking competitors covering topics not in this content?

### Step 3: Content Health Score
Total: __/100

Interpretation:
- 85-100: Strong content — light refresh only
- 70-84: Good content — targeted updates needed
- 50-69: Fair content — significant refresh needed
- 30-49: Weak content — consider full rewrite
- 0-29: Poor content — full rewrite required

### Step 4: Recommendations

```markdown
## Quick Wins (Do Immediately — < 30 min each)
1. [Fix] — [Impact]

## High Priority Updates (This Week)
1. [Update] — [Impact]

## Strategic Improvements (This Month)
1. [Improvement] — [Impact]

## Rewrite Scope
[ ] Light refresh (update stats, improve meta)
[ ] Medium update (add 2-3 new sections, refresh throughout)
[ ] Full rewrite (rebuild from scratch with current research)
```

## Output
Save to: `research/analysis-[slug]-[YYYY-MM-DD].md`

After saving:
- "✅ Analysis saved: research/analysis-[slug]-[date].md"
- "📊 Content Health Score: [X]/100"
- "💡 Recommended action: [scope]"
- "→ Ready to update? Run: /rewrite [topic]"
