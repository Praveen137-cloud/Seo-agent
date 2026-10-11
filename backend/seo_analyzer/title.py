from typing import List, Dict, Any
from urllib.parse import urlparse

def analyze_titles(pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    issues = []
    seen_titles: Dict[str, List[str]] = {}

    for page in pages:
        # Never evaluate pages that failed to fetch or returned HTTP errors
        if not page.get("is_fetched", True):
            continue

        url = page["url"]
        title = (page.get("title") or "").strip()
        parsed_path = urlparse(url).path.rstrip("/") or "/"
        page_label = f"Homepage" if parsed_path == "/" else f"'{parsed_path}'"

        if not title:
            issues.append({
                "page_url": url,
                "category": "on_page",
                "severity": "HIGH",
                "issue_code": "MISSING_TITLE",
                "title": f"Missing Page Title on {page_label}",
                "description": f"The page {url} was successfully retrieved but does not have a `<title>` tag.",
                "observed_value": "No <title> element found",
                "evidence": f"HTML inspection of {url} found 0 non-empty <title> tags.",
                "recommendation_summary": "Add a descriptive, keyword-optimized title tag between 30 and 60 characters.",
                "impact": "Search engines use title tags as the primary headline in search engine results pages (SERPs).",
                "verification_status": "verified"
            })
        else:
            length = len(title)
            if length < 25:
                issues.append({
                    "page_url": url,
                    "category": "on_page",
                    "severity": "LOW",
                    "issue_code": "TITLE_TOO_SHORT",
                    "title": f"Short Page Title ({length} chars) on {page_label}",
                    "description": f"The page title '{title}' is only {length} characters long.",
                    "observed_value": f"{length} characters ('{title}')",
                    "evidence": f"<title>{title}</title>",
                    "recommendation_summary": "Expand the title tag to 30-60 characters to include relevant target keywords.",
                    "impact": "Short titles miss opportunities to rank for relevant search queries.",
                    "verification_status": "verified"
                })
            elif length > 65:
                issues.append({
                    "page_url": url,
                    "category": "on_page",
                    "severity": "LOW",
                    "issue_code": "TITLE_TOO_LONG",
                    "title": f"Long Page Title ({length} chars) on {page_label}",
                    "description": f"The page title exceeds 65 characters and is likely to be truncated on Google SERPs.",
                    "observed_value": f"{length} characters ('{title[:50]}...')",
                    "evidence": f"<title>{title}</title>",
                    "recommendation_summary": "Shorten the title tag to under 60-65 characters so it fits on mobile and desktop search snippets.",
                    "impact": "Truncated titles reduce clarity and click-through rates (CTR).",
                    "verification_status": "verified"
                })

            if title in seen_titles:
                seen_titles[title].append(url)
            else:
                seen_titles[title] = [url]

    # Duplicate titles check (only if duplicate is on different distinct paths)
    for title, urls in seen_titles.items():
        if len(urls) > 1 and len(title) > 0:
            for duplicate_url in urls:
                dup_path = urlparse(duplicate_url).path.rstrip("/") or "/"
                issues.append({
                    "page_url": duplicate_url,
                    "category": "on_page",
                    "severity": "MEDIUM",
                    "issue_code": "DUPLICATE_TITLE",
                    "title": f"Duplicate Page Title on '{dup_path}'",
                    "description": f"The title '{title}' is shared identically across {len(urls)} distinct pages.",
                    "observed_value": f"Title '{title[:40]}...' shared on {len(urls)} URLs",
                    "evidence": f"Identical <title> tag on: {', '.join(urls[:3])}",
                    "recommendation_summary": "Ensure each page has a unique title tag reflecting its distinct content.",
                    "impact": "Duplicate titles confuse search engines about which page should rank.",
                    "verification_status": "verified"
                })

    return issues
