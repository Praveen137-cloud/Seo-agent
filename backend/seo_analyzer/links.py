from typing import List, Dict, Any

def analyze_links(pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    issues = []

    for page in pages:
        url = page["url"]
        links = page.get("links", [])
        
        if not links:
            if page.get("depth", 0) > 0:
                issues.append({
                    "page_url": url,
                    "category": "on_page",
                    "severity": "LOW",
                    "issue_code": "NO_OUTBOUND_LINKS",
                    "title": "Page Has No Links",
                    "description": f"The page {url} does not contain any outbound internal or external links.",
                    "recommendation_summary": "Include contextual links to related content on your site.",
                    "impact": "Dead-end pages restrict crawl depth and user navigation flow."
                })
            continue

        internal_links = [l for l in links if l.get("is_internal")]
        external_links = [l for l in links if not l.get("is_internal")]

        # Check empty anchor texts
        empty_anchors = [l for l in links if not l.get("anchor_text", "").strip()]
        if len(empty_anchors) > 2:
            issues.append({
                "page_url": url,
                "category": "on_page",
                "severity": "LOW",
                "issue_code": "GENERIC_EMPTY_ANCHOR",
                "title": "Links with Missing/Generic Anchor Text",
                "description": f"Found {len(empty_anchors)} links with empty anchor text on {url}.",
                "recommendation_summary": "Use descriptive keyword-rich anchor text instead of blank links or 'click here'.",
                "impact": "Clear anchor text helps search engines understand linked page context."
            })

    return issues
