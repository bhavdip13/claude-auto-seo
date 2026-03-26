"""
Claude Auto SEO — Content Scorer
Scores content quality across 5 dimensions: humanity, specificity, structure, SEO, readability.
"""

import re
from typing import Dict, List


GENERIC_PHRASES = [
    "in today's digital landscape", "it's important to note", "delve into",
    "leverage", "utilize", "furthermore", "moreover", "in conclusion",
    "it goes without saying", "game-changer", "paradigm shift", "synergy",
    "comprehensive solution", "holistic approach", "cutting-edge", "state-of-the-art",
    "at the end of the day", "move the needle", "circle back", "deep dive",
    "touch base", "low-hanging fruit", "best practices", "value-add",
]

HUMAN_SIGNALS = [
    r"\bI\b", r"\bwe\b", r"\bour\b", r"\byou'll\b", r"\bwe're\b", r"\bit's\b",
    r"\bdon't\b", r"\bwon't\b", r"\bcan't\b", r"\bisn't\b",  # contractions
    r"\bin my experience\b", r"\bI've found\b", r"\bI tested\b",
    r"here's the thing", r"the truth is", r"honestly",
]

SPECIFIC_SIGNALS = [
    r"\d+%", r"\$\d+", r"\d+ (days?|weeks?|months?|years?|hours?|minutes?)",
    r"\d{4}",  # years
    r"for example", r"for instance", r"specifically",
    r"case stud", r"according to", r"research shows",
]


def score_humanity(text: str) -> Dict:
    """Score how human-sounding the content is (0-20)."""
    text_lower = text.lower()
    score = 20

    # Penalize generic AI phrases
    generic_count = sum(1 for p in GENERIC_PHRASES if p in text_lower)
    score -= min(10, generic_count * 2)

    # Reward human signals
    human_count = sum(1 for p in HUMAN_SIGNALS if re.search(p, text, re.IGNORECASE))
    score += min(5, human_count)

    # Penalize all-same paragraph length (AI pattern)
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    if len(paragraphs) > 3:
        lengths = [len(p.split()) for p in paragraphs]
        variance = max(lengths) - min(lengths)
        if variance < 20:
            score -= 5  # All paragraphs same length = AI pattern

    return {
        "score": max(0, min(20, score)),
        "max": 20,
        "generic_phrases_found": generic_count,
        "human_signals_found": human_count,
    }


def score_specificity(text: str) -> Dict:
    """Score how specific and concrete the content is (0-20)."""
    score = 0

    specific_count = sum(1 for p in SPECIFIC_SIGNALS if re.search(p, text, re.IGNORECASE))
    score = min(20, specific_count * 3)

    # Check for named examples
    has_examples = any(x in text.lower() for x in
                       ["for example", "for instance", "such as", "like ", "including "])
    if has_examples:
        score += 3

    return {
        "score": min(20, score),
        "max": 20,
        "specific_signals": specific_count,
    }


def score_structure(text: str, html: str = "") -> Dict:
    """Score content structure and formatting (0-20)."""
    score = 0

    # H2 headings present
    h2_count = len(re.findall(r"^##\s", text, re.MULTILINE)) + \
               len(re.findall(r"<h2", html, re.IGNORECASE))
    score += min(8, h2_count * 2)

    # Lists present
    if re.search(r"^[-*]\s", text, re.MULTILINE) or "<ul>" in html.lower():
        score += 4

    # Has intro and conclusion
    word_count = len(text.split())
    if word_count >= 1500:
        score += 4

    # Short paragraphs (good UX)
    paragraphs = [p.strip() for p in re.split(r"\n\n+", text) if p.strip()]
    if paragraphs:
        avg_para_len = sum(len(p.split()) for p in paragraphs) / len(paragraphs)
        if avg_para_len <= 80:
            score += 4

    return {"score": min(20, score), "max": 20, "h2_count": h2_count}


