from typing import List, Dict, Any
from urllib.parse import urlparse

def analyze_meta_descriptions(pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    issues = []
    seen_metas: Dict[str, List[str]] = {}

    for page in pages:
        # Never evaluate pages that failed to fetch
        if not page.get("is_fetched", True):
            continue

        url = page["url"]
        meta_desc = (page.get("meta_description") or "").strip()
        parsed_path = urlparse(url).path.rstrip("/") or "/"
        page_label = f"Homepage" if parsed_path == "/" else f"'{parsed_path}'"

        if not meta_desc:
            issues.append({
                "page_url": url,
                "category": "on_page",
                "severity": "MEDIUM",
                "issue_code": "MISSING_META_DESCRIPTION",
                "title": f"Missing Meta Description on {page_label}",
                "description": f"The page {url} does not have a `<meta name='description'>` tag.",
                "observed_value": "No meta description tag found",
                "evidence": f"Head tags on {url} contained no <meta name='description'> or og:description.",
                "recommendation_summary": "Craft an engaging meta description between 120 and 155 characters with a clear call-to-action.",
                "impact": "Meta descriptions provide the summary text in search results; absent descriptions lead to auto-generated text snippets.",
                "verification_status": "verified"
            })
        else:
            length = len(meta_desc)
            if length < 60:
                issues.append({
                    "page_url": url,
                    "category": "on_page",
                    "severity": "LOW",
                    "issue_code": "META_DESCRIPTION_TOO_SHORT",
                    "title": f"Short Meta Description ({length} chars) on {page_label}",
                    "description": f"Meta description is only {length} characters. Recommended range is 120-155 characters.",
                    "observed_value": f"{length} characters ('{meta_desc}')",
                    "evidence": f'<meta name="description" content="{meta_desc}">',
                    "recommendation_summary": "Elaborate on the page summary to use the search snippet space effectively.",
                    "impact": "Underutilized snippet space yields lower organic click-through rates.",
                    "verification_status": "verified"
                })
            elif length > 165:
                issues.append({
                    "page_url": url,
                    "category": "on_page",
                    "severity": "LOW",
                    "issue_code": "META_DESCRIPTION_TOO_LONG",
                    "title": f"Long Meta Description ({length} chars) on {page_label}",
                    "description": f"Meta description is {length} characters and will be cut off by search engines.",
                    "observed_value": f"{length} characters ('{meta_desc[:50]}...')",
                    "evidence": f'<meta name="description" content="{meta_desc[:60]}...">',
                    "recommendation_summary": "Trim description to under 155-160 characters so the full message is visible.",
                    "impact": "Truncated descriptions appear incomplete to searchers.",
                    "verification_status": "verified"
                })

            if meta_desc in seen_metas:
                seen_metas[meta_desc].append(url)
            else:
                seen_metas[meta_desc] = [url]

    # Duplicate meta description check
    for meta_desc, urls in seen_metas.items():
        if len(urls) > 1 and len(meta_desc) > 0:
            for duplicate_url in urls:
                dup_path = urlparse(duplicate_url).path.rstrip("/") or "/"
                issues.append({
                    "page_url": duplicate_url,
                    "category": "on_page",
                    "severity": "LOW",
                    "issue_code": "DUPLICATE_META_DESCRIPTION",
                    "title": f"Duplicate Meta Description on '{dup_path}'",
                    "description": f"Identical meta description is shared across {len(urls)} distinct pages.",
                    "observed_value": f"Snippet '{meta_desc[:40]}...' shared on {len(urls)} pages",
                    "evidence": f"Identical meta description content on: {', '.join(urls[:3])}",
                    "recommendation_summary": "Provide a unique meta description tailored specifically to each individual page.",
                    "impact": "Duplicates reduce search engine snippet diversity.",
                    "verification_status": "verified"
                })

    return issues
