from typing import List, Dict, Any
from urllib.parse import urlparse, parse_qs

def analyze_url_structure(pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    issues = []

    for page in pages:
        url = page["url"]
        parsed = urlparse(url)
        path = parsed.path
        query = parsed.query
        page_label = f"Homepage" if path in ("", "/") else f"'{path}'"

        # 1. Uppercase in path
        if any(c.isupper() for c in path):
            issues.append({
                "page_url": url,
                "category": "technical",
                "severity": "LOW",
                "issue_code": "URL_UPPERCASE_CHARACTERS",
                "title": f"Uppercase Characters in URL on {page_label}",
                "description": f"The URL path '{path}' contains uppercase characters.",
                "observed_value": f"Path: '{path}'",
                "evidence": f"URL string '{url}' contains uppercase characters.",
                "recommendation_summary": "Standardize all URLs to lowercase and implement 301 redirects from uppercase variants.",
                "impact": "URLs are case-sensitive on Linux/Unix web servers, potentially causing duplicate page penalties.",
                "verification_status": "verified"
            })

        # 2. Underscores in slug
        if "_" in path:
            issues.append({
                "page_url": url,
                "category": "on_page",
                "severity": "LOW",
                "issue_code": "URL_UNDERSCORES_USED",
                "title": f"Underscores Found in Slug on {page_label}",
                "description": f"The URL slug '{path}' contains underscores (`_`). Google explicitly recommends hyphens (`-`).",
                "observed_value": f"Path: '{path}'",
                "evidence": f"Found underscore character in path: {path}",
                "recommendation_summary": "Use hyphens (`-`) instead of underscores (`_`) to separate words in URL slugs.",
                "impact": "Google treats hyphens as word separators, but considers underscores as connecting characters.",
                "verification_status": "verified"
            })

        # 3. Excessive Query Parameters
        qs = parse_qs(query)
        if len(qs) >= 3:
            issues.append({
                "page_url": url,
                "category": "technical",
                "severity": "LOW",
                "issue_code": "URL_EXCESSIVE_QUERY_PARAMS",
                "title": f"Excessive Query Parameters on {page_label}",
                "description": f"The URL has {len(qs)} query parameters ({', '.join(list(qs.keys())[:4])}).",
                "observed_value": f"{len(qs)} parameters: {query}",
                "evidence": f"Query string has multiple parameters: {query}",
                "recommendation_summary": "Use clean, static URL rewrites or configure parameter handling in Google Search Console.",
                "impact": "Parameter-heavy URLs can lead to duplicate content and inefficient crawl budget usage.",
                "verification_status": "verified"
            })

    return issues