def score_content_seo(text: str, primary_keyword: str = "") -> Dict:
    """Score SEO optimization of content (0-20)."""
    score = 0

    if primary_keyword:
        text_lower = text.lower()
        kw_lower = primary_keyword.lower()
        word_count = len(text.split())

        # Keyword in first 100 words
        first_100 = " ".join(text.split()[:100]).lower()
        if kw_lower in first_100:
            score += 5

        # Keyword density
        kw_count = text_lower.count(kw_lower)
        density = kw_count / max(word_count, 1) * 100
        if 1.0 <= density <= 2.0:
            score += 10
        elif 0.5 <= density < 1.0:
            score += 5
    else:
        score += 10  # No keyword specified, give benefit of doubt

    # Internal links
    link_count = len(re.findall(r"\[([^\]]+)\]\(", text))
    if link_count >= 3:
        score += 5

    return {"score": min(20, score), "max": 20}


def generate_content_score_report(text: str, primary_keyword: str = "",
                                   html: str = "") -> Dict:
    """Full content quality score across all 5 dimensions."""
    humanity    = score_humanity(text)
    specificity = score_specificity(text)
    structure   = score_structure(text, html)
    seo         = score_content_seo(text, primary_keyword)

    # Readability uses readability_scorer module
    try:
        import sys
        sys.path.insert(0, os.path.dirname(__file__))
        from readability_scorer import generate_readability_report
        read_report = generate_readability_report(text)
        read_score  = min(20, read_report["overall_score"] // 5)
    except Exception:
        read_score = 12  # Default

    readability = {"score": read_score, "max": 20}

    total = humanity["score"] + specificity["score"] + structure["score"] + \
            seo["score"] + readability["score"]

    return {
        "total_score": total,
        "max_score": 100,
        "publishing_ready": total >= 70,
        "dimensions": {
            "humanity": humanity,
            "specificity": specificity,
            "structure": structure,
            "seo": seo,
            "readability": readability,
        },
        "recommendations": _get_content_recommendations(humanity, specificity, structure, seo),
    }


def _get_content_recommendations(humanity, specificity, structure, seo) -> List[str]:
    recs = []
    if humanity["score"] < 12:
        recs.append(f"Remove {humanity['generic_phrases_found']} generic AI phrases. Add contractions and first-person language.")
    if specificity["score"] < 12:
        recs.append("Add specific numbers, percentages, dates, and named examples.")
    if structure["score"] < 12:
        recs.append(f"Add more H2 subheadings (have {structure.get('h2_count',0)}, need 4+). Add bullet lists.")
    if seo["score"] < 12:
        recs.append("Include primary keyword in first 100 words and add 3+ internal links.")
    return recs


import os


# ── Competitor Gap Analyzer ───────────────────────────────────────────────────

def analyze_competitor_gaps(your_keywords: List[str],
                              competitor_keywords: Dict[str, List[str]]) -> Dict:
    """
    Find keywords competitors rank for that you don't.

    Args:
        your_keywords: List of keywords you rank for
        competitor_keywords: Dict of {competitor_name: [keywords]}
    """
    your_set = set(k.lower() for k in your_keywords)
    gaps = {}
    advantages = {}

    all_competitor_kws = set()
    for comp, kws in competitor_keywords.items():
        comp_set = set(k.lower() for k in kws)
        all_competitor_kws.update(comp_set)

        # Keywords they have that you don't
        their_gaps = comp_set - your_set
        # Keywords you have that they don't
        your_advantages = your_set - comp_set

        gaps[comp] = list(their_gaps)[:50]
        advantages[comp] = list(your_advantages)[:20]

    # Universal gaps: keywords ALL competitors rank for that you don't
    universal_gaps = all_competitor_kws - your_set

    return {
        "universal_gaps": list(universal_gaps)[:30],
        "per_competitor_gaps": gaps,
        "your_advantages": advantages,
        "total_gaps": len(universal_gaps),
        "summary": f"You're missing {len(universal_gaps)} keywords that competitors rank for.",
    }


# ── Landing Page CRO Modules ──────────────────────────────────────────────────

def analyze_above_fold(html: str) -> Dict:
    """Analyze above-the-fold content for CRO effectiveness."""
    html_lower = html.lower()

    score = 0
    issues = []

    # H1 present
    if re.search(r"<h1", html_lower):
        score += 20
    else:
        issues.append("No H1 tag found — headline is critical for above-fold clarity")

    # CTA button above fold (approximation: in first 3000 chars)
    first_3k = html[:3000].lower()
    if any(x in first_3k for x in ["<button", 'type="submit"', "btn", "cta"]):
        score += 20
    else:
        issues.append("No CTA button detected in first content area")

    # Subheadline
    if re.search(r"<h2|<p", first_3k):
        score += 20
    else:
        issues.append("No supporting text below headline")

    # Trust signal above fold
    trust_words = ["customer", "review", "star", "rating", "trust", "secure",
                   "guarantee", "free trial", "no credit card"]
    if any(w in first_3k for w in trust_words):
        score += 20
    else:
        issues.append("No trust signal visible above fold")

    # Hero image
    if "<img" in first_3k:
        score += 20
    else:
        issues.append("No image in hero area")

    return {"score": score, "max": 100, "issues": issues,
            "label": "Excellent" if score >= 80 else "Good" if score >= 60 else "Needs Work"}


def analyze_cta(html: str) -> Dict:
    """Analyze CTA buttons and their effectiveness."""
    buttons = re.findall(r"<(?:button|a)[^>]*>([^<]+)</(?:button|a)>", html, re.IGNORECASE)
    score = 0
    issues = []

    weak_cta_words = ["submit", "click here", "learn more", "read more", "go", "next"]
    strong_cta_words = ["start", "get", "try", "join", "download", "free",
                        "sign up", "create", "build", "discover"]

    button_count = len(buttons)
    weak_count = sum(1 for b in buttons if any(w in b.lower() for w in weak_cta_words))
    strong_count = sum(1 for b in buttons if any(w in b.lower() for w in strong_cta_words))

    if button_count >= 2:
        score += 25
    elif button_count >= 1:
        score += 15
    else:
        issues.append("No CTA buttons found")

    if strong_count > 0:
        score += 50
    elif weak_count > 0:
        score += 20
        issues.append(f"Weak CTA copy detected: {[b for b in buttons if any(w in b.lower() for w in weak_cta_words)]}")

    if button_count >= 3:
        score += 25
    else:
        issues.append("CTA should appear at least 3 times (top, middle, bottom)")

    return {"score": min(100, score), "max": 100, "button_count": button_count,
            "strong_ctas": strong_count, "weak_ctas": weak_count, "issues": issues}


def analyze_trust_signals(html: str) -> Dict:
    """Analyze trust signals on a page."""
    html_lower = html.lower()
    score = 0
    found = []

    trust_checks = {
        "testimonials": ["testimonial", "review", "said about", "customers say"],
        "social_proof": ["customers", "users", "companies", "businesses", "clients"],
        "numbers": [re.search(r"\d{3,}[\+k]?\s*(customers|users|reviews)", html_lower)],
        "guarantee": ["guarantee", "money-back", "refund", "no risk"],
        "security": ["secure", "ssl", "encrypted", "privacy", "safe"],
        "logos": ["logo", "as seen in", "featured in", "partner"],
        "ratings": ["⭐", "★", "stars", "rated", "rating"],
    }

    for signal_type, checks in trust_checks.items():
        found_signal = False
        for check in checks:
            if isinstance(check, str) and check in html_lower:
                found_signal = True
            elif check:  # regex match object
                found_signal = True
        if found_signal:
            score += 14
            found.append(signal_type)

    return {
        "score": min(100, score),
        "max": 100,
        "trust_signals_found": found,
        "missing": [s for s in trust_checks if s not in found],
    }


if __name__ == "__main__":
    sample = """
    I've been testing SEO strategies for 5 years. Here's what actually works in 2026.
    
    After analyzing 200+ websites, I found that 73% of ranking improvements come from 
    just 3 changes. In my experience working with B2B SaaS companies, the biggest mistake
    is skipping keyword research.
    
    ## Why Keyword Research Matters
    
    For example, one client increased traffic by 340% in 6 months by targeting 
    long-tail keywords.
    """

    report = generate_content_score_report(sample, "seo strategies")
    print(f"Content Score: {report['total_score']}/100")
    for dim, data in report["dimensions"].items():
        print(f"  {dim}: {data['score']}/{data['max']}")
