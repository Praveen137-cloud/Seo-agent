from typing import List, Dict, Any
from urllib.parse import urlparse

def analyze_security(target_url: str, pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    issues = []
    parsed = urlparse(target_url)

    # 1. Target URL HTTPS Check
    if parsed.scheme.lower() != "https":
        issues.append({
            "page_url": target_url,
            "category": "security",
            "severity": "CRITICAL",
            "issue_code": "NO_HTTPS",
            "title": "Website Not Using HTTPS Protocol",
            "description": f"The target URL '{target_url}' uses unencrypted HTTP protocol.",
            "observed_value": f"Scheme: {parsed.scheme.lower()}",
            "evidence": f"Initial target URL lacks https:// protocol.",
            "recommendation_summary": "Install a valid SSL/TLS certificate (e.g. Let's Encrypt) and enforce HTTPS redirection.",
            "impact": "HTTPS is a confirmed Google ranking factor and essential for browser security trust.",
            "verification_status": "verified"
        })

    # 2. Check for mixed content / non-HTTPS internal pages
    non_https_pages = [p["url"] for p in pages if urlparse(p["url"]).scheme.lower() != "https"]
    if non_https_pages and parsed.scheme.lower() == "https":
        issues.append({
            "page_url": target_url,
            "category": "security",
            "severity": "HIGH",
            "issue_code": "MIXED_CONTENT_PAGES",
            "title": f"Non-HTTPS Internal Links Discovered ({len(non_https_pages)})",
            "description": f"Found {len(non_https_pages)} internal page links using insecure http:// protocol.",
            "observed_value": f"{len(non_https_pages)} insecure links",
            "evidence": f"Sample insecure internal links: {', '.join(non_https_pages[:3])}",
            "recommendation_summary": "Update all internal URLs to use https:// or relative paths.",
            "impact": "Insecure pages trigger security warnings in modern browsers.",
            "verification_status": "verified"
        })

    return issues
