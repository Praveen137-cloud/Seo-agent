from typing import List, Dict, Any
from urllib.parse import urlparse

def analyze_content(pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    issues = []

    for page in pages:
        if not page.get("is_fetched", True):
            continue

        url = page["url"]
        word_count = page.get("word_count", 0)
        html_lang = (page.get("html_lang") or "").strip()
        has_charset = page.get("has_charset", True)
        is_spa = page.get("is_spa", False)
        parsed_path = urlparse(url).path.rstrip("/") or "/"
        page_label = f"Homepage" if parsed_path == "/" else f"'{parsed_path}'"

        # 1. Thin Content Check (Only flag if static page has very few words, skip if SPA where content renders client-side)
        if not is_spa and word_count < 80 and page.get("status_code", 200) == 200:
            issues.append({
                "page_url": url,
                "category": "on_page",
                "severity": "MEDIUM",
                "issue_code": "THIN_CONTENT",
                "title": f"Thin Content Flagged ({word_count} Words) on {page_label}",
                "description": f"The page {url} contains only {word_count} words of readable body copy.",
                "observed_value": f"{word_count} words detected",
                "evidence": f"Body text extraction yielded {word_count} words (Recommended: 300+ words).",
                "recommendation_summary": "Enrich the page with comprehensive, informative copy matching user search intent.",
                "impact": "Google's helpful content systems de-rank thin pages that provide insufficient depth.",
                "verification_status": "verified"
            })

        # 2. Missing Language Tag
        if not html_lang:
            issues.append({
                "page_url": url,
                "category": "on_page",
                "severity": "LOW",
                "issue_code": "MISSING_HTML_LANG",
                "title": f"Missing HTML Language Attribute on {page_label}",
                "description": f"The `<html>` element on {url} lacks a `lang` attribute (e.g. `<html lang='en'>`).",
                "observed_value": "<html> element has no lang attribute",
                "evidence": "Opening <html> tag lacks lang='...' specification.",
                "recommendation_summary": "Add `<html lang='en'>` to explicitly declare the primary document language.",
                "impact": "Helps search engines and screen readers correctly parse typography and regional results.",
                "verification_status": "verified"
            })

        # 3. Missing Character Encoding
        if not has_charset:
            issues.append({
                "page_url": url,
                "category": "technical",
                "severity": "LOW",
                "issue_code": "MISSING_CHARSET",
                "title": f"Missing Character Encoding Declaration on {page_label}",
                "description": f"No `<meta charset='utf-8'>` declaration found in the `<head>` of {url}.",
                "observed_value": "No charset meta tag found",
                "evidence": "<head> lacks <meta charset='...'> tag.",
                "recommendation_summary": "Specify `<meta charset='utf-8'>` near the beginning of the `<head>`.",
                "impact": "Prevents character encoding artifacts across international browsers.",
                "verification_status": "verified"
            })

    return issues
