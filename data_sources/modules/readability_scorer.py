"""
Claude Auto SEO — Readability Scorer Module
Calculates Flesch Reading Ease, Flesch-Kincaid Grade Level, and other readability metrics.
"""

import re
import math
from typing import Dict, List


def count_syllables(word: str) -> int:
    """Count syllables in a word using heuristics."""
    word = word.lower().strip(".,!?;:'\"")
    if len(word) <= 3:
        return 1

    # Remove silent e at end
    if word.endswith('e') and not word.endswith('le'):
        word = word[:-1]

    # Count vowel groups
    vowels = "aeiouy"
    count = 0
    prev_vowel = False

    for char in word:
        is_vowel = char in vowels
        if is_vowel and not prev_vowel:
            count += 1
        prev_vowel = is_vowel

    return max(1, count)


def get_sentences(text: str) -> List[str]:
    """Split text into sentences."""
    text = re.sub(r'<[^>]+>', ' ', text)  # Strip HTML
    sentences = re.split(r'[.!?]+', text)
    return [s.strip() for s in sentences if len(s.strip()) > 10]


def get_words(text: str) -> List[str]:
    """Extract words from text."""
    text = re.sub(r'<[^>]+>', ' ', text)
    return re.findall(r'\b[a-zA-Z]+\b', text)


def flesch_reading_ease(text: str) -> float:
    """
    Calculate Flesch Reading Ease score.
    90-100: Very Easy (5th grade)
    70-90: Easy (6th grade)
    60-70: Standard (7th grade)
    50-60: Fairly Difficult (8th-9th grade) ← Target for SEO content
    30-50: Difficult (10th-12th grade)
    0-30: Very Difficult (College+)
    """
    sentences = get_sentences(text)
    words = get_words(text)

    if not sentences or not words:
        return 0.0

    num_sentences = len(sentences)
    num_words = len(words)
    num_syllables = sum(count_syllables(w) for w in words)

    if num_sentences == 0 or num_words == 0:
        return 0.0

    score = 206.835 - (1.015 * (num_words / num_sentences)) - (84.6 * (num_syllables / num_words))
    return round(max(0, min(100, score)), 1)


def flesch_kincaid_grade(text: str) -> float:
    """
    Calculate Flesch-Kincaid Grade Level.
    Target for SEO content: Grade 8-10.
    """
    sentences = get_sentences(text)
    words = get_words(text)

    if not sentences or not words:
        return 0.0

    num_sentences = len(sentences)
    num_words = len(words)
    num_syllables = sum(count_syllables(w) for w in words)

    grade = (0.39 * (num_words / num_sentences)) + (11.8 * (num_syllables / num_words)) - 15.59
    return round(max(0, grade), 1)


def average_sentence_length(text: str) -> float:
    """Calculate average words per sentence. Target: 15-20."""
    sentences = get_sentences(text)
    words = get_words(text)

    if not sentences:
        return 0.0

    return round(len(words) / len(sentences), 1)


def passive_voice_ratio(text: str) -> float:
    """Estimate passive voice ratio. Target: < 15%."""
    sentences = get_sentences(text)
    if not sentences:
        return 0.0

    passive_patterns = [
        r'\b(is|are|was|were|be|been|being)\s+\w+ed\b',
        r'\b(is|are|was|were|be|been|being)\s+\w+en\b',
        r'\bhas been\b', r'\bhave been\b', r'\bhad been\b',
        r'\bwas made\b', r'\bwere made\b', r'\bwas done\b',
        r'\bwere done\b', r'\bwas given\b', r'\bwere given\b',
    ]

    passive_count = 0
    for sentence in sentences:
        sentence_lower = sentence.lower()
        for pattern in passive_patterns:
            if re.search(pattern, sentence_lower):
                passive_count += 1
                break

    return round((passive_count / len(sentences)) * 100, 1)


def complex_word_ratio(text: str) -> float:
    """Ratio of words with 3+ syllables. Target: < 20%."""
    words = get_words(text)
    if not words:
        return 0.0

    complex_count = sum(1 for w in words if count_syllables(w) >= 3)
    return round((complex_count / len(words)) * 100, 1)


def transition_word_ratio(text: str) -> float:
    """Check transition word usage. Target: > 30% of sentences."""
    transition_words = [
        'however', 'therefore', 'furthermore', 'additionally', 'moreover',
        'consequently', 'nevertheless', 'meanwhile', 'subsequently', 'thus',
        'hence', 'accordingly', 'otherwise', 'similarly', 'likewise',
        'first', 'second', 'third', 'finally', 'next', 'then', 'also',
        'but', 'yet', 'so', 'for example', 'for instance', 'in addition',
        'in contrast', 'as a result', 'in conclusion', 'in summary',
        'on the other hand', 'at the same time', 'in fact', 'indeed'
    ]

    sentences = get_sentences(text)
    if not sentences:
        return 0.0

    sentences_with_transitions = 0
    for sentence in sentences:
        sentence_lower = sentence.lower()
        for tw in transition_words:
            if tw in sentence_lower:
                sentences_with_transitions += 1
                break

    return round((sentences_with_transitions / len(sentences)) * 100, 1)


