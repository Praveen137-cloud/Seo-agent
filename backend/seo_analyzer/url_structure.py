from typing import List, Dict, Any
from urllib.parse import urlparse, parse_qs

def analyze_url_structure(pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    issues = []

    for page in pages:
        url = page["url"]
        parsed = urlparse(url)
        path = parsed.path
        query = parsed.query

        # 1. Uppercase in path
        if any(c.isupper() for c in path):
            issues.append({
                "page_url": url,
                "category": "technical",
                "severity": "LOW",
                "issue_code": "URL_UPPERCASE_CHARACTERS",
                "title": "Uppercase Characters in URL Path",
                "description": f"The URL path '{path}' contains uppercase characters.",
                "recommendation_summary": "Standardize all URLs to lowercase and implement 301 redirects from uppercase variants.",
                "impact": "URLs are case-sensitive on Linux/Unix web servers, which can lead to duplicate page penalties."
            })

        # 2. Underscores in path
        if "_" in path:
            issues.append({
                "page_url": url,
                "category": "on_page",
                "severity": "LOW",
                "issue_code": "URL_UNDERSCORES_USED",
                "title": "Underscores Found in URL Slug",
                "description": f"The URL slug '{path}' contains underscores (`_`). Google explicitly recommends hyphens (`-`) over underscores.",
                "recommendation_summary": "Use hyphens (`-`) instead of underscores (`_`) to separate words in URL slugs.",
                "impact": "Google treats hyphens as word separators, but considers underscores as connecting characters."
            })

        # 3. Excessive URL Length
        if len(url) > 100:
            issues.append({
                "page_url": url,
                "category": "technical",
                "severity": "LOW",
                "issue_code": "URL_EXCESSIVE_LENGTH",
                "title": f"Excessively Long URL ({len(url)} Chars)",
                "description": f"URL length is {len(url)} characters (Recommended < 75-80 chars).",
                "recommendation_summary": "Keep URL slugs concise, punchy, and keyword-focused.",
                "impact": "Shorter URLs are easier to read, share, and achieve higher click-through rates in search snippets."
            })

        # 4. Excessive Query Parameters
        qs = parse_qs(query)
        if len(qs) >= 3:
            issues.append({
                "page_url": url,
                "category": "technical",
                "severity": "MEDIUM",
                "issue_code": "URL_EXCESSIVE_QUERY_PARAMS",
                "title": "Excessive URL Query Parameters",
                "description": f"The URL has {len(qs)} query parameters ({', '.join(list(qs.keys())[:4])}).",
                "recommendation_summary": "Use clean, static URL rewrites or specify URL parameters inside Google Search Console.",
                "impact": "Parameter-heavy URLs cause crawler traps, duplicate indexing, and inefficient crawl budget usage."
            })

    return issues
