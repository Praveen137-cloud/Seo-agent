from typing import List, Dict, Any

def analyze_meta_descriptions(pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    issues = []
    seen_metas = {}

    for page in pages:
        url = page["url"]
        meta_desc = page.get("meta_description", "").strip()

        if not meta_desc:
            issues.append({
                "page_url": url,
                "category": "on_page",
                "severity": "HIGH",
                "issue_code": "MISSING_META_DESCRIPTION",
                "title": "Missing Meta Description",
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
                    "title": "Meta Description Too Short",
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
                    "title": "Meta Description Too Long",
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
                issues.append({
                    "page_url": duplicate_url,
                    "category": "on_page",
                    "severity": "MEDIUM",
                    "issue_code": "DUPLICATE_META_DESCRIPTION",
                    "title": "Duplicate Meta Description",
                    "description": f"Meta description is identical on {len(urls)} pages.",
                    "recommendation_summary": "Provide a unique meta description tailored to each page.",
                    "impact": "Duplicates reduce search engine snippet diversity."
                })

    return issues
