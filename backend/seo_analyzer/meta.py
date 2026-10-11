from typing import List, Dict, Any
from urllib.parse import urlparse

def analyze_meta_descriptions(pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    issues = []
    seen_metas = {}

    for page in pages:
        url = page["url"]
        meta_desc = page.get("meta_description", "").strip()
        parsed_path = urlparse(url).path.rstrip("/") or "/"

        if not meta_desc:
            issues.append({
                "page_url": url,
                "category": "on_page",
                "severity": "HIGH",
                "issue_code": "MISSING_META_DESCRIPTION",
                "title": f"Missing Meta Description on {parsed_path}",
                "description": f"The page {url} is missing a meta description tag.",
                "recommendation_summary": "Craft an engaging meta description between 120 and 160 characters with a clear call-to-action.",
                "impact": "Meta descriptions directly influence user click-through rates from search results."
            })
        else:
            length = len(meta_desc)
            if length < 70:
                issues.append({
                    "page_url": url,
                    "category": "on_page",
                    "severity": "LOW",
                    "issue_code": "META_DESCRIPTION_TOO_SHORT",
                    "title": f"Short Meta Description ({length} chars) on {parsed_path}",
                    "description": f"Meta description is only {length} characters. Recommended range is 120-160 characters.",
                    "recommendation_summary": "Elaborate on the page summary to use the snippet space effectively.",
                    "impact": "Underutilized snippet space yields lower engagement."
                })
            elif length > 160:
                issues.append({
                    "page_url": url,
                    "category": "on_page",
                    "severity": "MEDIUM",
                    "issue_code": "META_DESCRIPTION_TOO_LONG",
                    "title": f"Long Meta Description ({length} chars) on {parsed_path}",
                    "description": f"Meta description is {length} characters and will be cut off by search engines.",
                    "recommendation_summary": "Trim description to under 160 characters.",
                    "impact": "Truncated descriptions appear incomplete to searchers."
                })

            if meta_desc in seen_metas:
                seen_metas[meta_desc].append(url)
            else:
                seen_metas[meta_desc] = [url]

    # Duplicate meta description check
    for meta_desc, urls in seen_metas.items():
        if len(urls) > 1:
            for duplicate_url in urls:
                dup_path = urlparse(duplicate_url).path.rstrip("/") or "/"
                issues.append({
                    "page_url": duplicate_url,
                    "category": "on_page",
                    "severity": "MEDIUM",
                    "issue_code": "DUPLICATE_META_DESCRIPTION",
                    "title": f"Duplicate Meta Description on {dup_path}",
                    "description": f"Meta description is identical across {len(urls)} pages ({meta_desc[:60]}...).",
                    "recommendation_summary": "Provide a unique meta description tailored specifically to each individual page.",
                    "impact": "Duplicates reduce search engine snippet diversity and click clarity."
                })

    return issues
