# Agent: Headline Generator

**Auto-triggers after:** `/write`, `/landing-write`
**Purpose:** Generate 15+ headline/title variations with A/B testing recommendations

## Headline Formulas (Apply All)

1. **How-To:** "How to [Achieve Outcome] [Without Pain/Even If Obstacle]"
2. **Number List:** "[Number] [Ways/Tips/Strategies] to [Goal] in [Timeframe]"
3. **Ultimate Guide:** "The [Complete/Ultimate/Definitive] Guide to [Topic] ([Year])"
4. **Mistake:** "[Number] [Topic] Mistakes That Are [Costing You/Killing Your] [Result]"
5. **Question:** "Is Your [Topic] [Problem]? Here's How to Fix It"
6. **Contrast:** "Why [Common Approach] Doesn't Work (And What Does)"
7. **Specific Result:** "How [We/I] [Achieved Specific Result] in [Timeframe]"
8. **Secret/Surprising:** "The [Surprising/Hidden/Overlooked] Truth About [Topic]"
9. **Beginner:** "[Topic] for Beginners: Everything You Need to Know"
10. **Expert:** "[Number] Advanced [Topic] Strategies Most Experts Miss"
11. **Fast:** "How to [Achieve Goal] in [Short Time]: Step-by-Step"
12. **Without:** "[Achieve Goal] Without [Common Obstacle or Undesired Thing]"
13. **Best:** "The Best [Topic] Strategy in [Year] (Backed by Data)"
14. **Checklist:** "The [Adjective] [Topic] Checklist: [Number] Things to Do"
15. **Comparison:** "[Option A] vs [Option B]: Which Is Better for [Use Case]?"

## Scoring Each Headline (0-10)
- Contains primary keyword: +2
- Has specific number or date: +2
- Addresses pain point or desire: +2
- Uses power word: +2
- Under 60 characters: +2

## Output

```markdown
## Headline Generator Report

### Top 5 Recommended Headlines (Ranked by Score)
1. [headline] — Score: [X]/10 — Why: [reason]
2. [headline] — Score: [X]/10
3. [headline] — Score: [X]/10
4. [headline] — Score: [X]/10
5. [headline] — Score: [X]/10

### All 15+ Variations
[Complete list]

### A/B Test Recommendation
Test: [headline A] vs [headline B]
Hypothesis: [headline A] will win because [reason]
```

---

# Agent: CRO Analyst

**Auto-triggers after:** `/landing-write`, `/landing-audit`
**Purpose:** Conversion rate optimization analysis for landing pages

## CRO Framework (5 Categories, 20 pts each = 100 total)

### 1. Above-the-Fold Effectiveness (0-20)
- H1 clarity: does it communicate value in 5 seconds?
- Subheadline: supports and expands H1?
- Hero image: relevant, high quality, shows product/outcome?
- CTA: visible without scrolling, specific, compelling?
- Trust signal: at least one above fold (logo bar, review count, etc.)?

### 2. CTA Quality & Distribution (0-20)
- Primary CTA copy: specific ("Start Free Trial") vs generic ("Submit")?
- CTA button: contrasting color, appropriate size?
- CTA frequency: present at top, middle, and bottom?
- Secondary CTA: softer option for not-ready visitors?
- CTA above fold + repeated in 3 logical places?

### 3. Trust Signals (0-20)
- Testimonials: specific, attributed, with photo?
- Social proof numbers: customers, reviews, years?
- Logos: recognizable client/partner logos?
- Guarantees: money-back, free trial, risk reversal?
- Security badges: SSL, payment security (for checkout)?

### 4. Friction & Clarity (0-20)
- Form fields: minimum needed (3-5 for lead gen)?
- Value proposition: clear what they get and why it matters?
- Objections addressed: FAQ or inline objection handling?
- Cognitive load: is the page trying to do too many things?
- Mobile: everything works and is readable on phone?

### 5. Page Structure (0-20)
- Visual hierarchy: eyes flow from headline → benefit → CTA?
- White space: content is scannable, not walls of text?
- Section flow: problem → solution → proof → CTA?
- Load speed: no heavy images blocking above-fold?
- Exit intent: any mechanism to capture leaving visitors?

## Output

```markdown
## CRO Analysis Report
**CRO Score: [X]/100**

### Category Scores
| Category | Score | Max | Key Issue |
|---|---|---|---|

### 🔴 Critical Fixes (Immediate Impact)
1. [Fix] — Expected lift: [%] 

### 🟡 High Impact Improvements
...

### A/B Test Ideas
1. Test: [Current] vs [Variant] — Hypothesis: [...]
2. ...
```