def calculate_readability_score(fre: float, fk_grade: float,
                                  passive_ratio: float, complex_ratio: float) -> int:
    """Calculate overall readability score 0-100."""
    score = 100

    # FRE: Ideal 50-70 for SEO content
    if fre < 30:
        score -= 25
    elif fre < 50:
        score -= 10
    elif fre > 80:
        score -= 5  # Too simple

    # FK Grade: Ideal 8-10
    if fk_grade > 14:
        score -= 20
    elif fk_grade > 12:
        score -= 10
    elif fk_grade < 6:
        score -= 5

    # Passive voice: ideal < 15%
    if passive_ratio > 30:
        score -= 20
    elif passive_ratio > 15:
        score -= 10

    # Complex words: ideal < 20%
    if complex_ratio > 35:
        score -= 15
    elif complex_ratio > 20:
        score -= 5

    return max(0, min(100, score))


def generate_readability_report(text: str) -> Dict:
    """Generate complete readability analysis."""
    fre = flesch_reading_ease(text)
    fk_grade = flesch_kincaid_grade(text)
    avg_sentence = average_sentence_length(text)
    passive = passive_voice_ratio(text)
    complex_words = complex_word_ratio(text)
    transitions = transition_word_ratio(text)
    overall_score = calculate_readability_score(fre, fk_grade, passive, complex_words)

    # Grade interpretation
    fk_interpretation = (
        "Very Easy" if fk_grade <= 6 else
        "Easy" if fk_grade <= 8 else
        "Optimal for SEO" if fk_grade <= 10 else
        "Slightly Complex" if fk_grade <= 12 else
        "Complex" if fk_grade <= 14 else
        "Very Complex"
    )

    return {
        "overall_score": overall_score,
        "flesch_reading_ease": {
            "score": fre,
            "status": "good" if 50 <= fre <= 70 else "needs_work",
            "interpretation": "Standard" if 60 <= fre <= 70 else "Fairly Difficult" if 50 <= fre < 60 else "Too Easy" if fre > 70 else "Too Hard"
        },
        "flesch_kincaid_grade": {
            "grade": fk_grade,
            "interpretation": fk_interpretation,
            "status": "optimal" if 8 <= fk_grade <= 10 else "acceptable" if 6 <= fk_grade <= 12 else "needs_work"
        },
        "avg_sentence_length": {
            "value": avg_sentence,
            "status": "good" if 15 <= avg_sentence <= 20 else "too_short" if avg_sentence < 15 else "too_long",
            "target": "15-20 words"
        },
        "passive_voice": {
            "ratio_percent": passive,
            "status": "good" if passive <= 15 else "needs_work",
            "target": "< 15%"
        },
        "complex_words": {
            "ratio_percent": complex_words,
            "status": "good" if complex_words <= 20 else "needs_work",
            "target": "< 20%"
        },
        "transition_words": {
            "ratio_percent": transitions,
            "status": "good" if transitions >= 30 else "needs_work",
            "target": "> 30% of sentences"
        },
        "word_count": len(get_words(text)),
        "sentence_count": len(get_sentences(text)),
        "recommendations": _generate_recommendations(fre, fk_grade, avg_sentence, passive, complex_words, transitions)
    }


def _generate_recommendations(fre, fk_grade, avg_sentence, passive, complex_words, transitions) -> List[str]:
    recs = []
    if fk_grade > 10:
        recs.append(f"Reduce reading level from grade {fk_grade} to 8-10 by simplifying sentences and word choices.")
    if avg_sentence > 20:
        recs.append(f"Shorten sentences (avg {avg_sentence} words). Break long sentences into two shorter ones.")
    if passive > 15:
        recs.append(f"Reduce passive voice from {passive}% to under 15%. Use active voice (subject → verb → object).")
    if complex_words > 20:
        recs.append(f"Replace complex words ({complex_words}% of content). Use simpler alternatives.")
    if transitions < 30:
        recs.append(f"Add more transition words. Only {transitions}% of sentences use transitions. Target: 30%+.")
    return recs


if __name__ == "__main__":
    sample = """
    The implementation of comprehensive SEO strategies necessitates a thorough understanding
    of search engine algorithms. It is recommended that practitioners utilize sophisticated
    methodologies when optimizing their websites. Furthermore, the utilization of advanced
    analytics tools has been demonstrated to significantly improve performance metrics.
    """
    report = generate_readability_report(sample)
    print(f"Overall Score: {report['overall_score']}/100")
    print(f"Flesch Reading Ease: {report['flesch_reading_ease']['score']}")
    print(f"Grade Level: {report['flesch_kincaid_grade']['grade']}")
    print(f"Passive Voice: {report['passive_voice']['ratio_percent']}%")
