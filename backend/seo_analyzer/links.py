from typing import List, Dict, Any, Optional
from urllib.parse import urlparse

def analyze_links(pages: List[Dict[str, Any]], tested_links: Optional[Dict[str, Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
    issues = []

    # 1. Evaluate verified broken links tested during crawling
    if tested_links:
        for target_url, link_meta in tested_links.items():
            source_url = link_meta.get("source_url", "")
            status_code = link_meta.get("status_code", 0)
            is_broken = link_meta.get("is_broken", False)
            verified = link_meta.get("verified", False)

            if verified and is_broken:
                issues.append({
                    "page_url": source_url,
                    "category": "technical",
                    "severity": "HIGH",
                    "issue_code": "VERIFIED_BROKEN_LINK",
                    "title": f"Verified Broken Link (404) to {target_url}",
                    "description": f"Internal link on {source_url} points to {target_url}, which returned verified HTTP 404 Not Found.",
                    "observed_value": f"HTTP 404 response on destination {target_url}",
                    "evidence": f"Source: {source_url} -> Destination: {target_url} (Status: 404)",
                    "recommendation_summary": "Update the link href to point to the correct live page or set up a 301 redirect.",
                    "impact": "Broken links frustrate users and waste search engine crawl efficiency.",
                    "verification_status": "verified"
                })
            elif not verified:
                # Timed out during verification - mark unverified
                issues.append({
                    "page_url": source_url,
                    "category": "technical",
                    "severity": "LOW",
                    "issue_code": "UNVERIFIED_LINK_TIMEOUT",
                    "title": f"Unverified Link (Timeout) to {target_url}",
                    "description": f"Verification request to {target_url} timed out; destination could not be confirmed as live.",
                    "observed_value": "Connection timeout",
                    "evidence": f"Request to {target_url} timed out after 3.0s.",
                    "recommendation_summary": "Manually verify that this link resolves quickly without blocking bot requests.",
                    "impact": "Slow or unresponsive link destinations may negatively impact user experience.",
                    "verification_status": "unverified"
                })

    # 2. Check empty anchor text on fetched pages
    for page in pages:
        if not page.get("is_fetched", True):
            continue

        url = page["url"]
        links = page.get("links", [])
        parsed_path = urlparse(url).path.rstrip("/") or "/"
        page_label = f"Homepage" if parsed_path == "/" else f"'{parsed_path}'"

        empty_anchors = [l for l in links if not l.get("anchor_text", "").strip() and not "img" in l.get("url", "")]
        if len(empty_anchors) >= 3:
            sample_empty_urls = [l["url"] for l in empty_anchors[:3]]
            issues.append({
                "page_url": url,
                "category": "on_page",
                "severity": "LOW",
                "issue_code": "EMPTY_ANCHOR_TEXT",
                "title": f"Links with Missing Anchor Text ({len(empty_anchors)}) on {page_label}",
                "description": f"Found {len(empty_anchors)} links on {url} with blank or whitespace anchor text.",
                "observed_value": f"{len(empty_anchors)} links without text description",
                "evidence": f"Sample link targets missing text: {', '.join(sample_empty_urls)}",
                "recommendation_summary": "Provide descriptive text for links rather than empty tags or generic 'click here'.",
                "impact": "Descriptive anchor text provides context to search engines about the destination page.",
                "verification_status": "verified"
            })

    return issues
