from typing import List, Dict, Any
from urllib.parse import urlparse

def analyze_security(target_url: str, pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    issues = []
    parsed = urlparse(target_url)

    if parsed.scheme.lower() != "https":
        issues.append({
            "page_url": target_url,
            "category": "security",
            "severity": "CRITICAL",
            "issue_code": "NO_HTTPS",
            "title": "Website Not Using HTTPS",
            "description": f"The target URL '{target_url}' uses unencrypted HTTP.",
            "recommendation_summary": "Install an SSL certificate (e.g. via Let's Encrypt) and enforce HTTPS redirection.",
            "impact": "HTTPS is a confirmed Google ranking signal and essential for user security."
        })

    # Check for mixed content or non-HTTPS internal pages
    non_https_pages = [p["url"] for p in pages if urlparse(p["url"]).scheme.lower() != "https"]
    if non_https_pages and parsed.scheme.lower() == "https":
        issues.append({
            "page_url": target_url,
            "category": "security",
            "severity": "HIGH",
            "issue_code": "MIXED_CONTENT_PAGES",
            "title": "Non-HTTPS Internal Links Discovered",
            "description": f"Found {len(non_https_pages)} internal pages loading via insecure HTTP.",
            "recommendation_summary": "Update all internal URLs and resources to use relative paths or explicit https:// schemes.",
            "impact": "Insecure pages trigger security warnings in modern browsers."
        })

    return issues
