from typing import List, Dict, Any
from urllib.parse import urlparse

def analyze_images(pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    issues = []

    for page in pages:
        if not page.get("is_fetched", True):
            continue

        url = page["url"]
        images = page.get("images", [])
        parsed_path = urlparse(url).path.rstrip("/") or "/"
        page_label = f"Homepage" if parsed_path == "/" else f"'{parsed_path}'"

        if not images:
            continue

        missing_alt = [img for img in images if not img.get("has_alt")]
        missing_count = len(missing_alt)

        if missing_count > 0:
            sample_srcs = [img.get("src", "") for img in missing_alt[:3]]
            severity = "MEDIUM" if missing_count > 4 else "LOW"
            issues.append({
                "page_url": url,
                "category": "on_page",
                "severity": severity,
                "issue_code": "IMAGES_MISSING_ALT",
                "title": f"Images Missing Alt Text ({missing_count}) on {page_label}",
                "description": f"Found {missing_count} out of {len(images)} images on {url} without `alt` text attributes.",
                "observed_value": f"{missing_count} images without alt text",
                "evidence": f"Sample image sources without alt: {', '.join(sample_srcs)}",
                "recommendation_summary": "Add descriptive alt attributes to all content and product images.",
                "impact": "Alt text enables indexing in Google Image Search and ensures accessibility compliance for screen readers.",
                "verification_status": "verified"
            })

    return issues
