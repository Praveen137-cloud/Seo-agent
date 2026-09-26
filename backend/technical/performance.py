from typing import List, Dict, Any

def analyze_performance(pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    issues = []

    for page in pages:
        url = page["url"]
        load_time_ms = page.get("load_time_ms", 0)
        html_size = page.get("html_size", 0)

        # Response time check
        if load_time_ms > 2000:
            issues.append({
                "page_url": url,
                "category": "performance",
                "severity": "HIGH",
                "issue_code": "SLOW_SERVER_RESPONSE",
                "title": "Slow Server Response Time",
                "description": f"Page took {round(load_time_ms / 1000, 2)}s to respond (Threshold: 2.0s).",
                "recommendation_summary": "Optimize server backend queries, enable caching, or leverage a CDN.",
                "impact": "Slow server response negatively impacts Core Web Vitals (TTFB) and user bounce rates."
            })
        elif load_time_ms > 1000:
            issues.append({
                "page_url": url,
                "category": "performance",
                "severity": "LOW",
                "issue_code": "MODERATE_SERVER_RESPONSE",
                "title": "Moderate Server Response Time",
                "description": f"Page took {round(load_time_ms / 1000, 2)}s to respond.",
                "recommendation_summary": "Consider page caching or lightweight asset minification to reach under 1.0s.",
                "impact": "Faster load speeds improve conversion rates."
            })

        # HTML document payload size
        if html_size > 500000:  # > 500 KB raw HTML
            issues.append({
                "page_url": url,
                "category": "performance",
                "severity": "MEDIUM",
                "issue_code": "LARGE_DOM_SIZE",
                "title": "Excessive HTML Document Size",
                "description": f"HTML document size is {round(html_size / 1024, 1)} KB (Recommended < 200 KB).",
                "recommendation_summary": "Reduce inline scripts, CSS, or complex nested DOM elements.",
                "impact": "Large HTML payloads slow down parsing and rendering speed."
            })

    return issues
