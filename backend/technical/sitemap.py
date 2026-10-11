from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse
import requests

def analyze_sitemap(target_url: str, detected_sitemaps: Optional[List[str]] = None) -> List[Dict[str, Any]]:
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
            resp = requests.get(
                sm_url,
                timeout=5,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            )
            if resp.status_code == 200 and ("xml" in resp.headers.get("Content-Type", "").lower() or "<xml" in resp.text[:100].lower() or "<urlset" in resp.text[:200].lower()):
                found_sitemap = True
                break
            elif resp.status_code in (403, 503) or "challenge" in str(resp.headers.get("Cf-Mitigated", "")).lower():
                try:
                    fb = requests.get(f"https://r.jina.ai/{sm_url}", timeout=8)
                    if fb.status_code == 200 and ("xml" in fb.text[:100].lower() or "urlset" in fb.text[:200].lower()):
                        found_sitemap = True
                        break
                except Exception:
                    pass
        except Exception:
            continue

    if not found_sitemap:
        issues.append({
            "page_url": base_url,
            "category": "technical",
            "severity": "MEDIUM",
            "issue_code": "MISSING_SITEMAP",
            "title": "XML Sitemap Not Found",
            "description": f"No accessible XML sitemap was found at standard locations (/sitemap.xml) for {base_url}.",
            "observed_value": "No valid sitemap at standard locations",
            "evidence": f"Checked locations: {', '.join(candidates[:2])} (Status: 404 or non-XML).",
            "recommendation_summary": "Generate an automated XML sitemap (sitemap.xml) and reference it in robots.txt.",
            "impact": "XML sitemaps help search engine crawlers discover, crawl, and prioritize pages efficiently.",
            "verification_status": "verified"
        })

    return issues
