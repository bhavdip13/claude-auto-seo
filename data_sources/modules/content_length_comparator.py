"""
Claude Auto SEO — Content Length Comparator
Analyzes word counts of top SERP results to determine optimal content length.
"""

import re
import statistics
import urllib.request
from typing import Dict, List, Optional
from urllib.error import URLError


def fetch_page_text(url: str, timeout: int = 10) -> Optional[str]:
    """Fetch a page and extract plain text."""
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; ClaudeAutoSEO/1.0)"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
        return _extract_text(html)
    except (URLError, Exception):
        return None


def _extract_text(html: str) -> str:
    """Strip HTML and return plain text."""
    # Remove script and style blocks
    html = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', html, flags=re.DOTALL | re.IGNORECASE)
    # Remove all tags
    text = re.sub(r'<[^>]+>', ' ', html)
    # Normalise whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def count_words(text: str) -> int:
    """Count words in plain text."""
    if not text:
        return 0
    return len(re.findall(r'\b[a-zA-Z]+\b', text))


def analyze_competitor_lengths(urls: List[str]) -> Dict:
    """
    Fetch and analyze word counts for a list of competitor URLs.

    Args:
        urls: List of URLs from SERP top 10

    Returns:
        Dict with statistics and optimal target length.
    """
    results = []
    failed = []

    print(f"Analyzing {len(urls)} competitor pages...")
    for i, url in enumerate(urls, 1):
        text = fetch_page_text(url)
        if text:
            wc = count_words(text)
            if wc > 200:  # Filter out pages with almost no content
                results.append({"url": url, "word_count": wc, "rank": i})
                print(f"  ✓ #{i}: {url[:60]}... — {wc:,} words")
            else:
                failed.append(url)
                print(f"  ✗ #{i}: {url[:60]}... — too short or blocked")
        else:
            failed.append(url)
            print(f"  ✗ #{i}: {url[:60]}... — fetch failed")

    if not results:
        return {
            "error": "Could not fetch any competitor pages",
            "failed_urls": failed,
        }

    word_counts = [r["word_count"] for r in results]

    # Statistics
    avg = round(statistics.mean(word_counts))
    median = round(statistics.median(word_counts))
    p75 = round(sorted(word_counts)[int(len(word_counts) * 0.75)])
    min_wc = min(word_counts)
    max_wc = max(word_counts)

    # Recommended target = 75th percentile + 10% (beat most competitors)
    target = round(p75 * 1.1 / 100) * 100  # Round to nearest 100

    return {
        "pages_analyzed": len(results),
        "pages_failed": len(failed),
        "word_count_stats": {
            "average": avg,
            "median": median,
            "75th_percentile": p75,
            "minimum": min_wc,
            "maximum": max_wc,
        },
        "recommended_target": target,
        "recommendation": _generate_recommendation(target),
        "results": sorted(results, key=lambda x: x["rank"]),
        "failed_urls": failed,
    }


def compare_to_competitors(your_word_count: int, competitor_stats: Dict) -> Dict:
    """
    Compare your content length to competitors.

    Args:
        your_word_count: Your article's word count
        competitor_stats: Output from analyze_competitor_lengths()

    Returns:
        Dict with gap analysis and specific recommendation.
    """
    if "error" in competitor_stats:
        return {"error": competitor_stats["error"]}

    avg = competitor_stats["word_count_stats"]["average"]
    median = competitor_stats["word_count_stats"]["median"]
    target = competitor_stats["recommended_target"]

    gap_to_average = target - your_word_count
    gap_to_target = target - your_word_count

    if your_word_count >= target:
        position = "above_target"
        label = "✅ Above target length"
        action = "Content length is competitive. Focus on quality, not length."
    elif your_word_count >= avg:
        position = "at_average"
        label = "🟡 At average — could be stronger"
        action = f"Add {gap_to_target:,} more words to reach the top 25% of competitors."
    elif your_word_count >= median:
        position = "below_average"
        label = "🟠 Below average"
        action = f"Add {gap_to_target:,} more words. You're below the average ({avg:,} words)."
    else:
        position = "thin_content"
        label = "🔴 Thin content — significantly below competitors"
        action = f"Expand significantly. Target {target:,} words (you have {your_word_count:,})."

    sections_to_add = max(0, round(gap_to_target / 300))  # ~300 words per section

    return {
        "your_word_count": your_word_count,
        "competitor_average": avg,
        "competitor_median": median,
        "recommended_target": target,
        "gap_to_target": max(0, gap_to_target),
        "position": position,
        "label": label,
        "action": action,
        "sections_to_add": sections_to_add,
        "sections_to_add_note": f"Add approximately {sections_to_add} new H2 sections to reach target." if sections_to_add > 0 else "No sections need to be added.",
    }


def _generate_recommendation(target: int) -> str:
    if target < 1000:
        return f"Target {target:,} words. This is a short-form topic — be concise and focused."
    elif target < 2000:
        return f"Target {target:,} words. Medium-length content. Cover the topic thoroughly but efficiently."
    elif target < 3500:
        return f"Target {target:,} words. This topic requires comprehensive coverage. Include examples, data, and FAQs."
    else:
        return f"Target {target:,} words. This is a deep, competitive topic. Create a definitive resource."


def estimate_from_keyword(keyword: str) -> Dict:
    """
    Estimate optimal length based on keyword type (when live fetch isn't possible).
    Uses heuristics based on keyword patterns.
    """
    keyword_lower = keyword.lower()

    # Long-form content signals
    if any(x in keyword_lower for x in ["guide", "tutorial", "how to", "complete", "ultimate", "everything"]):
        return {"estimated_target": 3500, "basis": "keyword signals comprehensive guide format"}

    # Comparison / review
    if any(x in keyword_lower for x in ["vs", "versus", "compare", "best", "review", "alternative"]):
        return {"estimated_target": 2800, "basis": "keyword signals comparison/review format"}

    # Definition / what is
    if any(x in keyword_lower for x in ["what is", "what are", "definition", "meaning", "explained"]):
        return {"estimated_target": 1800, "basis": "keyword signals explainer format"}

    # Lists
    if re.search(r'\b\d+\s+(ways|tips|tricks|tools|examples|ideas|steps)\b', keyword_lower):
        return {"estimated_target": 2200, "basis": "keyword signals list-format article"}

    # Default
    return {"estimated_target": 2000, "basis": "standard blog post estimate"}


if __name__ == "__main__":
    # Example: estimate without live fetch
    result = estimate_from_keyword("how to do technical SEO audit")
    print(f"Estimated target: {result['estimated_target']:,} words")
    print(f"Basis: {result['basis']}")

    # Compare your content
    comparison = compare_to_competitors(
        your_word_count=1200,
        competitor_stats={
            "word_count_stats": {"average": 2100, "median": 1900, "75th_percentile": 2600},
            "recommended_target": 2860,
        }
    )
    print(f"\nYour 1,200 words vs competitors:")
    print(f"  Status: {comparison['label']}")
    print(f"  Action: {comparison['action']}")
