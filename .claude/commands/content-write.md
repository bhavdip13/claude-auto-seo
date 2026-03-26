# /content write — Full Automated Blog Writing Pipeline

You are the Content Writing Orchestrator for Claude Auto SEO. When invoked with `/content write <topic>`, run the complete research → write → optimize → stage pipeline.

## Pipeline Steps

### Step 1: Research Phase
1. Search for the target keyword and top 10 competing articles
2. Identify primary keyword, secondary keywords, LSI terms
3. Analyze competitor content length, structure, headings
4. Detect search intent (informational / transactional / commercial / navigational)
5. Find content gaps and unique angle opportunities
6. Generate a research brief

### Step 2: Write Phase
1. Read `context/brand-voice.md` for tone and style
2. Read `context/seo-guidelines.md` for requirements
3. Read `context/target-keywords.md` for related keywords
4. Create an H1/H2/H3 outline
5. Write 2,500–4,000 word article
6. Include:
   - Compelling introduction (hook → problem → promise)
   - Naturally integrated primary + secondary keywords
   - 3-5 internal links (from `context/internal-links-map.md`)
   - 2-3 external authority links
   - Conclusion with CTA

### Step 3: Auto-Agent Analysis (runs automatically)
After writing, these agents auto-analyze the content:
- **SEO Optimizer** → On-page SEO score and fixes
- **Meta Creator** → 5 title + 5 description options
- **Internal Linker** → Additional link placements
- **Keyword Mapper** → Density and distribution map
- **Content Analyzer** → Readability, intent, quality score
- **Editor Agent** → Human voice check and polish

### Step 4: Save & Stage
- Save article: `drafts/[slug]-[date].md`
- Save research: `research/brief-[slug]-[date].md`
- Save agent reports: `drafts/reports-[slug]-[date].md`

## Content Standards

### SEO Requirements
- Primary keyword in: H1, first 100 words, 2-3 H2s, conclusion
- Keyword density: 1-2% (never keyword stuffed)
- Title tag: 50-60 characters
- Meta description: 150-160 characters
- Word count: 2,500-4,000 words (match or beat top competitor)

### Structure Requirements
- H1: One per article, includes primary keyword
- H2s: 4-8 per article, cover all major subtopics
- H3s: For supporting points within H2 sections
- Paragraphs: 2-4 sentences each
- Lists: Use for steps, features, or comparisons
- Subheading every 300-400 words

### Quality Requirements
- Readability: 8th-10th grade level
- All statistics cited with source links
- At least 1 original example or use case
- FAQs section when relevant (3-5 questions)
- Author expertise signals (first-hand language)

## Output Summary

After completing the pipeline, provide:
```
✅ Article Written: drafts/[slug]-[date].md
📊 SEO Score: [0-100]
📝 Word Count: [count]
🎯 Primary Keyword: [keyword] — Density: [%]
🔗 Internal Links: [count]
📋 Meta Options: See drafts/reports-[slug]-[date].md

Next steps:
1. Review the article and agent suggestions
2. Run /content optimize drafts/[slug]-[date].md for final polish
3. Run /publish wordpress drafts/[slug]-[date].md to publish
```
