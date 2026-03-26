"""
Claude Auto SEO — Search Intent Analyzer
Classifies search queries into informational, navigational, transactional,
or commercial investigation intent with confidence scoring.
"""

import re
from typing import Dict, List, Tuple


# Intent signal word lists
INFORMATIONAL_SIGNALS = [
    "what is", "what are", "how to", "how do", "how does", "why is", "why does",
    "when did", "when is", "where is", "who is", "which", "explain", "definition",
    "meaning", "guide", "tutorial", "examples", "types of", "list of", "history of",
    "difference between", "vs", "versus", "compare", "overview", "introduction",
    "benefits of", "advantages", "disadvantages", "pros and cons", "tips",
    "ideas", "ways to", "steps to", "learn", "understand", "facts about"
]

NAVIGATIONAL_SIGNALS = [
    "login", "sign in", "sign up", "register", "official", "website", "homepage",
    "contact", "support", "download", "app", "portal", "account", "dashboard",
    "careers", "jobs", "about us", "blog", "forum", "community"
]

TRANSACTIONAL_SIGNALS = [
    "buy", "purchase", "order", "shop", "deal", "discount", "coupon", "promo",
    "cheap", "affordable", "price", "cost", "how much", "free trial", "free download",
    "get started", "sign up for", "subscribe", "hire", "book", "reserve", "rent",
    "near me", "delivery", "shipping", "checkout", "add to cart", "for sale"
]

COMMERCIAL_SIGNALS = [
    "best", "top", "review", "reviews", "rating", "comparison", "alternative",
    "alternatives", "vs", "versus", "recommend", "recommendation", "worth it",
    "is it good", "should i", "which is better", "most popular", "leading",
    "ranked", "award", "top rated", "highest rated", "expert", "professional"
]


def classify_intent(query: str) -> Dict:
    """
    Classify search intent for a query.

    Returns:
        Dict with primary_intent, confidence, scores per intent type,
        and content_recommendations.
    """
    query_lower = query.lower().strip()
    words = query_lower.split()

    scores = {
        "informational": 0,
        "navigational": 0,
        "transactional": 0,
        "commercial": 0,
    }

    # Check multi-word signals
    for signal in INFORMATIONAL_SIGNALS:
        if signal in query_lower:
            scores["informational"] += 3 if len(signal.split()) > 1 else 1

    for signal in NAVIGATIONAL_SIGNALS:
        if signal in query_lower:
            scores["navigational"] += 3 if len(signal.split()) > 1 else 1

    for signal in TRANSACTIONAL_SIGNALS:
        if signal in query_lower:
            scores["transactional"] += 3 if len(signal.split()) > 1 else 1

    for signal in COMMERCIAL_SIGNALS:
        if signal in query_lower:
            scores["commercial"] += 3 if len(signal.split()) > 1 else 1

    # Heuristic boosts
    # Questions are almost always informational
    if query_lower.startswith(("what ", "how ", "why ", "when ", "where ", "who ", "which ")):
        scores["informational"] += 5

    # Brand + product name patterns → navigational
    if re.search(r'\b(amazon|google|facebook|twitter|linkedin|youtube|netflix)\b', query_lower):
        scores["navigational"] += 3

    # Price/location modifiers → transactional
    if re.search(r'\b(near me|online|store|shop)\b', query_lower):
        scores["transactional"] += 2

    # "Best X" without "how" → commercial
    if re.match(r'^best\s', query_lower) and "how" not in query_lower:
        scores["commercial"] += 4

    # Normalise — avoid all zeros
    total = sum(scores.values()) or 1
    normalized = {k: round(v / total * 100, 1) for k, v in scores.items()}

    # Primary intent = highest score
    primary = max(scores, key=scores.get)

    # Confidence: how dominant is the top score vs second
    sorted_scores = sorted(scores.values(), reverse=True)
    confidence = "high" if sorted_scores[0] >= sorted_scores[1] * 2 else \
                 "medium" if sorted_scores[0] > sorted_scores[1] else "low"

    content_recs = _get_content_recommendations(primary, query_lower)

    return {
        "query": query,
        "primary_intent": primary,
        "confidence": confidence,
        "scores": normalized,
        "content_recommendations": content_recs,
        "serp_features_likely": _predict_serp_features(primary, query_lower),
    }


