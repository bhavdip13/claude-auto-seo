"""
Claude Auto SEO — Keyword Analyzer Module
Analyzes keyword density, distribution, clustering, and LSI coverage.
"""

import re
import math
from collections import Counter
from typing import Dict, List, Tuple


def clean_text(text: str) -> str:
    """Remove HTML tags and normalize whitespace."""
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip().lower()


def get_word_count(text: str) -> int:
    words = clean_text(text).split()
    return len(words)


def calculate_keyword_density(text: str, keyword: str) -> Dict:
    """Calculate keyword density and return detailed stats."""
    clean = clean_text(text)
    words = clean.split()
    total_words = len(words)

    keyword_lower = keyword.lower()
    keyword_words = keyword_lower.split()
    keyword_len = len(keyword_words)

    # Count exact phrase occurrences
    count = 0
    for i in range(len(words) - keyword_len + 1):
        if words[i:i + keyword_len] == keyword_words:
            count += 1

    density = (count / total_words * 100) if total_words > 0 else 0

    # Determine status
    if density < 0.5:
        status = "too_low"
        message = f"Keyword density {density:.2f}% is too low. Target: 1-2%."
    elif density <= 2.0:
        status = "optimal"
        message = f"Keyword density {density:.2f}% is optimal."
    elif density <= 3.0:
        status = "slightly_high"
        message = f"Keyword density {density:.2f}% is slightly high. Risk of over-optimization."
    else:
        status = "stuffed"
        message = f"Keyword density {density:.2f}% is too high. Keyword stuffing risk!"

    return {
        "keyword": keyword,
        "count": count,
        "total_words": total_words,
        "density_percent": round(density, 2),
        "status": status,
        "message": message,
        "target_count": round(total_words * 0.015),  # 1.5% target
    }


def check_keyword_placements(text: str, keyword: str, html: str = "") -> Dict:
    """Check if keyword appears in critical SEO positions."""
    kw = keyword.lower()

    # Extract sections from HTML if provided
    h1 = re.findall(r'<h1[^>]*>(.*?)</h1>', html, re.IGNORECASE | re.DOTALL)
    h2s = re.findall(r'<h2[^>]*>(.*?)</h2>', html, re.IGNORECASE | re.DOTALL)
    title = re.findall(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
    meta_desc = re.findall(r'<meta[^>]*name=["\']description["\'][^>]*content=["\'](.*?)["\']', html, re.IGNORECASE)

    # First 100 words
    first_100 = ' '.join(clean_text(text).split()[:100])

    placements = {
        "in_title_tag": any(kw in clean_text(t) for t in title),
        "in_h1": any(kw in clean_text(h) for h in h1),
        "in_first_100_words": kw in first_100,
        "in_h2_count": sum(1 for h in h2s if kw in clean_text(h)),
        "in_meta_description": any(kw in clean_text(m) for m in meta_desc),
    }

    score = 0
    if placements["in_title_tag"]: score += 25
    if placements["in_h1"]: score += 25
    if placements["in_first_100_words"]: score += 20
    if placements["in_h2_count"] >= 1: score += 20
    if placements["in_meta_description"]: score += 10

    placements["placement_score"] = score
    placements["placement_status"] = "excellent" if score >= 80 else "good" if score >= 60 else "needs_work"

    return placements


def get_section_distribution(text: str, keyword: str, html: str = "") -> List[Dict]:
    """Map keyword distribution across H2 sections."""
    kw = keyword.lower()

    if html:
        # Split by H2 headings
        sections = re.split(r'<h2[^>]*>.*?</h2>', html, flags=re.IGNORECASE | re.DOTALL)
        headings = re.findall(r'<h2[^>]*>(.*?)</h2>', html, re.IGNORECASE | re.DOTALL)
    else:
        sections = [text]
        headings = ["Full Content"]

    distribution = []
    for i, (heading, section) in enumerate(zip(
        ["Introduction"] + [clean_text(h) for h in headings],
        sections
    )):
        section_text = clean_text(section)
        section_words = section_text.split()
        count = sum(1 for j in range(len(section_words) - len(kw.split()) + 1)
                    if ' '.join(section_words[j:j+len(kw.split())]) == kw)
        density = (count / len(section_words) * 100) if section_words else 0

        distribution.append({
            "section": heading[:50],
            "word_count": len(section_words),
            "keyword_count": count,
            "density": round(density, 2),
            "bar": "█" * min(count * 2, 20) + "░" * max(0, 20 - count * 2)
        })

    return distribution


def detect_keyword_stuffing(text: str, primary_keyword: str) -> Dict:
    """Detect keyword stuffing patterns."""
    clean = clean_text(text)
    words = clean.split()

    # Check for consecutive keyword repetitions
    kw_words = primary_keyword.lower().split()
    kw_len = len(kw_words)
    positions = []

    for i in range(len(words) - kw_len + 1):
        if words[i:i + kw_len] == kw_words:
            positions.append(i)

    # Check if any two occurrences are within 20 words
    suspicious_clusters = []
    for i in range(len(positions) - 1):
        if positions[i + 1] - positions[i] < 20:
            suspicious_clusters.append({
                "position_1": positions[i],
                "position_2": positions[i + 1],
                "gap": positions[i + 1] - positions[i]
            })

    stuffing_risk = "high" if len(suspicious_clusters) >= 3 else \
                    "medium" if len(suspicious_clusters) >= 1 else "low"

    return {
        "stuffing_risk": stuffing_risk,
        "suspicious_clusters": suspicious_clusters,
        "total_keyword_positions": positions,
        "recommendation": "Reduce keyword frequency and ensure natural distribution." if stuffing_risk != "low" else "Keyword distribution looks natural."
    }


def generate_keyword_report(text: str, primary_keyword: str,
                             secondary_keywords: List[str] = None,
                             html: str = "") -> Dict:
    """Generate a complete keyword analysis report."""
    secondary_keywords = secondary_keywords or []

    report = {
        "primary": {
            "keyword": primary_keyword,
            "density": calculate_keyword_density(text, primary_keyword),
            "placements": check_keyword_placements(text, primary_keyword, html),
            "distribution": get_section_distribution(text, primary_keyword, html),
            "stuffing_check": detect_keyword_stuffing(text, primary_keyword),
        },
        "secondary": [],
        "word_count": get_word_count(text),
    }

    for kw in secondary_keywords:
        report["secondary"].append({
            "keyword": kw,
            "density": calculate_keyword_density(text, kw),
            "in_h2": any(kw.lower() in h.lower() for h in
                         re.findall(r'<h2[^>]*>(.*?)</h2>', html, re.IGNORECASE) if html),
        })

    return report


if __name__ == "__main__":
    # Example usage
    sample_text = """
    SEO optimization is crucial for any website. Good SEO optimization practices
    help websites rank higher. When you implement SEO optimization correctly,
    you can see significant traffic improvements. This guide covers SEO optimization
    from basics to advanced techniques.
    """

    result = generate_keyword_report(sample_text, "seo optimization",
                                     secondary_keywords=["website ranking", "traffic"])
    print(f"Primary keyword density: {result['primary']['density']['density_percent']}%")
    print(f"Stuffing risk: {result['primary']['stuffing_check']['stuffing_risk']}")
