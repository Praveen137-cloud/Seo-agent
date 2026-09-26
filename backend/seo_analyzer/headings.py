from typing import List, Dict, Any

def analyze_headings(pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    issues = []

    for page in pages:
        url = page["url"]
        h1_tags = page.get("h1_tags", [])
        h2_tags = page.get("h2_tags", [])

        # H1 Checks
        if not h1_tags:
            issues.append({
                "page_url": url,
                "category": "on_page",
                "severity": "HIGH",
                "issue_code": "MISSING_H1",
                "title": "Missing H1 Heading",
                "description": f"The page {url} does not contain an `<h1>` heading tag.",
                "recommendation_summary": "Add a single, prominent <h1> tag that describes the primary topic of the page.",
                "impact": "H1 headings communicate the main subject matter to both search engines and users."
            })
        elif len(h1_tags) > 1:
            issues.append({
                "page_url": url,
                "category": "on_page",
                "severity": "LOW",
                "issue_code": "MULTIPLE_H1",
                "title": "Multiple H1 Headings",
                "description": f"The page has {len(h1_tags)} `<h1>` tags ({', '.join([repr(h) for h in h1_tags[:3]])}).",
                "recommendation_summary": "Use a single <h1> heading per page for best SEO structural clarity.",
                "impact": "Multiple H1 tags can dilute the primary heading signal."
            })
        else:
            # Check empty H1
            if not h1_tags[0].strip():
                issues.append({
                    "page_url": url,
                    "category": "on_page",
                    "severity": "MEDIUM",
                    "issue_code": "EMPTY_H1",
                    "title": "Empty H1 Heading Tag",
                    "description": f"An `<h1>` tag exists on {url}, but contains no text.",
                    "recommendation_summary": "Populate the <h1> tag with relevant text.",
                    "impact": "Empty heading tags waste valuable structural signals."
                })

        # H2 Checks
        if not h2_tags and page.get("word_count", 0) > 300:
            issues.append({
                "page_url": url,
                "category": "on_page",
                "severity": "LOW",
                "issue_code": "MISSING_H2",
                "title": "Lack of Subheadings (H2)",
                "description": f"Page content has {page.get('word_count')} words but lacks `<h2>` subheadings.",
                "recommendation_summary": "Break content into logical sections with descriptive <h2> subheadings.",
                "impact": "Subheadings improve content readability and semantic indexing."
            })

    return issues
