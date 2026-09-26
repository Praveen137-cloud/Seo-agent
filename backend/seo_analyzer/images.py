from typing import List, Dict, Any

def analyze_images(pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    issues = []

    for page in pages:
        url = page["url"]
        images = page.get("images", [])

        if not images:
            continue

        missing_alt = [img for img in images if not img.get("has_alt")]
        missing_count = len(missing_alt)

        if missing_count > 0:
            severity = "HIGH" if missing_count > 3 else "MEDIUM"
            issues.append({
                "page_url": url,
                "category": "on_page",
                "severity": severity,
                "issue_code": "IMAGES_MISSING_ALT",
                "title": f"Images Missing Alt Text ({missing_count})",
                "description": f"Found {missing_count} out of {len(images)} images on {url} without `alt` text attributes.",
                "recommendation_summary": "Add descriptive alt attributes to all image tags.",
                "impact": "Alt text enables image search indexing and improves accessibility for visual impairment tools."
            })

    return issues
