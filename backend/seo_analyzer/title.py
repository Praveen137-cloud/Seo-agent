from typing import List, Dict, Any

def analyze_titles(pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    issues = []
    seen_titles = {}

    for page in pages:
        url = page["url"]
        title = page.get("title", "").strip()

        if not title:
            issues.append({
                "page_url": url,
                "category": "on_page",
                "severity": "CRITICAL",
                "issue_code": "MISSING_TITLE",
                "title": "Missing Page Title",
                "description": f"The page {url} does not have a `<title>` tag.",
                "recommendation_summary": "Add a descriptive, keyword-optimized title tag between 30 and 60 characters.",
                "impact": "Search engines use title tags as the primary headline in search engine results pages (SERPs)."
            })
        else:
            length = len(title)
            if length < 30:
                issues.append({
                    "page_url": url,
                    "category": "on_page",
                    "severity": "LOW",
                    "issue_code": "TITLE_TOO_SHORT",
                    "title": "Page Title Too Short",
                    "description": f"The page title '{title}' ({length} chars) is under 30 characters.",
                    "recommendation_summary": "Expand the title tag to 30-60 characters to include relevant target keywords.",
                    "impact": "Short titles miss opportunities to rank for relevant search terms."
                })
            elif length > 60:
                issues.append({
                    "page_url": url,
                    "category": "on_page",
                    "severity": "MEDIUM",
                    "issue_code": "TITLE_TOO_LONG",
                    "title": "Page Title Too Long",
                    "description": f"The page title '{title}' ({length} chars) exceeds 60 characters and may be truncated in search results.",
                    "recommendation_summary": "Shorten the title tag to under 60 characters so it fits on desktop and mobile SERPs.",
                    "impact": "Truncated titles reduce Click-Through Rate (CTR)."
                })

            if title in seen_titles:
                seen_titles[title].append(url)
            else:
                seen_titles[title] = [url]

    # Duplicate titles check
    for title, urls in seen_titles.items():
        if len(urls) > 1:
            for duplicate_url in urls:
                issues.append({
                    "page_url": duplicate_url,
                    "category": "on_page",
                    "severity": "HIGH",
                    "issue_code": "DUPLICATE_TITLE",
                    "title": "Duplicate Page Title",
                    "description": f"The title '{title}' is shared across {len(urls)} pages.",
                    "recommendation_summary": "Ensure each page has a unique title tag reflecting its distinct content.",
                    "impact": "Duplicate titles confuse search engines about which page to rank."
                })

    return issues
