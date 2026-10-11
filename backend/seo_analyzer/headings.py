from typing import List, Dict, Any
from urllib.parse import urlparse

def analyze_headings(pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    issues = []

    for page in pages:
        # Never evaluate pages that failed to fetch
        if not page.get("is_fetched", True):
            continue

        url = page["url"]
        h1_tags = page.get("h1_tags", [])
        h2_tags = page.get("h2_tags", [])
        parsed_path = urlparse(url).path.rstrip("/") or "/"
        page_label = f"Homepage" if parsed_path == "/" else f"'{parsed_path}'"

        # H1 Checks
        if not h1_tags:
            # If SPA, mark as client-rendered advisory
            if page.get("is_spa"):
                issues.append({
                    "page_url": url,
                    "category": "on_page",
                    "severity": "LOW",
                    "issue_code": "SPA_H1_CHECK",
                    "title": f"Single Page App / Client-Side H1 on {page_label}",
                    "description": f"The page {url} uses client-side JavaScript rendering; static HTML contains 0 `<h1>` tags.",
                    "observed_value": "0 static <h1> tags (Client-side JS app detected)",
                    "evidence": "HTML shell has client hydration div (#root or #__next).",
                    "recommendation_summary": "Ensure server-side rendering (SSR) or pre-rendering delivers an <h1> tag in the initial HTML payload.",
                    "impact": "Bots that do not execute client-side JavaScript might not detect the primary heading.",
                    "verification_status": "verified"
                })
            else:
                issues.append({
                    "page_url": url,
                    "category": "on_page",
                    "severity": "MEDIUM",
                    "issue_code": "MISSING_H1",
                    "title": f"Missing H1 Heading on {page_label}",
                    "description": f"The page {url} does not contain an `<h1>` heading tag.",
                    "observed_value": "0 <h1> tags found in HTML",
                    "evidence": f"Scanned complete DOM of {url} - no <h1> element present.",
                    "recommendation_summary": "Add a single, prominent <h1> tag that describes the primary topic of the page.",
                    "impact": "H1 headings communicate the main subject matter to both search engines and users.",
                    "verification_status": "verified"
                })
        elif len(h1_tags) > 1:
            # Multiple H1 is strictly LOW severity (HTML5 specification allows it, but single H1 is best practice)
            sample_h1s = ", ".join([f'"{h[:30]}"' for h in h1_tags[:3]])
            issues.append({
                "page_url": url,
                "category": "on_page",
                "severity": "LOW",
                "issue_code": "MULTIPLE_H1",
                "title": f"Multiple H1 Tags ({len(h1_tags)}) on {page_label}",
                "description": f"The page has {len(h1_tags)} `<h1>` tags ({sample_h1s}).",
                "observed_value": f"{len(h1_tags)} <h1> elements found",
                "evidence": f"Found multiple <h1> tags: {sample_h1s}",
                "recommendation_summary": "Use a single <h1> heading per page for maximum structural clarity and accessibility.",
                "impact": "Multiple H1 tags can dilute heading emphasis, though modern search engines handle multiple H1s gracefully.",
                "verification_status": "verified"
            })
        else:
            # Single H1 present: check if empty whitespace
            h1_text = h1_tags[0].strip()
            if not h1_text:
                issues.append({
                    "page_url": url,
                    "category": "on_page",
                    "severity": "LOW",
                    "issue_code": "EMPTY_H1",
                    "title": f"Empty H1 Tag on {page_label}",
                    "description": f"An `<h1>` tag exists on {url}, but contains no readable text.",
                    "observed_value": "<h1></h1> (empty)",
                    "evidence": "Observed <h1> tag with 0 text characters.",
                    "recommendation_summary": "Populate the <h1> tag with descriptive text representing the page topic.",
                    "impact": "Empty heading tags provide no semantic value to search engine crawlers.",
                    "verification_status": "verified"
                })

        # H2 Checks (only flagged if long content has 0 subheadings)
        if not h2_tags and page.get("word_count", 0) > 400:
            issues.append({
                "page_url": url,
                "category": "on_page",
                "severity": "LOW",
                "issue_code": "MISSING_H2",
                "title": f"Lack of Subheadings (H2) on {page_label}",
                "description": f"Page content has {page.get('word_count')} words but lacks `<h2>` subheadings.",
                "observed_value": f"{page.get('word_count')} words with 0 <h2> tags",
                "evidence": "Long editorial body with no <h2> structural markers.",
                "recommendation_summary": "Break body copy into readable sections using descriptive <h2> subheadings.",
                "impact": "Subheadings improve content readability and allow Google to extract snippet sections.",
                "verification_status": "verified"
            })

    return issues
