from typing import List, Dict, Any
from urllib.parse import urlparse

def analyze_canonicals(pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    issues = []

    for page in pages:
        url = page["url"]
        canonical_url = page.get("canonical_url", "").strip()

        if not canonical_url:
            issues.append({
                "page_url": url,
                "category": "technical",
                "severity": "MEDIUM",
                "issue_code": "MISSING_CANONICAL",
                "title": "Missing Canonical Tag",
                "description": f"The page {url} does not declare a `<link rel='canonical'>` URL.",
                "recommendation_summary": "Add a self-referencing canonical tag or point to the master version of this page.",
                "impact": "Canonical tags prevent duplicate content issues when URLs share similar parameters."
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
                    "title": "Canonical Tag Points to Different Page",
                    "description": f"Page URL is '{url}' but canonical tag points to '{canonical_url}'.",
                    "recommendation_summary": "Ensure the canonical tag correctly targets the canonical source page.",
                    "impact": "Mismatched canonicals instruct search engines to index a different URL than the one crawled."
                })

    return issues
