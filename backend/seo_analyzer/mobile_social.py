from typing import List, Dict, Any
from urllib.parse import urlparse

def analyze_mobile_social(pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    issues = []

    for page in pages:
        if not page.get("is_fetched", True):
            continue

        url = page["url"]
        viewport = (page.get("viewport") or "").strip()
        og_tags = page.get("og_tags", {}) or {}
        has_favicon = page.get("has_favicon", False)
        parsed_path = urlparse(url).path.rstrip("/") or "/"
        page_label = f"Homepage" if parsed_path == "/" else f"'{parsed_path}'"

        # 1. Viewport / Mobile Responsiveness
        if not viewport:
            issues.append({
                "page_url": url,
                "category": "technical",
                "severity": "HIGH",
                "issue_code": "MISSING_VIEWPORT",
                "title": f"Missing Mobile Viewport Meta Tag on {page_label}",
                "description": f"The page {url} does not declare a `<meta name='viewport'>` tag.",
                "observed_value": "No viewport meta tag present",
                "evidence": f"<head> of {url} lacks <meta name='viewport'>.",
                "recommendation_summary": "Add `<meta name='viewport' content='width=device-width, initial-scale=1.0'>` to the `<head>`.",
                "impact": "Google uses mobile-first indexing; pages without a responsive viewport suffer mobile ranking penalties.",
                "verification_status": "verified"
            })
        elif "width=device-width" not in viewport:
            issues.append({
                "page_url": url,
                "category": "technical",
                "severity": "LOW",
                "issue_code": "SUBOPTIMAL_VIEWPORT",
                "title": f"Suboptimal Viewport Configuration on {page_label}",
                "description": f"Viewport tag is set to '{viewport}' rather than 'width=device-width, initial-scale=1.0'.",
                "observed_value": f"content='{viewport}'",
                "evidence": f'<meta name="viewport" content="{viewport}">',
                "recommendation_summary": "Configure viewport to 'width=device-width, initial-scale=1.0' for standard mobile rendering.",
                "impact": "Non-standard viewport settings can cause unexpected horizontal scrolling on mobile devices.",
                "verification_status": "verified"
            })

        # 2. Open Graph Tags on Homepage
        if page.get("depth", 0) == 0:
            missing_social = []
            if not og_tags.get("og_title"):
                missing_social.append("og:title")
            if not og_tags.get("og_image"):
                missing_social.append("og:image")
            if not og_tags.get("og_desc"):
                missing_social.append("og:description")

            if len(missing_social) >= 2:
                issues.append({
                    "page_url": url,
                    "category": "on_page",
                    "severity": "LOW",
                    "issue_code": "MISSING_OPEN_GRAPH",
                    "title": f"Missing Open Graph Social Metadata on {page_label}",
                    "description": f"The homepage lacks essential social sharing tags: {', '.join(missing_social)}.",
                    "observed_value": f"Missing {', '.join(missing_social)}",
                    "evidence": f"Head tags missing Open Graph properties: {', '.join(missing_social)}",
                    "recommendation_summary": "Add Open Graph meta tags (og:title, og:description, og:image) for rich social sharing cards.",
                    "impact": "Shared links appear as plain text instead of rich interactive preview cards.",
                    "verification_status": "verified"
                })

            # 3. Favicon on Homepage
            if not has_favicon:
                issues.append({
                    "page_url": url,
                    "category": "technical",
                    "severity": "LOW",
                    "issue_code": "MISSING_FAVICON",
                    "title": f"Missing Favicon Icon on {page_label}",
                    "description": f"No `<link rel='icon'>` favicon tag found on the homepage.",
                    "observed_value": "No favicon link element found",
                    "evidence": "DOM search found no <link rel='icon'> or <link rel='shortcut icon'>.",
                    "recommendation_summary": "Add a modern SVG or PNG favicon link.",
                    "impact": "Favicons appear in Google mobile search results next to URLs; missing favicons reduce visual click appeal.",
                    "verification_status": "verified"
                })

    return issues
