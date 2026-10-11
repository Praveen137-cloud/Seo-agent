from typing import List, Dict, Any

def analyze_indexing(pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    issues = []

    for page in pages:
        url = page["url"]
        status_code = page.get("status_code", 200)
        robots_meta = page.get("robots_meta", "")
        has_schema = page.get("has_schema", False)

        # 1. HTTP Status Code Errors (404, 500, etc.)
        if status_code == 404:
            issues.append({
                "page_url": url,
                "category": "technical",
                "severity": "CRITICAL",
                "issue_code": "PAGE_NOT_FOUND_404",
                "title": "404 Not Found Broken Page Error",
                "description": f"The URL {url} returned an HTTP 404 Not Found status code.",
                "recommendation_summary": "Fix broken internal links or implement a 301 permanent redirect to a relevant live page.",
                "impact": "404 errors waste search engine crawl budget and result in immediate visitor bounce."
            })
        elif status_code >= 500:
            issues.append({
                "page_url": url,
                "category": "technical",
                "severity": "CRITICAL",
                "issue_code": "SERVER_ERROR_5XX",
                "title": f"HTTP {status_code} Internal Server Error",
                "description": f"The page {url} threw an internal server error (HTTP {status_code}).",
                "recommendation_summary": "Investigate web server and application logs to resolve crashes.",
                "impact": "Search engine crawlers drop unserviceable 5xx pages from the search index."
            })
        elif status_code in (401, 403):
            issues.append({
                "page_url": url,
                "category": "technical",
                "severity": "HIGH",
                "issue_code": "FORBIDDEN_OR_AUTH_REQUIRED",
                "title": f"HTTP {status_code} Access Blocked",
                "description": f"The crawler received HTTP {status_code} when attempting to access {url}.",
                "recommendation_summary": "Ensure public pages are not accidentally protected by basic auth or IP firewalls.",
                "impact": "Restricted access prevents search engine indexing."
            })

        # 2. Robots Noindex Directives
        if "noindex" in robots_meta:
            issues.append({
                "page_url": url,
                "category": "technical",
                "severity": "CRITICAL",
                "issue_code": "PAGE_BLOCKED_BY_NOINDEX",
                "title": "Page Explicitly Blocked by 'noindex' Tag",
                "description": f"The page {url} contains a `<meta name='robots' content='noindex'>` or X-Robots-Tag directive.",
                "recommendation_summary": "Remove the 'noindex' directive if you intend this page to appear on Google search results.",
                "impact": "Search engines are strictly commanded NOT to display this page in search results."
            })

        # 3. Structured Data (Schema.org JSON-LD)
        if not has_schema and page.get("depth", 0) <= 1:
            issues.append({
                "page_url": url,
                "category": "technical",
                "severity": "MEDIUM",
                "issue_code": "MISSING_STRUCTURED_DATA",
                "title": "Missing Schema.org Structured Data (JSON-LD)",
                "description": f"The page {url} has no Schema.org JSON-LD structured data markup.",
                "recommendation_summary": "Add Schema.org markup (such as Organization, WebSite, Article, or Product schema) via JSON-LD scripts.",
                "impact": "Structured data enables Google rich snippets (star ratings, site breadcrumbs, author bios, FAQs) in search results."
            })

    return issues
