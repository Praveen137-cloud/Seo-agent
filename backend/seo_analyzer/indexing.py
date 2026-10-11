from typing import List, Dict, Any
from urllib.parse import urlparse

def analyze_indexing(pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    issues = []

    for page in pages:
        url = page["url"]
        status_code = page.get("status_code", 200)
        is_fetched = page.get("is_fetched", True)
        fetch_error = page.get("fetch_error", "")
        robots_meta = (page.get("robots_meta") or "").lower()
        has_schema = page.get("has_schema", False)
        parsed_path = urlparse(url).path.rstrip("/") or "/"
        page_label = f"Homepage" if parsed_path == "/" else f"'{parsed_path}'"

        # 1. HTTP Status Code Errors
        if status_code == 404:
            issues.append({
                "page_url": url,
                "category": "technical",
                "severity": "CRITICAL",
                "issue_code": "PAGE_NOT_FOUND_404",
                "title": f"404 Not Found Broken Page Error on {page_label}",
                "description": f"The URL {url} returned an HTTP 404 Not Found status code.",
                "observed_value": "HTTP status code 404",
                "evidence": f"Direct request to {url} produced status 404.",
                "recommendation_summary": "Fix broken internal links or implement a 301 permanent redirect to a live relevant page.",
                "impact": "404 errors prevent page indexing and cause immediate visitor drop-off.",
                "verification_status": "verified"
            })
        elif status_code >= 500:
            issues.append({
                "page_url": url,
                "category": "technical",
                "severity": "CRITICAL",
                "issue_code": "SERVER_ERROR_5XX",
                "title": f"HTTP {status_code} Server Error on {page_label}",
                "description": f"The page {url} threw an internal server error (HTTP {status_code}).",
                "observed_value": f"HTTP status code {status_code}",
                "evidence": f"Server responded with error status {status_code}.",
                "recommendation_summary": "Check backend application error logs and web server availability.",
                "impact": "Search engine crawlers drop unserviceable 5xx pages from the index.",
                "verification_status": "verified"
            })
        elif not is_fetched and status_code == 0:
            # Genuine network/timeout failure
            issues.append({
                "page_url": url,
                "category": "technical",
                "severity": "HIGH",
                "issue_code": "UNREACHABLE_PAGE",
                "title": f"Unreachable Page (Network Error) on {page_label}",
                "description": f"Could not connect to {url}: {fetch_error or 'Network connection failed'}.",
                "observed_value": f"Connection failure: {fetch_error}",
                "evidence": f"Socket request to {url} failed with: {fetch_error}",
                "recommendation_summary": "Ensure DNS records, SSL certificates, and web hosting servers are operational.",
                "impact": "Unreachable pages cannot be audited or indexed by search engines.",
                "verification_status": "verified"
            })

        # Only evaluate robots and schema on successfully fetched pages
        if not is_fetched:
            continue

        # 2. Robots Noindex Directives
        if "noindex" in robots_meta:
            issues.append({
                "page_url": url,
                "category": "technical",
                "severity": "CRITICAL",
                "issue_code": "PAGE_BLOCKED_BY_NOINDEX",
                "title": f"Page Explicitly Blocked by 'noindex' Tag on {page_label}",
                "description": f"The page {url} contains a `<meta name='robots' content='noindex'>` or X-Robots-Tag directive.",
                "observed_value": f"Robots directive: '{robots_meta}'",
                "evidence": f"Observed tag/header: {robots_meta}",
                "recommendation_summary": "Remove the 'noindex' directive if you intend this page to appear on Google search results.",
                "impact": "Search engines are strictly instructed not to index or display this page.",
                "verification_status": "verified"
            })

        # 3. Structured Data (Schema.org JSON-LD) on Homepage
        if not has_schema and page.get("depth", 0) == 0:
            issues.append({
                "page_url": url,
                "category": "technical",
                "severity": "LOW",
                "issue_code": "MISSING_STRUCTURED_DATA",
                "title": f"Missing Schema.org Structured Data (JSON-LD) on {page_label}",
                "description": f"The homepage {url} has no Schema.org JSON-LD structured data markup.",
                "observed_value": "0 <script type='application/ld+json'> tags",
                "evidence": "DOM search found no JSON-LD schema blocks.",
                "recommendation_summary": "Add Schema.org markup (such as Organization or WebSite schema) via JSON-LD.",
                "impact": "Structured data enables Google rich snippets (breadcrumbs, star ratings, sitelinks searchbox).",
                "verification_status": "verified"
            })

    return issues
