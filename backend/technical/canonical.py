from typing import List, Dict, Any
from urllib.parse import urlparse

def analyze_canonicals(pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    issues = []

    for page in pages:
        if not page.get("is_fetched", True):
            continue

        url = page["url"]
        canonical_url = (page.get("canonical_url") or "").strip()
        parsed_path = urlparse(url).path.rstrip("/") or "/"
        page_label = f"Homepage" if parsed_path == "/" else f"'{parsed_path}'"

        if not canonical_url:
            issues.append({
                "page_url": url,
                "category": "technical",
                "severity": "LOW",
                "issue_code": "MISSING_CANONICAL",
                "title": f"Missing Canonical Tag on {page_label}",
                "description": f"The page {url} does not declare a `<link rel='canonical'>` URL.",
                "observed_value": "No canonical link element found",
                "evidence": f"<head> of {url} lacks <link rel='canonical'>.",
                "recommendation_summary": "Add a self-referencing canonical tag or point to the master version of this page.",
                "impact": "Canonical tags prevent duplicate content issues when URLs share query parameters.",
                "verification_status": "verified"
            })
        else:
            # Check self-referencing canonical normalization mismatch
            p_url = urlparse(url)
            p_can = urlparse(canonical_url)
            if p_url.netloc == p_can.netloc and p_url.path.rstrip("/") != p_can.path.rstrip("/"):
                issues.append({
                    "page_url": url,
                    "category": "technical",
                    "severity": "MEDIUM",
                    "issue_code": "CANONICAL_MISMATCH",
                    "title": f"Canonical Tag Points to Different Path on {page_label}",
                    "description": f"Page URL is '{url}' but canonical tag points to '{canonical_url}'.",
                    "observed_value": f"Canonical targets '{canonical_url}'",
                    "evidence": f'<link rel="canonical" href="{canonical_url}"> on page {url}',
                    "recommendation_summary": "Ensure the canonical tag correctly targets the canonical source page.",
                    "impact": "Mismatched canonicals instruct search engines to index a different URL than the one crawled.",
                    "verification_status": "verified"
                })

    return issues