def _get_content_recommendations(intent: str, query: str) -> Dict:
    """Return content format and structure recommendations per intent."""
    recs = {
        "informational": {
            "content_type": "Educational guide or explainer article",
            "ideal_format": "Long-form guide with H2/H3 structure, examples, FAQ section",
            "word_count": "2,000–4,000 words",
            "must_include": ["Clear definition in first paragraph", "Step-by-step if applicable",
                             "Examples and use cases", "FAQ section"],
            "cta_type": "Resource download, newsletter signup, related articles",
        },
        "navigational": {
            "content_type": "Brand/product page or directory listing",
            "ideal_format": "Clean landing page with clear navigation and CTAs",
            "word_count": "500–1,500 words",
            "must_include": ["Brand name in H1 and title", "Quick access to destination",
                             "Trust signals"],
            "cta_type": "Direct link to destination page",
        },
        "transactional": {
            "content_type": "Product page, pricing page, or service page",
            "ideal_format": "Conversion-focused with price, CTA above fold, trust signals",
            "word_count": "500–1,200 words",
            "must_include": ["Price/offer prominently displayed", "Buy/signup CTA",
                             "Social proof (reviews, testimonials)", "Urgency if applicable"],
            "cta_type": "Buy now, Add to cart, Start free trial, Book now",
        },
        "commercial": {
            "content_type": "Comparison article, roundup, or review",
            "ideal_format": "Comparison table, pros/cons lists, expert scoring",
            "word_count": "2,500–5,000 words",
            "must_include": ["Comparison table", "Clear winner recommendation",
                             "Pros and cons per option", "Use case guidance"],
            "cta_type": "Try X, See pricing, Read full review",
        },
    }
    return recs.get(intent, recs["informational"])


def _predict_serp_features(intent: str, query: str) -> List[str]:
    """Predict which SERP features are likely to appear."""
    features = []

    if intent == "informational":
        features.extend(["Featured Snippet", "People Also Ask"])
        if "how to" in query or "steps" in query:
            features.append("How-To rich result")

    if intent == "commercial":
        features.extend(["People Also Ask", "Top Stories (sometimes)"])

    if intent == "transactional":
        features.extend(["Shopping ads", "Product carousel", "Local Pack (if local)"])

    if intent == "navigational":
        features.append("Sitelinks")

    if re.search(r'\b(recipe|food|dish|cook)\b', query):
        features.append("Recipe rich result")

    if re.search(r'\b(near me|in [a-z]+|location)\b', query):
        features.append("Local Pack (Google Maps)")

    return list(set(features))


def batch_classify(queries: List[str]) -> List[Dict]:
    """Classify a list of queries."""
    return [classify_intent(q) for q in queries]


def get_intent_summary(queries: List[str]) -> Dict:
    """Summarize intent distribution across a keyword list."""
    results = batch_classify(queries)
    distribution = {"informational": 0, "navigational": 0,
                    "transactional": 0, "commercial": 0}

    for r in results:
        distribution[r["primary_intent"]] += 1

    total = len(queries) or 1
    return {
        "total_keywords": total,
        "distribution": {k: {"count": v, "percent": round(v / total * 100, 1)}
                         for k, v in distribution.items()},
        "dominant_intent": max(distribution, key=distribution.get),
        "details": results,
    }


if __name__ == "__main__":
    test_queries = [
        "what is technical SEO",
        "best SEO tools 2026",
        "buy SEMrush subscription",
        "ahrefs login",
        "how to fix crawl errors",
        "SEMrush vs Ahrefs",
        "free SEO audit tool",
    ]

    print("Search Intent Analysis\n" + "=" * 50)
    for q in test_queries:
        result = classify_intent(q)
        print(f"\nQuery: '{q}'")
        print(f"  Intent:     {result['primary_intent']} ({result['confidence']} confidence)")
        print(f"  Scores:     {result['scores']}")
        print(f"  Content:    {result['content_recommendations']['content_type']}")
