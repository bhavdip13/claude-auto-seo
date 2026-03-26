"""
Claude Auto SEO — SEO Quality Rater Module
Rates content against SEO best practices and returns a 0-100 score.
"""

import re
from typing import Dict, List, Tuple
from keyword_analyzer import calculate_keyword_density, check_keyword_placements
from readability_scorer import generate_readability_report, get_words


def extract_meta(html: str) -> Dict:
    """Extract meta tags from HTML."""
    title = re.findall(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
    desc = re.findall(
        r'<meta[^>]*name=["\']description["\'][^>]*content=["\'](.*?)["\']',
        html, re.IGNORECASE
    )
    h1s = re.findall(r'<h1[^>]*>(.*?)</h1>', html, re.IGNORECASE | re.DOTALL)
    h2s = re.findall(r'<h2[^>]*>(.*?)</h2>', html, re.IGNORECASE | re.DOTALL)
    h3s = re.findall(r'<h3[^>]*>(.*?)</h3>', html, re.IGNORECASE | re.DOTALL)
    images = re.findall(r'<img[^>]*>', html, re.IGNORECASE)
    images_with_alt = re.findall(r'<img[^>]*alt=["\'][^"\']+["\'][^>]*>', html, re.IGNORECASE)
    internal_links = re.findall(r'<a[^>]*href=["\'][^"\']*["\'][^>]*>', html, re.IGNORECASE)

    return {
        "title": re.sub(r'<[^>]+>', '', title[0]).strip() if title else "",
        "description": desc[0].strip() if desc else "",
        "h1s": [re.sub(r'<[^>]+>', '', h).strip() for h in h1s],
        "h2s": [re.sub(r'<[^>]+>', '', h).strip() for h in h2s],
        "h3s": [re.sub(r'<[^>]+>', '', h).strip() for h in h3s],
        "image_count": len(images),
        "images_with_alt": len(images_with_alt),
        "link_count": len(internal_links),
    }


def rate_content_quality(text: str, word_count: int) -> Tuple[int, List[str]]:
    """Rate content quality. Max 25 points."""
    score = 0
    issues = []

    # Word count
    if word_count >= 2500:
        score += 10
    elif word_count >= 1500:
        score += 7
        issues.append(f"Word count {word_count} is below recommended 2500+")
    elif word_count >= 800:
        score += 4
        issues.append(f"Word count {word_count} is low. Expand to 1500+ minimum.")
    else:
        issues.append(f"Word count {word_count} is too low. Content may be seen as thin.")

    # Readability
    read_report = generate_readability_report(text)
    read_score = read_report["overall_score"]
    if read_score >= 80:
        score += 10
    elif read_score >= 60:
        score += 7
    elif read_score >= 40:
        score += 4
        issues.append("Readability needs improvement. Simplify sentences.")
    else:
        issues.append("Content is very difficult to read. Major simplification needed.")

    # Has lists (signals structured, scannable content)
    if re.search(r'<[uo]l>', text, re.IGNORECASE) or '- ' in text or '• ' in text:
        score += 5
    else:
        issues.append("Add bullet points or numbered lists to improve scannability.")

    return min(25, score), issues


def rate_keyword_optimization(text: str, keyword: str, html: str = "") -> Tuple[int, List[str]]:
    """Rate keyword optimization. Max 25 points."""
    score = 0
    issues = []

    density_data = calculate_keyword_density(text, keyword)
    placement_data = check_keyword_placements(text, keyword, html)

    density = density_data["density_percent"]
    placement_score = placement_data["placement_score"]

    # Density scoring
    if 1.0 <= density <= 2.0:
        score += 10
    elif 0.5 <= density < 1.0 or 2.0 < density <= 2.5:
        score += 6
        issues.append(f"Keyword density {density}% is slightly off. Target 1-2%.")
    elif density > 2.5:
        score += 2
        issues.append(f"Keyword density {density}% is too high. Reduce usage.")
    else:
        issues.append(f"Keyword density {density}% is too low. Add more natural uses.")

    # Placement scoring (out of 100 → scale to 15 points)
    placement_pts = round(placement_score * 0.15)
    score += placement_pts

    if not placement_data.get("in_h1"):
        issues.append("Add primary keyword to H1 heading.")
    if not placement_data.get("in_first_100_words"):
        issues.append("Include primary keyword in the first 100 words.")
    if not placement_data.get("in_title_tag"):
        issues.append("Add primary keyword to the page title tag.")

    return min(25, score), issues


def rate_meta_elements(meta: Dict) -> Tuple[int, List[str]]:
    """Rate meta tags and headings. Max 25 points."""
    score = 0
    issues = []

    # Title tag
    title = meta.get("title", "")
    if title:
        title_len = len(title)
        if 50 <= title_len <= 60:
            score += 8
        elif 45 <= title_len <= 65:
            score += 5
            issues.append(f"Title tag is {title_len} chars. Ideal: 50-60 chars.")
        else:
            score += 2
            issues.append(f"Title tag is {title_len} chars — {'too long' if title_len > 65 else 'too short'}. Target: 50-60.")
    else:
        issues.append("Missing title tag — critical SEO issue.")

    # Meta description
    desc = meta.get("description", "")
    if desc:
        desc_len = len(desc)
        if 150 <= desc_len <= 160:
            score += 7
        elif 120 <= desc_len <= 175:
            score += 4
            issues.append(f"Meta description is {desc_len} chars. Ideal: 150-160 chars.")
        else:
            score += 2
            issues.append(f"Meta description is {desc_len} chars — {'too long' if desc_len > 175 else 'too short'}.")
    else:
        issues.append("Missing meta description.")

    # H1
    h1s = meta.get("h1s", [])
    if len(h1s) == 1:
        score += 5
    elif len(h1s) == 0:
        issues.append("Missing H1 tag.")
    else:
        score += 2
        issues.append(f"Multiple H1 tags found ({len(h1s)}). Use only one H1 per page.")

    # H2 structure
    h2s = meta.get("h2s", [])
    if len(h2s) >= 3:
        score += 5
    elif len(h2s) >= 1:
        score += 3
        issues.append(f"Only {len(h2s)} H2 tag(s). Add more subheadings to improve structure.")
    else:
        issues.append("No H2 tags found. Add subheadings to organize content.")

    return min(25, score), issues


def rate_links_and_images(meta: Dict, word_count: int) -> Tuple[int, List[str]]:
    """Rate internal links and image optimization. Max 25 points."""
    score = 0
    issues = []

    # Internal links
    link_count = meta.get("link_count", 0)
    if link_count >= 3:
        score += 10
        if link_count > 10:
            issues.append(f"{link_count} internal links may be too many. Keep under 10 per article.")
    elif link_count >= 1:
        score += 6
        issues.append(f"Only {link_count} internal link(s). Add 3-5 internal links.")
    else:
        issues.append("No internal links found. Add 3-5 internal links to boost SEO.")

    # Images
    img_count = meta.get("image_count", 0)
    img_with_alt = meta.get("images_with_alt", 0)

    if img_count > 0:
        score += 5
        alt_ratio = img_with_alt / img_count
        if alt_ratio >= 0.9:
            score += 10
        elif alt_ratio >= 0.5:
            score += 6
            issues.append(f"{img_count - img_with_alt} images missing alt text.")
        else:
            score += 2
            issues.append(f"Most images ({img_count - img_with_alt}/{img_count}) are missing alt text.")
    else:
        issues.append("No images found. Add at least 1 relevant image with descriptive alt text.")

    return min(25, score), issues


def generate_seo_quality_report(text: str, keyword: str,
                                  html: str = "",
                                  word_count: int = None) -> Dict:
    """Generate complete SEO quality rating report."""
    if word_count is None:
        word_count = len(get_words(text))

    meta = extract_meta(html) if html else {
        "title": "", "description": "", "h1s": [], "h2s": [],
        "h3s": [], "image_count": 0, "images_with_alt": 0, "link_count": 0
    }

    content_score, content_issues = rate_content_quality(text, word_count)
    keyword_score, keyword_issues = rate_keyword_optimization(text, keyword, html)
    meta_score, meta_issues = rate_meta_elements(meta)
    link_score, link_issues = rate_links_and_images(meta, word_count)

    total_score = content_score + keyword_score + meta_score + link_score
    all_issues = content_issues + keyword_issues + meta_issues + link_issues

    # Determine publishing readiness
    if total_score >= 80:
        readiness = "ready_to_publish"
        readiness_label = "✅ Ready to Publish"
    elif total_score >= 65:
        readiness = "minor_fixes_needed"
        readiness_label = "🟡 Minor Fixes Needed"
    elif total_score >= 45:
        readiness = "significant_work_needed"
        readiness_label = "🟠 Significant Work Needed"
    else:
        readiness = "not_ready"
        readiness_label = "🔴 Not Ready — Major Issues"

    return {
        "overall_score": total_score,
        "publishing_readiness": readiness,
        "publishing_readiness_label": readiness_label,
        "dimension_scores": {
            "content_quality": {"score": content_score, "max": 25},
            "keyword_optimization": {"score": keyword_score, "max": 25},
            "meta_elements": {"score": meta_score, "max": 25},
            "links_and_images": {"score": link_score, "max": 25},
        },
        "issues": all_issues,
        "word_count": word_count,
        "keyword": keyword,
    }


if __name__ == "__main__":
    sample_text = """
    Search engine optimization is the practice of improving a website's visibility
    in search engines. Good SEO practices include keyword research, quality content
    creation, and technical optimization. By following SEO best practices, websites
    can rank higher and attract more organic traffic.
    """

    sample_html = """
    <html><head>
    <title>SEO Guide — Complete 2026 Tutorial</title>
    <meta name="description" content="Learn search engine optimization with our complete 2026 guide covering all key techniques to rank higher in Google.">
    </head><body>
    <h1>Complete SEO Guide for 2026</h1>
    <h2>What is SEO?</h2>
    <h2>Keyword Research</h2>
    <h2>Technical SEO</h2>
    <img src="seo-guide.jpg" alt="SEO guide diagram">
    <a href="/keyword-research">Learn keyword research</a>
    </body></html>
    """

    report = generate_seo_quality_report(sample_text, "seo", sample_html)
    print(f"SEO Score: {report['overall_score']}/100")
    print(f"Status: {report['publishing_readiness_label']}")
    for issue in report["issues"]:
        print(f"  → {issue}")
