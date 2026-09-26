from typing import List, Dict, Any
from urllib.parse import urljoin, urlparse
import requests

def analyze_sitemap(target_url: str, detected_sitemaps: List[str] = None) -> List[Dict[str, Any]]:
    issues = []
    parsed = urlparse(target_url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    candidates = [
        urljoin(base_url, "/sitemap.xml"),
        urljoin(base_url, "/sitemap_index.xml")
    ]
    if detected_sitemaps:
        candidates.extend(detected_sitemaps)

    found_sitemap = False
    for sm_url in candidates:
        try:
            resp = requests.get(sm_url, timeout=5, headers={"User-Agent": "SEOAgentBot/1.0"})
            if resp.status_code == 200 and ("xml" in resp.headers.get("Content-Type", "").lower() or "<xml" in resp.text[:100].lower()):
                found_sitemap = True
                break
        except Exception:
            continue

    if not found_sitemap:
        issues.append({
            "page_url": base_url,
            "category": "technical",
            "severity": "HIGH",
            "issue_code": "MISSING_SITEMAP",
            "title": "XML Sitemap Not Found",
            "description": f"No valid XML sitemap was accessible at standard paths for {base_url}.",
            "recommendation_summary": "Generate an XML sitemap (sitemap.xml) and submit it to Google Search Console.",
            "impact": "XML sitemaps help search engine bots discover and index new or updated pages faster."
        })

    return issues
