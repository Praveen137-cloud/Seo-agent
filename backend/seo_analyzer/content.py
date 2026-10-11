from typing import List, Dict, Any

def analyze_content(pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    issues = []

    for page in pages:
        url = page["url"]
        word_count = page.get("word_count", 0)
        html_lang = page.get("html_lang", "").strip()
        has_charset = page.get("has_charset", True)

        # 1. Thin Content Check
        if word_count < 100 and page.get("status_code", 200) == 200:
            issues.append({
                "page_url": url,
                "category": "on_page",
                "severity": "HIGH",
                "issue_code": "THIN_CONTENT",
                "title": f"Thin Content Flagged ({word_count} Words)",
                "description": f"The page {url} contains only {word_count} words of readable body copy (Minimum recommended: 300+ words).",
                "recommendation_summary": "Enrich the page with comprehensive, high-value editorial or descriptive content.",
                "impact": "Google's helpful content systems penalize low-effort thin pages that do not provide comprehensive value."
            })
        elif word_count < 250 and page.get("depth", 0) == 0:
            issues.append({
                "page_url": url,
                "category": "on_page",
                "severity": "MEDIUM",
                "issue_code": "LOW_HOMEPAGE_WORD_COUNT",
                "title": f"Low Homepage Copy Density ({word_count} Words)",
                "description": f"The homepage has only {word_count} words. Clear explanatory copy is crucial for defining your topical authority.",
                "recommendation_summary": "Expand the homepage copy with benefit bullets, feature overviews, and keyword-aligned paragraphs.",
                "impact": "Insufficient text makes it harder for search engines to identify the core topics and services of your domain."
            })

        # 2. Missing HTML Language Attribute
        if not html_lang and page.get("status_code", 200) == 200:
            issues.append({
                "page_url": url,
                "category": "on_page",
                "severity": "LOW",
                "issue_code": "MISSING_HTML_LANG",
                "title": "Missing HTML Language Attribute",
                "description": f"The `<html>` element on {url} lacks a `lang` attribute (e.g. `<html lang='en'>`).",
                "recommendation_summary": "Add `<html lang='en'>` to explicitly declare the primary document language.",
                "impact": "Helps search engines and screen readers correctly parse typography, translation, and localized search results."
            })

        # 3. Missing Character Encoding
        if not has_charset:
            issues.append({
                "page_url": url,
                "category": "technical",
                "severity": "LOW",
                "issue_code": "MISSING_CHARSET",
                "title": "Missing Character Encoding Declaration",
                "description": f"No `<meta charset='utf-8'>` declaration found in the `<head>` of {url}.",
                "recommendation_summary": "Specify `<meta charset='utf-8'>` as the first tag in the document `<head>`.",
                "impact": "Prevents strange text rendering symbols and encoding glitches across international browsers."
            })

    return issues
