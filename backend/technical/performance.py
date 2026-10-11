from typing import List, Dict, Any
from urllib.parse import urlparse

def analyze_performance(pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    issues = []

    for page in pages:
        if not page.get("is_fetched", True):
            continue

        url = page["url"]
        load_time_ms = page.get("load_time_ms", 0)
        html_size = page.get("html_size", 0)
        parsed_path = urlparse(url).path.rstrip("/") or "/"
        page_label = f"Homepage" if parsed_path == "/" else f"'{parsed_path}'"

        # Response time check
        if load_time_ms > 2500:
            issues.append({
                "page_url": url,
                "category": "performance",
                "severity": "HIGH",
                "issue_code": "SLOW_SERVER_RESPONSE",
                "title": f"Slow Server Response ({round(load_time_ms / 1000, 2)}s) on {page_label}",
                "description": f"Page took {round(load_time_ms / 1000, 2)} seconds to respond (Google recommends < 1.0s).",
                "observed_value": f"{round(load_time_ms, 0)}ms ({round(load_time_ms / 1000, 2)}s)",
                "evidence": f"Initial HTML TTFB latency clocked at {load_time_ms}ms.",
                "recommendation_summary": "Optimize backend queries, enable server-side caching, and utilize a CDN.",
                "impact": "Slow server response directly hurts Core Web Vitals (TTFB) and increases bounce rates.",
                "verification_status": "verified"
            })
        elif load_time_ms > 1200:
            issues.append({
                "page_url": url,
                "category": "performance",
                "severity": "LOW",
                "issue_code": "MODERATE_SERVER_RESPONSE",
                "title": f"Moderate Server Latency ({round(load_time_ms / 1000, 2)}s) on {page_label}",
                "description": f"Page responded in {round(load_time_ms / 1000, 2)} seconds.",
                "observed_value": f"{round(load_time_ms, 0)}ms",
                "evidence": f"Response latency {load_time_ms}ms exceeds 1.2s target.",
                "recommendation_summary": "Enable edge caching and gzip/brotli compression to bring latency below 800ms.",
                "impact": "Faster page load speeds improve mobile engagement and conversion rates.",
                "verification_status": "verified"
            })

        # HTML document payload size
        if html_size > 500000:  # > 500 KB
            size_kb = round(html_size / 1024, 1)
            issues.append({
                "page_url": url,
                "category": "performance",
                "severity": "MEDIUM",
                "issue_code": "LARGE_DOM_SIZE",
                "title": f"Excessive HTML Size ({size_kb} KB) on {page_label}",
                "description": f"Raw HTML document size is {size_kb} KB (Recommended < 200 KB).",
                "observed_value": f"{size_kb} KB payload",
                "evidence": f"Document length: {html_size} bytes.",
                "recommendation_summary": "Minify HTML, defer inline scripts, and remove redundant DOM elements.",
                "impact": "Large HTML payloads slow browser DOM parsing and first contentful paint (FCP).",
                "verification_status": "verified"
            })

    return issues
